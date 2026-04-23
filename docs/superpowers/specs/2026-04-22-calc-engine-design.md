# Calc Engine Design

## Goal
Diseñar el tercer subproyecto de `renovacion`: el motor de cálculo que consumirá `/proyectos/[id]/input.json`, aplicará reglas de renovación de aire desde `rules/renovacion.json`, y producirá `/proyectos/[id]/resultados.json` con trazabilidad completa.

## Scope
Incluye:
- Contrato de `resultados.json`
- Reglas de cálculo por renovaciones/hora
- Reglas de cálculo por personas
- Política de selección `max-of-both`
- Política de midpoint para rangos
- Política `aprox -> min=max=aprox`
- Trazas humanas y estructuradas
- Resultados por área, por equipo y resumen de proyecto
- Criterios de prueba para `AURORA GMR`

No incluye todavía:
- Selección de mercado y `spec.json`
- Dimensionamiento automático de equipos desde catálogo
- Generación de memoria HTML/PDF
- Optimización avanzada de cantidades de equipos
- Soporte para múltiples normas adicionales

## Decisions Confirmed With User
- Prioridad cuando hay personas: `max-of-both`
- Política RH por rango: `midpoint`
- Granularidad de salida: `both`
- Sizing de equipos en v1: `calc-only`
- Trazas: `both`
- Redondeo almacenado: `round-2-decimals`
- `aprox`: `range-same`
- Método personas sin datos: `yes-null`
- Enfoque recomendado: `full calc summary engine`
- Política de rango para caudal por persona: `same-as-rh-policy`

## Architecture

### Roles

#### calculator-dev-agent
Responsable de:
- construir tooling reusable del motor de cálculo
- definir contrato de `resultados.json`
- implementar fórmulas y trazabilidad
- implementar políticas de rango y selección de método gobernante
- crear pruebas del motor

#### calculator-agent
Responsable de:
- consumir `/proyectos/[id]/input.json`
- ejecutar tooling del motor de cálculo
- producir `/proyectos/[id]/resultados.json`
- devolver estado y handoff al siguiente agente

### Engine Strategy
Se usará un motor de cálculo orientado a resumen completo.

Esto significa:
- calcula resultados por área
- genera placeholders/resultados agregados por equipo
- genera resumen de proyecto
- no selecciona equipos comerciales todavía

### Governing Logic Per Area
Para cada área:
1. calcular método RH
2. calcular método personas si aplica
3. elegir resultado final con `max-of-both`
4. guardar trazas humanas y estructuradas de cada método
5. guardar método gobernante y resultado final

## Proposed `resultados.json` Shape

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
            "inputs": {
              "people": null
            },
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

## Top-Level Rules

### `project`
Campos:
- `id`
- `name`
- `source_input`
- `calculation_status`

### `summary`
Campos mínimos:
- `total_required_m3_h`
- `areas_count`
- `equipment_count`
- `areas_with_people`
- `areas_without_people`
- `governing_method_counts`

### `area_results`
Lista de resultados por área.

### `equipment_results`
Lista de resultados agregados por equipo.
En v1 no hace sizing comercial, solo arrastra o agrega demanda asociada.

### `calculation_trace`
Bloque de metapolíticas del cálculo para auditoría global.

## Formula Rules

## RH Method
Para cada área:
1. leer `volume_m3`
2. resolver regla RH desde `rules/renovacion.json`
3. si existe `min/max`, usar `midpoint`
4. si existe `aprox`, tratar como `min=max=aprox`
5. calcular:
   - `required_m3_h_rh = volume_m3 * rh_target`
6. redondear resultado almacenado a 2 decimales

### RH Range Policy
- si `min/max`: `rh_target = (min + max) / 2`
- si `aprox`: `rh_min = rh_max = aprox`, `rh_target = aprox`

## People Method
Si `people` existe y el tipo de local tiene fila compatible en `tabla_caudal_por_persona`:
1. resolver `caudal_por_persona`
2. si es valor único, usarlo directo
3. si es rango, usar misma política que RH: `midpoint`
4. calcular:
   - `required_m3_h_people = people * caudal_persona_target`
