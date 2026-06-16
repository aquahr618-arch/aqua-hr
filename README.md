# AQUA HR — Internal HR Management System

A login-protected web app that replaces the Excel HR tracker. Built with
Streamlit + Supabase (PostgreSQL). Three roles — MD, HR, Employee — and a full
audit log of every change. Runs on free tiers (about ₹0/month at your size).

---

## Features

**For HR / MD**
- Employees, Leave Records, Attendance, Payroll, Documents (view / add / edit / delete)
- Leave Requests — approve or reject employee leave (auto-adjusts CL/SL balance)
- Complaints & Feedback — review, respond, change status
- Notice Board — post announcements everyone sees
- Payslip PDF — generate a clean salary slip for any payroll record
- Dashboard — headcount, upcoming birthdays & work anniversaries, pending-document
  alerts, charts, recent activity
- Audit Log — who changed what, when, old value → new value
- User Management — create logins, link employees, reset passwords, enable/disable

**For Employees**
- My Profile — view own record (Aadhaar/bank masked) and request corrections
- My Leave Requests — apply for leave and track status
- My Payslips — view and download payslip PDFs
- My Complaints & Feedback — submit and track
- Notice Board — read announcements
- My Account — change own password

**Roles:** MD = everything (incl. delete + manage all users). HR = manage HR data,
approve leave, handle complaints, manage Employee logins. Employee = self-service only.

---

## Cost

Everything below runs on **free tiers — ₹0/month**. Optional: a custom domain
(~₹1,000/year). Passwords use our own hashing (no paid auth service), and payslip
PDFs are generated in-app (no paid service), so adding all employees costs nothing.

---

## One-time setup (in order)

You will create **3 free accounts**: GitHub, Supabase, Streamlit.

### Step 1 — Put the code on GitHub
1. Create a free account at github.com.
2. New repository → name `aqua-hr` → **Private** → Create.
3. Upload the unzipped project files (drag-and-drop in GitHub's upload page, or use Git).
   > Do not upload your real Excel file or any `secrets.toml`. The included
   > `.gitignore` already blocks them.

### Step 2 — Create the database (Supabase)
1. Free account at supabase.com → New project. Pick a nearby region
   (Mumbai/Singapore), set a strong database password and **save it**.
2. Open **SQL Editor** → New query → paste all of `scripts/schema.sql` → **Run**.
   This creates every table, the audit log, and the triggers.
3. Click **Connect** → copy the **connection string (URI)**. Replace
   `[YOUR-PASSWORD]` with your database password. This is your `DATABASE_URL`.

### Step 3 — Load data & create the first MD login (from your computer)
Needs Python installed.

```bash
pip install -r requirements.txt

# Windows PowerShell:  $env:DATABASE_URL="postgresql://...:6543/postgres"
# Mac/Linux:           export DATABASE_URL="postgresql://...:6543/postgres"

python scripts/seed_users.py        # creates your first login (choose role MD)
python scripts/migrate_excel.py "Professional_HR_Employee_Tracker_Template.xlsx"
```
Add `--dry-run` to the migrate command to preview first.

### Step 4 — Deploy the website (Streamlit)
1. Free account at share.streamlit.io, connected to GitHub.
2. Create app → pick the `aqua-hr` repo → main file `streamlit_app.py` → Deploy.
3. App **Settings → Secrets** → paste:
   ```toml
   [db]
   url = "postgresql://postgres.xxxx:[YOUR-PASSWORD]@aws-0-xx.pooler.supabase.com:6543/postgres"
   ```
4. The app restarts. Sign in with the MD login from Step 3.

### Step 5 — Create the other logins (inside the app)
Open **Users**:
- Create HR logins (role HR).
- Create Employee logins (role Employee) and **link each to its employee record**
  from the dropdown — that is what powers "My Profile" and "My Payslips".
- Share the app URL with staff. Anyone can open the URL, but only valid logins
  get past the sign-in screen.

Done. The URL looks like `https://aqua-hr.streamlit.app` and works on phone or
laptop. On a phone: browser menu → "Add to Home screen" for an app-like icon.

---

## Who has access to what

| Place | Who | Purpose |
|---|---|---|
| App URL | MD, HR, Employees | Use the app, per role |
| Supabase console | You / MD | Raw data, audit log, backups |
| GitHub repo | You / developer | The code |
| Streamlit console | You / MD | Deploy & manage the app |

Employees only ever see their own data. HR/MD never touch the database or code directly.

---

## Password handling (no email service needed)
- Anyone can change their own password under **My Account**.
- If someone is locked out, MD (or HR for employees) resets it from **Users**.
- True "forgot password — email me a link" would need an email service; not
  included because it would add setup. The reset-by-admin flow covers it for free.

---

## Keeping it safe
- Never commit `secrets.toml` or the real Excel (the `.gitignore` blocks them).
- Supabase free tier has no auto-backups — periodically export from
  Supabase → Database. A free project pauses after ~1 week idle; daily use avoids this.
- This data is sensitive (Aadhaar/PAN/bank/salary) under India's DPDP Act 2023:
  keep the repo private, share the app only with staff, mask sensitive fields
  (already done in the UI), and limit who can export the full database.

---

## Local testing (optional)
```bash
pip install -r requirements.txt
# copy .streamlit/secrets.toml.example -> .streamlit/secrets.toml and fill in the url
streamlit run streamlit_app.py
```

---

## Project structure
```
streamlit_app.py        entry: login + role-based navigation + theme
.streamlit/config.toml  AQUA colour theme
lib/  db.py             database access (audited writes)
      auth.py           login, roles, password change
      utils.py          masking + reusable CRUD page
      pdf.py            payslip PDF generator
modules/                dashboard, employees, leave, attendance, payroll,
                        documents, leave_requests, complaints, notices,
                        my_profile, my_payslips, account, audit_log, users_admin
scripts/ schema.sql     run once in Supabase
         seed_users.py  create the first login
         migrate_excel.py  import the Excel
```
