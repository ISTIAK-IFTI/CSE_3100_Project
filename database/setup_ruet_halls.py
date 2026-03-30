#!/usr/bin/env python3
"""
Setup hall managers for all RUET halls
Run this to initialize all RUET halls in the database
"""

import sqlite3
import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"

# All RUET Halls
RUET_HALLS = [
    ("Shahid President Ziaur Rahman Hall", "zimur"),
    ("Shahid Abdul Hamid Hall", "hamid"),
    ("Tinshed Hall", "tinshed"),
    ("Shahid Shahidul Islam Hall", "shahid"),
    ("Sher-e-Bangla A K Fazlul Huq Hall", "fazlul"),
    ("Shahid Lt. Selim Hall", "selim"),
    ("Male Hall 1", "male1"),
    ("Male Hall 2", "male2"),
    ("Male Hall 3", "male3"),
    ("Female Hall 1", "female1"),
    ("Female Hall 2", "female2"),
]

def setup_halls():
    """Add all RUET halls to database"""
    try:
        db = sqlite3.connect(DB_PATH)
        cur = db.cursor()
        
        print("=" * 70)
        print("RUET HALLS - DATABASE SETUP")
        print("=" * 70)
        
        created = 0
        skipped = 0
        
        for hall_name, short_code in RUET_HALLS:
            email = f"{short_code}@hall.ruet.ac.bd"
            password = short_code  # Same as short code for simplicity
            
            # Check if already exists
            cur.execute("SELECT id FROM halls WHERE LOWER(email) = LOWER(?)", (email,))
            if cur.fetchone():
                print(f"⏭️  {hall_name:45} (already exists)")
                skipped += 1
                continue
            
            # Create password hash
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert hall
            try:
                cur.execute("""
                    INSERT INTO halls (email, hall_name, password_hash, total_rooms)
                    VALUES (?, ?, ?, ?)
                """, (email, hall_name, password_hash, 0))
                print(f"✅ {hall_name:45} → {email}")
                created += 1
            except Exception as e:
                print(f"❌ {hall_name:45} (Error: {str(e)[:30]})")
        
        db.commit()
        db.close()
        
        print("\n" + "=" * 70)
        print(f"SUMMARY: {created} halls created, {skipped} already exist")
        print("=" * 70)
        
        # Display login credentials
        if created > 0:
            print("\n📝 LOGIN CREDENTIALS FOR HALL MANAGERS:")
            print("-" * 70)
            for hall_name, short_code in RUET_HALLS:
                email = f"{short_code}@hall.ruet.ac.bd"
                print(f"Hall: {hall_name:45}")
                print(f"  Email:    {email}")
                print(f"  Password: {short_code}")
                print()
        
        return created, skipped
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0, 0

if __name__ == "__main__":
    created, skipped = setup_halls()
    exit(0 if created > 0 or skipped > 0 else 1)
