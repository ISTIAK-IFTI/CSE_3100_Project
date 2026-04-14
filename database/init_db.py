def dml():
    import sqlite3
    from pathlib import Path
    import bcrypt

    db_path = Path(__file__).parent / "ruet.db"

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    password = "676"
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    # if True:
    #     studentId = 2203177
    #     cur.execute(f"deleted from students where id = {studentId}")
    #     print(f"id {studentId} delete successfully ✅")
    # cur.execute("update students set verified = 1 where id = 2203177")
    # cur.execute(
    # "INSERT INTO students (id, name, dept, email, password_hash, verified) VALUES (?, ?, ?, ?, ?, ?)",
    # (2203133, "Abdullah", "CSE", "2203133@student.ruet.ac.bd", hashed, 1)
    # )

    # cur.execute("""
    #     CREATE TABLE IF NOT EXISTS department_dues (
    #         dept_id VARCHAR(10), 
    #         student_id VARCHAR(20), 
    #         fee_id VARCHAR(10), 
    #         amount DECIMAL(10, 2) CHECK (amount >= 0),
    #         status VARCHAR(20) DEFAULT 'unpaid',
    #         created_at DATE DEFAULT (CURRENT_DATE),
    #         PRIMARY KEY(dept_id, student_id, fee_id)
    #     )
    # """)
    try:
        cur.execute("alter table department_dues add column deadline date")
        print("✅ Done")
    except:
        print("❌ Not working")

    # cur.execute("""
    # insert into halls (email, hall_name, password_hash)
    # values ('hall001@hall.ruet.ac.bd', 'Shahid Abdul Hamid Hall', ?) 
    # """,(hashed,))

    # cur.execute("update students set verified = 1 where id = 2203177")
    # cur.execute("update halls set hall_name = 'Shahid Lt. Selim Hall' where email = 'hall001@hall.ruet.ac.bd'")

    con.commit()
    con.close()

    print("✅")


def get_table_columns(table_name):
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent / "ruet.db"

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    try:
        # টেবিল খালি থাকলেও এটি কলামের লিস্ট দিবে
        cur.execute(f"PRAGMA table_info({table_name})")
        
        columns = cur.fetchall()
        
        print(f"--- Columns in '{table_name}' ---")
        column_names = []
        for col in columns:
            # col[0] = Field Name, col[1] = Type, col[2] = Null, col[3] = Key
            print(f"Field: {col[0]} | Type: {col[1]} | Null: {col[2]}")
            column_names.append(col[0])
            
        return column_names

    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        con.close()

def ddl():
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent / "ruet.db"

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()


    # {'name': 'books'}
    # {'name': 'librarians'}
    # {'name': 'hall_managers'}
    # {'name': 'halls'}
    # {'name': 'sqlite_sequence'}
    # {'name': 'rooms'}
    # {'name': 'room_allocations'}
    # {'name': 'hall_monthly_fees'}
    # {'name': 'hall_dues'}
    # {'name': 'students'}
    # {'name': 'hall_accounts'}
    # {'name': 'payment_accounts'}
    # {'name': 'departments'}
    # {'name': 'department_dues'}

    # cur.execute("SELECT name FROM sqlite_master WHERE type='table';")


    table_name = "payment_accounts"
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()

    # # execute query
    # cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # # # fetch results
    # tables = cur.fetchall()
    # # print table names
    # print("Tables in database:")
    # for table in tables:
    #     print(table[0])

    if not rows:
        print(f"No {table_name} found.")
    else:
        for row in rows:
            print(dict(row))

    con.close()

    print("✅ Database file:", db_path)


# dml()
ddl()
# get_table_columns('department_dues')