from flask import Flask
from .config import SECRET_KEY, FLASK_ENV
from .Repositories.db import close_db, init_db, PlantsRepository
from .Metrics.prometheus import before_request as metrics_before, after_request as metrics_after
from .Routes.auth import create_auth_bp, AuthService
from .Routes.plants import create_plants_bp

def create_app(config: dict | None = None, services: dict | None = None):
    services = services or {}
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["ENV"] = FLASK_ENV
    if config:
        app.config.update(config)

    # DB lifecycle (allow override)
    db_helpers = services.get("db") or {"close": close_db, "init": init_db}
    app.teardown_appcontext(db_helpers["close"])
    db_helpers["init"]()

    # Metrics middleware (optional via services)
    metrics = services.get("metrics")
    if metrics is None:
        metrics = {"before": metrics_before, "after": metrics_after}
    if metrics:
        app.before_request(metrics["before"])
        app.after_request(metrics["after"])

    # Blueprints
    from .Routes.health import bp as health_bp
    from .Routes.pages import bp as pages_bp

    auth_service = services.get("auth_service") or AuthService()
    plants_repo = services.get("plants_repo") or PlantsRepository()

    app.register_blueprint(health_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(create_auth_bp(auth_service))
    app.register_blueprint(create_plants_bp(plants_repo))

    return app
