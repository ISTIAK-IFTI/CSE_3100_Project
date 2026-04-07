"""
Run this script to initialize/update the database with hall management tables.
Execute this once before using the hall management features.

Usage:
    python init_db.py
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"

def init_hall_tables():
    """Create hall management tables if they don't exist."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    
    # Halls table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS halls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hall_name TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        total_rooms INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Rooms table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_id INTEGER NOT NULL,
        room_number TEXT NOT NULL,
        capacity INTEGER DEFAULT 1,
        occupied_seats INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        UNIQUE(hall_id, room_number)
    )
    """)
    
    # Room Allocations (maps students to rooms)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS room_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_id INTEGER NOT NULL,
        room_id INTEGER NOT NULL,
        student_id TEXT NOT NULL UNIQUE,
        allocation_date TEXT NOT NULL,
        allocation_type TEXT DEFAULT 'single',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        FOREIGN KEY (room_id) REFERENCES rooms(id),
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """)
    
    # Hall Monthly Fees
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hall_monthly_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        amount INTEGER NOT NULL,
        deadline TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hall_id) REFERENCES halls(id)
    )
    """)
    
    # Hall Dues (student-specific dues)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hall_dues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_id INTEGER NOT NULL,
        student_id TEXT NOT NULL,
        month TEXT NOT NULL,
        amount INTEGER NOT NULL,
        paid_date TEXT,
        status TEXT DEFAULT 'unpaid',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        FOREIGN KEY (student_id) REFERENCES students(id),
        UNIQUE(student_id, month)
    )
    """)
    
    # Hall Accounts (for payment purposes)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS hall_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_id INTEGER NOT NULL,
        account_name TEXT NOT NULL,
        account_number TEXT,
        bank_name TEXT DEFAULT 'RUPALI BANK',
        account_holder TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (hall_id) REFERENCES halls(id)
    )
    """)
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_allocations_hall ON room_allocations(hall_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_allocations_student ON room_allocations(student_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_hall ON hall_dues(hall_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_student ON hall_dues(student_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_month ON hall_dues(month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fees_month ON hall_monthly_fees(month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_accounts_hall ON hall_accounts(hall_id)")
    
    con.commit()
    con.close()
    
    print("✅ Hall management tables created/updated successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    try:
        init_hall_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
