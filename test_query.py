import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "database" / "ruet.db"
con = sqlite3.connect(db_path)
con.row_factory = sqlite3.Row
cur = con.cursor()

print("Testing the exact query from the API...")

query = """
    SELECT 
        dd.id,
        dd.fee_id,
        dd.due_type,
        dd.amount,
        dd.status,
        dd.deadline,
        dd.created_at,
        d.dept_name,
        pa.account_name
    FROM department_dues dd
    JOIN departments d ON dd.dept_id = d.id
    LEFT JOIN payment_accounts pa ON pa.account_type = 'department' AND pa.entity_identifier = d.dept_code AND pa.is_active = 1
    WHERE dd.student_id = ?
    ORDER BY dd.created_at DESC
"""

try:
    cur.execute(query, ('2203177',))
    rows = cur.fetchall()
    print(f"Found {len(rows)} rows")
    for i, row in enumerate(rows):
        print(f"\nRow {i+1}:")
        for key in row.keys():
            print(f"  {key}: {row[key]}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()

con.close()
