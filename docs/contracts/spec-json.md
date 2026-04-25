# spec.json Contract

## Purpose
Equipment technical specification artifact output from spec-engine.

## Location
`/proyectos/[id]/spec.json`

## Schema

### Top-Level Structure
```json
{
  "project": {},
  "summary": {},
  "equipment_specs": [],
  "catalog_trace": {}
}
```

### `project`
Project identity and status.

**Required:**
- `id` (int): project ID
- `name` (str): project name
- `source_input` (str): path to input.json
- `source_results` (str): path to resultados.json
- `spec_status` (str): `completed` | `failed` | `partial`

### `summary`
Aggregate counts.

**Required:**
- `equipment_count` (int): total equipment count
- `selected_models_count` (int): count with `selection_status=selected`
- `failed_selections_count` (int): count with `selection_status=failed`

### `equipment_specs`
Array of specs, one per equipment node.

**Each spec:**
- `equipment_id` (str): matches input.json
- `equipment_alias` (str): matches input.json
- `kind` (str): extractor, inyector, etc.
- `required_m3_h` (float): from resultados.json
- `selection_status` (str): `selected` | `failed`
- `selection_policy` (str): `closest-airflow-above`
- `selection_reason` (str): human trace
- `selected_model` (obj | null): model fields if selected
- `alternatives` (array): up to 3 valid models excluding selected
- `constraints_used` (obj): filters applied
- `notes` (array): warnings/issues

**`selected_model` fields (if selected):**
- `brand` (str)
- `model` (str)
- `airflow_m3_h` (float)
- `voltage` (int)
- `frequency_hz` (int)
- `power_w` (float)
- `power_kw` (float)
- `installation_type` (str)
- `image_asset` (str, optional)

**`alternatives` fields:**
Same as `selected_model`.

### `catalog_trace`
Metadata about catalog and policy.

**Required:**
- `catalog_source` (str): `local-catalog-v1`
- `catalog_version` (str): version identifier
- `local_only` (bool): true for v1
- `selection_mode` (str): `auto-select-model`

## Selection Statuses

### `selected`
Model found meeting `required_m3_h`.

### `failed`
No eligible model with `airflow_m3_h >= required_m3_h`.

## Selection Policy

### v1: `closest-airflow-above`
- Filter eligible models: `airflow_m3_h >= required_m3_h`
- Select minimum excess over required
- Tie-break: lower `power_w`

## Failure Rules
- No model below required airflow used
- No multi-unit optimization
- No web fallback
- `selection_status = failed` and `selected_model = null`

## Alternatives Policy
- Top 3 valid models excluding selected
- Ordered by selection criterion
- Empty array if < 2 valid models total

## Version
Contract v1 — 2026-04-23
