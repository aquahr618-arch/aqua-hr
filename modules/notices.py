import pandas as pd
import streamlit as st
from lib import db, auth


def render_view():
    """Everyone sees active notices."""
    st.markdown("## Notice Board")
    rows = db.query("select title, body, posted_by, created_at from notices "
                    "where is_active = true order by id desc")
    if not rows:
        st.info("No notices right now.")
        return
    for n in rows:
        with st.container(border=True):
            st.markdown(f"### {n['title']}")
            st.caption(f"{n.get('posted_by') or ''} · {n['created_at']:%Y-%m-%d}")
            if n.get("body"):
                st.write(n["body"])


def render_admin():
    """HR/MD post and manage notices."""
    st.markdown("## Notice Board")

    with st.expander("Post a new notice", expanded=True):
        with st.form("new_notice", clear_on_submit=True):
            title = st.text_input("Title")
            body = st.text_area("Message")
            if st.form_submit_button("Post"):
                if not title.strip():
                    st.error("Title is required.")
                else:
                    db.execute("insert into notices (title, body, posted_by) "
                               "values (%s,%s,%s)",
                               (title, body, auth.current_user()), actor=auth.current_user())
                    st.success("Notice posted.")
                    st.rerun()

    st.markdown("#### All notices")
    rows = db.query("select * from notices order by id desc")
    if not rows:
        st.info("No notices yet.")
        return
    for n in rows:
        with st.container(border=True):
            state = "active" if n["is_active"] else "hidden"
            st.markdown(f"**{n['title']}**  ·  _{state}_")
            st.caption(f"{n.get('posted_by') or ''} · {n['created_at']:%Y-%m-%d}")
            if n.get("body"):
                st.write(n["body"])
            c1, c2, _ = st.columns([1, 1, 4])
            toggle = "Hide" if n["is_active"] else "Show"
            if c1.button(toggle, key=f"tg_{n['id']}"):
                db.execute("update notices set is_active = %s where id = %s",
                           (not n["is_active"], n["id"]), actor=auth.current_user())
                st.rerun()
            if auth.is_md() and c2.button("Delete", key=f"del_{n['id']}"):
                db.execute("delete from notices where id = %s", (n["id"],),
                           actor=auth.current_user())
                st.rerun()
