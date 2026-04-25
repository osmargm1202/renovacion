# HTML V1 Hardening Design

## Goal
Diseñar el subproyecto de endurecimiento de la v1 HTML del pipeline `renovacion`, para dejar el flujo reproducible, offline en fórmulas, limpio en repo y ejecutable con un solo comando de smoke test.

## Scope
Incluye:
- vendorización local de KaTeX
- eliminación de dependencia CDN en `memoria.html`
- script único de smoke test para proyecto 1
- runbook de ejecución
- limpieza agresiva de archivos temporales/noise
- baseline commit con tooling + artifacts de proyecto 1 (`input.json`, `resultados.json`, `spec.json`, `memoria.html`)

No incluye:
- rediseño de motores existentes
- PDF final
- reestructuración grande de paquetes
- nuevos features de cálculo/spec/memory

## Decisions Confirmed With User
- KaTeX: `vendor-katex`
- Commit strategy: `commit-tooling+project1-json-html`
- Cleanup policy: `aggressive-clean`
- Smoke style: `single-script`
- Enfoque recomendado: `release hardening`

## Architecture

### Offline Math Strategy
Se eliminará dependencia de CDN para KaTeX.

Regla:
- assets de KaTeX vivirán localmente en repo
- `memoria.html` final no debe apuntar a CDN externa para fórmulas

Ubicación recomendada:
- `assets/vendor/katex/`

Debe incluir:
- CSS KaTeX
- JS KaTeX
- JS auto-render si el engine lo usa

### Smoke Strategy
Se agregará un único script para ejecutar pipeline de proyecto 1.

Ruta recomendada:
- `scripts/run-project-1.sh`

Responsabilidad:
1. verificar precondiciones
2. ejecutar calc engine
3. ejecutar spec engine
4. ejecutar memory engine
5. reportar rutas de salida

### Runbook Strategy
Se documentará el flujo de smoke y verificación.

Ruta recomendada:
- `docs/runbooks/project-1-smoke.md`

Contenido mínimo:
- prerequisitos
- comando
- outputs esperados
- checklist de verificación rápida

## Files To Keep
Se consideran parte del baseline estable:
- `.pi/agents/...`
- `docs/superpowers/specs/...`
- `docs/contracts/...`
- runbooks estables
- `lib/input-pipeline/...`
- `lib/calc-engine/...`
- `lib/spec-engine/...`
- `lib/memory-engine/...`
- `tests/...`
- `scripts/run-project-1.sh`
- `rules/renovacion.json`
- `proyectos/1/input.json`
- `proyectos/1/resultados.json`
- `proyectos/1/spec.json`
- `proyectos/1/memoria.html`
- assets locales requeridos por `memoria.html`
- `assets/vendor/katex/...`

## Files To Remove
La limpieza agresiva debe remover ruido temporal y no reproducible.

Candidatos confirmados:
- `README_1.md`
- `integration-test-results.md`
- `test_input_pipeline_integration.py`
- `.pi/agent-sessions/`
- `__pycache__/`
- otros archivos temporales equivalentes no necesarios

Regla:
- no remover archivos requeridos por contratos, motores, tests o smoke run

## Behavior Rules
### Final `memoria.html`
Debe:
- conservar assets locales de proyecto para imágenes/logos
- conservar CSS inline embebido
- usar KaTeX local vendorizado, no CDN
- seguir cumpliendo contrato de secciones y contenido

### Commit Boundary
Commit final debe representar:
- pipeline HTML v1 estable
- repo limpio de ruido temporal
- smoke reproducible
- baseline de proyecto 1 preservado

## Risks
- path mismatch al migrar KaTeX de CDN a local
- limpieza agresiva puede borrar algo útil si no se revisa con cuidado
- smoke script puede asumir paths frágiles
- assets adicionales pueden aumentar tamaño del commit

## Acceptance Criteria
Hardening queda listo cuando:
- `memoria.html` no contiene URLs CDN para KaTeX
- assets KaTeX están vendorizados localmente
- `scripts/run-project-1.sh` ejecuta pipeline completo
- `docs/runbooks/project-1-smoke.md` existe y es suficiente
- archivos temporales/aggressive-clean targets removidos
- artifacts proyecto 1 siguen válidos
- repo queda listo para commit baseline

## Testing Strategy
- verificar ausencia de `cdn.jsdelivr` u otras CDN en `proyectos/1/memoria.html`
- verificar que fórmulas siguen renderizando con assets locales
- ejecutar smoke script con salida exitosa
- confirmar existencia de:
  - `proyectos/1/input.json`
  - `proyectos/1/resultados.json`
  - `proyectos/1/spec.json`
  - `proyectos/1/memoria.html`
- confirmar contenido esperado en HTML:
  - portada
  - RH `129.6`
  - `EX-150`
  - alternativas
- confirmar archivos temporales removidos

## Recommendation
Siguiente paso tras aprobación: implementar hardening v1 HTML, limpiar repo, regenerar `memoria.html` offline, agregar smoke script y crear commit baseline.
