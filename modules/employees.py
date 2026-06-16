from lib.utils import crud_page

GENDER = ["", "Male", "Female", "Other"]
EMP_TYPE = ["", "Full-Time", "Part-Time", "Intern", "Contract", "Consultant"]
STATUS = ["", "Ongoing", "On Notice", "Exited", "On Leave"]

COLUMNS = [
    {"name": "employee_code", "label": "Employee Code"},
    {"name": "full_name", "label": "Full Name"},
    {"name": "gender", "label": "Gender", "type": "select", "options": GENDER},
    {"name": "dob", "label": "Date of Birth", "type": "date"},
    {"name": "mobile", "label": "Mobile"},
    {"name": "official_email", "label": "Official Email"},
    {"name": "personal_email", "label": "Personal Email"},
    {"name": "department", "label": "Department"},
    {"name": "designation", "label": "Designation"},
    {"name": "reporting_manager", "label": "Reporting Manager"},
    {"name": "date_of_joining", "label": "Date of Joining", "type": "date"},
    {"name": "employment_type", "label": "Employment Type", "type": "select", "options": EMP_TYPE},
    {"name": "employment_status", "label": "Employment Status", "type": "select", "options": STATUS},
    {"name": "work_location", "label": "Work Location"},
    {"name": "pan", "label": "PAN", "sensitive": True},
    {"name": "aadhaar", "label": "Aadhaar", "sensitive": True},
    {"name": "uan", "label": "UAN"},
    {"name": "pf_no", "label": "PF No"},
    {"name": "esic_no", "label": "ESIC No"},
    {"name": "bank_name", "label": "Bank Name"},
    {"name": "account_no", "label": "Account No", "sensitive": True},
    {"name": "ifsc", "label": "IFSC"},
    {"name": "ctc", "label": "CTC", "type": "number"},
    {"name": "notice_period", "label": "Notice Period"},
    {"name": "emergency_contact", "label": "Emergency Contact"},
    {"name": "emergency_phone", "label": "Emergency Phone"},
    {"name": "qualification", "label": "Qualification"},
    {"name": "experience_years", "label": "Experience (Years)", "type": "number"},
    {"name": "skills", "label": "Skills", "type": "textarea"},
    {"name": "last_appraisal", "label": "Last Appraisal"},
    {"name": "next_appraisal", "label": "Next Appraisal"},
    {"name": "leave_balance", "label": "Leave Balance", "type": "number"},
    {"name": "remarks", "label": "Remarks", "type": "textarea"},
]


def render():
    crud_page("employees", COLUMNS, "Employees", icon="👥")
