from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import sqlite3
import bcrypt
from pathlib import Path

app = Flask(__name__)
CORS(app)

# =========================
# PATH CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"
FRONTEND_DIR = BASE_DIR / "frontend"


# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# =========================
# SERVE FRONTEND
# =========================
@app.route("/frontend/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# =========================
# GET ONE STUDENT
# =========================
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
            {"title": "Department Fee", "amount": dept_fee}
        ]
    }

    return jsonify(data)


# =========================
# GET ALL STUDENTS (OPTIONAL)
# =========================
@app.route("/api/students")
def students():
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
        ORDER BY id ASC
    """)

    rows = cur.fetchall()
    con.close()

    return jsonify([dict(r) for r in rows])


# =========================
# LOGIN API
# =========================
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({"message": "Invalid request"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password required"}), 400

    con = get_db()
    cur = con.cursor()

    cur.execute("""
        SELECT id, password_hash
        FROM students
        WHERE LOWER(email) = LOWER(?)
    """, (email,))

    user = cur.fetchone()
    con.close()

    if not user:
        return jsonify({"message": "Email not found"}), 404

    stored_hash = user["password_hash"]

    # Verify password
    if not bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
        return jsonify({"message": "Wrong password"}), 401

    # SUCCESS
    return jsonify({
        "message": "Login successful",
        "studentId": user["id"],
        "role": "student1",
        "token": "demo-token"  # Later replace with JWT
    }), 200


# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

