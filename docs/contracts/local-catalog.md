# Local Catalog Contract

## Purpose
Local model database for spec-engine selection. Policy: `local-only`, `install-basic`.

## Location
`lib/spec-engine/catalog/models.json`

## Schema

### Top-Level Structure
```json
{
  "catalog": {
    "version": "1",
    "source": "local-catalog-v1",
    "last_updated": "2026-04-23"
  },
  "models": []
}
```

### `models` Array
Each model entry:

**Required fields:**
- `brand` (str): manufacturer
- `model` (str): model identifier
- `kind` (str): `extractor`, `inyector`, etc.
- `airflow_m3_h` (float): airflow in m³/h
- `voltage` (int): volts
- `frequency_hz` (int): Hz
- `power_w` (float): power in watts
- `power_kw` (float): power in kilowatts (redundant for convenience)
- `installation_type` (str): `muro`, `techo`, `conducto`, etc.

**Optional fields:**
- `image_asset` (str): relative path to image
- `notes` (array): internal notes

## Validation Rules

### Field Presence
All required fields must exist.

### Type Constraints
- `airflow_m3_h > 0`
- `voltage > 0`
- `frequency_hz > 0`
- `power_w >= 0`
- `power_kw >= 0`
- `power_kw == power_w / 1000` (consistency)

### Enum Constraints
- `kind`: must match known equipment types
- `installation_type`: must match known installation modes

## Filter Compatibility
Models filtered by:
- `kind` (exact match)
- `installation_type` (exact match if specified in input)
- `voltage` (exact match if specified in input)
- `frequency_hz` (exact match if specified in input)

## Eligibility Criterion
Model eligible if:
- passes filters
- `airflow_m3_h >= required_m3_h`

## Version
Contract v1 — 2026-04-23
