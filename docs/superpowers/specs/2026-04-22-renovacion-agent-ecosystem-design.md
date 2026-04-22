# Renovación Agent Ecosystem Design

## Goal
Diseñar primer subproyecto del sistema: ecosistema de agentes para `renovacion`, incluyendo orquestador principal, subagentes, equipos, contratos de handoff y reglas de ejecución. Este documento no cubre todavía la implementación de herramientas Python, cálculos, plantillas HTML/PDF ni generación de memorias finales.

## Scope
Incluye:
- Estructura de agentes en `.pi/agents/renovacion-agent/`
- Definición de equipos `calculador-team` y `developer-team`
- Reglas del orquestador principal
- Contratos de entrada/salida entre agentes
- Reglas de ejecución en paralelo, en cadena y persistente
- Convención de almacenamiento por proyecto en filesystem
- Defaults del proyecto de prueba `AURORA GMR`
- Estrategia de validación del ecosistema de agentes

No incluye todavía:
- Implementación Python de validación
- Implementación Python de cálculos
- Implementación de catálogo técnico o caché local
- Implementación de generador HTML/PDF
- Fórmulas de cálculo detalladas
- Templates finales de memoria

## Decisions Confirmed With User
- Primer subproyecto: `ecosistema-agentes`
- Enfoque de ruteo: `hybrid`
- Persistencia de estado: `filesystem-only`
- Ubicación de agentes: `all-in-folder`
- Flag `desarrollador=true`: default del prompt del orquestador
- Contacto con usuario: `yes-via-orchestrator`
- Enfoque recomendado: `typed contract`

## Architecture

### Main Orchestrator
Archivo principal:
- `.pi/agents/renovacion-agent/index.md`

Responsabilidades:
- Recibir requerimientos del usuario
- Detectar intención del requerimiento
- Elegir equipo y subagente responsable
- Elegir estrategia de ejecución: paralelo, cadena, persistente o efímera
- Empaquetar y reenviar contexto útil entre agentes
- Consolidar respuestas de subagentes
- Ser único canal de comunicación con usuario

Restricciones:
- No ejecuta código
- No modifica código de aplicación
- No realiza cálculos directamente
- No genera artefactos técnicos finales por sí mismo
- No permite contacto directo subagente ↔ usuario

### Operating Modes
El orquestador opera en modo híbrido.

#### Developer mode
`desarrollador=true` por defecto en esta etapa.

Comportamiento:
- Prioriza `developer-team`
- Se usa para crear herramientas, validadores, plantillas y utilidades que luego usarán los agentes calculadores
- Puede invocar agentes calculadores solo para validar integración o probar flujos

#### Production mode
`desarrollador=false`

Comportamiento:
- Prioriza `calculador-team`
- Se usa para ejecutar proyectos reales con artefactos existentes
- Sigue flujo de cálculo desde input validado hasta memoria final

## Agent Layout
Todos los agentes vivirán en una sola carpeta:

- `.pi/agents/renovacion-agent/index.md`
- `.pi/agents/renovacion-agent/input-validator-agent.md`
- `.pi/agents/renovacion-agent/calculator-agent.md`
- `.pi/agents/renovacion-agent/spec-agent.md`
- `.pi/agents/renovacion-agent/memory-generator-agent.md`
- `.pi/agents/renovacion-agent/validator-dev-agent.md`
- `.pi/agents/renovacion-agent/calculator-dev-agent.md`
- `.pi/agents/renovacion-agent/spec-dev-agent.md`
- `.pi/agents/renovacion-agent/memory-dev-generator-agent.md`
- `.pi/agents/teams.yaml`

## Teams

### calculador-team
Miembros:
- `input-validator-agent`
- `calculator-agent`
- `spec-agent`
- `memory-generator-agent`

Propósito:
- Ejecutar cálculos y producir artefactos de proyecto usando herramientas ya existentes

### developer-team
Miembros:
- `validator-dev-agent`
- `calculator-dev-agent`
- `spec-dev-agent`
- `memory-dev-generator-agent`

Propósito:
- Crear las herramientas, validadores, plantillas y estructuras que luego usarán los agentes del equipo calculador

## Filesystem Contract
Cada proyecto se organiza por id numérico:

- `/proyectos/[id]/input.json`
- `/proyectos/[id]/resultados.json`
- `/proyectos/[id]/spec.json`
- `/proyectos/[id]/memoria.html`
- `/proyectos/[id]/memoria.pdf` (opcional, no versionado)
- `/proyectos/[id]/assets/` (opcional)

Reglas:
- `input.json`, `resultados.json`, `spec.json`, `memoria.html` sí deben poder versionarse
- `memoria.pdf` debe excluirse del git
- El estado del sistema vive en filesystem; no se depende de memoria externa para verdad de proyecto
- Los nombres de archivo son deterministas
- En esta primera etapa no se define historial por versiones de artefactos; el estado actual reemplaza el previo

