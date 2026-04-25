# Calculation Rules Documentation

## Overview
Calculation policies for air renewal using DIN 1946 standards. Defines how RH (renovations per hour) and people-based methods compute required airflow, how ranges are resolved, and how governing method is selected.

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

Example:
- Volume: 21.6 m³
- RH target: 6.0 renovations/hour
- Result: `21.6 * 6.0 = 129.6 m³/h`

### Error Handling

**Missing RH rule**:
- Condition: No match for `catalog_sector` + `catalog_type`
- Action: Calculation **fails**
- Status: `failed`
- Message: `"Missing canonical RH rule for catalog_sector=X, catalog_type=Y"`

**Invalid rule format**:
- Condition: Rule has neither `min/max` nor `aprox`
- Action: Calculation **fails**
- Status: `failed`

## People Method

### Rule Lookup
Match on `catalog_type` only (no sector filter in people table).

Source: `rules/renovacion.json.tabla_caudal_por_persona`

### Applicability

**People is null**:
- Method marked `not_applicable`
- `result_m3_h = null`
- Trace: `"Not applicable: people is null"`
- Calculation proceeds using RH only

**People present**:
- Must find matching rule
- If no match found: calculation **fails**

### Rule Format

#### Single Value
```json
{
  "tipo_de_local": "Escuelas",
  "caudal_por_persona_m3_h": {
    "valor": 50
  }
}
```

Policy: **direct value**
- `caudal_persona_target = 50.0`

#### Min/Max Range
```json
{
  "tipo_de_local": "Habitaciones",
  "caudal_por_persona_m3_h": {
    "min": 40,
    "max": 80
  }
}
```

Policy: **same-as-rh-policy** (midpoint)
- `caudal_persona_target = (40 + 80) / 2 = 60.0`

### Calculation Formula
```
required_m3_h_people = people * caudal_persona_target
```

Example:
- People: 4
- Caudal per person: 75.0 m³/h
- Result: `4 * 75.0 = 300.0 m³/h`

### Error Handling

**People present but no mapping**:
- Condition: `people != null` and no rule found
- Action: Calculation **fails**
- Status: `failed`
- Message: `"People present (N) but no mapping found for catalog_type=X"`

**Invalid rule format**:
- Condition: Rule has neither `valor` nor `min/max`
- Action: Calculation **fails**
- Status: `failed`

## Governing Method Selection

### Policy: `max-of-both`

#### Logic
1. If both RH and people applicable:
   - Compare `result_m3_h_rh` vs `result_m3_h_people`
   - Select higher value
   - If equal: mark `tie`, use either (same value)

2. If only RH applicable (people null):
   - Use RH result

3. If only people applicable (RH missing):
   - Use people result
   - *Note*: RH always applicable in v1, this case theoretical

#### Outcomes
- `governing_method = "rh"`: RH result higher or people not applicable
- `governing_method = "people"`: People result higher
- `governing_method = "tie"`: Both methods equal

#### Examples

**RH wins**:
- RH result: 150.0 m³/h
- People result: 100.0 m³/h
- Final: 150.0 m³/h
- Governing: `rh`

**People wins**:
- RH result: 100.0 m³/h
- People result: 200.0 m³/h
- Final: 200.0 m³/h
- Governing: `people`

**Tie**:
- RH result: 150.0 m³/h
- People result: 150.0 m³/h
- Final: 150.0 m³/h
- Governing: `tie`

**Only RH (people null)**:
- RH result: 129.6 m³/h
- People result: null
- Final: 129.6 m³/h
- Governing: `rh`

## Rounding Policy

### Policy: `round-2-decimals`

All stored results rounded to 2 decimal places:
- `rh_target`
- `caudal_persona_target`
- `result_m3_h` (both methods)
- `required_m3_h_final`
- `required_m3_h_assigned` (equipment)
- `total_required_m3_h` (summary)

### Implementation
Python: `round(value, 2)`

