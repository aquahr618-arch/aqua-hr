from lib.utils import crud_page

STAT = ["", "Given", "Pending", "Yes", "No", "N/A"]

COLUMNS = [
    {"name": "employee_id", "label": "Employee", "type": "employee"},
    {"name": "pan", "label": "PAN", "sensitive": True},
    {"name": "aadhaar", "label": "Aadhaar", "sensitive": True},
    {"name": "photo", "label": "Photo", "type": "select", "options": STAT},
    {"name": "education", "label": "Education"},
    {"name": "experience", "label": "Experience"},
    {"name": "bank_proof", "label": "Bank Proof", "type": "select", "options": STAT},
    {"name": "offer_letter", "label": "Offer Letter", "type": "select", "options": STAT},
    {"name": "appointment_letter", "label": "Appointment Letter", "type": "select", "options": STAT},
]

def render():
    crud_page("documents", COLUMNS, "Documents", icon="📁")
