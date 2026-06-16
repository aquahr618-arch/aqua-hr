import streamlit as st
from lib.utils import crud_page
from lib import db, auth
from lib.pdf import build_payslip_pdf

COLUMNS = [
    {"name": "employee_id", "label": "Employee", "type": "employee"},
    {"name": "period", "label": "Period (YYYY-MM)"},
    {"name": "gross", "label": "Gross", "type": "number"},
    {"name": "pf", "label": "PF"},
    {"name": "esic", "label": "ESIC"},
    {"name": "tds", "label": "TDS"},
    {"name": "deductions", "label": "Deductions"},
    {"name": "net_salary", "label": "Net Salary", "type": "number"},
    {"name": "payment_date", "label": "Payment Date"},
]


def render():
    crud_page("payroll", COLUMNS, "Payroll")

    st.divider()
    st.markdown("#### Generate a payslip PDF")
    rows = db.query("select * from payroll order by id desc")
    emp_map = db.get_employee_map()
    if not rows:
        st.caption("Add a payroll record first.")
        return
    opts = {f"#{r['id']} - {emp_map.get(r['employee_id'],'?')} ({r.get('period') or ''})": r
            for r in rows}
    pick = st.selectbox("Choose a payroll record", list(opts.keys()))
    pay = opts[pick]
    emp = db.get_employee(pay["employee_id"])
    if emp:
        pdf_bytes = build_payslip_pdf(emp, pay)
        st.download_button("Download payslip PDF", data=pdf_bytes,
                           file_name=f"payslip_{emp['full_name'].replace(' ','_')}_{pay.get('period') or pay['id']}.pdf",
                           mime="application/pdf")
