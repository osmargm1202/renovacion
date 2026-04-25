# Resultados JSON Contract

## Purpose
`resultados.json` stores calculation results for air renewal projects. Contains per-area calculations with dual-method tracing (RH + people), governing method selection, equipment aggregation, and project summary.

Target path:
- `/proyectos/[id]/resultados.json`

## Top-Level Shape
```json
{
  "project": {},
  "summary": {},
  "area_results": [],
  "equipment_results": [],
  "calculation_trace": {}
}
```

## `project`

| Field | Type | Required | Notes |
|---|---|---:|---|
| `id` | integer | yes | project ID from input |
| `name` | string | yes | project name from input |
| `source_input` | string | yes | path to source input.json |
| `calculation_status` | enum | yes | `completed`, `failed`, `partial` |

## `summary`

Project-level aggregated metrics.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `total_required_m3_h` | number | yes | sum of all area finals, 2 decimals |
| `total_required_cfm` | number | yes | sum converted to CFM, 2 decimals |
| `areas_count` | integer | yes | total areas calculated |
| `equipment_count` | integer | yes | total equipment entries |
| `areas_with_people` | integer | yes | areas where people != null |
| `areas_without_people` | integer | yes | areas where people == null |
| `governing_method_counts` | object | yes | count per method: `{rh, people, tie}` |

## `area_results[]`

List of calculation results per area.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `area_id` | string | yes | matches input area ID |
| `area_alias` | string | yes | human name |
| `catalog_type` | string | yes | canonical type from catalog |
| `catalog_sector` | string | yes | canonical sector from catalog |
| `inputs` | object | yes | echoed inputs used |
| `methods` | object | yes | RH + people method blocks |
| `governing_method` | enum | yes | `rh`, `people`, or `tie` |
| `required_m3_h_final` | number | yes | final result, 2 decimals |
| `required_cfm_final` | number | yes | final result converted to CFM, 2 decimals |
| `linked_equipment_ids` | string[] | yes | equipment serving this area |
| `notes` | string[] | yes | calc-specific notes |

### `area_results[].inputs`

```json
{
  "dimensions": {
    "length_m": 2.0,
    "width_m": 4.0,
    "height_m": 2.7,
    "area_m2": 8.0,
    "volume_m3": 21.6
  },
  "volume_m3": 21.6,
  "people": null
}
```

### `area_results[].methods`

Contains both `rh` and `people` method blocks.

#### RH Method Block

| Field | Type | Required | Notes |
|---|---|---:|---|
| `applicable` | boolean | yes | always `true` for RH |
| `source` | string | yes | rule source reference |
| `rh_min` | number\|null | yes | from rule |
| `rh_max` | number\|null | yes | from rule |
| `rh_target` | number | yes | midpoint or aprox value |
| `result_m3_h` | number | yes | V * RH, 2 decimals |
| `result_cfm` | number | yes | result converted to CFM, 2 decimals |
| `trace_human` | string | yes | readable formula trace |
| `trace_structured` | object | yes | machine trace |

Example:
```json
{
  "applicable": true,
  "source": "rules/renovacion.json.tablas_renovaciones_aire",
  "rh_min": 5,
  "rh_max": 7,
  "rh_target": 6.0,
  "result_m3_h": 129.6,
  "result_cfm": 76.28,
  "trace_human": "Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h",
  "trace_structured": {
    "formula": "required_m3_h = volume_m3 * rh_target",
    "inputs": {
      "volume_m3": 21.6,
      "rh_target": 6.0
    },
    "operation": "multiply",
    "output": 129.6,
    "unit": "m3/h"
  }
}
```

#### People Method Block

| Field | Type | Required | Notes |
|---|---|---:|---|
| `applicable` | boolean | yes | `false` if people null |
| `source` | string | yes | rule source reference |
| `caudal_persona_target` | number\|null | yes | target from rule or null |
| `result_m3_h` | number\|null | yes | P * q, or null |
| `trace_human` | string | yes | readable trace or not-applicable |
| `trace_structured` | object | yes | machine trace |

Example (not applicable):
```json
{
  "applicable": false,
  "source": "rules/renovacion.json.tabla_caudal_por_persona",
  "caudal_persona_target": null,
  "result_m3_h": null,
  "trace_human": "Not applicable: people is null",
  "trace_structured": {
    "formula": null,
    "inputs": {},
    "operation": null,
    "output": null,
    "unit": "m3/h"
  }
}
```

Example (applicable):
```json
{
  "applicable": true,
  "source": "rules/renovacion.json.tabla_caudal_por_persona",
  "caudal_persona_target": 75.0,
  "result_m3_h": 300.0,
  "trace_human": "Q_people = P * q = 4 * 75.00 = 300.00 m3/h",
  "trace_structured": {
    "formula": "required_m3_h = people * caudal_persona_target",
    "inputs": {
      "people": 4,
      "caudal_persona_target": 75.0
    },
    "operation": "multiply",
    "output": 300.0,
    "unit": "m3/h"
  }
}
```

## `equipment_results[]`

Aggregated results per equipment.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `equipment_id` | string | yes | matches input equipment ID |
| `equipment_alias` | string | yes | human name |
| `kind` | string\|null | yes | functional type |
| `cantidad` | number\|null | yes | quantity from input |
| `serves_area_ids` | string[] | yes | areas served |
| `required_m3_h_assigned` | number | yes | sum of area demands, 2 decimals |
| `required_cfm_assigned` | number | yes | assigned demand converted to CFM, 2 decimals |
| `sizing_status` | enum | yes | `not_sized_v1` in v1 |
| `notes` | string[] | yes | equipment-specific notes |

