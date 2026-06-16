import datetime
import pandas as pd
import streamlit as st
from lib import db

WINDOW_DAYS = 14
DOC_FIELDS = [("photo", "Photo"), ("bank_proof", "Bank Proof"),
              ("offer_letter", "Offer Letter"), ("appointment_letter", "Appointment Letter")]


def _days_until(d, today):
    """Days until the next occurrence of month/day d, ignoring year."""
    if not d:
        return None
    try:
        nxt = d.replace(year=today.year)
    except ValueError:  # Feb 29
        nxt = d.replace(year=today.year, day=28)
    if nxt < today:
        try:
            nxt = d.replace(year=today.year + 1)
        except ValueError:
            nxt = d.replace(year=today.year + 1, day=28)
    return (nxt - today).days


def render():
    st.markdown("## Dashboard")
    today = datetime.date.today()

    emps = db.query("select * from employees")
    total = len(emps)
    ongoing = len([e for e in emps if (e.get("employment_status") or "") == "Ongoing"])
    depts = len({(e.get("department") or "-") for e in emps})

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Employees", total)
    c2.metric("Active (Ongoing)", ongoing)
    c3.metric("Departments", depts)

    if not emps:
        st.info("No employee data yet. Add records in the Employees tab.")
        return

    # ---- birthdays & anniversaries (next 14 days) ----
    bdays, annis = [], []
    for e in emps:
        d = _days_until(e.get("dob"), today)
        if d is not None and d <= WINDOW_DAYS:
            bdays.append((d, e["full_name"]))
        doj = e.get("date_of_joining")
        dd = _days_until(doj, today)
        if dd is not None and dd <= WINDOW_DAYS:
            years = today.year - doj.year + (1 if dd == 0 else 0)
            annis.append((dd, f"{e['full_name']} ({max(years,0)} yr)"))
    bdays.sort(); annis.sort()

    colA, colB = st.columns(2)
    with colA:
        st.markdown("#### Upcoming birthdays")
        if bdays:
            for d, name in bdays:
                when = "today" if d == 0 else f"in {d} day(s)"
                st.write(f"- {name} — {when}")
        else:
            st.caption("None in the next two weeks.")
    with colB:
        st.markdown("#### Work anniversaries")
        if annis:
            for d, name in annis:
                when = "today" if d == 0 else f"in {d} day(s)"
                st.write(f"- {name} — {when}")
        else:
            st.caption("None in the next two weeks.")

    # ---- pending documents ----
    st.markdown("#### Pending documents")
    docs = db.query("select * from documents")
    doc_by_emp = {d["employee_id"]: d for d in docs}
    pending_rows = []
    for e in emps:
        d = doc_by_emp.get(e["id"])
        missing = []
        for field, label in DOC_FIELDS:
            val = (d or {}).get(field)
            if val in (None, "") or str(val).strip().lower() in ("pending", "no", "n/a"):
                missing.append(label)
        if missing:
            pending_rows.append({"Employee": e["full_name"], "Missing / pending": ", ".join(missing)})
    if pending_rows:
        st.dataframe(pd.DataFrame(pending_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("All tracked documents are in order.")

    # ---- charts ----
    st.divider()
    df = pd.DataFrame(emps)
    a, b = st.columns(2)
    with a:
        st.markdown("#### By Department")
        if "department" in df:
            st.bar_chart(df["department"].fillna("-").value_counts())
    with b:
        st.markdown("#### By Employment Type")
        if "employment_type" in df:
            st.bar_chart(df["employment_type"].fillna("-").value_counts())

    # ---- recent activity ----
    st.divider()
    st.markdown("#### Recent activity")
    logs = db.query("select action_time, app_user, action, table_name, record_id "
                    "from audit_log order by id desc limit 10")
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
    else:
        st.caption("No activity recorded yet.")
