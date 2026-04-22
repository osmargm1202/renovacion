# Input Pipeline Design

## Goal
Diseñar el segundo subproyecto de `renovacion`: el pipeline de entrada que permitirá crear, validar, normalizar y almacenar `/proyectos/[id]/input.json` como base para los cálculos posteriores.

## Scope
Incluye:
- Contrato unificado de `input.json`
- Reglas de validación crítica vs no crítica
- Reglas de normalización de dimensiones
- Regla de ids secuenciales por proyecto
- Reglas de selección de tipo de local desde `rules/renovacion.json`
- Modelo híbrido de áreas y equipos
- Estrategia de drafts vs estado `calc_ready`
- Criterios de prueba iniciales para `AURORA GMR`

No incluye todavía:
- Implementación Python de validadores
- Cálculos y `resultados.json`
- Selección técnica de equipos y `spec.json`
- Generación de memoria HTML/PDF

## Decisions Confirmed With User
- Siguiente subproyecto: `input-pipeline`
- Modelo de espacios: `hybrid`
- Cantidad de equipos: `fixed-only`
- Id de proyecto: `sequential-int`
- Manejo de faltantes: `mixed`
- Campos críticos antes de cálculo: `project-core-only`
- Dimensiones por área: `flexible`
- Tipo de local: `catalog+alias`
- Enfoque recomendado: `unified project contract`

## Architecture

### Roles

#### validator-dev-agent
Responsable de:
- definir schema del `input.json`
- definir reglas críticas y no críticas
- definir validaciones de estructura y tipos
- definir reglas de normalización
- definir reglas de id secuencial y consistencia multi-proyecto

#### input-validator-agent
Responsable de:
- recibir datos iniciales del usuario
- aplicar defaults del proyecto cuando correspondan
- asignar o reusar `/proyectos/[id]/`
- crear o actualizar `/proyectos/[id]/input.json`
- pedir faltantes mínimos a través del orquestador
- dejar el archivo en estado `draft` o `calc_ready`

### Unified Input Contract
Se usará un solo archivo `/proyectos/[id]/input.json`.

Este archivo debe contener:
- metadata del proyecto
- datos normalizados de áreas
- lista de equipos
- vínculos explícitos área↔equipo
- placeholders para información futura de especificación
- resumen de validación y faltantes

No se creará `input.raw.json` en esta primera versión.

## Proposed `input.json` Shape

```json
{
  "project": {
    "id": 1,
    "name": "AURORA GMR",
    "cliente": "BOHC SRL",
    "ubicacion": "Distrito Nacional",
    "ingeniero": "Osmar Garcia",
    "codia": "36467",
    "empresa_calculo": "ORGM",
    "logo_empresa": "https://r2.or-gm.com/orgm.png",
    "logo_cliente": "https://r2.or-gm.com/bohc.png",
    "status": "draft"
  },
  "validation": {
    "critical_complete": false,
    "missing_critical": [],
    "missing_non_critical": [],
    "notes": []
  },
  "areas": [
    {
      "id": "A1",
      "alias": "Baño principal",
      "catalog_type": "Cuartos de baño",
      "catalog_sector": "residencial_domestico",
      "dimensions": {
        "area_m2": 8,
        "height_m": 2.7,
        "volume_m3": 21.6
      },
      "people": null,
      "equipment_ids": ["E1"],
      "notes": []
    }
  ],
  "equipment": [
    {
      "id": "E1",
      "alias": "Extractor baño principal",
      "kind": "extractor",
      "cantidad": 1,
      "serves_area_ids": ["A1"],
      "voltage": null,
      "frequency_hz": null,
      "installation_type": null,
      "power_w": null,
      "power_kw": null,
      "airflow_cfm": null,
      "airflow_m3_h": null,
      "notes": []
    }
  ],
  "defaults_applied": [
    "ingeniero",
    "codia",
    "empresa_calculo",
    "logo_empresa",
    "cliente",
    "logo_cliente",
    "ubicacion"
  ]
}
```

## Field Rules

### project
Campos:
- `id`: entero secuencial local
- `name`: nombre del proyecto
- `cliente`
- `ubicacion`
- `ingeniero`
- `codia`
- `empresa_calculo`
- `logo_empresa`
- `logo_cliente`
- `status`: `draft` o `calc_ready`

### validation
Campos:
- `critical_complete`: booleano
- `missing_critical`: lista de rutas/campos faltantes críticos
- `missing_non_critical`: lista de rutas/campos faltantes no críticos
- `notes`: observaciones de validación

### areas
Cada área debe incluir:
- `id`
- `alias`
- `catalog_type`
- `catalog_sector`
- `dimensions`
- `people` opcional
- `equipment_ids`
- `notes`

### equipment
Cada equipo debe incluir:
- `id`
- `alias`
- `kind`
- `cantidad`
- `serves_area_ids`
- placeholders de especificación técnica
- `notes`

### defaults_applied
Lista de defaults aplicados automáticamente para trazabilidad.

## Hybrid Area/Equipment Model
El modelo será híbrido.

Esto significa:
- existe una lista de `areas`
- existe una lista de `equipment`
- la relación entre ambas se guarda explícitamente mediante:
  - `areas[].equipment_ids`
  - `equipment[].serves_area_ids`

Regla:
- ambas referencias deben ser consistentes entre sí

