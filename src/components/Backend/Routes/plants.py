import logging
import os
import sqlite3
from pathlib import Path
from flask import Blueprint, request, jsonify
from ..Repositories.db import PlantsRepository
from ..config import PLANT_DB_PATH

DEFAULT_LIMIT = 25

def create_plants_bp(repo: PlantsRepository | None = None) -> Blueprint:
    repo = repo or PlantsRepository()
    bp = Blueprint("plants", __name__)

    @bp.get("/api/debug/plant-path")
    def debug_plant_path():
        db_path = Path(os.getenv("PLANT_DB_PATH") or PLANT_DB_PATH)
        return jsonify({"exists": db_path.exists(), "path": str(db_path)})

    @bp.get("/api/plants/search")
    def search_plants():
        q = request.args.get("q", "").strip()
        db_path = Path(os.getenv("PLANT_DB_PATH") or PLANT_DB_PATH)
        if not q or not db_path.exists():
            return jsonify([])
        try:
            rows = repo.search(q, limit=DEFAULT_LIMIT)
            return jsonify(rows)
        except sqlite3.Error:
            logging.exception("Failed to query plants")
            return jsonify({"error": "database unavailable"}), 500

    return bp
