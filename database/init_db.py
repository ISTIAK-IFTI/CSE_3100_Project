# import sqlite3
# from pathlib import Path
# import bcrypt

# db_path = Path(__file__).parent / "ruet.db"

# con = sqlite3.connect(db_path)
# con.row_factory = sqlite3.Row
# cur = con.cursor()

# # cur.execute("""
# # CREATE TABLE IF NOT EXISTS students (
# #   id TEXT PRIMARY KEY,
# #   name TEXT,
# #   dept TEXT,
# #   hall TEXT,
# #   room TEXT
# # )
# # """)

# # cur.execute("""
# # INSERT OR IGNORE INTO students (id, name, dept, hall, room)
# # VALUES (?, ?, ?, ?, ?)
# # """, ("2203177", "Md Istiak Ahmed Ifti", "CSE", "Shahid Abdul Hamid Hall", "109"))

# # password = "demo_720"
# # password_bytes = password.encode("utf-8")
# # hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

# # cur.execute("""
# # INSERT INTO students
# # (id, name, dept, hall, room, email, password_hash,
# #  hall_fee, library_fee, dept_fee,
# #  verified, otp_hash, otp_expires_at, otp_attempts_left)
# # VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
# # """, (
# #     "demo_2203177",
# #     "DEMO : Md Istiak Ahmed Ifti",
# #     "Demo_CSE",
# #     "Demo_Hamid",
# #     "Demo_109",
# #     "iftimd3@gmail.com",
# #     hashed,
# #     560,
# #     10,
# #     490,
# #     1,
# #     None,
# #     None,
# #     5
# # ))

# if True:
#     cur.execute("delete from students where id = 2203177")
#     print(f"id 2203177 delete successfully ✅")
# # cur.execute("update students set verified = 1 where id = 2203177")


# con.commit()
# con.close()

# print("✅")



















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
