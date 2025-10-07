import sqlite3
from pathlib import Path
import pytest


import src.components.Backend.App as backend_app


@pytest.fixture(scope="session")
def plants_db(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("data") / "Plant.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS plants (
            name TEXT PRIMARY KEY,
            water_frequency INTEGER,
            sunlight_hours REAL,
            soil_type TEXT
        );
        """
    )

    rows = [
        ("Monstera", 7, 4.0, "Loamy"),
        ("Corn", 3, 8.0, "Sandy"),
        ("Tomato", 2, 6.0, "Loamy"),
    ]
    cur.executemany(
        "INSERT INTO plants(name, water_frequency, sunlight_hours, soil_type) VALUES(?, ?, ?, ?)",
        rows,
    )
    con.commit()
    con.close()
    return db_path


@pytest.fixture()
def client(plants_db, monkeypatch):
    # Point the app to the temp DB for tests
    monkeypatch.setattr(backend_app, "PLANT_DB_PATH", plants_db)
    with backend_app.app.test_client() as client:
        yield client


def test_debug_plant_path(client, plants_db):
    rv = client.get("/api/debug/plant-path")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["exists"] is True
    assert Path(data["path"]) == plants_db


def test_search_plants_returns_matches(client):
    rv = client.get("/api/plants/search?q=mon")
    assert rv.status_code == 200
    data = rv.get_json()
    names = [p["name"] for p in data]
    assert "Monstera" in names


def test_search_plants_empty_query(client):
    rv = client.get("/api/plants/search?q=")
    assert rv.status_code == 200
    assert rv.get_json() == []


def test_page_routes_serve(client):
    # Accept 200 (served) or 302 (redirect) for auth-related routes
    for path in ["/", "/dashboard", "/add-plant", "/login", "/signup"]:
        resp = client.get(path)
        assert resp.status_code in (200, 302), f"Unexpected status for {path}: {resp.status_code}"

