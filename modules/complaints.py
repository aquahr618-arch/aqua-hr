import pandas as pd
import streamlit as st
from lib import db, auth

CATEGORIES = ["HR", "Payroll", "Workplace", "Suggestion", "Profile Correction", "Other"]
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]


# ---------------- employee view ----------------
def render_employee():
    st.markdown("## My Complaints & Feedback")
    emp_id = auth.current_employee_id()

    with st.expander("Submit new", expanded=True):
        with st.form("new_complaint", clear_on_submit=True):
            category = st.selectbox("Category", CATEGORIES)
            subject = st.text_input("Subject")
            message = st.text_area("Details")
            if st.form_submit_button("Submit"):
                if not subject.strip():
                    st.error("Please add a subject.")
                else:
                    db.execute(
                        "insert into complaints (employee_id, submitted_by, category, "
                        "subject, message) values (%s,%s,%s,%s,%s)",
                        (emp_id, auth.current_user(), category, subject, message),
                        actor=auth.current_user(),
                    )
                    st.success("Submitted. You can track its status below.")
                    st.rerun()

    rows = db.query("select category, subject, status, response, created_at "
                    "from complaints where submitted_by = %s order by id desc",
                    (auth.current_user(),))
    st.markdown("#### My submissions")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Nothing submitted yet.")


# ---------------- HR / MD view ----------------
def render_admin():
    st.markdown("## Complaints & Feedback")
    emp_map = db.get_employee_map()

    flt = st.selectbox("Filter by status", ["All"] + STATUSES)
    where = "" if flt == "All" else "where status = %s"
    params = () if flt == "All" else (flt,)
    rows = db.query(f"select * from complaints {where} order by id desc", params)

    if not rows:
        st.info("No items.")
        return

    for r in rows:
        who = r.get("submitted_by") or emp_map.get(r.get("employee_id"), "?")
        with st.container(border=True):
            st.write(f"**#{r['id']} · {r['subject']}**  ·  _{r['category']}_  ·  "
                     f"status: **{r['status']}**")
            st.caption(f"By {who} on {r['created_at']:%Y-%m-%d}")
            if r.get("message"):
                st.write(r["message"])
            with st.form(f"resp_{r['id']}"):
                new_status = st.selectbox("Status", STATUSES,
                                          index=STATUSES.index(r["status"]),
                                          key=f"st_{r['id']}")
                response = st.text_area("Response / notes", value=r.get("response") or "",
                                        key=f"rs_{r['id']}")
                if st.form_submit_button("Update"):
                    db.execute(
                        "update complaints set status=%s, response=%s, resolved_by=%s "
                        "where id=%s",
                        (new_status, response, auth.current_user(), r["id"]),
                        actor=auth.current_user(),
                    )
                    st.success("Updated.")
                    st.rerun()
