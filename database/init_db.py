import sqlite3
from pathlib import Path
import bcrypt

db_path = Path(__file__).parent / "ruet.db"

con = sqlite3.connect(db_path)
cur = con.cursor()

# cur.execute("""
# CREATE TABLE IF NOT EXISTS students (
#   id TEXT PRIMARY KEY,
#   name TEXT,
#   dept TEXT,
#   hall TEXT,
#   room TEXT
# )
# """)

# cur.execute("""
# INSERT OR IGNORE INTO students (id, name, dept, hall, room)
# VALUES (?, ?, ?, ?, ?)
# """, ("2203177", "Md Istiak Ahmed Ifti", "CSE", "Shahid Abdul Hamid Hall", "109"))

cur.execute("DROP TABLE IF EXISTS students")

cur.execute("""
CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  name TEXT,
  dept TEXT,
  hall TEXT,
  room TEXT,
  email TEXT UNIQUE,
  password_hash TEXT,
  hall_fee INT,
  library_fee INT,
  dept_fee INT
)
""")

plain_password = "720"
password_hash = bcrypt.hashpw(
    plain_password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

cur.execute("""
INSERT INTO students
(id, name, dept, hall, room, email, password_hash, hall_fee, library_fee, dept_fee)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "2203177",
    "Md Istiak Ahmed Ifti",
    "CSE",
    "Shahid Abdul Hamid Hall",
    "109",
    "2203177@student.ruet.ac.bd",
    password_hash,
    560,
    27,
    590
))

con.commit()
con.close()

print("✅ Database created:", db_path)
