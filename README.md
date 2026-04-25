# renovacion

Pipeline local para generar memorias de cálculo de renovación de aire.

## Flujo v1
- `proyectos/[id]/input.json` — entrada validada
- `proyectos/[id]/resultados.json` — cálculo de caudal
- `proyectos/[id]/spec.json` — selección local de equipos
- `proyectos/[id]/memoria.html` — memoria HTML offline

## Motores
- `lib/input-pipeline/` — validación, normalización, ids, catálogo base
- `lib/calc-engine/` — cálculo RH/personas, trazas y agregados
- `lib/spec-engine/` — catálogo local y selección automática de modelo
- `lib/memory-engine/` — render HTML por secciones con assets locales y KaTeX vendorizado

## Proyecto baseline
- `proyectos/1/` = `AURORA GMR`

## Smoke test
```bash
bash scripts/run-project-1.sh
```

## Documentación clave
- `docs/contracts/` — contratos de artifacts
- `docs/runbooks/project-1-smoke.md` — ejecución/verificación rápida
- `docs/superpowers/specs/` — specs por subproyecto
