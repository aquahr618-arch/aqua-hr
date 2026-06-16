from lib.utils import crud_page

COLUMNS = [
    {"name": "employee_id", "label": "Employee", "type": "employee"},
    {"name": "month", "label": "Month"},
    {"name": "present", "label": "Present", "type": "number"},
    {"name": "absent", "label": "Absent", "type": "number"},
    {"name": "late", "label": "Late", "type": "number"},
    {"name": "wfh", "label": "WFH", "type": "number"},
    {"name": "overtime", "label": "Overtime", "type": "number"},
]

def render():
    crud_page("attendance", COLUMNS, "Attendance", icon="🗓️")
