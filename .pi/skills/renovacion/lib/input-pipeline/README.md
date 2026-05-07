# Input Pipeline Tooling

Validation and normalization tooling for `input.json` contract in renovation projects.

## Overview

This tooling implements the complete input validation pipeline for `./proyectos/[id]/input.json` in the current execution directory:
- **Schema validation** against unified contract
- **Critical/non-critical field** distinction for draft vs calc_ready
- **Flexible dimensions normalization** (shape A: area+height, shape B: length+width+height)
- **Catalog resolution** with normalized+synonyms policy against `rules/renovacion.json`
- **Sequential project ID allocation** (max + 1 rule) plus slug-compatible project directories
- **Cross-link validation** (area ↔ equipment consistency)

## Components

### 1. JSON Schema (`schema.json`)
Formal JSON Schema (draft-07) defining the complete `input.json` contract:
- Top-level keys: `project`, `validation`, `areas`, `equipment`, `defaults_applied`
- Null-present policy for metadata/placeholders
- Enum constraints for `status`, `catalog_sector`
- Flexible dimensions validation (anyOf: area_m2 OR length_m+width_m)

### 2. Python Validator (`validator.py`)
Full validation pipeline with:
- Schema compliance check
- Critical field validation (project.{id, name, ubicacion}, areas with sufficient dimensions)
- Non-critical field tracking
- Dimensions normalization (derives area_m2, volume_m3)
- Cross-link consistency (area ↔ equipment bidirectional references)
- Unique ID enforcement

**CLI Usage:**
```bash
python validator.py examples/input-pipeline/aurora-gmr.input.json
```

**Python Usage:**
```python
from validator import InputValidator

validator = InputValidator()
result = validator.validate(data, normalize=True)

# result = {
#     "valid": bool,
#     "errors": List[str],
#     "critical_complete": bool,
#     "missing_critical": List[str],
#     "missing_non_critical": List[str],
#     "notes": List[str],
#     "normalized_data": Dict (if normalize=True and valid)
# }
```

### 3. Catalog Resolver (`catalog_resolver.py`)
Resolves user input to canonical `catalog_type` + `catalog_sector` using:
- Exact normalized match (lowercase, trim, collapse spaces, remove accents)
- Explicit synonym mapping (e.g., "baño" → "Cuartos de baño")
- **No fuzzy matching** (strict policy)

**CLI Usage:**
```bash
python catalog_resolver.py "baño"
# Output:
# ✓ Resolved
#   Catalog Type: Cuartos de baño
#   Sector: residencial_domestico
```

**Python Usage:**
```python
from catalog_resolver import CatalogResolver

resolver = CatalogResolver()
catalog_type, sector, notes = resolver.resolve("oficina")
# → ("Oficinas", "terciario", ["Resolved synonym..."])
```

### 4. Project ID Allocator (`project_id_allocator.py`)
Sequential integer allocation for `./proyectos/[id]/`:
- Scans existing numeric directories
- Returns `max(existing_ids) + 1`
- Ignores non-numeric directories
- **No gap-filling** (always max + 1, not first available)

**CLI Usage:**
```bash
python project_id_allocator.py --next
# Next project ID: 2
# Path: /path/to/proyectos/2

python project_id_allocator.py --find "AURORA GMR"
# Found project 'AURORA GMR' with ID: 1
```

**Python Usage:**
```python
from project_id_allocator import ProjectIdAllocator

allocator = ProjectIdAllocator()
next_id = allocator.allocate_next_id()  # → 1, 2, 3, ...
project_path = allocator.ensure_project_dir(next_id)
```

## Critical vs Non-Critical Fields

### Critical (blocks calc_ready if missing):
- `project.id`
- `project.name`
- `project.ubicacion`
- At least one area
- Per area: `id`, `alias`, `catalog_type`, dimensions for volume derivation

### Non-Critical (can be null/missing in calc_ready):
- `project.{cliente, ingeniero, codia, empresa_calculo, logo_empresa, logo_cliente}`
- `areas[].people`
- Equipment list (can be empty)
- Equipment placeholders: `voltage`, `frequency_hz`, `installation_type`, `power_*`, `airflow_*`

## Dimensions Normalization

Two valid input shapes:

**Shape A: area + height**
```json
{
  "area_m2": 10.0,
  "height_m": 2.5
}
```
→ Derives `volume_m3 = 25.0`

**Shape B: length + width + height**
```json
{
  "length_m": 2.0,
  "width_m": 5.0,
  "height_m": 2.5
}
```
→ Derives `area_m2 = 10.0`, `volume_m3 = 25.0`

Normalization always produces:
- Preserved original fields
- Derived `area_m2` (if not provided)
- Derived `volume_m3`

## Catalog Resolution Policy

**Policy: normalized + synonyms only**

Resolution order:
1. Exact canonical match (normalized)
2. Synonym match (explicit map)
3. Unresolved → return None

**No fuzzy matching, no best-guess approximation.**

Synonym examples:
- `baño`, `baños`, `wc`, `sanitario` → `Cuartos de baño`
- `oficina` → `Oficinas`
- `garage`, `estacionamiento` → `Garages`

Extend synonyms in `catalog_resolver.py::_build_synonym_map()`.

## Cross-Link Validation

Areas and equipment maintain bidirectional references:
- `areas[].equipment_ids` → list of equipment IDs
- `equipment[].serves_area_ids` → list of area IDs

**Rules:**
- If area A references equipment E, E must reference A
- If equipment E references area A, A must reference E
- No dangling references (all IDs must exist)

## Draft vs Calc Ready

**Draft:**
- `project.status = "draft"`
- `validation.critical_complete = false`
- Can be saved with missing critical fields
- Used for iterative data collection

**Calc Ready:**
- `project.status = "calc_ready"`
- `validation.critical_complete = true`
- All critical fields present
- Non-critical fields may still be missing
- Ready for calculation engine downstream

## Testing

Run all tests:
```bash
cd tests/input-pipeline
pytest -v
```

Test modules:
- `test_schema.py`: JSON schema validation edge cases
- `test_catalog.py`: Catalog resolution (canonical, synonyms, normalization)
- `test_dimensions.py`: Normalization for shapes A/B, conflict resolution
- `test_project_id.py`: Sequential allocation, max+1 rule, gap handling
- `test_validation.py`: Critical/non-critical validation, cross-links, unique IDs

## Fixtures

Example input.json files for testing:
- `fixtures/valid_calc_ready.json`: Full valid calc_ready project
- `fixtures/valid_draft.json`: Valid draft with missing non-critical fields
- `fixtures/invalid_missing_critical.json`: Missing critical fields
- `fixtures/invalid_cross_links.json`: Broken area ↔ equipment references

## Next Steps

This tooling is consumed by **input-validator-agent**, which:
1. Receives user data
2. Applies defaults (if AURORA GMR bootstrap)
3. Allocates project ID
4. Normalizes dimensions
5. Resolves catalog types
6. Validates structure
7. Writes `./proyectos/[id]/input.json`
8. Reports status (draft/calc_ready) to orchestrator

Downstream of `input.json`:
- Calculation engine reads validated `input.json`
- Produces `resultados.json`
- Selector agent produces `spec.json`
- Memory generator produces HTML/PDF
