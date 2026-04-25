# Input Validation Rules

## Purpose
Congelar reglas de comportamiento del pipeline de entrada para `input.json`.

## Critical Fields
Un proyecto puede pasar a `calc_ready` solo cuando existen:
- `project.id`
- `project.name`
- `project.ubicacion`
- al menos un elemento en `areas`
- por cada área:
  - `id`
  - `alias`
  - `catalog_type`
  - dimensiones suficientes para derivar volumen

## Non-Critical Fields
Pueden faltar sin bloquear `calc_ready`:
- `project.cliente`
- `project.ingeniero`
- `project.codia`
- `project.empresa_calculo`
- `project.logo_empresa`
- `project.logo_cliente`
- `areas[].people`
- `equipment` completo o parcial
- placeholders técnicos de `equipment`
- `notes`

Nota:
- aunque metadata no crítica puede faltar lógicamente, en archivo se guarda con política `null-present`

## Draft vs Calc Ready
### Draft
Usar cuando falta al menos un campo crítico.

Reglas:
- `project.status = "draft"`
- `validation.critical_complete = false`
- `validation.missing_critical` lista faltantes exactos
- archivo puede guardarse aunque no esté listo para cálculo

### Calc Ready
Usar cuando todos los campos críticos están completos.

Reglas:
- `project.status = "calc_ready"`
- `validation.critical_complete = true`
- `validation.missing_critical = []`
- `validation.missing_non_critical` puede no estar vacío

## Flexible Dimensions Rules
Se aceptan dos formas válidas por área.

### Variant A
- `area_m2`
- `height_m`

Resultado esperado tras normalización:
- preservar `area_m2`
- preservar `height_m`
- derivar `volume_m3`

### Variant B
- `length_m`
- `width_m`
- `height_m`

Resultado esperado tras normalización:
- preservar `length_m`
- preservar `width_m`
- preservar `height_m`
- derivar `area_m2`
- derivar `volume_m3`

## Invalid Values Policy
Debe fallar cuando:
- dimensión requerida falta y no puede derivarse
- valores negativos
- cero donde invalida cálculo
- ids duplicados
- referencias cruzadas inconsistentes

## Catalog Resolution Policy
Política congelada para v1:
- `normalized+synonyms`
- sin fuzzy matching

Orden de resolución:
1. valor exacto canónico
2. valor normalizado exacto
3. mapa explícito de sinónimos
4. si no resuelve, no adivinar

### Normalization minimum
Normalización puede incluir:
- trim
- lowercase para comparar
- colapsar espacios repetidos
- remover diferencias de acentos si así se define en tooling

Salida canónica:
- `catalog_type` debe terminar con valor exacto de `rules/renovacion.json`
- `catalog_sector` debe terminar con sector exacto correspondiente

### Unresolved Catalog Behavior
- no usar mejor coincidencia aproximada
- devolver `needs_input` si falta aclaración del usuario
- devolver `failed` si dato es contradictorio o no puede resolverse bajo reglas del sistema

## Project Id Allocation Policy
Base path:
- `/proyectos/`

Regla:
- buscar directorios numéricos existentes
- siguiente id = `max + 1`
- si no hay directorios válidos, siguiente id = `1`
- directorios no numéricos se ignoran
- no usar “primer hueco libre”; usar siempre `max + 1`

## Existing Project Reuse Policy
No reusar proyecto existente solo por coincidencia exacta de nombre.

Reusar id solo cuando:
- usuario/orquestador indica explícitamente proyecto existente
- existe contexto de proyecto ya resuelto en handoff

Si no existe confirmación explícita:
- crear nuevo id secuencial

## Cross-Link Consistency Rules
Debe mantenerse consistencia entre:
- `areas[].equipment_ids`
- `equipment[].serves_area_ids`

Reglas:
- si un área referencia `E1`, `E1` debe referenciar esa área
- si un equipo referencia `A1`, `A1` debe referenciar ese equipo
- referencias a ids inexistentes fallan validación

## Status Handling
### `completed`
- `input.json` fue creado/actualizado de forma válida
- puede quedar en `draft` o `calc_ready`

### `needs_input`
- faltan datos de usuario o aclaración de catálogo
- preguntas se devuelven al orquestador

### `blocked`
- falta schema/tooling/dependencia upstream
- ejemplo: validador o resolver de catálogo aún no existe

### `failed`
- contradicción dura
- dimensiones inválidas
- ids duplicados
- enlaces inconsistentes

## AURORA GMR Bootstrap Defaults
Si no hay override explícito, aplicar:
- `name = AURORA GMR`
- `ubicacion = Distrito Nacional`
- `ingeniero = Osmar Garcia`
- `codia = 36467`
- `empresa_calculo = ORGM`
- `logo_empresa = https://r2.or-gm.com/orgm.png`
- `cliente = BOHC SRL`
- `logo_cliente = https://r2.or-gm.com/bohc.png`

Registrar campos aplicados en `defaults_applied`.
