"""Shared UI helpers: sensitive-data masking and a reusable CRUD page.

Every module (employees, leave, attendance, payroll, documents) describes its
columns with a small spec and calls `crud_page(...)`. That keeps each module
short while every write still flows through the audited db.execute().
"""
import datetime
import pandas as pd
import streamlit as st

from lib import db, auth


# ---------------------------------------------------------------- masking
def mask(value, visible=4):
    """Mask all but the last `visible` characters (for Aadhaar, account no.)."""
    if value is None or value == "":
        return ""
    s = str(value).replace(" ", "")
    if len(s) <= visible:
        return "•" * len(s)
    return "•" * (len(s) - visible) + s[-visible:]


# ---------------------------------------------------------------- field input
def _render_input(col, value, prefix="f"):
    """Render the right Streamlit widget for one column, return its value."""
    label = col["label"]
    ctype = col.get("type", "text")
    key = f"{prefix}_{col['name']}"

    if ctype == "employee":
        emp = db.get_employee_map()
        ids = list(emp.keys())
        if not ids:
            st.warning("Add employees first.")
            return None
        idx = ids.index(value) if value in ids else 0
        return st.selectbox(label, ids, index=idx,
                            format_func=lambda i: f"{i} — {emp[i]}", key=key)
    if ctype == "select":
        opts = col["options"]
        idx = opts.index(value) if value in opts else 0
        return st.selectbox(label, opts, index=idx, key=key)
    if ctype == "number":
        v = float(value) if value not in (None, "") else 0.0
        out = st.number_input(label, value=v, step=1.0, key=key)
        return out
    if ctype == "date":
        v = value if isinstance(value, (datetime.date, datetime.datetime)) else None
        out = st.date_input(label, value=v, key=key)
        return out
    if ctype == "textarea":
        return st.text_area(label, value=value or "", key=key)
    return st.text_input(label, value="" if value is None else str(value), key=key)


# ---------------------------------------------------------------- main builder
def crud_page(table, columns, title, icon=""):
    """Render a full view / add / edit / delete page for one table.

    columns: list of dicts -> {name, label, type, sensitive?, options?}
    """
    st.markdown(f"## {title}")
    role = auth.current_role()
    actor = auth.current_user()
    emp_map = db.get_employee_map()

    rows = db.query(f"select * from {table} order by id")

    # ----- reveal toggle for sensitive columns
    sensitive_cols = [c["name"] for c in columns if c.get("sensitive")]
    reveal = False
    if sensitive_cols:
        reveal = st.toggle("Reveal sensitive fields (Aadhaar / bank)", value=False)

    # ----- search
    term = st.text_input("Search", "").strip().lower()

    # ----- build display table
    display = []
    for r in rows:
        d = {}
        for c in columns:
            n = c["name"]
            val = r.get(n)
            if n == "employee_id":
                val = f"{val} — {emp_map.get(val, '?')}"
            elif c.get("sensitive") and not reveal:
                val = mask(val)
            d[c["label"]] = val
        d["_id"] = r["id"]
        display.append(d)

    if term:
        display = [d for d in display
                  if any(term in str(v).lower() for v in d.values())]

    if display:
        df = pd.DataFrame(display).set_index("_id")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records yet.")

    st.divider()

    # ----- ADD  (HR and MD)
    with st.expander(f"Add new {title[:-1] if title.endswith('s') else title}"):
        with st.form(f"add_{table}", clear_on_submit=True):
            new_vals = {}
            for c in columns:
                new_vals[c["name"]] = _render_input(c, None, prefix=f"add_{table}")
            if st.form_submit_button("Save new record"):
                cols = list(new_vals.keys())
                placeholders = ", ".join(["%s"] * len(cols))
                sql = (f"insert into {table} ({', '.join(cols)}) "
                       f"values ({placeholders}) returning id")
                db.execute(sql, tuple(_clean(new_vals[c]) for c in cols), actor=actor)
                st.success("Record added.")
                st.rerun()

    # ----- EDIT / DELETE
    if rows:
        with st.expander("Edit or delete a record"):
            ids = [r["id"] for r in rows]
            def _label(i):
                row = next(r for r in rows if r["id"] == i)
                name = row.get("full_name") or emp_map.get(row.get("employee_id"), "")
                return f"#{i}  {name}"
            sel = st.selectbox("Choose record", ids, format_func=_label, key=f"sel_{table}")
            current = next(r for r in rows if r["id"] == sel)

            with st.form(f"edit_{table}"):
                edit_vals = {}
                for c in columns:
                    edit_vals[c["name"]] = _render_input(c, current.get(c["name"]), prefix=f"edit_{table}")
                c1, c2 = st.columns(2)
                save = c1.form_submit_button("Update record")
                delete = c2.form_submit_button("Delete", type="secondary",
                                              disabled=not auth.is_md(),
                                              help="Only MD can delete")
            if save:
                sets = ", ".join(f"{c['name']} = %s" for c in columns)
                sql = f"update {table} set {sets} where id = %s"
                params = tuple(_clean(edit_vals[c["name"]]) for c in columns) + (sel,)
                db.execute(sql, params, actor=actor)
                st.success("Record updated.")
                st.rerun()
            if delete and auth.is_md():
                db.execute(f"delete from {table} where id = %s", (sel,), actor=actor)
                st.success("Record deleted.")
                st.rerun()


def _clean(v):
    """Normalise empty widget values to NULL."""
    if v == "" or v is None:
        return None
    return v
