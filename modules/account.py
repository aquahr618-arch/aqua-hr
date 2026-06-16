import streamlit as st
from lib import auth


def render():
    st.markdown("## My Account")
    user = st.session_state.get("auth", {})
    st.markdown(f"**Username:** {user.get('username')}")
    st.markdown(f"**Name:** {user.get('full_name') or '-'}")
    st.markdown(f"**Role:** {user.get('role')}")

    st.divider()
    st.markdown("#### Change password")
    with st.form("change_pw", clear_on_submit=True):
        current = st.text_input("Current password", type="password")
        new1 = st.text_input("New password", type="password")
        new2 = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update password"):
            if new1 != new2:
                st.error("New passwords do not match.")
            else:
                ok, msg = auth.change_own_password(current, new1)
                (st.success if ok else st.error)(msg)