Example:
```json
{
  "equipment_id": "E1",
  "equipment_alias": "Extractor baño principal",
  "kind": "extractor",
  "cantidad": 1,
  "serves_area_ids": ["A1"],
  "required_m3_h_assigned": 129.6,
  "sizing_status": "not_sized_v1",
  "notes": []
}
```

## `calculation_trace`

Global calculation metadata for audit.

| Field | Type | Required | Notes |
|---|---|---:|---|
| `rounding_policy` | string | yes | `round-2-decimals` |
| `range_policy` | string | yes | `midpoint` |
| `governing_policy` | string | yes | `max-of-both` |

Example:
```json
{
  "rounding_policy": "round-2-decimals",
  "range_policy": "midpoint",
  "governing_policy": "max-of-both"
}
```

## Governing Method Logic

### `max-of-both`
- If both RH and people applicable: use max value
- If only RH applicable: use RH
- If only people applicable: use people
- If both equal: mark `tie`, use either (same value)

## Rounding Policy

### `round-2-decimals`
- All stored `result_m3_h` values rounded to 2 decimal places
- All stored `required_m3_h_*` values rounded to 2 decimal places
- Intermediate calculations may use higher precision
- Display consistency: trace outputs match stored precision

## Error States

### Missing RH Rule
If `catalog_sector` + `catalog_type` has no match in `tablas_renovaciones_aire`:
- Calculation fails
- Status: `failed`
- Error must be reported to user

### People Present But No Mapping
If `people != null` but `catalog_type` has no match in `tabla_caudal_por_persona`:
- Calculation fails
- Status: `failed`
- Error must be reported to user

### People Null
If `people == null`:
- People method marked `not_applicable`
- RH method used
- Calculation proceeds normally

## V1 Limitations

### No Commercial Sizing
- `equipment_results` does not include commercial specs
- `sizing_status` always `not_sized_v1`
- No automatic equipment selection from catalog
- Quantity optimization not performed

### Direct Aggregation Only
- Equipment demand = sum of served area demands
- No load balancing or distribution optimization

## Full Example

See `proyectos/1/resultados.json` for AURORA GMR golden example.

```json
{
  "project": {
    "id": 1,
    "name": "AURORA GMR",
    "source_input": "/proyectos/1/input.json",
    "calculation_status": "completed"
  },
  "summary": {
    "total_required_m3_h": 129.6,
    "areas_count": 1,
    "equipment_count": 1,
    "areas_with_people": 0,
    "areas_without_people": 1,
    "governing_method_counts": {
      "rh": 1,
      "people": 0,
      "tie": 0
    }
  },
  "area_results": [
    {
      "area_id": "A1",
      "area_alias": "Baño principal",
      "catalog_type": "Cuartos de baño",
      "catalog_sector": "residencial_domestico",
      "inputs": {
        "dimensions": {
          "length_m": 2.0,
          "width_m": 4.0,
          "height_m": 2.7,
          "area_m2": 8.0,
          "volume_m3": 21.6
        },
        "volume_m3": 21.6,
        "people": null
      },
      "methods": {
        "rh": {
          "applicable": true,
          "source": "rules/renovacion.json.tablas_renovaciones_aire",
          "rh_min": 5,
          "rh_max": 7,
          "rh_target": 6.0,
          "result_m3_h": 129.6,
          "trace_human": "Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h",
          "trace_structured": {
            "formula": "required_m3_h = volume_m3 * rh_target",
            "inputs": {
              "volume_m3": 21.6,
              "rh_target": 6.0
            },
            "operation": "multiply",
            "output": 129.6,
            "unit": "m3/h"
          }
        },
        "people": {
          "applicable": false,
          "source": "rules/renovacion.json.tabla_caudal_por_persona",
          "caudal_persona_target": null,
          "result_m3_h": null,
          "trace_human": "Not applicable: people is null",
          "trace_structured": {
            "formula": null,
            "inputs": {},
            "operation": null,
            "output": null,
            "unit": "m3/h"
          }
        }
      },
      "governing_method": "rh",
      "required_m3_h_final": 129.6,
      "linked_equipment_ids": ["E1"],
      "notes": []
    }
  ],
  "equipment_results": [
    {
      "equipment_id": "E1",
      "equipment_alias": "Extractor baño principal",
      "kind": "extractor",
      "cantidad": 1,
      "serves_area_ids": ["A1"],
      "required_m3_h_assigned": 129.6,
      "sizing_status": "not_sized_v1",
      "notes": []
    }
  ],
  "calculation_trace": {
    "rounding_policy": "round-2-decimals",
    "range_policy": "midpoint",
    "governing_policy": "max-of-both"
  }
}
```

## Lifecycle

Input requirement: `input.json` with `status == "calc_ready"`

Output states:
- `completed`: all areas calculated successfully
- `failed`: calculation error (missing rules, invalid data)
- `partial`: some areas calculated (not implemented in v1)

## Consumer Agents

Primary consumers:
- `spec-agent` (future): uses `resultados.json` to select commercial equipment
- `memory-agent` (future): uses traces for report generation
- Human reviewers: audit calculations via traces
