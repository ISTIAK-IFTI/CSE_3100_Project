from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sqlite3
import bcrypt
import os
import random
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"
FRONTEND_DIR = BASE_DIR / "frontend"

# Save uploaded student photos here (optional)
STUDENT_PHOTO_DIR = FRONTEND_DIR / "media" / "students"
STUDENT_PHOTO_DIR.mkdir(parents=True, exist_ok=True)

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")


def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def send_otp_email(to_email: str, otp: str):
    """Send OTP email via Gmail SMTP."""
    if not EMAIL_USER or not EMAIL_PASS:
        raise RuntimeError("EMAIL_USER / EMAIL_PASS not set in environment variables")

    msg = EmailMessage()
    msg["Subject"] = "RUET Portal OTP Verification"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.set_content(
        f"Your OTP is: {otp}\n"
        f"It will expire in 10 minutes.\n\n"
        f"If you didn't request this, ignore the email."
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASS)
        smtp.send_message(msg)


def generate_otp():
    return str(random.randint(100000, 999999))


def now_iso():
    return datetime.utcnow().isoformat()


def iso_in_minutes(mins: int):
    return (datetime.utcnow() + timedelta(minutes=mins)).isoformat()


def is_student_email(email: str):
    return isinstance(email, str) and email.lower().endswith("@student.ruet.ac.bd")


# -------------------------
# Serve frontend
# -------------------------
@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# -------------------------
# Student APIs
# -------------------------
@app.route("/api/student/<student_id>")
def student(student_id):
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT
            id AS studentId,
            name,
            dept,
            hall,
            room,
            email,
            hall_fee,
            library_fee,
            dept_fee
        FROM students
        WHERE id = ?
    """, (student_id,))

    row = cur.fetchone()
    con.close()

    if not row:
        return jsonify({"message": "Student not found"}), 404

    data = dict(row)

    hall_fee = int(data.get("hall_fee") or 0)
    library_fee = int(data.get("library_fee") or 0)
    dept_fee = int(data.get("dept_fee") or 0)

    total_due = hall_fee + library_fee + dept_fee
    data["due"] = {
        "total": total_due,
        "items": [
            {"title": "Hall Fee", "amount": hall_fee},
            {"title": "Library Fine", "amount": library_fee},
            {"title": "Department Fee", "amount": dept_fee},
        ]
    }

    return jsonify(data)


# -------------------------
# STUDENT: Get current student profile
# -------------------------
@app.route("/api/student/me")
def student_me():
    """Get profile of currently logged-in student (requires studentId in query or sessionStorage)"""
    # Get from query parameter (sent from frontend)
    student_id = request.args.get("id") or request.headers.get("X-Student-Id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided. Use ?id=<studentId> or pass X-Student-Id header"}), 400
    
    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT
            id AS studentId,
            name,
            dept,
            hall,
            room,
            email,
            hall_fee,
            library_fee,
            dept_fee
        FROM students
        WHERE id = ?
    """, (student_id,))

    row = cur.fetchone()
    con.close()

    if not row:
        return jsonify({"message": "Student not found"}), 404

    data = dict(row)

    hall_fee = int(data.get("hall_fee") or 0)
    library_fee = int(data.get("library_fee") or 0)
    dept_fee = int(data.get("dept_fee") or 0)

    total_due = hall_fee + library_fee + dept_fee
    data["due"] = {
        "total": total_due,
        "items": [
            {"title": "Hall Fee", "amount": hall_fee},
            {"title": "Library Fine", "amount": library_fee},
            {"title": "Department Fee", "amount": dept_fee},
        ]
    }

    return jsonify(data)


