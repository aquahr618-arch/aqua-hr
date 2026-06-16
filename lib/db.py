"""Database access layer for the AQUA HR system.

A fresh short-lived connection is used per call. This is the most robust
pattern with Streamlit's re-run model and Supabase's connection pooler,
and is perfectly fast for a small internal tool.
"""
import psycopg2
import psycopg2.extras
import streamlit as st


def _conn():
    """Open a new connection using the URL stored in Streamlit secrets."""
    return psycopg2.connect(st.secrets["db"]["url"])


def query(sql, params=None):
    """Run a SELECT and return a list of dict rows."""
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def execute(sql, params=None, actor=None):
    """Run an INSERT/UPDATE/DELETE inside one transaction.

    If `actor` (the logged-in username) is given, it is recorded so the
    audit trigger knows WHO made the change.  Returns the new row id when
    the statement ends with `RETURNING id`.
    """
    conn = _conn()
    try:
        with conn:  # commits on success, rolls back on error
            with conn.cursor() as cur:
                if actor:
                    cur.execute("select set_config('app.current_user', %s, true)", (actor,))
                cur.execute(sql, params or ())
                new_id = None
                if cur.description is not None:
                    row = cur.fetchone()
                    if row:
                        new_id = row[0]
                return new_id
    finally:
        conn.close()


def get_employee_map():
    """Return {id: full_name} for dropdowns and display."""
    rows = query("select id, full_name from employees order by id")
    return {r["id"]: r["full_name"] for r in rows}


def get_employee(emp_id):
    """Return a single employee row as dict, or None."""
    if emp_id is None:
        return None
    rows = query("select * from employees where id = %s", (emp_id,))
    return rows[0] if rows else None
