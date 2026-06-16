import pandas as pd
import streamlit as st
from lib import db


def render():
    st.markdown("## 🧾 Audit Log")
    st.caption("Every change to employee data is recorded here — who, what, when, and the before/after values.")

    c1, c2, c3 = st.columns(3)
    table = c1.selectbox("Table", ["All", "employees", "leave_records",
                                  "attendance", "payroll", "documents"])
    action = c2.selectbox("Action", ["All", "INSERT", "UPDATE", "DELETE"])
    limit = c3.number_input("Rows", min_value=10, max_value=1000, value=100, step=10)

    where, params = [], []
    if table != "All":
        where.append("table_name = %s"); params.append(table)
    if action != "All":
        where.append("action = %s"); params.append(action)
    clause = ("where " + " and ".join(where)) if where else ""

    logs = db.query(
        f"select action_time, app_user, action, table_name, record_id, "
        f"field_name, old_value, new_value from audit_log {clause} "
        f"order by id desc limit %s",
        tuple(params) + (int(limit),),
    )
    if logs:
        st.dataframe(pd.DataFrame(logs), use_container_width=True, hide_index=True)
        st.caption(f"{len(logs)} entries shown.")
    else:
        st.info("No matching audit entries.")
