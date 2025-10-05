from pathlib import Path
from flask import Flask, request, jsonify, redirect, send_from_directory, url_for
from src.data.Auth import create_user, init_db, authenticate_user
import sqlite3
import logging


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "Frontend"
PLANT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "Plant.db"

def get_db():
    con = sqlite3.connect(PLANT_DB_PATH, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

app = Flask(__name__)
init_db()

@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/login")
@app.get("/login.html")
def login_form():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.get("/signup")
@app.get("/Sign_up")
def signup_form():
    return send_from_directory(FRONTEND_DIR, "Sign_up.html")

@app.get("/api/debug/plant-path")
def debug_plant_path(): return jsonify({"exists": PLANT_DB_PATH.exists(), "path": str(PLANT_DB_PATH)})



@app.get("/api/plants/search")
@app.get("/api/plants/search")
def search_plants():
    q = request.args.get("q", "").strip()
    if not q or not PLANT_DB_PATH.exists():
        return jsonify([])
    try:
        con = get_db()
        cur = con.cursor()
        
        cur.execute("""
            SELECT name, water_frequency, sunlight_hours, soil_type
            FROM plants
            WHERE name LIKE ? COLLATE NOCASE
            LIMIT 25
        """, (f"%{q}%",))
        
        rows = cur.fetchall()
        con.close()
        
        return jsonify([dict(r) for r in rows])
    except Exception:
        logging.exception("Failed to query plants")
        return jsonify([])
    

@app.get("/Reminder")
def reminders():
    return send_from_directory(FRONTEND_DIR, "Reminders.html")



@app.post("/signup")
def signup():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    if password != confirm or len(password) < 8:
        return jsonify({"error": "Passwords must match and be at least 8 characters"}), 400

    try:
        create_user(username, email, password)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 409

    return redirect(url_for("login_form"))

@app.post("/login")
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if not authenticate_user(email, password):
        return jsonify({"error": "Invalid credentials"}), 401

    return redirect(url_for("dashboard"))

@app.get("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "Dashboard.html")

@app.get("/add-plant")
@app.get("/Add_plant")
def add_plant():
    return send_from_directory(FRONTEND_DIR, "Add_plant.html")

if __name__ == "__main__":
    app.run(debug=True)


