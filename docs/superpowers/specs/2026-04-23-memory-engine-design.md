# Memory Engine Design

## Goal
Diseñar el quinto subproyecto de `renovacion`: el motor de generación de memoria que consumirá `/proyectos/[id]/input.json`, `/proyectos/[id]/resultados.json`, `/proyectos/[id]/spec.json` y assets asociados para producir `/proyectos/[id]/memoria.html`.

## Scope
Incluye:
- Contrato de `memoria.html`
- Motor de render por secciones
- Plantillas por sección
- CSS compartido y CSS por sección
- Integración KaTeX/LaTeX para fórmulas en HTML
- Reglas de staging de assets
- Política de branding y portada
- Índice HTML con anchors y estilo imprimible
- Criterios de prueba para `AURORA GMR`

No incluye todavía:
- Generación final de PDF
- Paginación avanzada
- Page numbers reales de PDF
- Crawling remoto de imágenes de equipos
- Temas alternos
- Editor visual de templates

## Decisions Confirmed With User
- Prioridad de output: `html-first`
- Alcance del documento: `full-doc`
- Política de fórmulas: `hybrid`
- Fórmulas en HTML con KaTeX/LaTeX
- Assets: `project+catalog-assets`
- Logos de portada por URL deben descargarse a `/proyectos/[id]/assets/`
- Portada: `full-branding`
- Índice: `both`
- Teoría de cálculo: `hybrid`
- Asset faltante: `continue-placeholder`
- Mostrar alternativas: `always`
- Enfoque recomendado: `sectioned document engine`

## Architecture

### Roles

#### memory-dev-generator-agent
Responsable de:
- definir contrato de `memoria.html`
- construir render engine por secciones
- construir templates por sección
- construir CSS compartido y CSS por sección
- construir lógica de staging/download de assets
- integrar KaTeX en HTML

#### memory-generator-agent
Responsable de:
- consumir `/proyectos/[id]/input.json`
- consumir `/proyectos/[id]/resultados.json`
- consumir `/proyectos/[id]/spec.json`
- resolver y stagear assets requeridos a `/proyectos/[id]/assets/`
- renderizar `/proyectos/[id]/memoria.html`

### Rendering Strategy
Motor orientado a documento completo por secciones.

Secciones congeladas:
1. portada
2. índice
3. teoría de cálculo
4. resultados de cálculo
5. selección de equipos
6. fin

## Proposed `memoria.html` Contract

## Output Artifact
- `/proyectos/[id]/memoria.html`

## Supporting Assets
- `/proyectos/[id]/assets/`
  - logos de portada
  - imágenes de equipos staged localmente
  - placeholders si hacen falta
  - assets auxiliares si el motor los requiere

## Section IDs
El documento HTML debe contener ids estables:
- `portada`
- `indice`
- `teoria-calculo`
- `resultados-calculo`
- `seleccion-equipos`
- `fin`

## Required Content By Section

### 1. Portada
Debe incluir:
- logo empresa
- logo cliente
- nombre del proyecto
- ubicación
- ingeniero
- CODIA
- fecha
- empresa de cálculo si aplica

### 2. Índice
Debe incluir:
- links a anchors internos de todas las secciones
- layout legible en HTML
- estructura que luego pueda servir para PDF

### 3. Teoría de cálculo
Debe incluir:
- explicación base de renovación de aire
- explicación de método RH
- explicación de método por personas
- inserts dinámicos según métodos realmente usados en proyecto
- referencia a políticas aplicadas: midpoint, max-of-both, round-2-decimals

### 4. Resultados de cálculo
Debe incluir:
- resumen global del proyecto
- breakdown por área
- método gobernante por área
- fórmulas/trazas renderizadas
- bloques RH y personas aunque personas no aplique

### 5. Selección de equipos
Debe incluir:
- ficha por equipo
- modelo seleccionado
- caudal requerido
- caudal del modelo
- datos eléctricos
- tipo de instalación
- imagen del equipo o placeholder
- alternativas siempre visibles
- bloque explícito si la selección falló