## Handoff Contract
Cada delegación del orquestador a un subagente debe incluir estructura uniforme.

### Required Request Fields
- `task_type`
- `mode`
- `project_context`
- `available_artifacts`
- `required_outputs`
- `constraints`

### task_type values
- `design-tools`
- `validate-input`
- `run-calculation`
- `build-spec`
- `generate-memory`
- `review-blocker`

### mode values
- `desarrollador`
- `produccion`

### project_context fields
- `project_id`
- `project_path`
- `project_name`
- `cliente`
- `ubicacion`
- `ingeniero`
- `codia`
- `empresa_calculo`
- `logo_empresa`
- `logo_cliente`

### constraints examples
- `no-user-contact`
- `filesystem-only`
- `use-persistent`
- `use-ephemeral`
- `parallel-safe`

## Standard Subagent Response Contract
Cada subagente debe responder con:
- `status`
- `summary`
- `artifacts_created`
- `artifacts_updated`
- `questions_for_user`
- `next_recommended_agent`
- `notes_for_orchestrator`

### status values
- `completed`
- `needs_input`
- `blocked`
- `failed`

### Status semantics
- `completed`: trabajo terminado con salidas listas
- `needs_input`: faltan datos del usuario o del proyecto
- `blocked`: depende de artefacto o herramienta upstream aún inexistente
- `failed`: ocurrió error de ejecución, contradicción o problema no recuperable automáticamente

Regla clave:
- Los subagentes pueden redactar preguntas, pero solo el orquestador habla con el usuario

## Agent Responsibilities

### input-validator-agent
Responsable de:
- Recibir datos iniciales del proyecto
- Detectar información faltante
- Normalizar datos a formato aceptado por el sistema
- Crear y actualizar `/proyectos/[id]/input.json`
- Organizar ids, áreas, alturas, alias de equipos, cantidades y requisitos mínimos necesarios para cálculo y especificaciones
- Preparar información útil para futuras fichas técnicas, incluyendo datos como tensión, frecuencia, tipo de instalación y límites de cantidad cuando estén disponibles

No hace:
- Cálculos matemáticos finales
- Selección técnica completa de equipos
- Generación de memoria

### calculator-agent
Responsable de:
- Consumir `input.json` validado
- Ejecutar herramientas Python mediante `uv`
- Generar `/proyectos/[id]/resultados.json`
- Registrar operaciones matemáticas y trazabilidad suficiente para verificar cada resultado

No hace:
- Preguntas directas al usuario
- Diseño de herramientas de cálculo
- Construcción de plantillas de memoria

### spec-agent
Responsable de:
- Consumir `input.json` y `resultados.json`
- Seleccionar o proponer fichas técnicas de equipos
- Generar `/proyectos/[id]/spec.json`
- Adjuntar referencias a assets relevantes
- Preferir fuentes locales o catálogos mantenidos por el sistema; usar búsqueda externa solo si herramienta/política lo permite y si la base local no basta

No hace:
- Implementación de cachés o catálogos base
- Generación de memoria final

### memory-generator-agent
Responsable de:
- Consumir `input.json`, `resultados.json`, `spec.json` y assets asociados
- Generar `/proyectos/[id]/memoria.html`
- Generar opcionalmente `/proyectos/[id]/memoria.pdf`
- Usar las herramientas, templates, CSS y reglas de formato creadas por `memory-dev-generator-agent`

No hace:
- Diseño base del sistema de templates
- Cálculo de resultados

### validator-dev-agent
Responsable de:
- Diseñar y construir funciones, esquemas y reglas que permitan validar estructura y tipos de datos del proyecto
- Asegurar compatibilidad entre input almacenado y calculadoras futuras
- Ayudar a separar correctamente proyectos distintos por id y estructura

### calculator-dev-agent
Responsable de:
- Diseñar y construir herramientas Python de cálculo que usará `calculator-agent`
- Definir interfaces de entrada/salida esperadas
- Mantener reglas y trazabilidad de operaciones

### spec-dev-agent
Responsable de:
- Diseñar y construir herramientas locales para selección técnica de equipos
- Crear bases, catálogos, validaciones o caches de mercado cuando sea posible
- Reducir dependencia de búsqueda externa

### memory-dev-generator-agent
Responsable de:
- Diseñar y construir sistema generador de memorias
- Crear templates por sección
- Crear CSS general y CSS específico por sección
- Definir formato con Arial y KaTeX para fórmulas
- Preparar estructura de documento dividida en portada, índice, teoría de cálculo, resultados, selección de equipos y cierre

## Workflow Rules

### Real Project Flow
Cuando `desarrollador=false`, el flujo por defecto será:
1. El orquestador inspecciona requerimiento y artefactos disponibles
2. Si falta o está incompleto `input.json`, delega a `input-validator-agent`
3. Con `input.json` válido, delega a `calculator-agent`
4. Luego delega a `spec-agent`
5. Con `resultados.json` y `spec.json` listos, delega a `memory-generator-agent`
6. El orquestador devuelve resumen final y rutas de artefactos

