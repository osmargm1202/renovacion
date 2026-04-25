# Skill Source of Truth Commercial Spec Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `.pi/skills/renovacion/` the only runtime source of truth and upgrade the skill-local spec engine to select source-backed commercial extractor models by explicit `areas[].extractor_type`.

**Architecture:** Add explicit area usage category to input, derive equipment category from served areas, filter catalog by exact category before airflow selection, then render category/provenance in spec and memory output. Keep runtime local-only for equipment catalog and images. Remove root duplicate runtime files after skill-local tests pass.

**Tech Stack:** Python 3.13, pytest, jsonschema, local JSON catalog, Node.js CommonJS, Bash skill wrappers, Git.

---

## Constraints
- TDD required: RED test first, verify failure, then implementation, then GREEN.
- Production changes only under `.pi/skills/renovacion/` until cleanup task.
- Preserve `.pi/skills/renovacion/proyectos/[id]/`.
- Preserve `docs/superpowers/**`, `pdd/**`, `.gitignore`.
- Runtime must not do live web lookup for equipment catalog/images.
- Use two local category images only: `assets/extractores/sencillo.png`, `assets/extractores/ducteable.png`.

## Task 0: Baseline

- [ ] Run:
```bash
git status --short
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
```
Expected: clean or only planning artifacts untracked; validator OK; current tests pass; smoke OK.

## Task 1: Input `areas[].extractor_type`

**Files:**
- Create `.pi/skills/renovacion/tests/test_input_extractor_type.py`
- Modify `.pi/skills/renovacion/lib/input-pipeline/schema.json`
- Modify `.pi/skills/renovacion/lib/input-pipeline/validator.py`
- Modify `.pi/skills/renovacion/examples/input-pipeline/aurora-gmr.input.json`
- Modify `.pi/skills/renovacion/proyectos/1/input.json`

- [ ] Write tests for:
  - missing `extractor_type` fails validation
  - invalid value `industrial` fails validation
  - valid values `sencillo` and `ducteable` pass
- [ ] Run RED:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_input_extractor_type.py
```
Expected: fails because schema currently lacks required enum.
- [ ] Update schema area required list and properties:
```json
"extractor_type": {
  "type": "string",
  "enum": ["sencillo", "ducteable"],
  "description": "Extractor usage category. Explicit input; not inferred from capacity."
}
```
- [ ] Add `extractor_type` to validator critical area fields.
- [ ] Add `"extractor_type": "sencillo"` to AURORA example and project 1 input area.
- [ ] Run GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_input_extractor_type.py
```
Expected: 3 passed.
- [ ] Commit:
```bash
git add .pi/skills/renovacion/tests/test_input_extractor_type.py .pi/skills/renovacion/lib/input-pipeline/schema.json .pi/skills/renovacion/lib/input-pipeline/validator.py .pi/skills/renovacion/examples/input-pipeline/aurora-gmr.input.json .pi/skills/renovacion/proyectos/1/input.json
git commit -m "feat: require extractor type on areas"
```

## Task 2: Commercial catalog validation + category images

**Files:**
- Create `.pi/skills/renovacion/tests/test_catalog_commercial_fields.py`
- Create `.pi/skills/renovacion/assets/extractores/sencillo.png`
- Create `.pi/skills/renovacion/assets/extractores/ducteable.png`
- Modify `.pi/skills/renovacion/lib/spec-engine/catalog_validator.py`
- Modify `.pi/skills/renovacion/lib/spec-engine/catalog/models.json`

- [ ] Write tests for:
  - valid commercial model with source fields passes
  - missing `extractor_type` and `source_url` fail
  - remote `image_asset` fails
  - invalid `extractor_type` fails
  - string voltage/frequency are accepted
