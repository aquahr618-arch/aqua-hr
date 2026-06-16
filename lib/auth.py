"""Login / role handling for AQUA HR.

Passwords are stored only as bcrypt hashes. Login state lives in
st.session_state for the session. Roles: MD, HR, Employee.
"""
import bcrypt
import streamlit as st
from lib import db


def _get_user(username):
    rows = db.query(
        "select * from users where username = %s and is_active = true",
        (username,),
    )
    return rows[0] if rows else None


def verify_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except Exception:
        return False


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def login_form():
    """Render the login screen. Returns True once logged in."""
    if st.session_state.get("auth"):
        return True

    st.markdown("## AQUA HR")
    st.markdown("#### Sign in")
    st.caption("Authorised access only.")

    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        user = _get_user(username.strip())
        if user and verify_password(password, user["password_hash"]):
            st.session_state["auth"] = {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
                "employee_id": user.get("employee_id"),
            }
            st.rerun()
        else:
            st.error("Invalid username or password.")
    return False


def logout():
    st.session_state.pop("auth", None)
    st.rerun()


def current_user():
    return st.session_state.get("auth", {}).get("username")


def current_role():
    return st.session_state.get("auth", {}).get("role")


def current_user_id():
    return st.session_state.get("auth", {}).get("id")


def current_employee_id():
    return st.session_state.get("auth", {}).get("employee_id")


def is_md():
    return current_role() == "MD"


def is_staff():
    """MD or HR (the people who manage data)."""
    return current_role() in ("MD", "HR")


def is_employee():
    return current_role() == "Employee"


def change_own_password(current_pw, new_pw):
    """Verify current password and set a new one. Returns (ok, message)."""
    rows = db.query("select password_hash from users where id = %s", (current_user_id(),))
    if not rows or not verify_password(current_pw, rows[0]["password_hash"]):
        return False, "Current password is incorrect."
    if len(new_pw) < 6:
        return False, "New password must be at least 6 characters."
    db.execute("update users set password_hash = %s where id = %s",
               (hash_password(new_pw), current_user_id()), actor=current_user())
    return True, "Password updated."
