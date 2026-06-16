import pandas as pd
import streamlit as st
from lib import db, auth


def render():
    st.markdown("## User Management")
    if not auth.is_staff():
        st.warning("Not authorised.")
        return

    md = auth.is_md()
    emp_map = db.get_employee_map()

    users = db.query("select id, username, full_name, email, role, employee_id, "
                     "is_active, created_at from users order by id")
    if users:
        disp = []
        for u in users:
            disp.append({"ID": u["id"], "Username": u["username"], "Name": u["full_name"],
                         "Role": u["role"],
                         "Linked employee": emp_map.get(u["employee_id"], ""),
                         "Active": u["is_active"]})
        st.dataframe(pd.DataFrame(disp), use_container_width=True, hide_index=True)

    # ---------------- create ----------------
    st.divider()
    st.markdown("#### Add a new login")
    allowed_roles = ["MD", "HR", "Employee"] if md else ["Employee"]
    if not md:
        st.caption("HR can create Employee logins. Ask MD to create HR/MD logins.")

    with st.form("add_user", clear_on_submit=True):
        username = st.text_input("Username")
        full_name = st.text_input("Full name")
        email = st.text_input("Email")
        role = st.selectbox("Role", allowed_roles)
        link_id = None
        ids = list(emp_map.keys())
        # link to an employee record (required for Employee role)
        link_choice = st.selectbox(
            "Link to employee record (required for Employee role)",
            ["(none)"] + ids,
            format_func=lambda i: i if i == "(none)" else f"{i} - {emp_map[i]}",
        )
        if link_choice != "(none)":
            link_id = link_choice
        pw1 = st.text_input("Password", type="password")
        pw2 = st.text_input("Confirm password", type="password")
        submit = st.form_submit_button("Create user")

    if submit:
        if not username or not pw1:
            st.error("Username and password are required.")
        elif pw1 != pw2:
            st.error("Passwords do not match.")
        elif role == "Employee" and link_id is None:
            st.error("Employee logins must be linked to an employee record.")
        elif db.query("select 1 from users where username = %s", (username.strip(),)):
            st.error("That username already exists.")
        else:
            db.execute(
                "insert into users (username, full_name, email, password_hash, role, employee_id) "
                "values (%s,%s,%s,%s,%s,%s)",
                (username.strip(), full_name, email, auth.hash_password(pw1), role, link_id),
                actor=auth.current_user(),
            )
            st.success(f"User '{username}' created.")
            st.rerun()

    if not users:
        return

    # who the current actor may manage
    def manageable(u):
        if md:
            return True
        return u["role"] == "Employee"   # HR manages employees only

    targets = [u for u in users if manageable(u) and u["id"] != auth.current_user_id()]

    # ---------------- reset password ----------------
    st.divider()
    st.markdown("#### Reset a user's password")
    if targets:
        opts = {f"{u['username']} ({u['role']})": u for u in targets}
        pick = st.selectbox("User", list(opts.keys()), key="reset_pick")
        with st.form("reset_pw", clear_on_submit=True):
            np1 = st.text_input("New password", type="password")
            np2 = st.text_input("Confirm", type="password")
            if st.form_submit_button("Reset password"):
                if np1 != np2 or len(np1) < 6:
                    st.error("Passwords must match and be at least 6 characters.")
                else:
                    db.execute("update users set password_hash = %s where id = %s",
                               (auth.hash_password(np1), opts[pick]["id"]),
                               actor=auth.current_user())
                    st.success(f"Password reset for {opts[pick]['username']}.")
    else:
        st.caption("No accounts you can reset.")

    # ---------------- enable / disable ----------------
    st.divider()
    st.markdown("#### Enable / disable a login")
    if targets:
        opts2 = {f"{u['username']} ({u['role']})": u for u in targets}
        pick2 = st.selectbox("Account", list(opts2.keys()), key="toggle_pick")
        u = opts2[pick2]
        new_state = not u["is_active"]
        if st.button(("Enable" if new_state else "Disable") + " this user"):
            db.execute("update users set is_active = %s where id = %s",
                       (new_state, u["id"]), actor=auth.current_user())
            st.success(f"{u['username']} {'enabled' if new_state else 'disabled'}.")
            st.rerun()
    else:
        st.caption("No accounts you can change.")
