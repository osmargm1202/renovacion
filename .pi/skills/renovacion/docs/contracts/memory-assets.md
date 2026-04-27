# Contract: Memory Assets

## Purpose

Política de staging y referencias de assets para `memoria.html` demand-only.

## Project assets directory

`.pi/skills/renovacion/proyectos/[id]/assets/`

Subdirectorios:

- `logos/`
- `placeholders/`

The runtime may keep `equipos/` for compatibility with existing fixtures, but demand-only memory does not depend on equipment images.

## Logo policy

Fuentes desde `input.json`:

- `project.logo_empresa`
- `project.logo_cliente`

Reglas:

1. asegurar `proyectos/[id]/assets/`
2. asegurar `proyectos/[id]/assets/logos/`
3. si el logo es URL, descargarlo a `assets/logos/`
4. si el logo es ruta local, copiarlo a `assets/logos/`
5. si falla, usar placeholder local
6. HTML final referencia solo rutas locales del proyecto

## Placeholder policy

- crear `assets/placeholders/placeholder-logo.svg`
- crear `assets/placeholders/placeholder-equipment.svg` solo por compatibilidad visual con fixtures existentes
- asset faltante no aborta render

## Asset policies

- `project-assets`: usar assets del proyecto para la memoria demand-only
- `continue-placeholder`: si falta asset, no abortar render
- `always-local`: HTML final sin URLs externas

## HTML references

Ejemplo logo empresa:

```html
<img src="assets/logos/empresa-orgm.png" alt="Logo empresa" />
```

Ejemplo logo cliente:

```html
<img src="assets/logos/cliente-bohc.png" alt="Logo cliente" />
```