5. redondear resultado almacenado a 2 decimales

Si `people` no existe:
- método se guarda con `applicable = false`
- `result_m3_h = null`
- traza marcada como no aplicable

## Governing Method
Política congelada: `max-of-both`

Reglas:
- si RH y personas aplican: usar mayor valor
- si solo RH aplica: usar RH
- si ambos dan mismo valor: marcar `tie`
- siempre guardar ambos bloques de método, aunque personas sea `not_applicable`

## Trace Policy
Se guardan dos tipos de trazas.

### Human Trace
Cadena legible para memoria y revisión manual.

Ejemplo RH:
- `Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h`

Ejemplo personas:
- `Q_people = P * q = 4 * 75.00 = 300.00 m3/h`

Ejemplo no aplicable:
- `Not applicable: people is null`

### Structured Trace
Objeto máquina-legible con:
- `formula`
- `inputs`
- `operation`
- `output`
- `unit`

## Rounding Policy
Política congelada: `round-2-decimals`

Reglas:
- resultados almacenados se redondean a 2 decimales
- valores derivados mostrados en traza deben ser consistentes con la salida almacenada
- no existe capa separada de display rounding en v1

## Equipment Results Policy
V1 usa `calc-only`.

Esto significa:
- no selecciona equipo comercial
- no calcula cantidad óptima desde catálogo
- no resuelve marca/modelo
- sí puede asignar demanda agregada a cada equipo existente en `input.json`
- `sizing_status = not_sized_v1`

## Area to Equipment Aggregation
Para cada equipo:
- sumar `required_m3_h_final` de áreas servidas, o mapear demanda según vínculo definido
- guardar en `required_m3_h_assigned`

En v1, se asume asignación directa sin optimización avanzada.

## Error Model
### `completed`
- `resultados.json` creado/actualizado correctamente

### `needs_input`
- faltan datos de usuario que impiden cálculo
- ejemplo: inconsistencia de método personas por tipo sin mapping y usuario debe aclarar

### `blocked`
- falta tooling del motor
- falta `input.json`
- `input.json` no está `calc_ready`

### `failed`
- contradicción o error de cálculo
- tipo de local no resoluble para RH
- entradas inválidas no recuperables

## Testing Strategy

### 1. RH Method Tests
- rango `min/max` usa midpoint
- `aprox` se trata como `min=max=aprox`

### 2. People Method Tests
- fila con valor único
- fila con rango usa midpoint por `same-as-rh-policy`
- sin `people` deja método `not_applicable`

### 3. Governing Method Tests
- RH gana
- personas gana
- empate marca `tie`

### 4. Trace Tests
- existe traza humana
- existe traza estructurada
- resultados almacenados quedan con 2 decimales

### 5. Integration Test
- consumir `proyectos/1/input.json`
- producir `/proyectos/1/resultados.json`
- verificar resumen, bloques por área y equipo, y trazas

## AURORA GMR Bootstrap Expectation
Con fixture actual:
- área `A1`
- tipo `Cuartos de baño`
- volumen `21.6 m3`
- RH `5–7` → midpoint `6.0`
- resultado RH esperado: `129.60 m3/h`
- sin personas → método personas `not_applicable`
- método gobernante: `rh`
- total proyecto esperado: `129.60 m3/h`

## First Implementation Boundary
La primera implementación de este subproyecto debe limitarse a:
- contrato de `resultados.json`
- tooling reusable del motor de cálculo
- RH lookup
- people lookup
- midpoint policy
- `aprox -> range-same`
- `max-of-both`
- trazas humanas y estructuradas
- integración con `proyectos/1/input.json`

No debe incluir todavía:
- `spec.json`
- selección técnica de mercado
- generador de memoria
- optimización avanzada de equipos

## Recommendation
Siguiente paso, tras aprobación de este diseño: crear plan de implementación solo para `calc-engine`, enfocado en `calculator-dev-agent` + `calculator-agent` y contrato inicial de `/proyectos/[id]/resultados.json`.
