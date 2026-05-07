# spec.json Contract

## Purpose
Artefacto de especificación técnica generado por spec-engine.

## Location
`./proyectos/[id]/spec.json` en la carpeta de ejecución actual

`[id]` puede ser numérico o slug seguro como `miniso-pr`.

## Top-level structure
```json
{
  "project": {},
  "summary": {},
  "equipment_specs": [],
  "catalog_trace": {}
}
```

## `project`
Campos requeridos:
- `id`
- `name`
- `source_input`
- `source_results`
- `spec_status` = `completed | failed | partial`

## `summary`
Campos requeridos:
- `equipment_count`
- `selected_models_count`
- `failed_selections_count`

## `equipment_specs[]`
Cada spec incluye:
- `equipment_id`
- `equipment_alias`
- `kind`
- `extractor_type` — tipo derivado desde áreas servidas
- `required_m3_h`
- `selection_status`
- `selection_policy`
- `selection_reason`
- `selected_model`
- `alternatives`
- `constraints_used`
- `notes`

### Derivation policy
- si áreas servidas son solo `sencillo` → equipo `sencillo`
- cualquier otro caso → equipo `ducteable`

### `constraints_used`
Debe registrar filtros realmente usados. Para extractores comerciales incluye al menos:
- `kind`
- `extractor_type`

Puede incluir además:
- `installation_type`
- `voltage`
- `frequency_hz`

## `selected_model` / `alternatives[]`
Campos requeridos por modelo seleccionado/alternativo:
- `brand`
- `model`
- `extractor_type`
- `airflow_cfm`
- `airflow_m3_h`
- `voltage`
- `frequency_hz`
- `power_w`
- `power_kw`
- `installation_type`
- `image_asset`
- `source_url`
- `catalog_url`
- `image_source_url`
- `rating_basis`
- `source_notes`
- `retrieved_at`

## `catalog_trace`
Campos requeridos:
- `catalog_source`
- `catalog_version`
- `local_only = true`
- `selection_mode = auto-select-model`

## Selection policy
### `closest-airflow-above`
- filtrar por `kind`
- filtrar por `extractor_type`
- aplicar filtros opcionales restantes
- elegir menor exceso sobre `required_m3_h`
- empate: menor `power_w`

## Failure rules
- no usar modelo bajo caudal requerido
- no fallback web
- `selection_status = failed`
- `selected_model = null`
