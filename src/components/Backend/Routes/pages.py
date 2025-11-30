from flask import Blueprint, send_from_directory
from ..config import FRONTEND_DIR

bp = Blueprint("pages", __name__)

@bp.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@bp.get("/login")
@bp.get("/login.html")
def login_form():
    return send_from_directory(FRONTEND_DIR, "login.html")

@bp.get("/signup")
@bp.get("/Sign_up")
def signup_form():
    return send_from_directory(FRONTEND_DIR, "Sign_up.html")

@bp.get("/dashboard")
def dashboard():
    return send_from_directory(FRONTEND_DIR, "Dashboard.html")

@bp.get("/Reminder")
def reminder():
    return send_from_directory(FRONTEND_DIR, "Reminders.html")

@bp.get("/add-plant")
@bp.get("/Add_plant")
def add_plant():
    return send_from_directory(FRONTEND_DIR, "Add_plant.html")
