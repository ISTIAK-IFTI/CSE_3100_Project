#!/usr/bin/env python3
"""
Setup department officers for all RUET departments
Run this to initialize all RUET departments in the database
"""

import sqlite3
import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"

# All RUET Departments
RUET_DEPARTMENTS = [
    ("00", "CIVIL", "civil"),
    ("01", "EEE", "eee"),
    ("02", "ME", "me"),
    ("03", "CSE", "cse"),
    ("04", "ETE", "ete"),
    ("05", "IPE", "ipe"),
    ("06", "GCE", "gce"),
    ("07", "URP", "urp"),
    ("08", "MTE", "mte"),
    ("09", "ARCH", "arch"),
    ("10", "ECE", "ece"),
    ("11", "CHE", "che"),
    ("12", "BECM", "becm"),
    ("13", "MSE", "mse"),
]

def setup_departments():
    """Add all RUET departments to database"""
    try:
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dept_code TEXT UNIQUE NOT NULL,
                dept_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("=" * 70)
        print("RUET DEPARTMENTS - DATABASE SETUP")
        print("=" * 70)
        
        created = 0
        skipped = 0
        
        for dept_code, dept_name, short_code in RUET_DEPARTMENTS:
            email = f"{short_code}@dept.ruet.ac.bd"
            password = short_code  # Password same as short code
            
            # Check if already exists
            cur.execute("SELECT id FROM departments WHERE LOWER(email) = LOWER(?)", (email,))
            if cur.fetchone():
                print(f"⏭️  {dept_name:10} ({dept_code}):  {email:30} (already exists)")
                skipped += 1
                continue
            
            # Create password hash
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert department
            try:
                cur.execute("""
                    INSERT INTO departments (dept_code, dept_name, email, password_hash)
                    VALUES (?, ?, ?, ?)
                """, (dept_code, dept_name, email, password_hash))
                print(f"✅ {dept_name:10} ({dept_code}):  {email:30}")
                created += 1
            except Exception as e:
                print(f"❌ {dept_name:10} ({dept_code}):  Error: {str(e)[:30]}")
        
        db.commit()
        db.close()
        
        print("\n" + "=" * 70)
        print(f"SUMMARY: {created} departments created, {skipped} already exist")
        print("=" * 70)
        
        # Display login credentials
        if created > 0:
            print("\n📝 LOGIN CREDENTIALS FOR DEPARTMENT OFFICERS:")
            print("-" * 70)
            for dept_code, dept_name, short_code in RUET_DEPARTMENTS:
                email = f"{short_code}@dept.ruet.ac.bd"
                print(f"{dept_name:10} ({dept_code}) - Email: {email:30} | Password: {short_code}")
        
        return created, skipped
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, 0

if __name__ == "__main__":
    created, skipped = setup_departments()
    exit(0 if created > 0 or skipped > 0 else 1)
