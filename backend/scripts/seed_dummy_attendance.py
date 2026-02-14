#!/usr/bin/env python3
"""
Seed realistic attendance records. employee_id is stored as BSON ObjectId (employee's _id).
Covers 3 calendar months; only weekdays (Mon–Fri). Realistic distribution.
Run from backend: python scripts/seed_dummy_attendance.py
Requires: MongoDB (e.g. Atlas); employees seeded first (e.g. python scripts/seed_employees.py).
"""
import os
import random
import sys
from datetime import datetime, date, timedelta, timezone
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

# Realistic weights: present 88%, leave 5%, half-day 4%, absent 3%
STATUS_WEIGHTS = [
    ("present", 88),
    ("leave", 5),
    ("half-day", 4),
    ("absent", 3),
]

# Dec 2025 through 5 Feb 2026 only (no attendance records after 5 Feb)
START_DATE = date(2025, 12, 1)
END_DATE = date(2026, 2, 5)


def date_range(start: date, end: date):
    """Inclusive date range."""
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def weekday_dates(start: date, end: date):
    """Yield only Mon–Fri in [start, end]."""
    for d in date_range(start, end):
        if d.weekday() < 5:  # 0=Mon .. 4=Fri
            yield d


def weighted_status(rng: random.Random):
    """Pick status from STATUS_WEIGHTS."""
    total = sum(w for _, w in STATUS_WEIGHTS)
    r = rng.randint(1, total)
    for status, weight in STATUS_WEIGHTS:
        r -= weight
        if r <= 0:
            return status
    return "present"


def main():
    print(f"Connecting to MongoDB ({MONGODB_DB_NAME})...")
    client = MongoClient(
        MONGODB_URL,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )
    client.admin.command("ping")
    db = client[MONGODB_DB_NAME]
    employees_coll = db["employees"]
    attendance_coll = db["attendance"]

    # 1) Delete all existing attendance records
    result = attendance_coll.delete_many({})
    print(f"Deleted {result.deleted_count} existing attendance record(s).\n")

    # 2) Get all employees' MongoDB _id (relation by _id, not employee_id code)
    employees = list(employees_coll.find({}, {"_id": 1}))
    if not employees:
        print("No employees in DB. Run seed_employees.py first.")
        client.close()
        sys.exit(1)

    now = datetime.now(timezone.utc)
    inserted = 0
    weekdays = list(weekday_dates(START_DATE, END_DATE))

    print(f"Seeding attendance for {len(employees)} employees, {len(weekdays)} weekdays ({START_DATE} to {END_DATE}).\n")

    rng = random.Random(42)
    for emp in employees:
        emp_mongo_id = emp["_id"]  # store as BSON ObjectId, not string
        for d in weekdays:
            date_dt = datetime.combine(d, datetime.min.time())
            status = weighted_status(rng)
            doc = {
                "employee_id": emp_mongo_id,
                "date": date_dt,
                "status": status,
                "notes": None,
                "marked_by": "Admin",
                "marked_at": now,
                "created_at": now,
                "updated_at": now,
            }
            attendance_coll.insert_one(doc)
            inserted += 1
        print(f"  + {emp_mongo_id} ({len(weekdays)} weekdays)")

    client.close()
    print(f"\nDone. Inserted {inserted} attendance records (up to 5 Feb only, weekdays, realistic distribution).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
