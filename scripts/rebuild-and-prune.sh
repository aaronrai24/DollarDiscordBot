#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$SCRIPT_DIR"

docker compose up -d --build

docker image prune -f
echo "Rebuild and prune complete"
