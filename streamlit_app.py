"""AQUA HR - internal HR management system. Streamlit entry point."""
import streamlit as st

from lib import auth
from modules import (dashboard, employees, leave, attendance, payroll, documents,
                     audit_log, users_admin, leave_requests, complaints, notices,
                     my_profile, my_payslips, account)

st.set_page_config(page_title="AQUA HR", page_icon="A", layout="wide")

# light AQUA styling
st.markdown(
    """
    <style>
      .stApp { }
      section[data-testid="stSidebar"] { background-color: #0d6e78; }
      section[data-testid="stSidebar"] * { color: #ffffff; }
      section[data-testid="stSidebar"] .stRadio label { color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)

if not auth.login_form():
    st.stop()

user = st.session_state["auth"]
role = user["role"]

# ---------------- navigation per role ----------------
if role in ("MD", "HR"):
    pages = {
        "Dashboard": dashboard.render,
        "Employees": employees.render,
        "Leave Records": leave.render,
        "Leave Requests": leave_requests.render_admin,
        "Attendance": attendance.render,
        "Payroll": payroll.render,
        "Documents": documents.render,
        "Complaints": complaints.render_admin,
        "Notice Board": notices.render_admin,
        "Audit Log": audit_log.render,
        "Users": users_admin.render,
        "My Account": account.render,
    }
else:  # Employee
    pages = {
        "My Profile": my_profile.render,
        "My Leave Requests": leave_requests.render_employee,
        "My Payslips": my_payslips.render,
        "My Complaints": complaints.render_employee,
        "Notice Board": notices.render_view,
        "My Account": account.render,
    }

with st.sidebar:
    st.markdown("# AQUA HR")
    st.markdown(f"**{user['full_name'] or user['username']}**  \n`{role}`")
    st.divider()
    choice = st.radio("Menu", list(pages.keys()), label_visibility="collapsed")
    st.divider()
    if st.button("Sign out", use_container_width=True):
        auth.logout()

try:
    pages[choice]()
except Exception as e:
    st.error("Something went wrong loading this page.")
    st.exception(e)
