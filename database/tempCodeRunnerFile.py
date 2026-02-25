import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "ruet.db"

con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row   # 🔥 IMPORTANT
cur = con.cursor()

cur.execute("SELECT * FROM students")
rows = cur.fetchall()

if not rows:
    print("No students found.")
else:
    for row in rows:
        print(dict(row))

con.close()

print("✅ Database file:", db_path)