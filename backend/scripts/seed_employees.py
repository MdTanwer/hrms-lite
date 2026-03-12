#!/usr/bin/env python3
"""
Seed 30 realistic employees matching the backend Employee model.
Fields: employee_id (EMP001–EMP030), full_name, email, department, position, status.
Run from backend: python scripts/seed_employees.py
Requires: MongoDB running; .env with MONGODB_URL (default: mongodb://localhost:27017).
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")
except ImportError:
    pass

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "hrms_lite")

try:
    from pymongo import MongoClient
except ImportError:
    print("Install pymongo: pip install pymongo", file=sys.stderr)
    sys.exit(1)

# 30 realistic employees: (full_name, email_local, department, position)
# Email domain must be one of: gmail.com, yahoo.com, outlook.com, hotmail.com, company.com, org.com, net.com
EMPLOYEES = [
    ("James Wilson", "james.wilson", "Engineering", "Software Engineer"),
    ("Sarah Chen", "sarah.chen", "Engineering", "Senior Software Engineer"),
    ("Michael Brown", "michael.brown", "Engineering", "DevOps Engineer"),
    ("Emily Davis", "emily.davis", "Engineering", "Frontend Developer"),
    ("David Martinez", "david.martinez", "Engineering", "Backend Developer"),
    ("Jessica Taylor", "jessica.taylor", "Human Resources", "HR Manager"),
    ("Robert Anderson", "robert.anderson", "Human Resources", "HR Specialist"),
    ("Amanda Thomas", "amanda.thomas", "Human Resources", "Recruiter"),
    ("Daniel Jackson", "daniel.jackson", "Finance", "Financial Analyst"),
    ("Lisa White", "lisa.white", "Finance", "Accountant"),
    ("Christopher Harris", "chris.harris", "Finance", "Finance Manager"),
    ("Jennifer Clark", "jennifer.clark", "Finance", "Payroll Specialist"),
    ("Matthew Lewis", "matthew.lewis", "Marketing", "Marketing Manager"),
    ("Ashley Robinson", "ashley.robinson", "Marketing", "Content Writer"),
    ("Andrew Walker", "andrew.walker", "Marketing", "Digital Marketing Specialist"),
    ("Stephanie Young", "stephanie.young", "Sales", "Sales Manager"),
    ("Kevin Hall", "kevin.hall", "Sales", "Sales Representative"),
    ("Nicole Allen", "nicole.allen", "Sales", "Account Executive"),
    ("Joshua King", "joshua.king", "Operations", "Operations Manager"),
    ("Rachel Wright", "rachel.wright", "Operations", "Logistics Coordinator"),
    ("Ryan Scott", "ryan.scott", "Operations", "Supply Chain Analyst"),
    ("Lauren Green", "lauren.green", "IT", "IT Support Specialist"),
    ("Brandon Adams", "brandon.adams", "IT", "System Administrator"),
    ("Megan Nelson", "megan.nelson", "IT", "Network Engineer"),
    ("Tyler Baker", "tyler.baker", "Engineering", "QA Engineer"),
    ("Samantha Hill", "samantha.hill", "Engineering", "Product Manager"),
    ("Justin Campbell", "justin.campbell", "Legal", "Legal Counsel"),
    ("Hannah Mitchell", "hannah.mitchell", "Legal", "Compliance Officer"),
    ("Nathan Roberts", "nathan.roberts", "Engineering", "Tech Lead"),
    ("Olivia Turner", "olivia.turner", "Human Resources", "Training Coordinator"),
]


def main():
    print(f"Connecting to MongoDB ({MONGODB_DB_NAME})...")
    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    client.admin.command("ping")
    db = client[MONGODB_DB_NAME]
    coll = db["employees"]

    # Delete all existing employees (and rely on attendance being cleared or using Mongo _id)
    result = coll.delete_many({})
    print(f"Deleted {result.deleted_count} existing employee(s).\n")

    now = datetime.now(timezone.utc)
    inserted = 0

    for i, (full_name, email_local, department, position) in enumerate(EMPLOYEES, start=1):
        emp_id = f"EMP{i:03d}"
        # Use company.com for corporate look; must match backend email validator
        email = f"{email_local}@company.com".lower().replace(" ", ".")
        doc = {
            "employee_id": emp_id,
            "full_name": full_name,
            "email": email,
            "department": department,
            "position": position,
            "status": "active",
            "created_at": now,
            "updated_at": now,
        }
        coll.insert_one(doc)
        inserted += 1
        print(f"  + {emp_id} {full_name} ({department})")

    client.close()
    print(f"\nDone. Inserted {inserted} employees.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
