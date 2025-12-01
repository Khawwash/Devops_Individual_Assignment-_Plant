# Plant Care API

Flask backend with SQLite, Prometheus metrics, and Docker/Compose support.

## Quickstart (local)
- Python 3.12+; create venv: `python3 -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Run app: `python -m src.components.Backend.App` (serves on `http://localhost:3000`)
- Key env vars: `FLASK_SECRET_KEY` (set in prod), `PORT` (default 3000), `PLANT_DB_PATH` (default `./data/Plant.db`)

## Tests & Coverage
- `pytest --cov=src --cov-report=term-missing --cov-fail-under=70`
- Pytest config: `pytest.ini` (adds `src` to path, filters Deprecation/Resource warnings)
- Coverage omit rules in `.coveragerc` (entrypoints/legacy files excluded)

## Docker
- Build: `docker build -t plants-api:dev .`
- Run:  
  ```sh
  docker run --rm -p 3000:3000 \
    -e FLASK_ENV=production \
    -e PLANT_DB_PATH=/data/Plant.db \
    -e FLASK_SECRET_KEY=change-me \
    -v "$PWD/data:/data" \
    plants-api:dev
  ```
- WSGI entry: `src/components/Backend/wsgi.py` (`src.components.Backend.wsgi:app`)

## Docker Compose + Prometheus
- `docker compose up -d --build`
- Prometheus scrapes `api:3000/metrics` (see `prometheus.yml`), Grafana at `http://localhost:3001`

## Endpoints
- Health: `GET /health`
- Metrics: `GET /metrics`
- Plants search: `GET /api/plants/search?q=...`
- Pages: `/`, `/login`, `/signup`, `/dashboard`, etc.

## CI/CD
- GitHub Actions workflow runs ruff lint, pytest w/ coverage (fail-under 70%), uploads coverage, builds Docker image.
- Optional deploy step triggers webhook on `main` (see `.github/workflows/ci.yml`).

## Env example
- `.env.example` provided; copy to `.env` and adjust secrets/paths as needed.
