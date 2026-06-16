"""Create a login account for AQUA HR.

Run this on your own computer AFTER creating the tables (schema.sql).
It asks for the password interactively so the password is never written
into any file or seen by anyone else.

Usage:
    set DATABASE_URL first (the Supabase connection string), then:
    python scripts/seed_users.py
"""
import getpass
import os
import sys

import bcrypt
import psycopg2

URL = os.environ.get("DATABASE_URL")
if not URL:
    sys.exit("Please set the DATABASE_URL environment variable first.")

print("=== Create an AQUA HR login ===")
username = input("Username: ").strip()
full_name = input("Full name: ").strip()
email = input("Email: ").strip()
role = ""
while role not in ("MD", "HR"):
    role = input("Role (MD/HR): ").strip().upper()

pw1 = getpass.getpass("Password: ")
pw2 = getpass.getpass("Confirm password: ")
if pw1 != pw2 or not pw1:
    sys.exit("Passwords empty or do not match. Nothing was created.")

pw_hash = bcrypt.hashpw(pw1.encode(), bcrypt.gensalt()).decode()

conn = psycopg2.connect(URL)
with conn, conn.cursor() as cur:
    cur.execute("select 1 from users where username = %s", (username,))
    if cur.fetchone():
        sys.exit(f"User '{username}' already exists.")
    cur.execute(
        "insert into users (username, full_name, email, password_hash, role) "
        "values (%s,%s,%s,%s,%s)",
        (username, full_name, email, pw_hash, role),
    )
conn.close()
print(f"\n✅ Created {role} login '{username}'. You can now sign in to the app.")
