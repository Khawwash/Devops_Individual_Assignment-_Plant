import os
import sys
import sqlite3
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.components.Backend.App_factory import create_app   

@pytest.fixture()
def plants_db(tmp_path, monkeypatch) -> Path:
    db_path = tmp_path / "data" / "Plant.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("PLANT_DB_PATH", str(db_path))

    con = sqlite3.connect(db_path)
    con.executescript("""
        PRAGMA foreign_keys=ON;
        CREATE TABLE IF NOT EXISTS plants(
          name TEXT,
          water_frequency INTEGER,
          sunlight_hours REAL,
          soil_type TEXT
        );
        INSERT INTO plants(name, water_frequency, sunlight_hours, soil_type)
        VALUES ('Pothos', 10, 4.0, 'Aroid mix');
    """)
    con.close()
    return db_path

@pytest.fixture()
def app(plants_db):
    app = create_app({"TESTING": True})
    return app

@pytest.fixture()
def client(app):
    return app.test_client()
