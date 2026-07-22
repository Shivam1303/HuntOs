#!/usr/bin/env bash

set -euo pipefail

api_port="${APP_PORT:-8000}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

require_command docker
require_command curl

echo "==> Validating Docker Compose configuration"
docker compose config --quiet

echo "==> Service status"
docker compose ps

echo "==> Checking PostgreSQL readiness"
docker compose exec -T postgres pg_isready -U hunter -d hunter

echo "==> Checking Alembic revision in the API container"
docker compose exec -T api alembic current

echo "==> Checking API health endpoint"
health_response="$(curl --fail --silent --show-error "http://localhost:${api_port}/health")"
if [[ "$health_response" != '{"status":"ok"}' ]]; then
  echo "Unexpected health response: $health_response" >&2
  exit 1
fi

echo "==> All Docker services are healthy"
