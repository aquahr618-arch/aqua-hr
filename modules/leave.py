from lib.utils import crud_page

COLUMNS = [
    {"name": "employee_id", "label": "Employee", "type": "employee"},
    {"name": "period", "label": "Period (Year)"},
    {"name": "cl", "label": "CL", "type": "number"},
    {"name": "sl", "label": "SL", "type": "number"},
    {"name": "leave_taken", "label": "Leave Taken", "type": "number"},
    {"name": "balance", "label": "Balance", "type": "number"},
    {"name": "wfh", "label": "WFH", "type": "number"},
    {"name": "notes", "label": "Notes", "type": "textarea"},
]

def render():
    crud_page("leave_records", COLUMNS, "Leave Records", icon="🌴")
