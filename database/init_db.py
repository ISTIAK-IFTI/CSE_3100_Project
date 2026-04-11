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
    #     cur.execute(f"delete from students where id = {studentId}")
    #     print(f"id {studentId} delete successfully ✅")
    # cur.execute("update students set verified = 1 where id = 2203177")
    # cur.execute(
    # "INSERT INTO students (id, name, dept, email, password_hash, verified) VALUES (?, ?, ?, ?, ?, ?)",
    # (2203133, "Abdullah", "CSE", "2203133@student.ruet.ac.bd", hashed, 1)
    # )

    # cur.execute("""
    # ALTER TABLE halls
    # RENAME TO hall_managers;
    # """)

    # cur.execute("""
    # insert into halls (email, hall_name, password_hash)
    # values ('hall001@hall.ruet.ac.bd', 'Shahid Abdul Hamid Hall', ?) 
    # """,(hashed,))

    # cur.execute("update students set verified = 1 where id = 2203177")
    # cur.execute("update halls set hall_name = 'Shahid Lt. Selim Hall' where email = 'hall001@hall.ruet.ac.bd'")

    con.commit()
    con.close()

    print("✅")


def ddl():
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).parent / "ruet.db"

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()


    # cur.execute("SELECT name FROM sqlite_master WHERE type='table';")


    table_name = "hall_accounts"
    cur.execute(f"SELECT * FROM {table_name}")
    rows = cur.fetchall()

    # # execute query
    # cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # # fetch results
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