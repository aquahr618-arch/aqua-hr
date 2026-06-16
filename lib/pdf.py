"""Generate a simple, clean salary-slip PDF from a payroll row."""
from fpdf import FPDF

TEAL = (13, 110, 120)


def _money(v):
    if v in (None, ""):
        return "-"
    try:
        return f"INR {float(v):,.2f}"
    except (ValueError, TypeError):
        return str(v)


def build_payslip_pdf(employee, pay):
    """employee: dict from employees table; pay: dict from payroll table.
    Returns PDF bytes."""
    pdf = FPDF(format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # header band
    pdf.set_fill_color(*TEAL)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 16, "AQUA", ln=1, align="L", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, f"Salary Slip - {pay.get('period') or ''}", ln=1)
    pdf.ln(2)

    # employee block
    pdf.set_font("Helvetica", "", 11)
    info = [
        ("Employee", employee.get("full_name", "")),
        ("Employee Code", employee.get("employee_code") or str(employee.get("id", ""))),
        ("Designation", employee.get("designation") or "-"),
        ("Department", employee.get("department") or "-"),
        ("Payment Date", pay.get("payment_date") or "-"),
    ]
    for label, value in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(45, 8, f"{label}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value), ln=1)
    pdf.ln(4)

    # earnings / deductions table
    def row(label, value, header=False):
        if header:
            pdf.set_fill_color(*TEAL)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 11)
        else:
            pdf.set_fill_color(245, 245, 245)
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Helvetica", "", 11)
        pdf.cell(120, 9, str(label), border=1, fill=True)
        pdf.cell(60, 9, str(value), border=1, ln=1, fill=True, align="R")

    row("Component", "Amount", header=True)
    row("Gross", _money(pay.get("gross")))
    row("PF", str(pay.get("pf") or "-"))
    row("ESIC", str(pay.get("esic") or "-"))
    row("TDS", str(pay.get("tds") or "-"))
    row("Other Deductions", str(pay.get("deductions") or "-"))

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(225, 240, 240)
    pdf.cell(120, 11, "Net Salary", border=1, fill=True)
    pdf.cell(60, 11, _money(pay.get("net_salary")), border=1, ln=1, fill=True, align="R")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(110, 110, 110)
    pdf.multi_cell(0, 5, "This is a system-generated salary slip from AQUA HR and "
                         "does not require a signature.")

    out = pdf.output()
    return bytes(out)
