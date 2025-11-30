from flask import Blueprint, jsonify
from ..Metrics.prometheus import metrics

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    return jsonify({"status":"ok"}), 200

@bp.get("/metrics")
def metrics_route():
    return metrics()
