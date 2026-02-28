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
        role = "student1"

    # ✅ Librarian login
    elif email.endswith("@library.ruet.ac.bd"):
        cur.execute("""
            SELECT email, name, password_hash
            FROM librarians
            WHERE LOWER(email)=LOWER(?)
        """, (email,))
        user = cur.fetchone()
        role = "librarian"

    con.close()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    # ✅ If student, require verified
    if role == "student1" and int(user["verified"] or 0) != 1:
        return jsonify({"message": "Please verify your email first."}), 403

    stored_hash = user["password_hash"] or ""
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return jsonify({"message": "Wrong password"}), 401

    # ✅ Return fields
    return jsonify({
        "token": "demo-token",
        "role": role,
        "studentId": user["id"] if role == "student1" else None,
        "name": user["name"] if role == "librarian" else None
    }), 200


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
            cur.execute(f"update students set library_fee = {libFee} where id = '{status}'")
        cur.execute("update books set status = 'available', issue_duration = NULL where id = ?",(bookId,))
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000,debug=True)
    