# import sqlite3
# from pathlib import Path
# import bcrypt

# db_path = Path(__file__).parent / "ruet.db"

# con = sqlite3.connect(db_path)
# con.row_factory = sqlite3.Row
# cur = con.cursor()

# # password = "hall001"
# # password_bytes = password.encode("utf-8")
# # hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

# # if True:
# #     cur.execute("delete from students where id = 2203177")
# #     print(f"id 2203177 delete successfully ✅")
# # cur.execute("update students set verified = 1 where id = 2203177")

# # cur.execute("""
# # CREATE TABLE halls (
# #   email TEXT PRIMARY KEY,
# #   hall_name TEXT,
# #   password_hash TEXT
# # );
# # """)

# # cur.execute("""
# # insert into halls (email, hall_name, password_hash)
# # values ('hall001@hall.ruet.ac.bd', 'Shahid Abdul Hamid Hall', ?) 
# # """,(hashed,))

# # cur.execute("update students set verified = 1 where id = 2203177")

# con.commit()
# con.close()

# print("✅")



















import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "ruet.db"

con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row
cur = con.cursor()

table_name = "halls"
cur.execute(f"SELECT * FROM {table_name}")
rows = cur.fetchall()

if not rows:
    print(f"No {table_name} found.")
else:
    for row in rows:
        print(dict(row))

con.close()

print("✅ Database file:", db_path)