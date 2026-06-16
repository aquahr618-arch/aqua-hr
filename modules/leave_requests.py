import datetime
import pandas as pd
import streamlit as st
from lib import db, auth

LEAVE_TYPES = ["CL", "SL", "WFH", "Other"]


def _apply_balance(employee_id, leave_type, num_days):
    """On approval, adjust this year's leave_records for CL/SL."""
    if leave_type not in ("CL", "SL"):
        return
    period = str(datetime.date.today().year)
    db.execute(
        "update leave_records set leave_taken = coalesce(leave_taken,0) + %s, "
        "balance = coalesce(balance,0) - %s where employee_id = %s and period = %s",
        (num_days, num_days, employee_id, period), actor=auth.current_user(),
    )


# ---------------- employee view ----------------
def render_employee():
    st.markdown("## My Leave Requests")
    emp_id = auth.current_employee_id()
    if not emp_id:
        st.warning("Your login is not linked to an employee record. Contact HR.")
        return

    with st.expander("Apply for leave", expanded=True):
        with st.form("apply_leave", clear_on_submit=True):
            ltype = st.selectbox("Type", LEAVE_TYPES)
            c1, c2 = st.columns(2)
            frm = c1.date_input("From", value=datetime.date.today())
            to = c2.date_input("To", value=datetime.date.today())
            reason = st.text_area("Reason")
            if st.form_submit_button("Submit request"):
                if to < frm:
                    st.error("'To' date cannot be before 'From' date.")
                else:
                    days = (to - frm).days + 1
                    db.execute(
                        "insert into leave_requests (employee_id, leave_type, from_date, "
                        "to_date, num_days, reason) values (%s,%s,%s,%s,%s,%s)",
                        (emp_id, ltype, frm, to, days, reason), actor=auth.current_user(),
                    )
                    st.success("Leave request submitted.")
                    st.rerun()

    rows = db.query("select leave_type, from_date, to_date, num_days, status, "
                    "reason, decided_by from leave_requests where employee_id = %s "
                    "order by id desc", (emp_id,))
    st.markdown("#### My requests")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No requests yet.")


# ---------------- HR / MD view ----------------
def render_admin():
    st.markdown("## Leave Requests")
    emp_map = db.get_employee_map()
    pending = db.query("select * from leave_requests where status = 'Pending' order by id")

    st.markdown("#### Pending approvals")
    if not pending:
        st.info("No pending requests.")
    for r in pending:
        name = emp_map.get(r["employee_id"], "?")
        with st.container(border=True):
            st.write(f"**{name}** — {r['leave_type']} | "
                     f"{r['from_date']} to {r['to_date']} ({r['num_days']} day(s))")
            if r.get("reason"):
                st.caption(r["reason"])
            c1, c2, _ = st.columns([1, 1, 4])
            if c1.button("Approve", key=f"ap_{r['id']}"):
                db.execute("update leave_requests set status='Approved', decided_by=%s, "
                           "decided_at=now() where id=%s",
                           (auth.current_user(), r["id"]), actor=auth.current_user())
                _apply_balance(r["employee_id"], r["leave_type"], r["num_days"])
                st.rerun()
            if c2.button("Reject", key=f"rj_{r['id']}"):
                db.execute("update leave_requests set status='Rejected', decided_by=%s, "
                           "decided_at=now() where id=%s",
                           (auth.current_user(), r["id"]), actor=auth.current_user())
                st.rerun()

    st.divider()
    st.markdown("#### All requests")
    allrows = db.query("select * from leave_requests order by id desc")
    if allrows:
        disp = []
        for r in allrows:
            disp.append({"ID": r["id"], "Employee": emp_map.get(r["employee_id"], "?"),
                         "Type": r["leave_type"], "From": r["from_date"], "To": r["to_date"],
                         "Days": r["num_days"], "Status": r["status"],
                         "Decided by": r["decided_by"]})
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)
