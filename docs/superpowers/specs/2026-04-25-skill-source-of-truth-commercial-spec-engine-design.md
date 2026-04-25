# Skill Source of Truth + Commercial Spec Engine Design

**Change:** `skill-source-of-truth-commercial-spec-engine`  
**Status:** Approved  
**Source of truth:** `.pi/skills/renovacion/`

## Goal
Make `.pi/skills/renovacion/` the only runtime source of truth, remove root duplicate runtime files, and upgrade the skill-local spec engine to select source-backed commercial extractor models by explicit area usage category.

## Approved Decisions
- `.pi/skills/renovacion/` is source of truth.
- Delete duplicate/non-used root runtime files outside the skill.
- Preserve `.pi/skills/renovacion/**`, `README.md` minimal usage doc, `docs/superpowers/**`, `pdd/**`, `.gitignore`.
- Preserve all project artifacts under `.pi/skills/renovacion/proyectos/[id]/`.
- Update spec-engine inside `.pi/skills/renovacion/` only.
- Add required `areas[].extractor_type` with enum values `sencillo` and `ducteable`.
- Equipment category derives from served areas: all `sencillo` => `sencillo`; otherwise `ducteable` (mixed uses `ducteable`).
- Category is intended use, not inferred from capacity.
- Selector filters exact `extractor_type` before airflow capacity.
- Catalog is local JSON, no live web lookup at runtime.
- Use two local category images: `assets/extractores/sencillo.png` and `assets/extractores/ducteable.png`.
- Catalog keeps source/provenance fields.

## Architecture
Pipeline stays self-contained inside skill:

```text
input.json areas[].extractor_type
  -> spec runner derives equipment extractor_type from served areas
  -> filters apply kind + exact extractor_type + optional install/electrical filters
  -> selector picks closest airflow above demand inside category
  -> assembler writes extractor_type + commercial provenance to spec.json
  -> memory renders extractor type + local category image
```

Runtime must not fetch commercial equipment data or equipment images from web. URLs in catalog are provenance only.

## Contract Changes

### Input area
Each area requires:

```json
"extractor_type": "sencillo"
```

Valid values:
- `sencillo`: simple bathroom/residential/kitchen-light extraction.
- `ducteable`: ducted, commercial, kitchen-capable, professional, or industrial extraction.

### Equipment category derivation
```python
served_types = {area["extractor_type"] for area in served_areas}
if served_types == {"sencillo"}:
    equipment_extractor_type = "sencillo"
else:
    equipment_extractor_type = "ducteable"
```

### Catalog model fields
Required fields per model:
- `brand`, `model`, `kind`, `extractor_type`
- `airflow_cfm`, `airflow_m3_h`
- `power_w`, `power_kw`, optional `power_hp`
- `voltage`, `frequency_hz`, `installation_type`
- `image_asset`
- `source_url`, `catalog_url`, `image_source_url`
- `rating_basis`, `source_notes`, `retrieved_at`
- `airflow_unit_original`, `power_unit_original`, `notes`

`image_asset` must be one of:
- `assets/extractores/sencillo.png`
- `assets/extractores/ducteable.png`

## Seed Catalog Data
Use source-backed seed rows from `pdd/skill-source-of-truth-commercial-spec-engine/explore-commercial-catalog-research`.

Simple (`sencillo`) seed brands:
- Delta Breez: 50F, 70F, 80F, 100F, 110F, 130HS.
- Broan-NuTone: AE80, AE110, LP80.

Ductable (`ducteable`) seed brands:
- Broan-NuTone: L200, L300, L300KMG, L400.
- Sodeca: NEOLINEO, NEOSILENT, CA/LINE, TUB rows.
- S&P USA: TD-MIXVENT, TD-SILENT rows.

Conversions:
- `m3_h = cfm * 1.69901082`
- `cfm = m3_h * 0.58857777`
- `power_kw = power_w / 1000`

## Selection Example
For AURORA bathroom (`129.6 m³/h`, `extractor_type: sencillo`):
- filter simple models only
- closest eligible at/above 129.6 m³/h includes Delta 80F and Broan AE80 at 135.9 m³/h
- tie breaks by lower power
- selected model should be `Delta Breez 80F / GreenBuilder`

For same airflow but `ducteable`, simple models are ignored; select closest ductable model above demand, such as `S&P USA TD-MIXVENT 100` or Sodeca NEOLINEO 100/V depending selector tie/power rules.

## Root Cleanup
Delete root duplicates/stale runtime files:

```text
assets/
examples/
lib/
rules/
proyectos/
scripts/
tests/
docs/contracts/
docs/runbooks/
docs/implementation-reports/
main.py
pyproject.toml
uv.lock
.python-version
.pi/agents/
.pi/.agents/
```

Clean ignored caches:
```text
.pytest_cache/
.venv/
.pi/agent-sessions/
__pycache__/
*.pyc
.pi/skills/renovacion/.venv/
```

Keep:
```text
.git/
.gitignore
.pi/skills/renovacion/**
docs/superpowers/**
pdd/**
README.md
```

## Acceptance Criteria
- Missing/invalid `areas[].extractor_type` fails validation.
- AURORA input/examples include `extractor_type`.
- Catalog validator rejects entries missing category/provenance or using remote runtime image asset.
- Selector filters exact `extractor_type` before capacity.
- Mixed served area types resolve to `ducteable`.
- `spec.json` includes `extractor_type` and provenance fields.
- `memoria.html` shows `Tipo de extractor`.
- Root duplicate files are removed; skill tests/smoke still pass.

## Final Validation
```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
test ! -e lib && test ! -e assets && test ! -e rules && test ! -e proyectos && test ! -e scripts && test ! -e tests
git grep -n "scripts/run-project-1\|lib/calc-engine\|proyectos/1" -- ':!docs/superpowers/**' ':!pdd/**' ':!.pi/skills/renovacion/**'
```

Expected: validator/tests/smoke pass, delete assertion passes, stale grep has no matches.
