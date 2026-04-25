#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/run-project.sh <project-id>" >&2
  exit 2
fi

PROJECT_ID="$1"
if ! [[ "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
  echo "Project id must be numeric" >&2
  exit 1
fi

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_PATH="proyectos/${PROJECT_ID}"

cd "$SKILL_ROOT"

echo "Renovacion skill smoke: project ${PROJECT_ID}"

python scripts/run-calc.py "$PROJECT_ID"
python scripts/run-spec.py "$PROJECT_ID"
bash scripts/run-memory.sh "$PROJECT_ID"

for file in input.json resultados.json spec.json memoria.html; do
  if [ ! -f "${PROJECT_PATH}/${file}" ]; then
    echo "Missing ${PROJECT_PATH}/${file}" >&2
    exit 1
  fi
done

if grep -qi "cdn.jsdelivr\|unpkg.com" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html contains CDN references" >&2
  exit 1
fi

if ! grep -q "AURORA GMR" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html missing AURORA GMR" >&2
  exit 1
fi

if ! grep -q "EX-150" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html missing EX-150" >&2
  exit 1
fi

echo "OK: ${PROJECT_PATH}"
