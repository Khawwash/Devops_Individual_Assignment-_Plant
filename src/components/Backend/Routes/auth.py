from flask import Blueprint, request, jsonify, redirect, url_for

class AuthService:
    """Thin wrapper around src.data.Auth to allow DI/mocking."""
    def __init__(self, impl=None):
        self._impl = impl

    @property
    def impl(self):
        if self._impl is None:
            from src.data import Auth as auth_module
            self._impl = auth_module
        return self._impl

    def init_db(self):
        return self.impl.init_db()

    def create_user(self, username: str, email: str, password: str):
        return self.impl.create_user(username, email, password)

    def authenticate_user(self, email: str, password: str) -> bool:
        return self.impl.authenticate_user(email, password)

def create_auth_bp(auth_service: AuthService) -> Blueprint:
    bp = Blueprint("auth", __name__)

    @bp.post("/signup")
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
            auth_service.create_user(username, email, password)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 409

        return redirect(url_for("pages.login_form"))

    @bp.post("/login")
    def login():
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        if not auth_service.authenticate_user(email, password):
            return jsonify({"error": "Invalid credentials"}), 401

        return redirect(url_for("pages.dashboard"))

    return bp
