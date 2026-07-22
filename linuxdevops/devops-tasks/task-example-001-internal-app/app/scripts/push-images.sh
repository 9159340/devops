#!/usr/bin/env bash
# Build images and push to local registry (default localhost:5000).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
REGISTRY="${REGISTRY:-localhost:5000}"
TAG="${TAG:-latest}"

export REGISTRY TAG

echo "Building images…"
docker compose -f "$ROOT/docker-compose.yml" build

echo "Pushing to ${REGISTRY}…"
docker push "${REGISTRY}/internal-messages-backend:${TAG}"
docker push "${REGISTRY}/internal-messages-frontend:${TAG}"

echo "Done: ${REGISTRY}/internal-messages-*:${TAG}"
