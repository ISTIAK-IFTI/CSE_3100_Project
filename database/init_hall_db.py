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
    
    # Payment Accounts (universal table for halls, library, departments)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_type TEXT NOT NULL,           -- 'hall', 'library', 'department'
        entity_identifier TEXT NOT NULL,      -- hall_name, 'library', or dept_code (e.g., '03' for CSE)
        account_name TEXT NOT NULL,           -- e.g., "Hamid Hall Account", "Library Account", "CSE Department Account"
        account_number TEXT,                  -- Real account number or placeholder (hall_name/dept_code for now)
        bank_name TEXT DEFAULT 'RUPALI BANK',
        account_holder TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(account_type, entity_identifier)
    )
    """)
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_allocations_hall ON room_allocations(hall_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_allocations_student ON room_allocations(student_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_hall ON hall_dues(hall_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_student ON hall_dues(student_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dues_month ON hall_dues(month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_fees_month ON hall_monthly_fees(month)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_accounts_type ON payment_accounts(account_type)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_accounts_identifier ON payment_accounts(entity_identifier)")
    
    con.commit()
    
    # ===== POPULATE DEFAULT PAYMENT ACCOUNTS =====
    # Department codes and names
    dept_map = {
        '00': 'CIVIL',
        '01': 'EEE',
        '02': 'ME',
        '03': 'CSE',
        '04': 'ETE',
        '05': 'IPE',
        '06': 'GCE',
        '07': 'URP',
        '08': 'MTE',
        '09': 'ARCH',
        '10': 'ECE',
        '11': 'CHE',
        '12': 'BECM',
        '13': 'MSE',
    }
    
    # Add hall accounts
    try:
        cur.execute("SELECT COUNT(*) as count FROM payment_accounts WHERE account_type='hall'")
        if cur.fetchone()[0] == 0:
            cur.execute("SELECT hall_name FROM halls ORDER BY id")
            halls = cur.fetchall()
            for hall in halls:
                hall_name = hall[0]
                account_name = f"{hall_name} Account"
                cur.execute("""
                    INSERT INTO payment_accounts 
                    (account_type, entity_identifier, account_name, account_number, bank_name, is_active)
                    VALUES ('hall', ?, ?, ?, 'RUPALI BANK', 1)
                """, (hall_name, account_name, hall_name))  # Placeholder: hall_name as account_number
            con.commit()
            print(f"✅ Added {len(halls)} hall accounts")
    except Exception as e:
        print(f"⚠️ Error adding hall accounts: {e}")
    
    # Add library account
    try:
        cur.execute("SELECT COUNT(*) as count FROM payment_accounts WHERE account_type='library'")
        if cur.fetchone()[0] == 0:
            cur.execute("""
                INSERT INTO payment_accounts 
                (account_type, entity_identifier, account_name, account_number, bank_name, is_active)
                VALUES ('library', 'library', 'Library Account', 'library', 'RUPALI BANK', 1)
            """)
            con.commit()
            print("✅ Added library account")
    except Exception as e:
        print(f"⚠️ Error adding library account: {e}")
    
    # Add department accounts
    try:
        cur.execute("SELECT COUNT(*) as count FROM payment_accounts WHERE account_type='department'")
        if cur.fetchone()[0] == 0:
            for dept_code, dept_name in dept_map.items():
                account_name = f"{dept_name} Department Account"
                cur.execute("""
                    INSERT INTO payment_accounts 
                    (account_type, entity_identifier, account_name, account_number, bank_name, is_active)
                    VALUES ('department', ?, ?, ?, 'RUPALI BANK', 1)
                """, (dept_code, account_name, dept_code))  # Placeholder: dept_code as account_number
            con.commit()
            print(f"✅ Added {len(dept_map)} department accounts")
    except Exception as e:
        print(f"⚠️ Error adding department accounts: {e}")
    
    con.close()
    
    print("✅ Hall management tables created/updated successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    try:
        init_hall_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
