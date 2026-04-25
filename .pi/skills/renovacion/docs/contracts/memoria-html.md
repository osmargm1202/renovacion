# Contract: memoria.html

## Purpose
Memoria HTML final de cálculo + selección de equipos.

## Location
`.pi/skills/renovacion/proyectos/[id]/memoria.html`

## Inputs required
- `input.json`
- `resultados.json`
- `spec.json`
- `assets/` del proyecto

## Required sections
1. `portada`
2. `indice`
3. `teoria-calculo`
4. `resultados-calculo`
5. `seleccion-equipos`
6. `fin`

## Selección de equipos
Contenido requerido por equipo:
- alias de equipo
- caudal requerido
- tipo funcional (`kind`)
- **tipo de extractor visible**
- modelo seleccionado (marca + modelo)
- datos eléctricos
- instalación
- imagen local o placeholder
- alternativas
- bloque explícito si selección falla

### Visible extractor type rule
Renderer debe mostrar `extractor_type || selected_model.extractor_type || 'N/A'`.

Salida visible esperada:
- subtítulo del equipo incluye `Tipo de extractor: ...`
- tabla/bloque de especificaciones incluye fila `Tipo de extractor`

## Asset policy
- usar assets locales del proyecto
- sin CDN ni URLs externas en HTML final
- fórmulas usan KaTeX vendorizado local

## Expected output for AURORA GMR project 1
### Resultados
- área A1: Baño principal
- RH: `129.6 m³/h`

### Selección
- equipo E1: Extractor baño principal
- tipo de extractor: `sencillo`
- seleccionado: `Delta Breez` / `80F / GreenBuilder`
- imagen: `assets/equipos/sencillo.png`
- alternativas visibles