Regla de optimización:
- `calculator-agent` y `spec-agent` podrán ejecutarse en paralelo solo cuando sus dependencias reales lo permitan
- Si `spec-agent` depende de resultados calculados, deben ejecutarse en cadena

### Developer Flow
Cuando `desarrollador=true`, el flujo por defecto será:
1. El orquestador detecta capacidad/herramienta a construir o mejorar
2. Selecciona agente del `developer-team` responsable
3. Mantiene sesión persistente si habrá iteraciones esperables
4. Cuando una herramienta queda lista, puede invocar agente del `calculador-team` para prueba de integración
5. El orquestador resume estado de avance y próximos pasos

## Execution Strategy

### Parallel
Usar cuando subproblemas sean independientes.
Ejemplos:
- diseño de reglas de validación y esqueletos de templates
- trabajo en distintos componentes que no comparten dependencia inmediata

### Chain
Usar cuando una salida sea prerequisito de la siguiente.
Ejemplos:
- `input.json` → `resultados.json` → `memoria.html`
- herramientas dev antes de pruebas calculadoras

### Persistent
Usar cuando el mismo especialista necesite continuidad de contexto entre iteraciones.
Ejemplos:
- afinación de templates
- evolución de validadores
- maduración de herramienta de cálculo

### Ephemeral
Usar para tareas aisladas de una sola vuelta.
Ejemplos:
- revisión puntual
- respuesta única sin seguimiento esperado

## Error and Escalation Model
Ningún subagente debe fallar en silencio.

### needs_input
Se usa cuando faltan datos de usuario o proyecto.
Acción esperada:
- el subagente lista qué falta
- el orquestador formula pregunta al usuario
- luego reintenta con el mismo agente

### blocked
Se usa cuando falta herramienta, artefacto upstream o dependencia de otro agente.
Acción esperada:
- el subagente indica qué lo bloquea
- el orquestador deriva al agente upstream correcto

### failed
Se usa cuando hay error de ejecución, contradicción lógica o salida insegura.
Acción esperada:
- el subagente devuelve causa exacta, acción intentada y recomendación de retry seguro

### completed
Se usa cuando el artefacto o entregable solicitado ya está listo

## Bootstrap Defaults
Para primeras pruebas se definen estos valores por defecto:
- Proyecto: `AURORA GMR`
- Ubicación: `Distrito Nacional`
- Ingeniero: `Osmar Garcia`
- CODIA: `36467`
- Empresa de cálculo: `ORGM`
- Logo empresa: `https://r2.or-gm.com/orgm.png`
- Cliente de prueba: `BOHC SRL`
- Logo cliente: `https://r2.or-gm.com/bohc.png`

Estos valores se aplican solo como defaults. El sistema debe permitir override explícito o desactivación de empresa de cálculo cuando el usuario lo indique.

## Testing Strategy For This Subproject
Esta primera etapa valida diseño del ecosistema, no corrección matemática.

### 1. Routing tests
Verificar que ejemplos de requerimientos se enruten al agente correcto según modo:
- developer mode → agente dev correspondiente
- production mode → flujo calculador correspondiente

### 2. Prompt contract tests
Cada prompt de agente debe declarar claramente:
- entradas aceptadas
- salidas requeridas
- vocabulario de `status`
- prohibición de contacto directo con usuario

### 3. Filesystem contract tests
Verificar consistencia documental de:
- `/proyectos/[id]/...`
- nombres de artefactos
- exclusión de PDFs del git

### 4. Bootstrap scenario test
Escenarios mínimos a soportar luego de implementar prompts:
- “crear herramientas para AURORA GMR” → rutea dev-first
- “calcular proyecto AURORA GMR” → rutea flujo calculador

## First Implementation Boundary
La primera implementación posterior a este diseño debe limitarse a:
- prompts del orquestador y subagentes
- `teams.yaml`
- contratos documentados dentro de prompts
- ajustes de repo necesarios para soportar estructura y salidas esperadas

No debe incluir todavía:
- lógica Python final
- motor de cálculo final
- motor de generación de memoria final
- catálogo técnico final

## Open Items Deferred To Later Specs
Estos temas quedan explícitamente fuera de este diseño y se abordarán en specs posteriores:
- detalle completo de `input.json`
- detalle completo de `resultados.json`
- detalle completo de `spec.json`
- modelo de assets en `spec.json`
- fórmulas de cálculo por tipo de local
- integración exacta con `rules/renovacion.json`
- estructura de plantillas HTML/CSS por sección
- reglas de exportación PDF

## Recommendation
Seguir con siguiente paso de planificación para implementar solo ecosistema de agentes y contratos. Después abrir specs separadas para:
1. input pipeline
2. calc engine
3. templates y memorias
