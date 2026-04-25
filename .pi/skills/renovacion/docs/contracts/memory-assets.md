# Contract: Memory Assets

## Purpose
Política de staging y referencias de assets para `memoria.html`.

## Project assets directory
`.pi/skills/renovacion/proyectos/[id]/assets/`

Subdirectorios:
- `logos/`
- `equipos/`
- `placeholders/`

## Catalog asset sources
Referencias de catálogo solo lectura:
- `assets/extractores/sencillo.png`
- `assets/extractores/ducteable.png`
- `assets/placeholders/*`

## Equipment image policy
Fuentes desde `spec.json`:
- `equipment_specs[].selected_model.image_asset`
- `equipment_specs[].alternatives[].image_asset`

Reglas:
1. revisar `proyectos/[id]/assets/equipos/[filename]`
2. si no existe, copiar desde referencia de catálogo local
3. si falla, usar placeholder
4. HTML final referencia solo rutas locales del proyecto

## Category image policy
Para extractores comerciales, runtime usa solo dos imágenes locales por categoría:
- `assets/extractores/sencillo.png`
- `assets/extractores/ducteable.png`

Efecto esperado en proyecto generado:
- selección/simple → `proyectos/[id]/assets/equipos/sencillo.png`
- selección/ductable → `proyectos/[id]/assets/equipos/ducteable.png`

No usar:
- imágenes remotas en runtime
- una imagen distinta por modelo comercial

## Asset policies
- `project+catalog-assets`: preferir asset local del proyecto; fallback a asset local de catálogo; copiar a proyecto
- `continue-placeholder`: si falta asset, no abortar render
- `always-local`: HTML final sin URLs externas

## HTML references
Ejemplo selección simple:
```html
<img src="assets/equipos/sencillo.png" alt="80F / GreenBuilder" class="equipment-image">
```

Ejemplo selección ductable:
```html
<img src="assets/equipos/ducteable.png" alt="TD-SILENT 125XS" class="equipment-image">
```