### 6. Fin
Debe incluir:
- cierre del documento
- nota final o pie técnico
- layout de cierre consistente

## HTML/CSS Rules
Debe existir:
- CSS compartido global
- CSS específico por sección
- tipografía base Arial
- estilos KaTeX para fórmulas

## Formula Rendering Rules
Política: `hybrid`

Orden:
1. si existe trace estructurado usable, convertir a fórmula KaTeX/LaTeX
2. si no, renderizar trace humana como fallback legible

Reglas:
- RH y personas deben poder representarse en HTML
- personas no aplicable debe mostrarse como estado explícito, no omitirse

## Asset Staging Rules
Antes de renderizar:
1. asegurar `/proyectos/[id]/assets/`
2. resolver logos de portada
3. si logo viene por URL, descargar a assets del proyecto
4. resolver imágenes de equipos
5. preferir asset ya local del proyecto
6. si no existe, usar referencia local de catálogo/spec
7. si asset no aparece, usar placeholder
8. HTML final debe apuntar a assets locales del proyecto

## Asset Failure Policy
Política congelada: `continue-placeholder`

Significa:
- imagen faltante no rompe render
- se sustituye por placeholder visual
- el documento sigue generándose

## Alternatives Rendering Policy
Política congelada: `always`

Significa:
- la sección de equipos siempre muestra alternativas si existen
- no solo cuando la selección falla

## Theory Rendering Rules
Política: `hybrid`

Composición:
- base estática explicativa
- inserts dinámicos desde reglas/métodos aplicados al proyecto
- mención de tipos de local, RH objetivo, y método gobernante cuando aporte contexto

## Error Model
### `completed`
- `memoria.html` generado correctamente

### `needs_input`
- solo si faltara metadata indispensable de portada no resoluble desde defaults/artefactos

### `blocked`
- faltan artefactos upstream (`input.json`, `resultados.json`, `spec.json`)
- falta tooling/render engine

### `failed`
- error duro de render
- contrato incompatible entre artefactos
- fallo crítico de asset staging no recuperable

## Testing Strategy

### 1. Template Tests
- existen todos los section ids
- índice apunta a anchors válidos

### 2. Asset Tests
- logo remoto se descarga a assets del proyecto
- imagen faltante renderiza placeholder sin abortar

### 3. Formula Tests
- structured trace produce bloque KaTeX válido
- fallback a trace humana se renderiza correctamente

### 4. Content Tests
- resultados incluyen resumen y breakdown por área
- selección equipos incluye modelo + alternativas

### 5. Integration Test
- consumir `proyectos/1/input.json`
- consumir `proyectos/1/resultados.json`
- consumir `proyectos/1/spec.json`
- producir `/proyectos/1/memoria.html`

## AURORA GMR Bootstrap Expectation
Con artifacts actuales, memoria v1 debe:
- generar portada con branding completo
- mostrar área A1 con cálculo RH `129.6 m3/h`
- mostrar equipo E1 con modelo `EX-150`
- mostrar alternativas `EX-160`, `EX-200`, `EX-250`
- renderizar HTML final con assets locales del proyecto

## First Implementation Boundary
La primera implementación de este subproyecto debe limitarse a:
- contrato de `memoria.html`
- render engine HTML por secciones
- templates por sección
- CSS global + CSS por sección
- staging de assets
- integración KaTeX
- integración con proyecto 1

No debe incluir todavía:
- renderer PDF final
- numeración real de páginas
- refinamientos avanzados de impresión
- temas alternativos
- edición visual de plantillas

## Recommendation
Siguiente paso, tras aprobación de este diseño: crear plan de implementación solo para `memory-engine`, enfocado en `memory-dev-generator-agent` + `memory-generator-agent` y generación de `/proyectos/[id]/memoria.html`.
