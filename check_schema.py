import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "database" / "ruet.db"
con = sqlite3.connect(db_path)
cur = con.cursor()

print("DEPARTMENT_DUES SCHEMA:")
cur.execute("PRAGMA table_info(department_dues)")
columns = cur.fetchall()
for col in columns:
    print(f"  {col}")

print("\nDEPARTMENTS SCHEMA:")
cur.execute("PRAGMA table_info(departments)")
columns = cur.fetchall()
for col in columns:
    print(f"  {col}")

con.close()
