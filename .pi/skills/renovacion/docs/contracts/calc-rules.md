# Calculation Rules Documentation

## Overview

Calculation policies for air renewal using DIN 1946 standards. Defines how RH (renovations per hour) and people-based methods compute required airflow, how ranges are resolved, and how governing method is selected.

Default output is demand-only and area-only: calculation emits project summary plus per-area demand. Equipment aggregation and commercial selection stay outside default `resultados.json`.

## Data Source

All rules loaded from: `rules/renovacion.json`

## RH Method

### Rule Lookup

Exact match required on:

- `catalog_sector` (e.g., `residencial_domestico`, `terciario`, `industrial`)
- `catalog_type` (e.g., `Cuartos de baño`, `Aulas`, `Oficinas`)

Source: `rules/renovacion.json.tablas_renovaciones_aire`

### Rule Format

#### Min/Max Range

```json
{
  "tipo_de_local": "Cuartos de baño",
  "renovaciones_aire_por_hora": {
    "min": 5,
    "max": 7
  }
}
```

Policy: **midpoint**

- `rh_min = 5`
- `rh_max = 7`
- `rh_target = (5 + 7) / 2 = 6.0`

#### Approximate Value

```json
{
  "tipo_de_local": "Garages",
  "renovaciones_aire_por_hora": {
    "aprox": 5
  }
}
```

Policy: **range-same** (treat as single value)

- `rh_min = 5`
- `rh_max = 5`
- `rh_target = 5.0`

### Calculation Formula

```
required_m3_h_rh = volume_m3 * rh_target
```

## People Method

### Rule Lookup

Match on `catalog_type` only (no sector filter in people table).

Source: `rules/renovacion.json.tabla_caudal_por_persona`

### Applicability

**People is null**:

- Method marked `not_applicable`
- `result_m3_h = null`
- `result_cfm = null`
- Trace: `"Not applicable: people is null"`
- Calculation proceeds using RH only

**People present**:

- Must find matching rule
- If no match found: calculation **fails**

### Calculation Formula

```
required_m3_h_people = people * caudal_persona_target
```

## Governing Method Selection

### Policy: `max-of-both`

1. If both RH and people applicable, choose higher value.
2. If only RH applicable, use RH.
3. If values tie, mark `tie`.

## Unit Conversion Policy

Airflow results are stored in both m³/h and CFM.

Formula:

```text
Q_CFM = Q_m3_h * 0.5885777702
Q_m3_h = Q_CFM * 1.6990107955
```

Stored CFM fields:

- `result_cfm` (method blocks)
- `required_cfm_final` (area results)
- `total_required_cfm` (summary)

## Rounding Policy

### Policy: `round-2-decimals`

All stored results rounded to 2 decimal places:

- `rh_target`
- `caudal_persona_target`
- `result_m3_h` and `result_cfm` (both methods)
- `required_m3_h_final` and `required_cfm_final`
- `total_required_m3_h` and `total_required_cfm` (summary)

## Trace Generation

### Human Trace

- RH: `Q_rh = V * RH = {volume:.2f} * {rh_target:.2f} = {result:.2f} m3/h`
- People: `Q_people = P * q = {people} * {caudal:.2f} = {result:.2f} m3/h`
- Not applicable: `Not applicable: {reason}`

### Structured Trace

Machine-readable formula, inputs, operation, output, and unit.

## Project Summary

### Aggregation Rules

- `total_required_m3_h`: sum all `area_results[].required_m3_h_final`
- `areas_with_people`: count areas where `inputs.people != null`
- `areas_without_people`: count areas where `inputs.people == null`
- `governing_method_counts`: count per method `rh`, `people`, `tie`

### Example

```json
{
  "total_required_m3_h": 579.6,
  "total_required_cfm": 341.11,
  "areas_count": 3,
  "areas_with_people": 2,
  "areas_without_people": 1,
  "governing_method_counts": {
    "rh": 1,
    "people": 1,
    "tie": 1
  }
}
```

## Demand-only exclusions

Default calculation output does not include:

- equipment aggregation blocks
- equipment counters in summary
- area-to-equipment link echoes
- commercial catalog decisions

## Future Extensions (Not V1)

- Multiple standard support (ASHRAE, etc.)
- Custom range policies per project
- Automatic rule suggestion for unmapped types
- Future/manual equipment aggregation or commercial selection via separate scope
