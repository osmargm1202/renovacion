#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
	echo "Usage: bash scripts/run-memory.sh <project-id>" >&2
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

if [ ! -f "${PROJECT_PATH}/input.json" ]; then
	echo "Missing ${PROJECT_PATH}/input.json" >&2
	exit 1
fi
if [ ! -f "${PROJECT_PATH}/resultados.json" ]; then
	echo "Missing ${PROJECT_PATH}/resultados.json" >&2
	exit 1
fi

node lib/memory-engine/runner.js "$PROJECT_ID" "$PROJECT_PATH"
