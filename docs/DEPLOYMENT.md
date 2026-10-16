# Deployment and clean-checkout verification

The application is a single Python process with a file-based SQLite database. It needs no external
services: the schema and the demo content are created on first start.

## Configuration

All settings come from environment variables, so the same code runs on a laptop, in CI and in a
container. `.env.example` documents the keys; never commit real values.

| Variable | Default | Purpose |
|---|---|---|
| `APP_NAME` | `Greenhill Food Co-op` | Application title |
| `APP_SECRET` | `dev-only-change-me` | Session signing key - **must be set outside local development** |
| `APP_DB_PATH` | `data/greenhill.db` | SQLite file, relative to the project root or absolute |
| `APP_HOST` | `127.0.0.1` | Listen address; use `0.0.0.0` inside a container |
| `APP_PORT` | `8000` | Listen port |
| `APP_DEBUG` | `0` | `1` enables debug behaviour |

`APP_HOST` matters for deployment: a container that binds `127.0.0.1` cannot be reached through a
published port even though `EXPOSE` and `ports:` are declared. The Dockerfile and `docker-compose.yml`
therefore set `APP_HOST=0.0.0.0`.

## Local

```bash
git clone https://github.com/zhihe-zhang1/greenhill-food-coop.git
cd greenhill-food-coop-main
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Open <http://127.0.0.1:8000> and sign in with a demo account (see the README).

## Docker

```bash
docker build -t greenhill-food-coop .
docker run --rm -p 8000:8000 -v "$PWD/data:/app/data" greenhill-food-coop

# or, with the compose file (adds a restart policy and a health check):
docker compose up --build
```

The image runs as the unprivileged `app` user, publishes port 8000 and defines a health check that
polls `/api/health`. `.dockerignore` keeps the virtual environment, local databases, secrets and
caches out of the build context.

## Verification

Run these steps from a clean checkout; they are the release checklist in `docs/RELEASE_PLAN.md`.

```bash
pytest -q                                       # expect: all tests pass
python run.py                                   # start the local server
curl -s http://127.0.0.1:8000/api/health       # expect: {"status":"ok"}
APP_HOST=0.0.0.0 APP_PORT=8123 python run.py   # expect "Uvicorn running on http://0.0.0.0:8123"
```

| Check | Expected result |
|---|---|
| `pytest -q` | Whole suite passes |
| `/api/health` | `{"status":"ok"}` with HTTP 200 |
| Unauthenticated `/packing/round/1` | HTTP 401 |
| Member requesting `/api/rounds/1/totals` | HTTP 403 |
| Coordinator `/reports/round/<id>/csv` | CSV download named `greenhill_round_<n>.csv` |
| Container start | `docker compose ps` shows the service `healthy` |

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `http://127.0.0.1:8000` unreachable after `docker run -p 8000:8000` | The process bound loopback inside the container. Set `APP_HOST=0.0.0.0` (the image already does). |
| `OSError: [Errno 98] Address already in use` | Another process holds the port; set `APP_PORT` or stop the other process. |
| Session lost on every request | `APP_SECRET` changes between starts; set a stable value. |
| `data/greenhill.db` missing | The file is created on first start by the schema in `app/db.py`; confirm the working directory is writable. |
| Tests fail with a database error | `APP_DB_PATH` points at a read-only location; the test suite sets its own temporary path. |
