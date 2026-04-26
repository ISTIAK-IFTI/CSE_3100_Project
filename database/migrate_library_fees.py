"""
Migration script to create library_fines table and migrate existing library_fee data.
This creates individual library fine records for tracking and payment processing.

Usage:
    python migrate_library_fees.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"

def migrate_library_fees():
    """Create library_fines table and migrate existing library_fee data."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    try:
        # Create library_fines table (similar to hall_dues and department_dues)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS library_fines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            fine_description TEXT DEFAULT 'Library Fine',
            amount INTEGER NOT NULL,
            fine_date TEXT DEFAULT CURRENT_DATE,
            paid_date TEXT,
            status TEXT DEFAULT 'unpaid',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            UNIQUE(student_id)
        )
        """)
        print("✅ Created library_fines table")
        
        # Migrate existing library fees from students table to library_fines
        # Get all students with library_fee > 0
        cur.execute("""
            SELECT id, library_fee FROM students WHERE library_fee > 0
        """)
        students = cur.fetchall()
        
        migrated_count = 0
        for student_id, library_fee in students:
            try:
                cur.execute("""
                    INSERT OR REPLACE INTO library_fines 
                    (student_id, fine_description, amount, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, "Library Fine", library_fee, "unpaid", datetime.utcnow().isoformat()))
                migrated_count += 1
            except sqlite3.IntegrityError:
                print(f"  ⚠️ Student {student_id} already has a library fine record")
        
        con.commit()
        print(f"✅ Migrated {migrated_count} library fees to library_fines table")
        
        # Create index for faster queries
        cur.execute("CREATE INDEX IF NOT EXISTS idx_library_fines_student ON library_fines(student_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_library_fines_status ON library_fines(status)")
        con.commit()
        print("✅ Created indexes on library_fines table")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        con.rollback()
    finally:
        con.close()

if __name__ == "__main__":
    migrate_library_fees()
