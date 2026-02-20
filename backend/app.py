from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from pathlib import Path

app = Flask(__name__)
CORS(app)  # allow frontend (Live Server) to call API

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "ruet.db"
FRONTEND_DIR = BASE_DIR / "frontend"

def get_db():
  con = sqlite3.connect(DB_PATH)
  con.row_factory = sqlite3.Row
  return con

# Optional: serve your html from flask (one port system)
@app.route("/frontend/<path:filename>")
def frontend_files(filename):
  return send_from_directory(FRONTEND_DIR, filename)

# API: get student info by ID
@app.route("/api/student/<student_id>")
def student(student_id):
  con = get_db()
  cur = con.cursor()
  cur.execute("SELECT id as studentId, name, dept, hall, room FROM students WHERE id = ?", (student_id,))
  row = cur.fetchone()
  con.close()

  if not row:
    return jsonify({"message": "Student not found"}), 404

  data = dict(row) 

  # add sample due info (you can load from DB later)
  data["due"] = {
    "total": 1200,
    "items": [
      {"title": "Hall Fee", "amount": 600},
      {"title": "Library Fine", "amount": 300},
      {"title": "Department Fee", "amount": 300},
    ]
  }

  return jsonify(data)

if __name__ == "__main__":
  app.run(host="127.0.0.1", port=5000, debug=True)
