# Spec Engine Design

## Goal
Diseñar el cuarto subproyecto de `renovacion`: el motor de especificación técnica que consumirá `/proyectos/[id]/input.json` y `/proyectos/[id]/resultados.json`, usará un catálogo local, y producirá `/proyectos/[id]/spec.json` con fichas técnicas seleccionadas automáticamente.

## Scope
Incluye:
- Contrato de `spec.json`
- Contrato mínimo del catálogo local
- Reglas de elegibilidad y selección
- Política `local-only`
- Política `auto-select-model`
- Criterio `closest-airflow-above`
- Regla de fallo si no existe modelo válido
- Política de desempate `lower-power`
- Política de alternativas `top-3-valid`
- Criterios de prueba para `AURORA GMR`

No incluye todavía:
- Web search
- Fallback por internet
- Multi-unit optimization
- Vendor availability
- Pricing
- Memory generation
- Comparación comercial avanzada

## Decisions Confirmed With User
- Estrategia de sourcing: `local-only`
- Modo de selección: `auto-select-model`
- Criterio principal: `closest-airflow-above`
- Si no hay modelo suficiente: `fail`
- Campos mínimos de catálogo: `install-basic`
- Base de selección: `hybrid`
- Enfoque recomendado: `catalog + ficha assembler`
- Desempate: `lower-power`
- Alternativas: `top-3-valid`

## Architecture

### Roles

#### spec-dev-agent
Responsable de:
- definir contrato y estructura del catálogo local
- definir contrato de `spec.json`
- implementar selector técnico reusable
- definir reglas de elegibilidad y desempate
- definir validación mínima del catálogo

#### spec-agent
Responsable de:
- consumir `/proyectos/[id]/input.json`
- consumir `/proyectos/[id]/resultados.json`
- usar identidad de equipo desde input
- usar demanda requerida desde resultados
- seleccionar modelo local
- producir `/proyectos/[id]/spec.json`

### Selection Strategy
Base `hybrid`:
- identidad del equipo viene de `input.json`
- demanda de caudal viene de `resultados.json`

Flujo por equipo:
1. leer nodo de equipo en `input.json`
2. leer `required_m3_h_assigned` o demanda equivalente en `resultados.json`
3. filtrar catálogo local por compatibilidad
4. seleccionar mejor modelo según `closest-airflow-above`
5. desempatar con `lower-power`
6. si no hay modelo suficiente, marcar `failed`
7. generar ficha estructurada y alternativas

## Proposed `spec.json` Shape

```json
{
  "project": {
    "id": 1,
    "name": "AURORA GMR",
    "source_input": "/proyectos/1/input.json",
    "source_results": "/proyectos/1/resultados.json",
    "spec_status": "completed"
  },
  "summary": {
    "equipment_count": 1,
    "selected_models_count": 1,
    "failed_selections_count": 0
  },
  "equipment_specs": [
    {
      "equipment_id": "E1",
      "equipment_alias": "Extractor baño principal",
      "kind": "extractor",
      "required_m3_h": 129.6,
      "selection_status": "selected",
      "selection_policy": "closest-airflow-above",
      "selection_reason": "Selected smallest airflow above required demand; tie broken by lower power.",
      "selected_model": {
        "brand": "ORGM",
        "model": "EX-150",
        "airflow_m3_h": 140.0,
        "voltage": 120,
        "frequency_hz": 60,
        "power_w": 45,
        "power_kw": 0.045,
        "installation_type": "muro",
        "image_asset": "assets/extractores/ex-150.png"
      },
      "alternatives": [
        {
          "brand": "ORGM",
          "model": "EX-160",
          "airflow_m3_h": 160.0,
          "voltage": 120,
          "frequency_hz": 60,
          "power_w": 50,
          "power_kw": 0.05,
          "installation_type": "muro",
          "image_asset": "assets/extractores/ex-160.png"
        }
      ],
      "constraints_used": {
        "installation_type": "muro",
        "voltage": 120,
        "frequency_hz": 60
      },
      "notes": []
    }
  ],
  "catalog_trace": {
    "catalog_source": "local-catalog-v1",
    "catalog_version": "1",
    "local_only": true,
    "selection_mode": "auto-select-model"
  }
}
```

## Top-Level Rules