### Examples
- `21.6 * 6.0 = 129.6` → stored as `129.6`
- `50.0 * 3.5 = 175.0` → stored as `175.0`
- `(5 + 7) / 2 = 6.0` → stored as `6.0`

## Trace Generation

### Human Trace

#### RH Method
Format: `Q_rh = V * RH = {volume:.2f} * {rh_target:.2f} = {result:.2f} m3/h`

Example: `"Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h"`

#### People Method
Format: `Q_people = P * q = {people} * {caudal:.2f} = {result:.2f} m3/h`

Example: `"Q_people = P * q = 4 * 75.00 = 300.00 m3/h"`

#### Not Applicable
Format: `Not applicable: {reason}`

Example: `"Not applicable: people is null"`

### Structured Trace

#### RH Method
```json
{
  "formula": "required_m3_h = volume_m3 * rh_target",
  "inputs": {
    "volume_m3": 21.6,
    "rh_target": 6.0
  },
  "operation": "multiply",
  "output": 129.6,
  "unit": "m3/h"
}
```

#### People Method
```json
{
  "formula": "required_m3_h = people * caudal_persona_target",
  "inputs": {
    "people": 4,
    "caudal_persona_target": 75.0
  },
  "operation": "multiply",
  "output": 300.0,
  "unit": "m3/h"
}
```

#### Not Applicable
```json
{
  "formula": null,
  "inputs": {},
  "operation": null,
  "output": null,
  "unit": "m3/h"
}
```

## Equipment Aggregation

### V1 Strategy: Direct Sum

For each equipment:
1. Identify `serves_area_ids`
2. Sum `required_m3_h_final` from those areas
3. Store as `required_m3_h_assigned`
4. Round to 2 decimals

Example:
- Equipment E1 serves areas A1, A2
- A1 final: 100.0 m³/h
- A2 final: 150.0 m³/h
- E1 assigned: `100.0 + 150.0 = 250.0 m³/h`

### No Optimization
V1 does not:
- Balance loads across multiple equipment
- Optimize equipment quantity
- Select commercial equipment from catalog

Status: `sizing_status = "not_sized_v1"`

## Project Summary

### Aggregation Rules

**Total required m³/h**:
- Sum all `area_results[].required_m3_h_final`
- Round to 2 decimals

**Areas with people**:
- Count areas where `inputs.people != null`

**Areas without people**:
- Count areas where `inputs.people == null`

**Governing method counts**:
- Count per method: `rh`, `people`, `tie`

### Example
3 areas:
- A1: RH only (people null) → 129.6 m³/h
- A2: People wins → 300.0 m³/h
- A3: Tie → 150.0 m³/h

Summary:
```json
{
  "total_required_m3_h": 579.6,
  "areas_count": 3,
  "equipment_count": 2,
  "areas_with_people": 2,
  "areas_without_people": 1,
  "governing_method_counts": {
    "rh": 1,
    "people": 1,
    "tie": 1
  }
}
```

## Policy Decision History

All policies frozen per 2026-04-22 design decisions:

| Policy | Decision | Rationale |
|---|---|---|
| Governing priority | `max-of-both` | Conservative approach ensures adequate ventilation |
| RH range resolution | `midpoint` | Balanced middle-ground value |
| People range resolution | `same-as-rh-policy` | Consistency across methods |
| Aprox treatment | `range-same` | Single-value fields treated uniformly |
| Rounding | `round-2-decimals` | Engineering precision standard |
| People null handling | `not_applicable` | Explicit non-error state |
| Missing RH rule | `fail` | Critical data missing, cannot proceed |
| People present no mapping | `fail` | Explicit data required when people specified |

## Future Extensions (Not V1)

Not implemented in v1:
- Multiple standard support (ASHRAE, etc.)
- Custom range policies per project
- Weighted averaging for ranges
- Probabilistic/Monte Carlo methods
- Automatic rule suggestion for unmapped types
- Equipment optimization algorithms
- Load balancing across equipment
- Commercial catalog integration
