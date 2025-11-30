import sqlite3
from pathlib import Path
import pandas as pd

db_path = Path(__file__).resolve().parent / "Accounts.db"


def get_connection():
    return sqlite3.connect(db_path)

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()



def persist_sqlite(plants: pd.DataFrame, db_path: Path) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db_path)
    
    try:
        cur = con.cursor()
        
        cur.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS plants (
        name TEXT PRIMARY KEY,
        water_frequency INTEGER,
        sunlight_hours REAL,
        soil_type TEXT
        );
        """)
        
        # Upsert rows
        rows = [
            (
                str(r["name"]),
                None if pd.isna(r["water_frequency"]) else int(r["water_frequency"]),
                None if pd.isna(r["sunlight_hours"]) else float(r["sunlight_hours"]),
                None if pd.isna(r["soil_type"]) else str(r["soil_type"]),
            )
            for _, r in plants.iterrows()
        ]
        
        cur.executemany("""
        INSERT INTO plants(name, water_frequency, sunlight_hours, soil_type)
        VALUES(?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        water_frequency=excluded.water_frequency,
        sunlight_hours=excluded.sunlight_hours,
        soil_type=excluded.soil_type
        """, rows)
        
        cur.execute("CREATE INDEX IF NOT EXISTS idx_plants_name ON plants(name);")
        
        try:
            cur.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS plants_fts USING fts5(name, content='plants', content_rowid='rowid');
            INSERT INTO plants_fts(rowid, name)
            SELECT rowid, name FROM plants WHERE rowid NOT IN (SELECT rowid FROM plants_fts);
            
            CREATE TRIGGER IF NOT EXISTS plants_ai AFTER INSERT ON plants BEGIN
            INSERT INTO plants_fts(rowid, name) VALUES (new.rowid, new.name);
            END;
            
            CREATE TRIGGER IF NOT EXISTS plants_ad AFTER DELETE ON plants BEGIN
            INSERT INTO plants_fts(plants_fts, rowid, name) VALUES('delete', old.rowid, old.name);
            END;
            
            CREATE TRIGGER IF NOT EXISTS plants_au AFTER UPDATE ON plants BEGIN
            INSERT INTO plants_fts(plants_fts, rowid, name) VALUES('delete', old.rowid, old.name);
            INSERT INTO plants_fts(rowid, name) VALUES (new.rowid, new.name);
            END;
            """)
        except sqlite3.OperationalError:
            pass
            
        con.commit()
        
    finally:
        con.close()
        
    return db_path