### `project`
Campos:
- `id`
- `name`
- `source_input`
- `source_results`
- `spec_status`

### `summary`
Campos mínimos:
- `equipment_count`
- `selected_models_count`
- `failed_selections_count`

### `equipment_specs`
Lista de fichas por equipo.
Una ficha por nodo de equipo en input.

### `catalog_trace`
Bloque global de metadata del catálogo y política aplicada.

## Local Catalog Contract
Cada modelo local debe incluir al menos:
- `brand`
- `model`
- `kind`
- `airflow_m3_h`
- `voltage`
- `frequency_hz`
- `power_w` o `power_kw`
- `installation_type`
- `image_asset` opcional

Esto corresponde a política mínima `install-basic`.

## Eligibility Rules
Para cada equipo:
1. filtrar por `kind`
2. si input/equipo trae `installation_type`, filtrar exacto
3. si input/equipo trae `voltage`, filtrar exacto
4. si input/equipo trae `frequency_hz`, filtrar exacto

Modelos que no cumplan filtros quedan fuera antes de aplicar selección por caudal.

## Selection Rules
### Primary Criterion
Política congelada: `closest-airflow-above`

Regla:
- considerar solo modelos con `airflow_m3_h >= required_m3_h`
- elegir modelo con menor exceso positivo de caudal sobre lo requerido

### Tie Break
Si dos o más modelos tienen mismo exceso:
- elegir menor `power_w` o equivalente menor `power_kw`

### Failure Rule
Si no existe ningún modelo elegible con `airflow_m3_h >= required_m3_h`:
- `selection_status = failed`
- no usar modelo por debajo del requerimiento
- no dividir en múltiples unidades
- no usar web fallback

### Alternatives Rule
Guardar `top-3-valid`:
- hasta 3 modelos válidos
- ordenados por criterio de selección principal y luego desempate
- pueden incluir modelo seleccionado o solo secundarios, pero la convención de v1 debe ser consistente; se recomienda excluir el seleccionado y listar solo alternativas restantes

## Selection Inputs
Base `hybrid`:
- `equipment_id`, `equipment_alias`, `kind` y restricciones preferidas desde `input.json`
- `required_m3_h` desde `resultados.json`

## Error Model
### `completed`
- `spec.json` generado correctamente

### `needs_input`
- no se usa por defecto en v1 para faltas de catálogo; selección local incompleta debe verse como fallo técnico del sistema o del catálogo

### `blocked`
- falta catálogo local o tooling base

### `failed`
- catálogo inválido
- modelo requerido no existe
- demanda requerida no tiene ningún candidato elegible
- input/resultados inconsistentes para selección

## Testing Strategy

### 1. Catalog Validation Tests
- modelo sin campo mínimo obligatorio falla validación

### 2. Eligibility Tests
- kind incompatible se excluye
- installation_type incompatible se excluye
- voltage incompatible se excluye
- frequency incompatible se excluye

### 3. Selection Tests
- se elige menor airflow por encima del requerido
- empate por exceso usa `lower-power`
- sin modelo suficiente → `failed`

### 4. Alternatives Tests
- devuelve `top-3-valid` en orden correcto

### 5. Integration Test
- consumir `/proyectos/1/input.json`
- consumir `/proyectos/1/resultados.json`
- producir `/proyectos/1/spec.json`

## AURORA GMR Bootstrap Expectation
Para fixture inicial del catálogo local:
- equipo `E1`
- kind `extractor`
- demanda `129.6 m3/h`
- selección debe elegir modelo local más cercano por encima del requerimiento
- si no hay modelo suficiente en fixture, resultado debe fallar explícitamente

## First Implementation Boundary
La primera implementación debe limitarse a:
- contrato de `spec.json`
- contrato del catálogo local
- selector local reusable
- validación de catálogo
- integración `input.json + resultados.json -> spec.json`
- fixture local inicial para prueba con `AURORA GMR`

No debe incluir todavía:
- web fallback
- scraping
- comparaciones comerciales avanzadas
- optimización multi-unidad
- memory generation

## Recommendation
Siguiente paso, tras aprobación de este diseño: crear plan de implementación solo para `spec-engine`, enfocado en `spec-dev-agent` + `spec-agent`, catálogo local inicial y `/proyectos/[id]/spec.json`.
