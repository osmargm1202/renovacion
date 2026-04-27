# Renovacion Root Mode Contract

developer_mode = true

Root `AGENTS.md` controls manual repo mode only. `.pi/skills/renovacion/` is source of truth. Preserve `.pi/skills/renovacion/proyectos/[id]/` for project artifacts and never move Renovacion outputs outside that path.

## Developer mode

When manual flag stays `developer_mode = true`, agent works in developer mode.

- May modify `.pi/skills/renovacion/assets/`.
- May modify `.pi/skills/renovacion/lib/`.
- May modify `.pi/skills/renovacion/lib/spec-engine/catalog/`.
- May modify `.pi/skills/renovacion/docs/`.
- May modify `.pi/skills/renovacion/tests/`.
- Must use TDD for behavior changes.
- Must follow RED → GREEN → REFACTOR.
- Use red-green-refactor cadence for every approved change.
- Preserve `.pi/skills/renovacion/proyectos/[id]/` while changing code, docs, assets, or tests.

## Operator mode

When manual flag becomes `developer_mode = false`, agent is operator-only.

- Do not modify `.pi/skills/renovacion/assets/`.
- Do not modify `.pi/skills/renovacion/lib/`.
- Do not modify `.pi/skills/renovacion/lib/spec-engine/catalog/`.
- Do not modify `.pi/skills/renovacion/docs/`.
- Do not modify `.pi/skills/renovacion/tests/`.
- Interview client for missing information before running workflow.
- Ask one focused question at a time.
- Use `.pi/skills/renovacion/docs/contracts/input-json.md` as contract for missing fields and normalization rules.
- Review top-level keys `project`, `validation`, `areas`, `defaults_applied`.
- Default workflow is area/demand-only. Manual equipment data is optional and future-scope.
- Update `.pi/skills/renovacion/proyectos/[id]/input.json` with collected client data.
- Run `python .pi/skills/renovacion/scripts/run-calc.py [id]`.
- Run `bash .pi/skills/renovacion/scripts/run-memory.sh [id]`.
- Report outputs from `.pi/skills/renovacion/proyectos/[id]/resultados.json` and `.pi/skills/renovacion/proyectos/[id]/memoria.html`.

Spec engine remains available for future/manual equipment specification through `.pi/skills/renovacion/scripts/run-spec.py`, but it is not part of the default operator workflow.

## Client calculation workflow

1. Start from `.pi/skills/renovacion/proyectos/[id]/input.json`.
2. If client information is missing, ask one focused question at a time and align answers to `.pi/skills/renovacion/docs/contracts/input-json.md`.
3. Fill required data under top-level keys `project`, `validation`, `areas`, `defaults_applied`.
4. Leave manual equipment data omitted or empty unless future/manual equipment scope is explicitly requested.
5. Update `.pi/skills/renovacion/proyectos/[id]/input.json`.
6. Run calc, then memory.
7. Report outputs and file locations for `.pi/skills/renovacion/proyectos/[id]/resultados.json` and `.pi/skills/renovacion/proyectos/[id]/memoria.html`.