- [ ] Run RED:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_catalog_commercial_fields.py
```
Expected: fails because validator/catalog lacks commercial field requirements.
- [ ] Copy category images:
```bash
cp .pi/skills/renovacion/assets/extractores/ex-150.png .pi/skills/renovacion/assets/extractores/sencillo.png
cp .pi/skills/renovacion/assets/extractores/ex-250.png .pi/skills/renovacion/assets/extractores/ducteable.png
```
- [ ] Update catalog validator:
  - required fields: `brand`, `model`, `kind`, `extractor_type`, `airflow_cfm`, `airflow_m3_h`, `voltage`, `frequency_hz`, `power_w`, `power_kw`, `installation_type`, `image_asset`, `source_url`, `catalog_url`, `image_source_url`, `rating_basis`, `source_notes`, `retrieved_at`
  - enum: `sencillo`, `ducteable`
  - local image set only
  - voltage/frequency allow number or non-empty string
  - `power_kw` consistent with `power_w / 1000`
- [ ] Replace `models.json` with commercial seed data from `pdd/.../explore-commercial-catalog-research`.
  - simple rows use `extractor_type: sencillo`, image `assets/extractores/sencillo.png`
  - ductable rows use `extractor_type: ducteable`, image `assets/extractores/ducteable.png`
  - do not include synthetic ORGM `EX-*` or `INY-*` entries
- [ ] Validate actual catalog:
```bash
uv run --project .pi/skills/renovacion python - <<'PY'
import importlib.util, json, sys
from pathlib import Path
root = Path('.pi/skills/renovacion')
pkg = root / 'lib/spec-engine'
spec = importlib.util.spec_from_file_location('renovacion_spec_engine', pkg / '__init__.py', submodule_search_locations=[str(pkg)])
module = importlib.util.module_from_spec(spec)
sys.modules['renovacion_spec_engine'] = module
spec.loader.exec_module(module)
from renovacion_spec_engine.catalog_validator import validate_catalog
catalog = json.loads((pkg / 'catalog/models.json').read_text(encoding='utf-8'))
valid, invalid = validate_catalog(catalog['models'])
print(valid)
print(len(invalid))
if invalid: print(invalid)
PY
```
Expected: `True`, `0`.
- [ ] Run GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_catalog_commercial_fields.py
```
Expected: passes.
- [ ] Commit:
```bash
git add .pi/skills/renovacion/tests/test_catalog_commercial_fields.py .pi/skills/renovacion/lib/spec-engine/catalog_validator.py .pi/skills/renovacion/lib/spec-engine/catalog/models.json .pi/skills/renovacion/assets/extractores/sencillo.png .pi/skills/renovacion/assets/extractores/ducteable.png
git commit -m "feat: add source-backed extractor catalog"
```

## Task 3: Category filter + derived equipment type

**Files:**
- Create `.pi/skills/renovacion/tests/test_spec_engine_extractor_type.py`
- Modify `.pi/skills/renovacion/lib/spec-engine/filters.py`
- Modify `.pi/skills/renovacion/lib/spec-engine/runner.py`
- Modify `.pi/skills/renovacion/lib/spec-engine/assembler.py`

- [ ] Write tests for:
  - `apply_filters(... extractor_type='ducteable')` returns only ductable models
  - ductable equipment never selects simple model even if simple is closer
  - mixed served area types resolve to ducteable
  - selected model output includes source/provenance fields
- [ ] Run RED:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_spec_engine_extractor_type.py
```
Expected: fails because filters/runner/assembler lack category/provenance.
- [ ] Update `filters.apply_filters()` with optional `extractor_type` exact filter before installation/electrical filters.
- [ ] Add `derive_equipment_extractor_type(equipment, input_data)` to runner:
```python
if served_types == {"sencillo"}:
    return "sencillo"
return "ducteable"
```
- [ ] Pass derived type to filters and `constraints_used`.
- [ ] Update assembler output to include `equipment_specs[].extractor_type` and selected/alternative model fields: `extractor_type`, `airflow_cfm`, `source_url`, `catalog_url`, `image_source_url`, `rating_basis`, `source_notes`, `retrieved_at`.
- [ ] Run GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_spec_engine_extractor_type.py
```
Expected: passes.
- [ ] Commit:
```bash
git add .pi/skills/renovacion/tests/test_spec_engine_extractor_type.py .pi/skills/renovacion/lib/spec-engine/filters.py .pi/skills/renovacion/lib/spec-engine/runner.py .pi/skills/renovacion/lib/spec-engine/assembler.py
git commit -m "feat: select extractors by explicit category"
```

## Task 4: Memory output renders extractor type

**Files:**
- Create `.pi/skills/renovacion/tests/test_memory_extractor_type.py`
- Modify `.pi/skills/renovacion/lib/memory-engine/sections/seleccion-equipos.js`

- [ ] Write Node subprocess test asserting `renderSeleccionEquipos()` includes `Tipo de extractor: ducteable` and selected model text.
- [ ] Run RED:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_memory_extractor_type.py
```
Expected: fails because renderer does not show extractor type.
- [ ] Update memory equipment subtitle and spec rows to include `extractor_type || selected_model.extractor_type || 'N/A'`.
- [ ] Run GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_memory_extractor_type.py
```
Expected: passes.
- [ ] Commit:
```bash
git add .pi/skills/renovacion/tests/test_memory_extractor_type.py .pi/skills/renovacion/lib/memory-engine/sections/seleccion-equipos.js
git commit -m "feat: render extractor type in memory"
```

## Task 5: Smoke expectations + docs

**Files:**
- Modify `.pi/skills/renovacion/scripts/run-project.sh`
- Modify `.pi/skills/renovacion/tests/test_python_wrappers.py`
- Modify `.pi/skills/renovacion/tests/test_memory_wrapper.py`
- Modify docs under `.pi/skills/renovacion/docs/contracts/`
- Generated: `.pi/skills/renovacion/proyectos/1/{resultados.json,spec.json,memoria.html,assets/**}`