# -------------------------
# STUDENT: Get Student Dues
# -------------------------
@app.route("/api/student/dues")
def student_dues():
    """Get dues for currently logged-in student"""
    student_id = request.args.get("id") or request.headers.get("X-Student-Id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    cur.execute("SELECT hall_fee, library_fee, dept_fee FROM students WHERE id=?", (student_id,))
    row = cur.fetchone()
    con.close()
    
    if not row:
        return jsonify({"message": "Student not found"}), 404
    
    items = [
        {"feeType": "Hall Fee", "period": "Monthly", "amount": int(row["hall_fee"] or 0), "status": "unpaid" if row["hall_fee"] else "paid"},
        {"feeType": "Library Fine", "period": "Current", "amount": int(row["library_fee"] or 0), "status": "unpaid" if row["library_fee"] else "paid"},
        {"feeType": "Department Fee", "period": "Semester", "amount": int(row["dept_fee"] or 0), "status": "unpaid" if row["dept_fee"] else "paid"},
    ]
    
    return jsonify({"items": items}), 200


# -------------------------
# STUDENT: Get Monthly Hall Fees
# -------------------------
@app.route("/api/student/hall-fees")
def student_hall_fees():
    """Get monthly hall fees for currently logged-in student with hall and account info"""
    student_id = request.args.get("id") or request.headers.get("X-Student-Id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    # Fetch monthly fees from hall_dues with hall and account info
    cur.execute("""
        SELECT 
            hd.id,
            hd.month,
            hd.amount,
            hd.status,
            hd.paid_date,
            h.hall_name,
            pa.account_name
        FROM hall_dues hd
        LEFT JOIN halls h ON hd.hall_id = h.id
        LEFT JOIN payment_accounts pa ON pa.account_type = 'hall' AND pa.entity_identifier = h.hall_name AND pa.is_active = 1
        WHERE hd.student_id = ?
        ORDER BY hd.month DESC
    """, (student_id,))
    
    rows = cur.fetchall()
    con.close()
    
    if not rows:
        return jsonify({"items": []}), 200
    
    items = [
        {
            "id": row["id"],
            "month": row["month"],
            "amount": int(row["amount"] or 0),
            "status": row["status"],
            "paid_date": row["paid_date"],
            "hall_name": row["hall_name"],
            "account_name": row["account_name"]
        }
        for row in rows
    ]
    
    return jsonify({"items": items}), 200


# -------------------------
# STUDENT: Get Department Dues
# -------------------------
@app.route("/api/student/department-dues")
def student_department_dues():
    """Get all department dues for a student"""
    student_id = request.args.get("id") or request.headers.get("X-Student-Id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    # Fetch department dues with department account info
    cur.execute("""
        SELECT 
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
    """, (student_id,))
    
    rows = cur.fetchall()
    con.close()
    
    if not rows:
        return jsonify({"items": []}), 200
    
    items = [
        {
            "fee_id": row["fee_id"],
            "fee_type": row["due_type"],
            "amount": int(row["amount"] or 0),
            "status": row["status"],
            "deadline": row["deadline"],
            "created_at": row["created_at"],
            "dept_name": row["dept_name"],
            "account_name": row["account_name"]
        }
        for row in rows
    ]
    
    return jsonify({"items": items}), 200


# -------------------------
# STUDENT: Get Library Fines
# -------------------------
@app.route("/api/student/library-fines")
def student_library_fines():
    """Get library fines for a student"""
    student_id = request.args.get("id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    cur.execute("""
        SELECT 
            id,
            student_id,
            fine_description,
            amount,
            fine_date,
            status,
            created_at
        FROM library_fines
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,))
    
    rows = cur.fetchall()
    con.close()
    
    if not rows:
        return jsonify({"items": []}), 200
    
    items = [
        {
            "id": row["id"],
            "student_id": row["student_id"],
            "description": row["fine_description"],
            "amount": int(row["amount"] or 0),
            "fine_date": row["fine_date"],
            "status": row["status"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]
    
    return jsonify({"items": items}), 200


# -------------------------
# STUDENT: Get Payment History
# -------------------------
@app.route("/api/student/payments")
def student_payments():
    """Get payment history for currently logged-in student"""
    student_id = request.args.get("id") or request.headers.get("X-Student-Id")
    
    if not student_id:
        return jsonify({"message": "Student ID not provided"}), 400
    
    # For now, return empty payments (no payment table in DB yet)
    # In future, query from payments table
    items = []
    
    return jsonify({"items": items}), 200


# -------------------------
# AUTH: Register (send OTP)
# -------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    # register.html sends FormData (multipart). So read from request.form.
    student_id = (request.form.get("studentId") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    name = (request.form.get("name") or "").strip()
    password = request.form.get("password") or ""

    if not student_id or not email or not name or not password:
        return jsonify({"message": "studentId, email, name, password required"}), 400

    # Validate email domain
    if not is_student_email(email):
        return jsonify({"message": "Email must end with @student.ruet.ac.bd"}), 400

    # Validate email prefix == roll
    prefix = email.split("@")[0]
    if prefix != student_id:
        return jsonify({"message": "Email must be <roll>@student.ruet.ac.bd (prefix must match studentId)"}), 400

    # Assign department 
    allDept = {
        '00':'CIVIL',
        '01':'EEE',
        '02':'ME',
        '03':'CSE',
        '04':'ETE',
        '05':'IPE',
        '06':'GCE',
        '07':'URP',
        '08':'MTE',
        '09':'ARCH',
        '10':'ECE',
        '11':'CHE',
        '12':'BECM',
        '13':'MSE',
    }
    dept = allDept[student_id[2:4]]

    # Hash password
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    con = get_db()
    cur = con.cursor()

    # Check if email already exists
    cur.execute("SELECT id FROM students WHERE LOWER(email)=LOWER(?)", (email,))
    if cur.fetchone():
        con.close()
        return jsonify({"message": "Email already registered"}), 409

    # Check if ID already exists
    cur.execute("SELECT id FROM students WHERE id=?", (student_id,))
    if cur.fetchone():
        con.close()
        return jsonify({"message": "Student ID already registered"}), 409

    # Generate OTP + store hash + expiry
    otp = generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    otp_expires_at = iso_in_minutes(10)

    # Optional photo upload: JPG <= 500KB
    photo = request.files.get("photo")
    if photo and photo.filename:
        if not photo.filename.lower().endswith((".jpg", ".jpeg")):
            con.close()
            return jsonify({"message": "Photo must be JPG/JPEG"}), 400
        photo_bytes = photo.read()
        if len(photo_bytes) > 500 * 1024:
            con.close()
            return jsonify({"message": "Photo must be 500KB or smaller"}), 400

        # Save as <roll>.jpg
        out_path = STUDENT_PHOTO_DIR / f"{student_id}.jpg"
        with open(out_path, "wb") as f:
            f.write(photo_bytes)

    # Insert as unverified
    cur.execute("""
        INSERT INTO students
          (id, name, email, password_hash, verified, otp_hash, otp_expires_at, otp_attempts_left, dept)
        VALUES (?, ?, ?, ?, 0, ?, ?, 5, ?)
    """, (student_id, name, email, password_hash, otp_hash, otp_expires_at, dept))

    con.commit()
    con.close()

    # Send email
    try:
        send_otp_email(email, otp)
    except Exception as e:
        return jsonify({"message": f"Registered but OTP email failed: {str(e)}"}), 500

    return jsonify({"message": "Registered. OTP sent to email."}), 200


# -------------------------
# AUTH: Verify OTP
# -------------------------
@app.route("/api/auth/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    otp = (data.get("otp") or "").strip()

    if not email or not otp:
        return jsonify({"message": "email and otp required"}), 400

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, verified, otp_hash, otp_expires_at, otp_attempts_left
        FROM students
        WHERE LOWER(email)=LOWER(?)
    """, (email,))
    user = cur.fetchone()

    if not user:
        con.close()
        return jsonify({"message": "Email not found"}), 404

    if int(user["verified"] or 0) == 1:
        con.close()
        return jsonify({"message": "Already verified"}), 200

    attempts = int(user["otp_attempts_left"] or 0)
    if attempts <= 0:
        con.close()
        return jsonify({"message": "Too many attempts. Please resend OTP."}), 429

    expires_at = user["otp_expires_at"]
    if not expires_at or datetime.fromisoformat(expires_at) < datetime.utcnow():
        con.close()
        return jsonify({"message": "OTP expired. Please resend OTP."}), 400

    stored_hash = user["otp_hash"] or ""
    ok = False
    try:
        ok = bcrypt.checkpw(otp.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        ok = False

    if not ok:
        # decrease attempts
        cur.execute("""
            UPDATE students SET otp_attempts_left = otp_attempts_left - 1
            WHERE id = ?
        """, (user["id"],))
        con.commit()
        con.close()
        return jsonify({"message": "Invalid OTP"}), 400

    # mark verified and clear otp fields
    cur.execute("""
        UPDATE students
        SET verified=1, otp_hash=NULL, otp_expires_at=NULL, otp_attempts_left=0
        WHERE id = ?
    """, (user["id"],))
    con.commit()
    con.close()

    return jsonify({"message": "Email verified successfully"}), 200


# -------------------------
# AUTH: Resend OTP
# -------------------------
@app.route("/api/auth/resend-otp", methods=["POST"])
def resend_otp():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"message": "email required"}), 400

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, verified
        FROM students
        WHERE LOWER(email)=LOWER(?)
    """, (email,))
    user = cur.fetchone()

    if not user:
        con.close()
        return jsonify({"message": "Email not found"}), 404

    if int(user["verified"] or 0) == 1:
        con.close()
        return jsonify({"message": "Already verified"}), 200

    otp = generate_otp()
    otp_hash = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    otp_expires_at = iso_in_minutes(10)

    cur.execute("""
        UPDATE students
        SET otp_hash=?, otp_expires_at=?, otp_attempts_left=5
        WHERE id=?
    """, (otp_hash, otp_expires_at, user["id"]))

    con.commit()
    con.close()

    try:
        send_otp_email(email, otp)
    except Exception as e:
        return jsonify({"message": f"Failed to send OTP: {str(e)}"}), 500

    return jsonify({"message": "OTP resent"}), 200


# -------------------------
# AUTH: Login (block unverified)
# -------------------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}

    identifier = (data.get("identifier") or data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"message": "Email/ID and password required"}), 400

    email = identifier

    con = get_db()
    cur = con.cursor()

    user = None
    role = None

    # ✅ Student login (allow demo@gmail.com too)
    if email.endswith("@student.ruet.ac.bd") or email == "demo@gmail.com":
        cur.execute("""
            SELECT id, name, password_hash, verified
            FROM students
            WHERE LOWER(email)=LOWER(?)
        """, (email,))
        user = cur.fetchone()
        role = "student"

    # ✅ Librarian login
    elif email.endswith("@library.ruet.ac.bd"):
        cur.execute("""
            SELECT email, name, password_hash
            FROM librarians
            WHERE LOWER(email)=LOWER(?)
        """, (email,))
        user = cur.fetchone()
        role = "librarian"
    
    # ✅ Hall Manager login
    elif email.endswith("@hall.ruet.ac.bd"):
        cur.execute("""
            SELECT email, hall_name, password_hash
            FROM halls
            WHERE LOWER(email) = LOWER(?)
        """, (email,))
        user = cur.fetchone()
        role = "hall_manager"
    
    # ✅ Department Officer login
    elif email.endswith("@dept.ruet.ac.bd"):
        cur.execute("""
            SELECT dept_code, dept_name, password_hash
            FROM departments
            WHERE LOWER(email) = LOWER(?)
        """, (email,))
        user = cur.fetchone()
        role = "department_officer"

    con.close()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    # ✅ If student, require verified
    if role == "student" and int(user["verified"] or 0) != 1:
        return jsonify({"message": "Please verify your email first."}), 403

    stored_hash = user["password_hash"] or ""
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return jsonify({"message": "Wrong password"}), 401

    # ✅ Return fields based on role
    return jsonify({
        "token": "demo-token",
        "role": role,
        "studentId": user["id"] if role == "student" else None,
        "name": user["name"] if role == "librarian" else None,
        "hall_name": user["hall_name"] if role == "hall_manager" else None,
        "dept_code": user["dept_code"] if role == "department_officer" else None,
        "dept_name": user["dept_name"] if role == "department_officer" else None,
    }), 200


#  ---------------------------------------
#          LIBRARY SUMMARY RENDR API
#  ---------------------------------------
@app.route("/api/library/render")
def render():
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT SUM(COALESCE(library_fee, 0)) AS total_fine FROM students")
    row = cur.fetchone()
    total_fine = row["total_fine"]
    cur.execute("SELECT COUNT(*) FROM books WHERE status is not 'available'")
    row = cur.fetchone()
    total_issued = row[0]
    cur.execute("SELECT COUNT(*) FROM books WHERE issue_duration < DATE('now')")
    row = cur.fetchone()
    overdue = row[0]
    cur.execute("SELECT COUNT(*) FROM books WHERE issue_date = DATE('now')")
    row = cur.fetchone()
    issue_today = row[0]
    cur.execute("SELECT status, id, issue_duration from books where issue_duration < date('now') and status != 'available'")
    rows = cur.fetchall()
    overdue_list = [dict(r) for r in rows]
    con.close()
    return jsonify({
        "total_fine": total_fine or 0,
        "total_issued": total_issued or 0,
        "overdue": overdue or 0,
        "issue_today": issue_today or 0,
        "overdue_list": overdue_list
    })


# --------------------------------------
#         GENERATE NEXT BOOK ID 
# --------------------------------------
@app.route("/api/library/next-book-id")
def next_book_id():
    con = get_db()
    cur = con.cursor()

    # Get last inserted book ID
    cur.execute("""
        SELECT id FROM books
        ORDER BY id DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    con.close()

    if not row:
        next_number = 1
    else:
        last_id = row["id"]   # e.g., BK-0007
        last_number = int(last_id.split("-")[1])
        next_number = last_number + 1

    new_id = f"BK-{next_number:04d}"  # 4 digit format

    return jsonify({"bookId": new_id})


# -------------------------
#       ISSUE BOOK API
# -------------------------
@app.route("/api/library/issueBook", methods=["POST"])
def issue_book():
    data = request.json or {}
    studentId = (data.get("studentId") or "").strip()
    bookId = (data.get("bookId") or "").strip()
    dueDate = (data.get("dueDate") or "").strip()
    if not studentId or not bookId or not dueDate:
        return jsonify({"message": "Missing data"}), 400
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("SELECT status FROM books WHERE id = ?", (bookId,))
        row = cur.fetchone()
        if not row:
            return jsonify({"message": "Book not found"}), 404
        if row["status"] != "available":
            return jsonify({"message": f"Book already issued to {studentId}"}), 400
        cur.execute("UPDATE books SET status = ? WHERE id = ?", (f"{studentId}", bookId))
        cur.execute("UPDATE books SET issue_duration = ? WHERE id = ?", (f"{dueDate}", bookId))
        cur.execute("update books set issue_date = DATE('now') where id = ?",(bookId,))
        con.commit()
        return jsonify({"message": "Book issued successfully"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        con.close()


# ---------------------------
#       RETURN BOOK API
# ---------------------------
@app.route("/api/library/returnBook", methods=["POST"])
def return_book():
    data = request.json or {}
    bookId = (data.get("bookId") or "").strip()
    returnDate = (data.get("returnDate") or "")

    if not bookId or not returnDate: 
        return jsonify({"message": "Missing data"}), 400
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute("select status, issue_duration from books where id = ?",(bookId,))
        row = cur.fetchone()
        status = row["status"]
        if not row: 
            return jsonify({"message": "Book not found"}), 404
        if row["status"] == 'available':
            return jsonify({"message": "Book is already available"}), 400
        due_date = datetime.strptime(row["issue_duration"], "%Y-%m-%d")
        ret_date = datetime.strptime(returnDate, "%Y-%m-%d")
        late_days = (ret_date - due_date).days
        fine = 0
        if late_days > 0:
            PER_DAY_FINE = 2
            fine = late_days * PER_DAY_FINE
            cur.execute("select library_fee from students where id = ?",(status,))
            row = cur.fetchone()
            libFee = None
            if not row["library_fee"]:
                libFee = fine
            else:
                libFee = row["library_fee"] + fine
            cur.execute("""UPDATE students SET library_fee = ? WHERE id = ?""", (libFee, status))
            # cur.execute(f"update students set library_fee = {libFee} where id = '{status}'")
        cur.execute("update books set status = 'available', issue_duration = NULL, issue_date = NULL where id = ?",(bookId,))
        con.commit()
        return jsonify({"message": f"Book returned successfully. Fine: {fine}"})
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        con.close()


# -----------------------------
#         ADD BOOK 
# -----------------------------
from datetime import datetime
@app.route("/api/library/books", methods=["POST"])
def add_book():
    data = request.json or {}
    title = (data.get("title") or "").strip()
    author = (data.get("author") or "").strip()
    category = (data.get("category") or "").strip()

    if not title or not author:
        return jsonify({"message": "Title and author are required"}), 400

    con = get_db()
    cur = con.cursor()

    # Generate new ID safely
    cur.execute("SELECT id FROM books ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    next_no = 1 if not row else int(row["id"].split("-")[1]) + 1
    new_id = f"BK-{next_no:04d}"

    cur.execute("""
        INSERT INTO books (id, title, author, category, status, added_at)
        VALUES (?, ?, ?, ?, 'available', ?)
    """, (new_id, title, author, category, datetime.utcnow().isoformat()))

    con.commit()
    con.close()

    return jsonify({"message": "Book added", "bookId": new_id}), 200


# -------------------------
#       REMOVE BOOK
# -------------------------
@app.route("/api/library/books/<book_id>", methods=["DELETE"])
def remove_book(book_id):
    con = get_db()
    cur = con.cursor()

    # Check if book exists
    cur.execute("SELECT id FROM books WHERE id = ?", (book_id,))
    book = cur.fetchone()

    if not book:
        con.close()
        return jsonify({"message": "Book ID not found"}), 404

    # Delete book
    cur.execute("DELETE FROM books WHERE id = ?", (book_id,))
    con.commit()
    con.close()

    return jsonify({"message": "Book removed successfully"}), 200


# =========================================
#        HALL MANAGEMENT APIs
# =========================================

# -------------------------
# HALL AUTH: Get hall from email
# -------------------------
def get_hall_by_email(email: str):
    """Get hall_id and hall_name from email."""
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT id, hall_name FROM halls WHERE LOWER(email)=LOWER(?)", (email,))
    hall = cur.fetchone()
    con.close()
    return dict(hall) if hall else None


# -------------------------
# HALL: Dashboard Summary
# -------------------------
@app.route("/api/hall/render")
def hall_render():
    # Get hall from token/email (in real app, verify JWT)
    # For now, get hall_name from query parameter
    con = get_db()
    cur = con.cursor()
    
    # Get hall by name (or fallback to first hall if not provided)
    hall_name = (request.args.get("hall_name") or "").strip()
    
    if hall_name:
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
    else:
        cur.execute("SELECT id FROM halls LIMIT 1")
    
    hall_row = cur.fetchone()
    
    if not hall_row:
        con.close()
        return jsonify({"message": "No hall found"}), 404
    
    hall_id = hall_row["id"]
    
    # Total rooms
    cur.execute("SELECT COUNT(*) as count FROM rooms WHERE hall_id=?", (hall_id,))
    total_rooms = cur.fetchone()["count"]
    
    # Allocated seats
    cur.execute("SELECT COUNT(*) as count FROM room_allocations WHERE hall_id=?", (hall_id,))
    allocated_seats = cur.fetchone()["count"]
    
    # Unpaid students (count distinct student IDs, not individual fees)
    cur.execute("SELECT COUNT(DISTINCT student_id) as count FROM hall_dues WHERE hall_id=? AND status='unpaid'", (hall_id,))
    unpaid_count = cur.fetchone()["count"]
    
    # Monthly fee (latest)
    cur.execute("SELECT amount FROM hall_monthly_fees WHERE hall_id=? ORDER BY month DESC LIMIT 1", (hall_id,))
    fee_row = cur.fetchone()
    monthly_fee = fee_row["amount"] if fee_row else 0
    
    con.close()
    
    return jsonify({
        "totalRooms": total_rooms,
        "allocatedSeats": allocated_seats,
        "unpaidCount": unpaid_count,
        "monthlyFee": monthly_fee
    }), 200


# -------------------------
# HALL: Allocate Student to Room
# -------------------------
@app.route("/api/hall/allocate", methods=["POST"])
def allocate_student():
    data = request.json or {}
    student_ids = data.get("studentIds") or []  # List of student IDs
    room_number = (data.get("roomNumber") or "").strip()
    alloc_type = (data.get("allocType") or "single").strip()
    hall_name = (data.get("hallName") or "").strip()  # ✅ Get hall from request
    
    if not student_ids or not room_number or not hall_name:
        return jsonify({"message": "studentIds, roomNumber, and hallName required"}), 400
    
    # Validate at least 1 student
    if len(student_ids) < 1:
        return jsonify({"message": "At least 1 student ID required"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get hall by name (not just LIMIT 1!)
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
        hall_row = cur.fetchone()
        if not hall_row:
            con.close()
            return jsonify({"message": f"Hall '{hall_name}' not found"}), 404
        
        hall_id = hall_row["id"]
        
        # Check if room exists for this hall
        cur.execute("SELECT id, capacity FROM rooms WHERE hall_id=? AND room_number=?", (hall_id, room_number))
        room_row = cur.fetchone()
        
        if not room_row:
            # ✅ NEW ROOM: Create with declared capacity
            capacity = 1 if alloc_type == "single" else 4
            
            # For new shared(4) rooms, must start with exactly 4 students
            if alloc_type == "shared4" and len(student_ids) != 4:
                con.close()
                return jsonify({"message": "For new shared(4) room, must allocate exactly 4 students initially. Then you can add/remove students from existing rooms."}), 400
            
            # For new single rooms, must be exactly 1
            if alloc_type == "single" and len(student_ids) != 1:
                con.close()
                return jsonify({"message": "Single allocation requires exactly 1 student"}), 400
            
            cur.execute("""
                INSERT INTO rooms (hall_id, room_number, capacity, occupied_seats)
                VALUES (?, ?, ?, 0)
            """, (hall_id, room_number, capacity))
            con.commit()
            cur.execute("SELECT id, capacity FROM rooms WHERE hall_id=? AND room_number=?", (hall_id, room_number))
            room_row = cur.fetchone()
        # ✅ If room exists, no strict count requirement - capacity check below handles it
        
        room_id = room_row["id"]
        
        # Check room capacity
        cur.execute("SELECT occupied_seats, capacity FROM rooms WHERE id=?", (room_id,))
        room_info = cur.fetchone()
        if room_info["occupied_seats"] + len(student_ids) > room_info["capacity"]:
            con.close()
            return jsonify({"message": "Room capacity exceeded"}), 400
        
        # Check if students already allocated
        placeholders = ",".join("?" * len(student_ids))
        cur.execute(f"SELECT COUNT(*) as count FROM room_allocations WHERE student_id IN ({placeholders})", student_ids)
        if cur.fetchone()["count"] > 0:
            con.close()
            return jsonify({"message": "One or more students already allocated"}), 400
        
        # Verify students exist and are verified
        cur.execute(f"SELECT COUNT(*) as count FROM students WHERE id IN ({placeholders}) AND verified=1", student_ids)
        if cur.fetchone()["count"] != len(student_ids):
            con.close()
            return jsonify({"message": "One or more students not found or not verified"}), 400
        
        # Get hall name for updating student hall field
        cur.execute("SELECT hall_name FROM halls WHERE id=?", (hall_id,))
        hall_info = cur.fetchone()
        hall_name = hall_info["hall_name"] if hall_info else "Unknown Hall"
        
        # Insert allocations and update student hall/room
        allocation_date = now_iso()
        for sid in student_ids:
            cur.execute("""
                INSERT INTO room_allocations (hall_id, room_id, student_id, allocation_date, allocation_type)
                VALUES (?, ?, ?, ?, ?)
            """, (hall_id, room_id, sid, allocation_date, alloc_type))
            
            # ✅ Update student's hall and room fields
            cur.execute("""
                UPDATE students SET hall=?, room=? WHERE id=?
            """, (hall_name, room_number, sid))
        
        # Update room occupied seats
        cur.execute("UPDATE rooms SET occupied_seats = occupied_seats + ? WHERE id=?", (len(student_ids), room_id))
        
        con.commit()
        con.close()
        
        return jsonify({"message": f"Allocated {len(student_ids)} student(s) to room {room_number}"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# DEBUG: Check hall allocation status
# -------------------------
@app.route("/api/debug/hall-status")
def debug_hall_status():
    """Debug endpoint to check allocations for all halls"""
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get all halls
        cur.execute("SELECT id, hall_name FROM halls ORDER BY hall_name")
        halls = cur.fetchall()
        
        result = []
        for hall in halls:
            hall_id = hall["id"]
            hall_name = hall["hall_name"]
            
            # Count allocations
            cur.execute("SELECT COUNT(*) as count FROM room_allocations WHERE hall_id=?", (hall_id,))
            alloc_count = cur.fetchone()["count"]
            
            # Get details
            cur.execute("""
                SELECT ra.student_id, s.name, r.room_number
                FROM room_allocations ra
                JOIN rooms r ON ra.room_id = r.id
                JOIN students s ON ra.student_id = s.id
                WHERE ra.hall_id = ?
            """, (hall_id,))
            allocations = cur.fetchall()
            
            result.append({
                "hall_id": hall_id,
                "hall_name": hall_name,
                "allocation_count": alloc_count,
                "allocations": [{"student_id": a["student_id"], "name": a["name"], "room": a["room_number"]} for a in allocations]
            })
        
        con.close()
        return jsonify({"halls": result}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Get Allocations
# -------------------------
@app.route("/api/hall/allocations")
def get_allocations():
    con = get_db()
    cur = con.cursor()
    
    # Get hall_name from query parameter
    hall_name = (request.args.get("hall_name") or "").strip()
    
    # Get hall by name (or fallback to first hall if not provided)
    if hall_name:
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
    else:
        cur.execute("SELECT id FROM halls LIMIT 1")
    
    hall_row = cur.fetchone()
    if not hall_row:
        con.close()
        return jsonify({"message": "Hall not found"}), 404
    
    hall_id = hall_row["id"]
    
    cur.execute("""
        SELECT 
            ra.id,
            ra.hall_id,
            ra.student_id,
            r.room_number,
            ra.allocation_type,
            ra.allocation_date,
            s.name as student_name
        FROM room_allocations ra
        JOIN rooms r ON ra.room_id = r.id
        JOIN students s ON ra.student_id = s.id
        WHERE ra.hall_id = ?
        ORDER BY r.room_number, ra.allocation_date
    """, (hall_id,))
    
    rows = cur.fetchall()
    con.close()
    
    # Return as flat list (not grouped)
    allocations = [dict(row) for row in rows]
    
    return jsonify({"allocations": allocations}), 200




# -------------------------
# HALL: Get Room Inventory
# -------------------------
@app.route("/api/hall/rooms")
def get_rooms():
    con = get_db()
    cur = con.cursor()
    
    # Get hall_name from query parameter
    hall_name = (request.args.get("hall_name") or "").strip()
    
    # Get hall by name (or fallback to first hall if not provided)
    if hall_name:
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
    else:
        cur.execute("SELECT id FROM halls LIMIT 1")
    
    hall_row = cur.fetchone()
    if not hall_row:
        con.close()
        return jsonify({"message": "Hall not found"}), 404
    
    hall_id = hall_row["id"]
    
    # Get all rooms with allocation details
    cur.execute("""
        SELECT 
            r.id,
            r.hall_id,
            r.room_number,
            r.capacity,
            r.occupied_seats,
            CASE 
                WHEN r.capacity = 1 THEN 'single'
                ELSE 'shared'
            END as type
        FROM rooms r
        WHERE r.hall_id = ?
        ORDER BY CAST(r.room_number AS INTEGER)
    """, (hall_id,))
    
    room_rows = cur.fetchall()
    
    rooms = []
    for room in room_rows:
        room_id = room["id"]
        
        # Get students in this room
        cur.execute("""
            SELECT 
                ra.student_id,
                s.name
            FROM room_allocations ra
            JOIN students s ON ra.student_id = s.id
            WHERE ra.room_id = ?
            ORDER BY ra.allocation_date
        """, (room_id,))
        
        student_rows = cur.fetchall()
        student_list = ", ".join([f"{s['student_id']}" for s in student_rows])
        
        rooms.append({
            "room_number": room["room_number"],
            "type": room["type"],
            "max_capacity": room["capacity"],
            "current_occupancy": room["occupied_seats"],
            "student_list": student_list if student_list else ""
        })
    
    con.close()
    
    return jsonify({"rooms": rooms}), 200


# -------------------------
# HALL: Deallocate Student from Room
# -------------------------
@app.route("/api/hall/allocate/<allocation_id>", methods=["DELETE"])
def deallocate_student(allocation_id):
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get allocation details
        cur.execute("""
            SELECT ra.room_id, ra.student_id
            FROM room_allocations ra
            WHERE ra.id=?
        """, (allocation_id,))
        alloc_row = cur.fetchone()
        
        if not alloc_row:
            con.close()
            return jsonify({"message": "Allocation not found"}), 404
        
        room_id = alloc_row["room_id"]
        student_id = alloc_row["student_id"]
        
        # Delete allocation
        cur.execute("DELETE FROM room_allocations WHERE id=?", (allocation_id,))
        
        # ✅ Clear the student's hall and room fields
        cur.execute("UPDATE students SET hall=NULL, room=NULL WHERE id=?", (student_id,))
        
        # Update room occupied seats
        cur.execute("UPDATE rooms SET occupied_seats = occupied_seats - 1 WHERE id=?", (room_id,))
        
        con.commit()
        con.close()
        
        return jsonify({"message": "Student deallocated successfully"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Create/Update Monthly Fee
# -------------------------
@app.route("/api/hall/fees/monthly", methods=["POST"])
def create_monthly_fee():
    data = request.json or {}
    month = (data.get("month") or "").strip()  # YYYY-MM
    amount = int(data.get("amount") or 0)
    deadline = (data.get("deadline") or "").strip() or None
    
    if not month or amount <= 0:
        return jsonify({"message": "month and amount required"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get hall
        cur.execute("SELECT id FROM halls LIMIT 1")
        hall_row = cur.fetchone()
        if not hall_row:
            con.close()
            return jsonify({"message": "Hall not found"}), 404
        
        hall_id = hall_row["id"]
        
        # Check if fee already exists for this month
        cur.execute("SELECT id FROM hall_monthly_fees WHERE hall_id=? AND month=?", (hall_id, month))
        if cur.fetchone():
            con.close()
            return jsonify({"message": "Fee already exists for this month"}), 409
        
        # Insert monthly fee
        cur.execute("""
            INSERT INTO hall_monthly_fees (hall_id, month, amount, deadline)
            VALUES (?, ?, ?, ?)
        """, (hall_id, month, amount, deadline))
        
        con.commit()
        
        # Now create dues for all allocated students
        cur.execute("""
            SELECT DISTINCT student_id FROM room_allocations WHERE hall_id=?
        """, (hall_id,))
        students = cur.fetchall()
        
        for student_row in students:
            student_id = student_row["student_id"]
            # Check if due already exists
            cur.execute("""
                SELECT id FROM hall_dues WHERE student_id=? AND month=?
            """, (student_id, month))
            if not cur.fetchone():
                # Insert new due
                cur.execute("""
                    INSERT INTO hall_dues (hall_id, student_id, month, amount, status)
                    VALUES (?, ?, ?, ?, 'unpaid')
                """, (hall_id, student_id, month, amount))
        
        con.commit()
        con.close()
        
        return jsonify({"message": f"Monthly fee created for {len(students)} student(s)"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Get Hall Dues
# -------------------------
@app.route("/api/hall/dues")
def get_hall_dues():
    con = get_db()
    cur = con.cursor()
    
    # Get hall by name (or fallback to first hall if not provided)
    hall_name = (request.args.get("hall_name") or "").strip()
    
    if hall_name:
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
    else:
        cur.execute("SELECT id FROM halls LIMIT 1")
    
    hall_row = cur.fetchone()
    if not hall_row:
        con.close()
        return jsonify({"message": "Hall not found"}), 404
    
    hall_id = hall_row["id"]
    
    cur.execute("""
        SELECT 
            hd.id,
            hd.student_id,
            s.name as student_name,
            hd.month,
            hd.amount,
            hd.status,
            hd.paid_date
        FROM hall_dues hd
        JOIN students s ON hd.student_id = s.id
        WHERE hd.hall_id = ?
        ORDER BY hd.month DESC, hd.student_id
    """, (hall_id,))
    
    rows = cur.fetchall()
    con.close()
    
    dues = [dict(row) for row in rows]
    
    return jsonify({"dues": dues}), 200


# -------------------------
# HALL: Mark Due as Paid
# -------------------------
@app.route("/api/hall/dues/<due_id>/pay", methods=["POST"])
def mark_due_paid(due_id):
    data = request.json or {}
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Check if due exists
        cur.execute("SELECT student_id, amount FROM hall_dues WHERE id=?", (due_id,))
        due_row = cur.fetchone()
        
        if not due_row:
            con.close()
            return jsonify({"message": "Due not found"}), 404
        
        # Mark as paid
        paid_date = now_iso()
        cur.execute("""
            UPDATE hall_dues SET status='paid', paid_date=? WHERE id=?
        """, (paid_date, due_id))
        
        # Update student's hall_fee
        student_id = due_row["student_id"]
        cur.execute("SELECT hall_fee FROM students WHERE id=?", (student_id,))
        student = cur.fetchone()
        current_fee = int(student["hall_fee"] or 0)
        new_fee = max(0, current_fee - int(due_row["amount"]))
        cur.execute("UPDATE students SET hall_fee=? WHERE id=?", (new_fee, student_id))
        
        con.commit()
        con.close()
        
        return jsonify({"message": "Hall due marked as paid successfully"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# =========================================
#     HALL ACCOUNT MANAGEMENT
# =========================================

# -------------------------
# HALL: Get all accounts
# -------------------------
@app.route("/api/hall/accounts")
def get_hall_accounts():
    """Get all payment accounts (halls, library, departments)"""
    con = get_db()
    cur = con.cursor()
    
    # Optional filter by account type
    account_type = (request.args.get("account_type") or "").strip() or None  # 'hall', 'library', 'department'
    
    query = """
        SELECT 
            id,
            account_type,
            entity_identifier,
            account_name,
            account_number,
            bank_name,
            account_holder,
            is_active,
            created_at
        FROM payment_accounts
        WHERE is_active = 1
    """
    params = []
    
    if account_type:
        query += " AND account_type = ?"
        params.append(account_type)
    
    query += " ORDER BY account_type, created_at DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    con.close()
    
    accounts = [dict(row) for row in rows]
    
    return jsonify({"accounts": accounts}), 200


# -------------------------
# HALL: Create or update payment account
# -------------------------
@app.route("/api/hall/accounts", methods=["POST"])
def create_hall_account():
    """Create or update a payment account (hall, library, or department)"""
    data = request.json or {}
    account_type = (data.get("account_type") or "").strip()  # 'hall', 'library', 'department'
    entity_identifier = (data.get("entity_identifier") or "").strip()  # hall_name, 'library', or dept_code
    account_name = (data.get("account_name") or "").strip()
    account_number = (data.get("account_number") or "").strip() or None
    bank_name = (data.get("bank_name") or "RUPALI BANK").strip()
    account_holder = (data.get("account_holder") or "").strip() or None
    
    if not account_type or not entity_identifier or not account_name:
        return jsonify({"message": "account_type, entity_identifier, and account_name required"}), 400
    
    if account_type not in ['hall', 'library', 'department']:
        return jsonify({"message": "account_type must be 'hall', 'library', or 'department'"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Check if account already exists
        cur.execute("""
            SELECT id FROM payment_accounts 
            WHERE account_type = ? AND entity_identifier = ?
        """, (account_type, entity_identifier))
        
        existing = cur.fetchone()
        
        if existing:
            # Update existing account
            account_id = existing["id"]
            cur.execute("""
                UPDATE payment_accounts 
                SET account_name = ?, account_number = ?, bank_name = ?, account_holder = ?
                WHERE id = ?
            """, (account_name, account_number, bank_name, account_holder, account_id))
            con.commit()
            con.close()
            
            return jsonify({
                "message": "Account updated successfully",
                "account_id": account_id
            }), 200
        else:
            # Create new account
            cur.execute("""
                INSERT INTO payment_accounts 
                (account_type, entity_identifier, account_name, account_number, bank_name, account_holder, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (account_type, entity_identifier, account_name, account_number, bank_name, account_holder))
            
            con.commit()
            account_id = cur.lastrowid
            con.close()
            
            return jsonify({
                "message": "Account created successfully",
                "account_id": account_id
            }), 201
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# =========================================
#     MONTHLY FEE MANAGEMENT
# =========================================

# -------------------------
# HALL: Create monthly fee for all students
# -------------------------
@app.route("/api/hall/fees/create-for-all", methods=["POST"])
def create_fee_for_all():
    """Create monthly fee for all allocated students in a hall"""
    data = request.json or {}
    month = (data.get("month") or "").strip()  # YYYY-MM
    amount = int(data.get("amount") or 0)
    deadline = (data.get("deadline") or "").strip() or None
    hall_name = (data.get("hall_name") or "").strip()
    
    if not month or amount <= 0 or not hall_name:
        return jsonify({"message": "month, amount, and hall_name required"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get hall
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
        hall_row = cur.fetchone()
        if not hall_row:
            con.close()
            return jsonify({"message": f"Hall '{hall_name}' not found"}), 404
        
        hall_id = hall_row["id"]
        
        # Check if fee already exists for this month
        cur.execute("SELECT id FROM hall_monthly_fees WHERE hall_id=? AND month=?", (hall_id, month))
        if cur.fetchone():
            con.close()
            return jsonify({"message": "Fee already exists for this month"}), 409
        
        # Insert monthly fee
        cur.execute("""
            INSERT INTO hall_monthly_fees (hall_id, month, amount, deadline)
            VALUES (?, ?, ?, ?)
        """, (hall_id, month, amount, deadline))
        
        con.commit()
        
        # Now create dues for all allocated students
        cur.execute("""
            SELECT DISTINCT student_id FROM room_allocations WHERE hall_id=?
        """, (hall_id,))
        students = cur.fetchall()
        
        created_count = 0
        for student_row in students:
            student_id = student_row["student_id"]
            # Check if due already exists
            cur.execute("""
                SELECT id FROM hall_dues WHERE student_id=? AND month=?
            """, (student_id, month))
            if not cur.fetchone():
                # Insert new due
                cur.execute("""
                    INSERT INTO hall_dues (hall_id, student_id, month, amount, status)
                    VALUES (?, ?, ?, ?, 'unpaid')
                """, (hall_id, student_id, month, amount))
                created_count += 1
        
        con.commit()
        con.close()
        
        return jsonify({
            "message": f"Monthly fee created for {created_count} student(s)",
            "created_count": created_count,
            "total_students": len(students)
        }), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Create monthly fee for single student
# -------------------------
@app.route("/api/hall/fees/create-for-student", methods=["POST"])
def create_fee_for_student():
    """Create monthly fee for a single student"""
    data = request.json or {}
    student_id = (data.get("student_id") or "").strip()
    month = (data.get("month") or "").strip()  # YYYY-MM
    amount = int(data.get("amount") or 0)
    hall_name = (data.get("hall_name") or "").strip()
    
    if not student_id or not month or amount <= 0 or not hall_name:
        return jsonify({"message": "student_id, month, amount, and hall_name required"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get hall
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
        hall_row = cur.fetchone()
        if not hall_row:
            con.close()
            return jsonify({"message": f"Hall '{hall_name}' not found"}), 404
        
        hall_id = hall_row["id"]
        
        # Verify student exists and is allocated to this hall
        cur.execute("""
            SELECT ra.student_id FROM room_allocations ra 
            WHERE ra.hall_id=? AND ra.student_id=?
        """, (hall_id, student_id))
        
        if not cur.fetchone():
            con.close()
            return jsonify({"message": "Student not allocated to this hall"}), 404
        
        # Check if due already exists for this student and month
        cur.execute("""
            SELECT id FROM hall_dues WHERE student_id=? AND month=?
        """, (student_id, month))
        
        if cur.fetchone():
            con.close()
            return jsonify({"message": "Fee already exists for this student in this month"}), 409
        
        # Insert due for single student
        cur.execute("""
            INSERT INTO hall_dues (hall_id, student_id, month, amount, status)
            VALUES (?, ?, ?, ?, 'unpaid')
        """, (hall_id, student_id, month, amount))
        
        con.commit()
        con.close()
        
        return jsonify({
            "message": "Monthly fee created for student successfully",
            "student_id": student_id,
            "month": month,
            "amount": amount
        }), 201
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# =========================================
#     HALL DUES MANAGEMENT
# =========================================

# -------------------------
# HALL: Delete single due
# -------------------------
@app.route("/api/hall/dues/<due_id>", methods=["DELETE"])
def delete_due(due_id):
    """Delete a single due"""
    con = get_db()
    cur = con.cursor()
    
    try:
        # Check if due exists
        cur.execute("SELECT id FROM hall_dues WHERE id=?", (due_id,))
        if not cur.fetchone():
            con.close()
            return jsonify({"message": "Due not found"}), 404
        
        # Delete due
        cur.execute("DELETE FROM hall_dues WHERE id=?", (due_id,))
        
        con.commit()
        con.close()
        
        return jsonify({"message": "Due deleted successfully"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Delete all dues for student or by month
# -------------------------
@app.route("/api/hall/dues/delete-all", methods=["POST"])
def delete_all_dues():
    """Delete all dues by student or by month"""
    data = request.json or {}
    student_id = (data.get("student_id") or "").strip() or None
    month = (data.get("month") or "").strip() or None
    hall_name = (data.get("hall_name") or "").strip()
    
    if not hall_name:
        return jsonify({"message": "hall_name required"}), 400
    
    if not student_id and not month:
        return jsonify({"message": "Either student_id or month required"}), 400
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get hall
        cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
        hall_row = cur.fetchone()
        if not hall_row:
            con.close()
            return jsonify({"message": f"Hall '{hall_name}' not found"}), 404
        
        hall_id = hall_row["id"]
        
        # Delete dues based on criteria
        if student_id and month:
            cur.execute("""
                DELETE FROM hall_dues 
                WHERE hall_id=? AND student_id=? AND month=?
            """, (hall_id, student_id, month))
            message = f"Due deleted for student {student_id} in {month}"
        elif student_id:
            cur.execute("""
                DELETE FROM hall_dues 
                WHERE hall_id=? AND student_id=?
            """, (hall_id, student_id))
            message = f"All dues deleted for student {student_id}"
        elif month:
            cur.execute("""
                DELETE FROM hall_dues 
                WHERE hall_id=? AND month=?
            """, (hall_id, month))
            message = f"All dues deleted for {month}"
        
        deleted_count = cur.rowcount
        con.commit()
        con.close()
        
        return jsonify({
            "message": message,
            "deleted_count": deleted_count
        }), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# HALL: Search dues
# -------------------------
@app.route("/api/hall/dues/search")
def search_hall_dues():
    """Search dues by student ID or date (month)"""
    con = get_db()
    cur = con.cursor()
    
    hall_name = (request.args.get("hall_name") or "").strip()
    student_id = (request.args.get("student_id") or "").strip() or None
    month = (request.args.get("month") or "").strip() or None  # Format: YYYY-MM
    
    if not hall_name:
        con.close()
        return jsonify({"message": "hall_name required"}), 400
    
    # Get hall
    cur.execute("SELECT id FROM halls WHERE hall_name = ?", (hall_name,))
    hall_row = cur.fetchone()
    if not hall_row:
        con.close()
        return jsonify({"message": f"Hall '{hall_name}' not found"}), 404
    
    hall_id = hall_row["id"]
    
    # Build query based on filters
    query = """
        SELECT 
            hd.id,
            hd.student_id,
            s.name as student_name,
            hd.month,
            hd.amount,
            hd.status,
            hd.paid_date,
            hd.created_at
        FROM hall_dues hd
        JOIN students s ON hd.student_id = s.id
        WHERE hd.hall_id = ?
    """
    params = [hall_id]
    
    if student_id:
        query += " AND hd.student_id = ?"
        params.append(student_id)
    
    if month:
        query += " AND hd.month = ?"
        params.append(month)
    
    query += " ORDER BY hd.month DESC, hd.student_id"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    con.close()
    
    dues = [dict(row) for row in rows]
    
    return jsonify({
        "total": len(dues),
        "dues": dues
    }), 200


# =========================================
#     DEPARTMENT DUES PAYMENT
# =========================================

# -------------------------
# DEPT: Mark Due as Paid
# -------------------------
@app.route("/api/dept/dues/<fee_id>/pay", methods=["POST"])
def mark_dept_due_paid(fee_id):
    data = request.json or {}
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get the department due
        cur.execute("""
            SELECT student_id, amount, dept_id FROM department_dues WHERE fee_id=?
        """, (fee_id,))
        due_row = cur.fetchone()
        
        if not due_row:
            con.close()
            return jsonify({"message": "Due not found"}), 404
        
        student_id = due_row["student_id"]
        amount = int(due_row["amount"] or 0)
        
        # Mark as paid
        paid_date = now_iso()
        cur.execute("""
            UPDATE department_dues SET status='paid', paid_date=? WHERE fee_id=?
        """, (paid_date, fee_id))
        
        # Update student's dept_fee (subtract from total)
        cur.execute("SELECT dept_fee FROM students WHERE id=?", (student_id,))
        student = cur.fetchone()
        current_fee = int(student["dept_fee"] or 0)
        new_fee = max(0, current_fee - amount)
        cur.execute("UPDATE students SET dept_fee=? WHERE id=?", (new_fee, student_id))
        
        con.commit()
        con.close()
        
        return jsonify({"message": "Department due marked as paid successfully"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


# -------------------------
# LIBRARY: Pay Library Fine
# -------------------------
@app.route("/api/library/fines/<fine_id>/pay", methods=["POST"])
def mark_library_fine_paid(fine_id):
    """Mark a library fine as paid and update student's library_fee"""
    data = request.json or {}
    
    con = get_db()
    cur = con.cursor()
    
    try:
        # Get the library fine
        cur.execute("""
            SELECT student_id, amount FROM library_fines WHERE id=?
        """, (fine_id,))
        fine_row = cur.fetchone()
        
        if not fine_row:
            con.close()
            return jsonify({"message": "Library fine not found"}), 404
        
        student_id = fine_row["student_id"]
        amount = int(fine_row["amount"] or 0)
        
        # Mark as paid
        paid_date = now_iso()
        cur.execute("""
            UPDATE library_fines SET status='paid', paid_date=? WHERE id=?
        """, (paid_date, fine_id))
        
        # Update student's library_fee (subtract from total)
        cur.execute("SELECT library_fee FROM students WHERE id=?", (student_id,))
        student = cur.fetchone()
        current_fee = int(student["library_fee"] or 0)
        new_fee = max(0, current_fee - amount)
        cur.execute("UPDATE students SET library_fee=? WHERE id=?", (new_fee, student_id))
        
        con.commit()
        con.close()
        
        return jsonify({"message": "Library fine marked as paid successfully"}), 200
    
    except Exception as e:
        con.close()
        return jsonify({"message": str(e)}), 500


#  ------------------------------------------
#         Department SUMMARY RENDR API
#  ------------------------------------------
@app.route("/api/dept/render", methods=['POST'])
def dept_render():
    data = request.get_json()
    dept_name = data.get('deptName')
    
    con = get_db()
    cur = con.cursor()
    
    cur.execute("SELECT COUNT(id) AS total FROM students WHERE dept=?", (dept_name,))
    result = cur.fetchone() 
    totalStudents = result[0]
    cur.execute("select count(status) from department_dues where status='unpaid' and dept_id=(select id from departments where dept_name = ?)",(dept_name,))
    result = cur.fetchone()
    totalUnpaidRecord = result[0]
    cur.execute("select sum(amount) from department_dues where status='unpaid' and dept_id=(select id from departments where dept_name = ?)",(dept_name,))
    result = cur.fetchone()
    totalDues = result[0]
    cur.execute("select count(distinct fee_id) from department_dues where dept_id=(select id from departments where dept_name = ?)",(dept_name,))
    result = cur.fetchone()
    totaFeeCreated = result[0]
    query = """
        SELECT fee_id, due_type, created_at, amount, status, student_id
        FROM department_dues 
        WHERE dept_id = (select id from departments where dept_name = ?)
    """
    cur.execute(query, (dept_name,))
    result = cur.fetchall()
    info_of_department_dues = []
    for info in result:
        info_of_department_dues.append({
            "fee_id": info[0],
            "type": info[1],
            "created_at": str(info[2]), 
            "amount": float(info[3]),
            "status": str(info[4]),
            "student_id": str(info[5])
        })
    con.close()

    return jsonify({
        "status": "success",
        "studentCount": str(totalStudents),
        "unpaidRecords": str(totalUnpaidRecord),
        "totalDues": str(totalDues),
        "totaFeeCreated": str(totaFeeCreated),
        "feeDetails": info_of_department_dues
    })


#  ---------------------------------------
#         Department Fee  API
#  ---------------------------------------
@app.route("/api/deptfee", methods=['POST'])
def dept_fee():
    data = request.get_json()
    dept_name = data.get('deptName')
    mode = data.get('mode')
    amount = data.get('amount') 
    type = data.get('type')
    status = 'unpaid'
    fee_id = data.get('fee_id')
    deadline = data.get('deadline')
    session = data.get('session')

    con = get_db()
    cur = con.cursor()

    cur.execute("""select id from departments where dept_name = ?""",(dept_name,))
    dept_id = cur.fetchone()[0]

    if mode == "ids":
        try:
            student_ids = data.get('ids', [])
            placeholders = ','.join(['?' for _ in student_ids])
            cur.execute(f"SELECT student_id FROM students WHERE dept = ? AND student_id IN ({placeholders})", 
                        [dept_name] + student_ids)
            found_rows = cur.fetchall()
            found_ids = [row[0] for row in found_rows]
            not_found = set(student_ids) - set(found_ids)
            if not_found:
                return jsonify({
                    "status": "error",
                    "message": f"These IDs are invalid or not in {dept_name}: {list(not_found)}"
                }), 400
            sql = """
                INSERT INTO department_dues (dept_id, student_id, fee_id, amount, status, created_at, due_type, deadline)
                VALUES (?, ?, ?, ?, 'unpaid', CURRENT_TIMESTAMP, ?, ?)
            """
            for s_id in student_ids:
                cur.execute(sql, (dept_id, s_id, fee_id, amount, type, deadline))

            return jsonify({"status": "success", "message": "Fees assigned successfully!"})
        except Exception as e:
            con.rollback()
            return jsonify({"status": "error", "message": str(e)}), 500
        finally:
            con.close()
    elif mode == "session":
        session_pattern = session + "%"
        sql = """
            INSERT INTO department_dues (
                dept_id, student_id, fee_id, amount, status, 
                created_at, due_type, deadline
            )
            SELECT ?, student_id, ?, ?, 'unpaid', CURRENT_TIMESTAMP, ?, ?
            FROM students
            WHERE dept = ? AND student_id LIKE ?
        """
        values = (dept_id, fee_id, amount, type, deadline, dept_name, session_pattern)
        cur.execute(sql, values)
        con.commit()
        con.close()
        return jsonify({"status": "success", "message": "Fees assigned successfully!"})
    else:
        sql = '''
            insert into department_dues (
                dept_id, student_id, fee_id, amount, status, 
                created_at, due_type, deadline
            )
            select ?, id, ?, ?, 'unpaid', CURRENT_TIMESTAMP, ?, ?
            from students where dept = ?
        '''
        values = (dept_id, fee_id, amount, type, deadline, dept_name)
        cur.execute(sql, values)
        con.commit()
        con.close()
        return jsonify({"status": "success", "message": "Fees assigned successfully!"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000,debug=True)
    