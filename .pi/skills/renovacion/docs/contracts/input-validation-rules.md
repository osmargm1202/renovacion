# Input Validation Rules

## Purpose

Congelar reglas de validación para `input.json` en flujo demand-only de solo áreas/necesidad.

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
  - dimensiones suficientes para derivar volumen

## `areas[].extractor_type`

Regla opcional.

Valores válidos cuando existe:

- `sencillo`
- `ducteable`

Debe fallar cuando:

- valor no pertenece a enum
- valor vacío

No debe fallar cuando:

- falta `extractor_type` en flujo default demand-only

Política:

- categoría por uso explícito
- no inferir desde capacidad, CFM o m³/h
- reservar para future/manual equipment scope

## Non-critical fields

Pueden faltar sin bloquear `calc_ready`:

- `project.cliente`
- `project.ingeniero`
- `project.codia`
- `project.empresa_calculo`
- `project.logo_empresa`
- `project.logo_cliente`
- `areas[].people`
- `areas[].equipment_ids`
- top-level `equipment`
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
- referencias cruzadas inconsistentes cuando ambos lados de scope manual existen
- `areas[].extractor_type` fuera de enum

## Cross-link consistency rules

Solo aplica cuando existe payload manual de equipos.

Puede validarse consistencia entre:

- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

Si payload de equipos falta o está vacío, validación demand-only no falla por enlaces.
Si área omite `equipment_ids`, `equipment[].serves_area_ids` no obliga eco inverso.

## Status handling

### `completed`

`input.json` creado/actualizado de forma válida.

### `needs_input`

Faltan datos de usuario o aclaración de catálogo.

### `blocked`

Falta schema/tooling/dependencia upstream.

### `failed`

Contradicción dura, ids duplicados, dimensiones inválidas o enum inválido.
