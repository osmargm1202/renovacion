#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
	echo "Usage: bash scripts/run-project.sh <project-id>" >&2
	exit 2
fi

PROJECT_ID="$1"
if ! [[ "$PROJECT_ID" =~ ^[A-Za-z0-9_-][A-Za-z0-9._-]*$ ]]; then
	echo "Project id must contain only letters, numbers, dots, underscores, and hyphens" >&2
	exit 1
fi

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_PATH="${PWD}/proyectos/${PROJECT_ID}"

echo "Renovacion skill smoke: project ${PROJECT_ID}"
echo "Workflow: calc -> memory"

python "${SKILL_ROOT}/scripts/run-calc.py" "$PROJECT_ID"
bash "${SKILL_ROOT}/scripts/run-memory.sh" "$PROJECT_ID"

for file in input.json resultados.json memoria.html; do
	if [ ! -f "${PROJECT_PATH}/${file}" ]; then
		echo "Missing ${PROJECT_PATH}/${file}" >&2
		exit 1
	fi
done

if grep -qi "cdn.jsdelivr\|unpkg.com" "${PROJECT_PATH}/memoria.html"; then
	echo "memoria.html contains CDN references" >&2
	exit 1
fi

if ! grep -q "Resumen de Necesidad por Área" "${PROJECT_PATH}/memoria.html"; then
	echo "memoria.html missing Resumen de Necesidad por Área" >&2
	exit 1
fi

if grep -q "Selección de Equipos" "${PROJECT_PATH}/memoria.html"; then
	echo "memoria.html contains Selección de Equipos" >&2
	exit 1
fi

echo "OK: ${PROJECT_PATH}"
