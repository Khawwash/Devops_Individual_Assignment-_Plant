import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(os.getenv("BASE_DIR", Path(__file__).resolve().parents[3]))
FRONTEND_DIR = Path(os.getenv("FRONTEND_DIR", Path(__file__).resolve().parents[1] / "Frontend"))

DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

PLANT_DB_PATH = Path(os.getenv("PLANT_DB_PATH", DATA_DIR / "Plant.db"))

FLASK_ENV = os.getenv("FLASK_ENV", "development")

SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
if not SECRET_KEY:
    if FLASK_ENV.lower() == "production":
        raise RuntimeError("FLASK_SECRET_KEY must be set in production")
    SECRET_KEY = "dev-insecure-key"

PORT = int(os.getenv("PORT", "3000"))
