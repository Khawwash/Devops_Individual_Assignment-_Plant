# Assignment 2 Report

## Overview
Flask API with app factory (`src/components/Backend/App_factory.py`), SQLite repository layer, Prometheus metrics, Docker/Gunicorn, and Compose stack with Prometheus/Grafana. Target: keep behavior, improve testability/monitoring/CI.

## Refactors & Smells Addressed
- Dependency injection: `create_app(config=None, services=None)` allows injected db/auth/metrics services; routes now accept injected repos/services (plants, auth).
- Config hardening: `FLASK_SECRET_KEY` required in production; env overrides for base/data dirs; `PLANT_DB_PATH` honored across routes/repo.
- Metrics fallback: Prometheus optional with warning; fallback payload still exposes `http_requests_total`.
- Error handling: Plants route returns stable JSON/200 on unexpected errors; specific DB errors return 500 with message.
- Packaging/imports: Added `__init__.py` markers; pytest path fixing; wsgi entry in place.
- Docker/Compose: PYTHONPATH set; Gunicorn entry correct; compose builds image, sets PLANT_DB_PATH volume and default secret.

## Tests & Coverage
- Command: `pytest --cov=src --cov-report=term-missing --cov-fail-under=70`
- Coverage ~94% locally; `.coveragerc` omits entrypoints/legacy data helpers.
- Key tests: auth routes (validation/conflict), plants search (happy/empty/error), metrics/health/pages, DB env override, app factory config.

## CI Pipeline
- Workflow `.github/workflows/ci.yml`: checkout, Python 3.12, prep temp DB path, install deps (including lint/test tools), ruff lint, pytest with coverage gate (70%), upload coverage.xml, Docker build (tag plants-api:ci). Deploy job triggers webhook on `main` (DEPLOY_HOOK_URL secret).

## Docker & Monitoring
- Dockerfile: python:3.12-slim, installs requirements, runs Gunicorn `src.components.Backend.wsgi:app` on 3000, PYTHONPATH=/app.
- Compose: services api (builds image, mounts ./data to /data, PLANT_DB_PATH=/data/Plant.db, default secret), prometheus (scrapes api:3000/metrics), grafana (optional).
- Prometheus config: scrape_interval 5s, target `api:3000`, metrics_path `/metrics`.

## Future Work
- Add structured logging + request IDs.
- Seed plants data on first run or via migration script.
- Harden auth flow (sessions/JWT) and add rate limiting.
- Add integration tests for Prometheus endpoint with real client installed.
