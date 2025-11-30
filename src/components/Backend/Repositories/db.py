from __future__ import annotations
import os
import sqlite3
from pathlib import Path
from flask import g
from ..config import PLANT_DB_PATH

def _connect(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(db_path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    # Sensible SQLite pragmas for app use
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA journal_mode = WAL;")
    con.execute("PRAGMA synchronous = NORMAL;")
    return con

def resolve_db_path(db_path: Path | None = None) -> Path:
    override = os.getenv("PLANT_DB_PATH")
    return Path(db_path or override or PLANT_DB_PATH)

def get_db(db_path: Path | None = None) -> sqlite3.Connection:
    """One connection per request context."""
    if "db" not in g:
        target = resolve_db_path(db_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        g.db = _connect(target)
    return g.db

def close_db(_=None) -> None:
    con = g.pop("db", None)
    if con is not None:
        con.close()

def init_db(schema_path: Path | None = None, db_path: Path | None = None) -> None:
    """
    Ensure directory exists; optionally run schema.sql idempotently.
    Pass schema_path during one-time init or in tests.
    """
    target = resolve_db_path(db_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if schema_path and schema_path.exists():
        con = _connect(target)
        with open(schema_path, "r", encoding="utf-8") as f:
            con.executescript(f.read())
        con.close()

class PlantsRepository:
    """Thin repository wrapper to allow DI and testing."""
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path

    def search(self, query: str, limit: int = 25) -> list[dict]:
        con = get_db(self.db_path)
        cur = con.cursor()
        cur.execute(
            """
            SELECT name, water_frequency, sunlight_hours, soil_type
            FROM plants
            WHERE name LIKE ? COLLATE NOCASE
            LIMIT ?
            """,
            (f"%{query}%", limit),
        )
        return [dict(r) for r in cur.fetchall()]
