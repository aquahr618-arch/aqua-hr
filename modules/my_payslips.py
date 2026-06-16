import streamlit as st
from lib import db, auth
from lib.pdf import build_payslip_pdf


def render():
    st.markdown("## My Payslips")
    emp_id = auth.current_employee_id()
    emp = db.get_employee(emp_id)
    if not emp:
        st.warning("Your login is not linked to an employee record. Contact HR.")
        return

    rows = db.query("select * from payroll where employee_id = %s order by id desc", (emp_id,))
    if not rows:
        st.info("No payslips available yet.")
        return

    for p in rows:
        with st.container(border=True):
            st.write(f"**{p.get('period') or 'Payslip'}**  ·  Net: "
                     f"{p.get('net_salary') if p.get('net_salary') is not None else '-'}")
            st.caption(f"Payment date: {p.get('payment_date') or '-'}")
            pdf_bytes = build_payslip_pdf(emp, p)
            st.download_button("Download PDF", data=pdf_bytes,
                               file_name=f"payslip_{p.get('period') or p['id']}.pdf",
                               mime="application/pdf", key=f"dl_{p['id']}")
