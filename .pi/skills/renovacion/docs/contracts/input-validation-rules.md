# Input Validation Rules

## Purpose
Congelar reglas de validación para `input.json`.

## Critical fields
Proyecto puede pasar a `calc_ready` solo cuando existen:
- `project.id`
- `project.name`
- `project.ubicacion`
- al menos un elemento en `areas`
- por cada área:
  - `id`
  - `alias`
  - `catalog_type`
  - `extractor_type`
  - dimensiones suficientes para derivar volumen

## `areas[].extractor_type`
Regla crítica.

Valores válidos:
- `sencillo`
- `ducteable`

Debe fallar cuando:
- falta `extractor_type`
- valor no pertenece a enum
- valor vacío

Política:
- categoría por uso explícito
- no inferir desde capacidad, CFM o m³/h

## Non-critical fields
Pueden faltar sin bloquear `calc_ready`:
- `project.cliente`
- `project.ingeniero`
- `project.codia`
- `project.empresa_calculo`
- `project.logo_empresa`
- `project.logo_cliente`
- `areas[].people`
- placeholders técnicos de `equipment`
- `notes`

## Draft vs calc_ready
### Draft
Usar cuando falta al menos un campo crítico.

### Calc ready
Usar cuando todos los campos críticos están completos, aunque `missing_non_critical` no esté vacío.

## Flexible dimensions rules
### Variant A
- `area_m2`
- `height_m`

Resultado:
- preservar `area_m2`
- preservar `height_m`
- derivar `volume_m3`

### Variant B
- `length_m`
- `width_m`
- `height_m`

Resultado:
- preservar `length_m`
- preservar `width_m`
- derivar `area_m2`
- derivar `volume_m3`

## Invalid values policy
Debe fallar cuando:
- dimensión requerida falta y no puede derivarse
- valores negativos
- cero donde invalida cálculo
- ids duplicados
- referencias cruzadas inconsistentes
- `areas[].extractor_type` fuera de enum

## Cross-link consistency rules
Debe mantenerse consistencia entre:
- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

## Status handling
### `completed`
`input.json` creado/actualizado de forma válida.

### `needs_input`
Faltan datos de usuario o aclaración de catálogo.

### `blocked`
Falta schema/tooling/dependencia upstream.

### `failed`
Contradicción dura, ids duplicados, dimensiones inválidas o enum inválido.
