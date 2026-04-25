#!/usr/bin/env bash
# Smoke Test: Full pipeline for project 1 (AURORA GMR)
# Executes calc-engine → spec-engine → memory-engine and validates output

set -e

PROJECT_ID=1
PROJECT_PATH="proyectos/${PROJECT_ID}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$REPO_ROOT"

echo "=========================================="
echo "Project 1 Smoke Test - AURORA GMR"
echo "=========================================="
echo ""

# Preconditions
echo "Checking preconditions..."
if [ ! -f "${PROJECT_PATH}/input.json" ]; then
  echo "❌ Missing ${PROJECT_PATH}/input.json"
  exit 1
fi

if [ ! -d "lib/calc-engine" ]; then
  echo "❌ Missing lib/calc-engine/"
  exit 1
fi

if [ ! -d "lib/spec-engine" ]; then
  echo "❌ Missing lib/spec-engine/"
  exit 1
fi

if [ ! -d "lib/memory-engine" ]; then
  echo "❌ Missing lib/memory-engine/"
  exit 1
fi

echo "✅ Preconditions OK"
echo ""

# Step 1: Calc Engine
echo "Step 1/3: Checking calc-engine outputs..."
if [ ! -f "${PROJECT_PATH}/resultados.json" ]; then
  echo "❌ Missing ${PROJECT_PATH}/resultados.json"
  echo "   (calc-engine runner not yet implemented in v1)"
  exit 1
fi
echo "✅ resultados.json exists"
echo ""

# Step 2: Spec Engine
echo "Step 2/3: Checking spec-engine outputs..."
if [ ! -f "${PROJECT_PATH}/spec.json" ]; then
  echo "❌ Missing ${PROJECT_PATH}/spec.json"
  echo "   (spec-engine runner not yet implemented in v1)"
  exit 1
fi
echo "✅ spec.json exists"
echo ""

# Step 3: Memory Engine
echo "Step 3/3: Running memory-engine..."
if command -v node &> /dev/null; then
  node lib/memory-engine/runner.js "$PROJECT_ID" "$PROJECT_PATH"
else
  echo "❌ Node.js not found, cannot run memory-engine"
  exit 1
fi

if [ ! -f "${PROJECT_PATH}/memoria.html" ]; then
  echo "❌ Failed to generate memoria.html"
  exit 1
fi
echo "✅ memoria.html generated"
echo ""

# Validation
echo "Validating outputs..."

# Check expected content
if ! grep -q "AURORA GMR" "${PROJECT_PATH}/memoria.html"; then
  echo "❌ memoria.html missing 'AURORA GMR'"
  exit 1
fi

if ! grep -q "129.6" "${PROJECT_PATH}/memoria.html"; then
  echo "❌ memoria.html missing expected airflow '129.6'"
  exit 1
fi

if ! grep -q "EX-150" "${PROJECT_PATH}/memoria.html"; then
  echo "❌ memoria.html missing selected model 'EX-150'"
  exit 1
fi

# Check no CDN dependencies
if grep -qi "cdn.jsdelivr\|unpkg.com" "${PROJECT_PATH}/memoria.html"; then
  echo "❌ memoria.html contains CDN references (should be offline-capable)"
  exit 1
fi

# Check local KaTeX
if ! grep -q "assets/vendor/katex" "${PROJECT_PATH}/memoria.html"; then
  echo "❌ memoria.html not using vendored KaTeX"
  exit 1
fi

echo "✅ Content validation passed"
echo ""

# Summary
echo "=========================================="
echo "✅ SMOKE TEST PASSED"
echo "=========================================="
echo ""
echo "Outputs:"
echo "  - ${PROJECT_PATH}/resultados.json"
echo "  - ${PROJECT_PATH}/spec.json"
echo "  - ${PROJECT_PATH}/memoria.html"
echo "  - ${PROJECT_PATH}/assets/"
echo ""
echo "Memoria is offline-capable (vendored KaTeX)"
