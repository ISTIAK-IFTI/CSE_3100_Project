import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "ruet.db"

con = sqlite3.connect(db_path)
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  name TEXT,
  dept TEXT,
  hall TEXT,
  room TEXT
)
""")

cur.execute("""
INSERT OR IGNORE INTO students (id, name, dept, hall, room)
VALUES (?, ?, ?, ?, ?)
""", ("2203177", "Md Istiak Ahmed Ifti", "CSE", "Shahid Abdul Hamid Hall", "109"))

con.commit()
con.close()

print("✅ Database created:", db_path)
