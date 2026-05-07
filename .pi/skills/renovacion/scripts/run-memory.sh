#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
	echo "Usage: bash scripts/run-memory.sh <project-id>" >&2
	exit 2
fi

PROJECT_ID="$1"
if ! [[ "$PROJECT_ID" =~ ^[A-Za-z0-9_-][A-Za-z0-9._-]*$ ]]; then
	echo "Project id must contain only letters, numbers, dots, underscores, and hyphens" >&2
	exit 1
fi

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_PATH="${PWD}/proyectos/${PROJECT_ID}"

if [ ! -f "${PROJECT_PATH}/input.json" ]; then
	echo "Missing ${PROJECT_PATH}/input.json" >&2
	exit 1
fi
if [ ! -f "${PROJECT_PATH}/resultados.json" ]; then
	echo "Missing ${PROJECT_PATH}/resultados.json" >&2
	exit 1
fi

node "${SKILL_ROOT}/lib/memory-engine/runner.js" "$PROJECT_ID" "$PROJECT_PATH"
