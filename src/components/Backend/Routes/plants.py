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
        if not q:
            return jsonify([])

        try:
            rows = repo.search(q, limit=DEFAULT_LIMIT)
        except Exception as exc:
            # Log the error so we can see it in Cloud Run logs
            current_app.logger.exception("Plant search failed: %s", exc)
            return jsonify({"error": "internal server error"}), 500

        results = [row_to_dict(row) for row in rows]
        return jsonify(results)

    return bp
