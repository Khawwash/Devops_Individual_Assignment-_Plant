import bcrypt
import sqlite3 
from src.data.database import get_connection, init_db

init_db()  

def create_user(username: str, email: str, password: str) -> None:
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash),
            )
            conn.commit()
    except sqlite3.IntegrityError as err:
        raise ValueError("Username or email already exists") from err

    

def authenticate_user(email: str, password: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE email = ?",
            (email.lower(),),
        ).fetchone()
    if row is None:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), row[0].encode("utf-8"))

    