- [ ] Run wrapper tests RED after commercial catalog change:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_python_wrappers.py .pi/skills/renovacion/tests/test_memory_wrapper.py
```
Expected: old `EX-150` expectations fail.
- [ ] Update expectations to `Delta Breez` / `80F / GreenBuilder` / `extractor_type: sencillo` / source URL.
- [ ] Update `run-project.sh` smoke greps for `80F / GreenBuilder` and `Tipo de extractor: sencillo`.
- [ ] Update contract docs:
  - `input-json.md`: area `extractor_type`
  - `input-validation-rules.md`: critical enum
  - `local-catalog.md`: commercial source-backed schema + image policy
  - `spec-json.md`: output type/provenance
  - `memory-assets.md`: two category images
  - `memoria-html.md`: visible type
- [ ] Run GREEN:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_python_wrappers.py .pi/skills/renovacion/tests/test_memory_wrapper.py
bash .pi/skills/renovacion/scripts/run-project.sh 1
```
Expected: pass, smoke OK.
- [ ] Commit:
```bash
git add .pi/skills/renovacion/scripts/run-project.sh .pi/skills/renovacion/tests/test_python_wrappers.py .pi/skills/renovacion/tests/test_memory_wrapper.py .pi/skills/renovacion/docs/contracts .pi/skills/renovacion/proyectos/1
git commit -m "docs: document commercial extractor selection"
```

## Task 6: Root cleanup + README

**Files:**
- Modify `README.md`
- Delete root duplicates listed below.

- [ ] Safety check:
```bash
test -d .pi/skills/renovacion/proyectos/1 && test -d docs/superpowers && test -d pdd && test -f .gitignore
```
Expected: exit 0.
- [ ] Replace `README.md` with minimal usage:
```markdown
# Renovacion

Self-contained Pi skill for renovation-airflow calculation, equipment specification, and HTML memory generation.

## Source of truth

Runtime code and project artifacts live under `.pi/skills/renovacion/`.

Project artifacts are stored under `.pi/skills/renovacion/proyectos/[id]/`.

## Validate

```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

## Notes

The commercial extractor catalog is local JSON. Runtime does not perform live web lookup for equipment models or equipment images.
```
- [ ] Delete root duplicates:
```bash
rm -rf assets examples lib rules proyectos scripts tests docs/contracts
rm -rf docs/runbooks docs/implementation-reports
rm -f main.py pyproject.toml uv.lock .python-version
rm -rf .pi/agents .pi/.agents
rm -rf .pytest_cache .venv .pi/agent-sessions .pi/skills/renovacion/.venv
find . -name '__pycache__' -type d -prune -exec rm -rf {} +
find . -name '*.pyc' -delete
```
- [ ] Assert cleanup:
```bash
test ! -e lib && test ! -e assets && test ! -e rules && test ! -e proyectos && test ! -e scripts && test ! -e tests && test -d .pi/skills/renovacion/proyectos/1 && test -d docs/superpowers && test -d pdd && test -f README.md
```
Expected: exit 0.
- [ ] Assert stale root references gone:
```bash
git grep -n "scripts/run-project-1\|lib/calc-engine\|proyectos/1" -- ':!docs/superpowers/**' ':!pdd/**' ':!.pi/skills/renovacion/**'
```
Expected: no matches; command exits 1.
- [ ] Commit:
```bash
git add -A README.md assets examples lib rules proyectos scripts tests docs/contracts docs/runbooks docs/implementation-reports main.py pyproject.toml uv.lock .python-version .pi/agents .pi/.agents
git commit -m "chore: remove root duplicate runtime files"
```

## Task 7: Final validation

- [ ] Run:
```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
test ! -e lib && test ! -e assets && test ! -e rules && test ! -e proyectos && test ! -e scripts && test ! -e tests
git grep -n "scripts/run-project-1\|lib/calc-engine\|proyectos/1" -- ':!docs/superpowers/**' ':!pdd/**' ':!.pi/skills/renovacion/**'
git status --short
```
Expected: validator/tests/smoke pass; delete assertion passes; stale grep no matches; status clean except PDD/design artifacts if not committed.
- [ ] Commit final generated project artifacts if changed:
```bash
git add .pi/skills/renovacion/proyectos/1
git commit -m "test: refresh project one commercial outputs"
```
Expected: commit if changed, otherwise nothing to commit.

## Review groups
- `review-input-catalog`: input contract, catalog validator, commercial source fields, image policy.
- `review-spec-memory`: category derivation/filtering, spec output, memory output.
- `review-cleanup`: root cleanup, README, no stale root refs, skill still passes.