Razón:
- facilita cálculos por área
- facilita fichas por equipo
- reduce joins ambiguos para memorias futuras

## Catalog Rules
`catalog_type` no puede ser libre.

Debe:
- provenir de un valor controlado compatible con `rules/renovacion.json`
- poder acompañarse de `alias` humano para presentación

Ejemplo:
- `catalog_type = "Cuartos de baño"`
- `alias = "Baño principal"`

Reglas:
- `catalog_type` debe resolverse a un sector válido, guardado en `catalog_sector`
- si el usuario da texto libre, `input-validator-agent` debe normalizarlo o pedir aclaración
- no se permite estado final con `catalog_type` no resuelto

## Dimensions Rules
El modelo de dimensiones será `flexible`.

Se aceptan dos formas válidas:
1. `area_m2 + height_m`
2. `length_m + width_m + height_m`

Normalización:
- si se recibe `length_m + width_m + height_m`, se deriva `area_m2` y `volume_m3`
- si se recibe `area_m2 + height_m`, se deriva `volume_m3`
- se preservan los campos originales cuando sea posible

Reglas:
- no se aceptan dimensiones negativas o cero si invalidan cálculo
- toda área crítica debe tener suficiente información para derivar volumen

## Critical vs Non-Critical Data
El usuario definió que lo crítico inicial es `project-core-only`.

### Critical fields before calc-ready
Se requiere:
- `project.id`
- `project.name`
- `project.ubicacion`
- al menos una entrada en `areas`
- por cada área:
  - `id`
  - `alias`
  - `catalog_type`
  - dimensiones suficientes para derivar volumen

### Non-critical fields in first version
Pueden faltar sin bloquear `calc_ready`:
- `people`
- lista de equipos completa
- `cantidad` de equipos cuando aún no existan equipos definidos
- placeholders eléctricos o de instalación
- branding adicional si no se sobreescriben defaults
- notas

## Draft vs Calc-Ready Behavior
### Draft
Se permite guardar `input.json` en estado `draft` cuando falten campos críticos o no críticos.

Reglas:
- si faltan críticos:
  - `project.status = "draft"`
  - `validation.critical_complete = false`
  - se llenan `missing_critical`
  - el agente debe pedir el mínimo siguiente dato necesario

### Calc Ready
Se permite estado `calc_ready` cuando se cumplan todos los campos críticos.

Reglas:
- `project.status = "calc_ready"`
- `validation.critical_complete = true`
- `missing_non_critical` puede seguir teniendo elementos
- downstream puede iniciar cálculo

## Sequential Project Id Rule
El directorio base será `/proyectos/`.

Regla de creación:
- nuevo proyecto usa siguiente entero local disponible: `1`, `2`, `3`, ...

Regla de reuso:
- si el usuario se refiere a proyecto ya existente, debe reusarse su id
- en primera versión, identificación de proyecto existente se hará por:
  - referencia explícita del usuario
  - o coincidencia exacta de nombre confirmada por orquestador

## Error Model
### needs_input
Usar cuando faltan datos del usuario o del proyecto.

### blocked
Usar cuando falte schema, tooling o dependencia upstream.

### failed
Usar cuando existan contradicciones o errores duros, por ejemplo:
- ids duplicados
- referencias cruzadas inconsistentes
- `catalog_type` no resoluble
- dimensiones inválidas

### completed
Usar cuando `input.json` fue creado o actualizado de forma válida.

## Defaults For Bootstrap Project
Para `AURORA GMR`, salvo override:
- `name`: `AURORA GMR`
- `ubicacion`: `Distrito Nacional`
- `ingeniero`: `Osmar Garcia`
- `codia`: `36467`
- `empresa_calculo`: `ORGM`
- `logo_empresa`: `https://r2.or-gm.com/orgm.png`
- `cliente`: `BOHC SRL`
- `logo_cliente`: `https://r2.or-gm.com/bohc.png`

## Testing Strategy

### 1. Schema tests
- caso válido con `area_m2 + height_m`
- caso válido con `length_m + width_m + height_m`
- caso inválido con campos críticos faltantes
- caso inválido con `catalog_type` desconocido

### 2. Normalization tests
- derivar `area_m2`
- derivar `volume_m3`
- preservar `alias` y `catalog_type`

### 3. Project id tests
- sin proyectos previos → id `1`
- con `1, 2, 3` → siguiente `4`

### 4. Draft/calc_ready tests
- críticos faltantes → `draft`
- críticos completos → `calc_ready`

### 5. Bootstrap test
- `AURORA GMR` usa defaults
- crea `/proyectos/[id]/input.json`
- contiene al menos una área válida

## First Implementation Boundary
La primera implementación de este subproyecto debe limitarse a:
- definición del schema/contrato de `input.json`
- reglas de validación crítica/no crítica
- reglas de normalización
- reglas de ids secuenciales
- matching de catálogo con `rules/renovacion.json`
- fixture o ejemplo inicial de `AURORA GMR`

No debe incluir todavía:
- engine de cálculo
- `resultados.json`
- selección técnica de mercado
- `spec.json`
- generador HTML/PDF

## Recommendation
Siguiente paso, tras aprobación de este diseño: crear plan de implementación solo para `input-pipeline`, enfocado en `validator-dev-agent` + `input-validator-agent` y contrato inicial de `/proyectos/[id]/input.json`.
