import streamlit as st
from lib import db, auth
from lib.utils import mask

# fields an employee may see about themselves, with labels
VIEW_FIELDS = [
    ("employee_code", "Employee Code"), ("full_name", "Full Name"),
    ("gender", "Gender"), ("dob", "Date of Birth"), ("mobile", "Mobile"),
    ("official_email", "Official Email"), ("personal_email", "Personal Email"),
    ("department", "Department"), ("designation", "Designation"),
    ("reporting_manager", "Reporting Manager"), ("date_of_joining", "Date of Joining"),
    ("employment_type", "Employment Type"), ("employment_status", "Status"),
    ("work_location", "Work Location"), ("bank_name", "Bank Name"),
    ("ifsc", "IFSC"), ("qualification", "Qualification"),
    ("experience_years", "Experience (Years)"), ("skills", "Skills"),
    ("leave_balance", "Leave Balance"),
]
SENSITIVE = [("pan", "PAN"), ("aadhaar", "Aadhaar"), ("account_no", "Account No")]


def render():
    st.markdown("## My Profile")
    emp_id = auth.current_employee_id()
    emp = db.get_employee(emp_id)
    if not emp:
        st.warning("Your login is not linked to an employee record yet. Please contact HR.")
        return

    st.caption("This is your record on file. To fix anything, use 'Request a correction' below.")

    col1, col2 = st.columns(2)
    half = len(VIEW_FIELDS) // 2 + 1
    for i, (field, label) in enumerate(VIEW_FIELDS):
        target = col1 if i < half else col2
        val = emp.get(field)
        target.markdown(f"**{label}:** {'' if val is None else val}")

    st.markdown("#### Identity & bank (masked)")
    for field, label in SENSITIVE:
        st.markdown(f"**{label}:** {mask(emp.get(field))}")

    st.divider()
    with st.expander("Request a correction"):
        with st.form("correction", clear_on_submit=True):
            field = st.selectbox("Which detail is wrong?",
                                 [lbl for _, lbl in VIEW_FIELDS + SENSITIVE])
            correct = st.text_input("What should it be?")
            note = st.text_area("Any extra detail (optional)")
            if st.form_submit_button("Send to HR"):
                msg = f"Requested correction for '{field}'. Correct value: {correct}. {note}"
                db.execute(
                    "insert into complaints (employee_id, submitted_by, category, subject, message) "
                    "values (%s,%s,'Profile Correction',%s,%s)",
                    (emp_id, auth.current_user(), f"Correction: {field}", msg),
                    actor=auth.current_user(),
                )
                st.success("Sent to HR. You can track it under 'My Complaints'.")
