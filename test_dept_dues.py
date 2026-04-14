import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "database" / "ruet.db"
con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("=" * 60)
print("CHECKING DEPARTMENT DUES FOR STUDENT 2203177")
print("=" * 60)

# Check student info
cur.execute("SELECT id, name, dept FROM students WHERE id = '2203177'")
student = cur.fetchone()
if student:
    print(f"Student: {dict(student)}")
else:
    print("Student 2203177 not found!")

print("\n" + "=" * 60)
print("CHECKING DEPARTMENT DUES")
print("=" * 60)

# Check department dues
cur.execute("""
    SELECT dd.*, d.dept_name 
    FROM department_dues dd 
    JOIN departments d ON dd.dept_id = d.id
    WHERE dd.student_id = '2203177'
""")
dues = cur.fetchall()
print(f"Found {len(dues)} dues")
for due in dues:
    print(dict(due))

print("\n" + "=" * 60)
print("CHECKING DEPARTMENTS")
print("=" * 60)

cur.execute("SELECT * FROM departments WHERE dept_name = 'CSE'")
dept = cur.fetchone()
if dept:
    print(f"CSE Department: {dict(dept)}")

print("\n" + "=" * 60)
print("CHECKING PAYMENT ACCOUNTS FOR CSE")
print("=" * 60)

cur.execute("SELECT * FROM payment_accounts WHERE account_type = 'department' AND entity_identifier = (SELECT dept_code FROM departments WHERE dept_name = 'CSE')")
account = cur.fetchone()
if account:
    print(f"Account: {dict(account)}")
else:
    print("No payment account found for CSE")

con.close()
