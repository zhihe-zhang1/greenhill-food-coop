# Deployment Guide

## Overview

Greenhill Food Co-op is a FastAPI application backed by SQLite. The repository includes a Dockerfile and Docker Compose configuration so the application can be started consistently without manually configuring Python on the host.

## Prerequisites

- Docker Desktop or Docker Engine
- Docker Compose

## Start with Docker Compose

From the repository root:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

The health endpoint is:

```text
http://127.0.0.1:8000/api/health
```

A healthy response is:

```json
{"status":"ok"}
```

## Stop the application

```bash
docker compose down
```

The SQLite database is stored in the local `data/` directory and is mounted into the container, so application data remains available after the container is recreated.

## Environment configuration

The deployment uses the following settings:

| Variable | Purpose | Example |
| --- | --- | --- |
| `APP_NAME` | Application display name | `Greenhill Food Co-op` |
| `APP_SECRET` | Session signing secret | Set a private value |
| `APP_DB_PATH` | SQLite database path | `/app/data/greenhill.db` |
| `APP_DEBUG` | Debug setting | `0` |

For any deployment outside local demonstration, replace the default `APP_SECRET` before starting the container.

Example:

```bash
APP_SECRET="replace-with-a-long-random-secret" docker compose up --build
```

## Build and run without Compose

```bash
docker build -t greenhill-food-coop .
docker run --rm -p 8000:8000 \
  -e APP_SECRET="replace-with-a-long-random-secret" \
  -e APP_DB_PATH="/app/data/greenhill.db" \
  -v "$(pwd)/data:/app/data" \
  greenhill-food-coop
```

## Deployment checks

After deployment:

1. Open `/api/health` and confirm the response is `{"status":"ok"}`.
2. Open the login page and sign in with a demo account.
3. Confirm the member, coordinator and packing pages load.
4. Run `pytest -q` before a release or deployment.

## Production considerations

This configuration is suitable for coursework demonstration and repeatable local deployment. A real production deployment should additionally use HTTPS, a secure externally managed session secret, regular database backups, restricted host access and an appropriate reverse proxy or managed hosting platform.
