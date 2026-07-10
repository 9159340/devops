# Minimal internal messaging app for on-prem deploy labs.

## Stack

| Layer | Choice | Vendor |
|-------|--------|--------|
| Backend | Python + [FastAPI](https://fastapi.tiangolo.com/) | — |
| Frontend | Static HTML/JS (no build step) behind [Nginx](https://nginx.org/) | F5 / Nginx |
| Database | [PostgreSQL](https://www.postgresql.org/) 16 | PostgreSQL Global Development Group |
| Runtime | [Docker](https://www.docker.com/) Compose | Docker Inc. |
| Artifacts | Images in local [Distribution registry](https://distribution.github.io/distribution/) | CNCF / Distribution |

## Features

1. Registration (username + password, no email confirmation) → JWT session.
2. Compose page: text field + Submit → row in DB (`user_id`, `text`, `created_at`).
3. My messages: only the current user's messages.

## Quick start (local)

```bash
cd app
docker compose up --build -d
```

Open http://localhost:8080

- Register → compose → submit → **My messages**.
- Health: http://localhost:8080/health

Stop:

```bash
docker compose down
```

## Local registry (artifacts)

Start registry on port 5000:

```bash
docker compose -f docker-compose.registry.yml up -d
```

If the daemon treats `localhost:5000` as insecure, add to Docker daemon config (`insecure-registries`) or use HTTPS in a real lab.

Build & push:

```bash
# Git Bash / WSL / Linux
chmod +x scripts/push-images.sh
./scripts/push-images.sh

# or manually
export REGISTRY=localhost:5000 TAG=v1
docker compose build
docker push localhost:5000/internal-messages-backend:v1
docker push localhost:5000/internal-messages-frontend:v1
```

Pull & run from registry (example):

```bash
export REGISTRY=localhost:5000 TAG=v1
docker compose pull   # if images already pushed
docker compose up -d
```

## Layout

```
app/
  backend/          # FastAPI + SQLAlchemy
  frontend/         # static UI + nginx reverse proxy to API
  scripts/          # push helpers
  docker-compose.yml
  docker-compose.registry.yml
```

## API (brief)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/register` | — | create user, return JWT |
| POST | `/api/login` | — | login, return JWT |
| GET | `/api/me` | Bearer | current user |
| POST | `/api/messages` | Bearer | create message |
| GET | `/api/messages` | Bearer | list own messages |
| GET | `/health` | — | liveness |

## Env

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql://app:app@db:5432/messages` | set in compose |
| `SECRET_KEY` | `dev-secret-change-me` | override in prod |
| `REGISTRY` | `localhost:5000` | image prefix |
| `TAG` | `latest` | image tag |

Do not commit real secrets; use `.env` (gitignored) or a vault outside VCS.
