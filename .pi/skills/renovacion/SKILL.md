---
name: renovacion
description: Run the Renovacion airflow calculation and demand-only HTML memory workflow from a self-contained project skill.
---

# Renovacion Skill

Use this skill for Renovacion ventilation projects.

## Project file rule

Runtime project files must live in the current execution directory using:

```text
./proyectos/[id]/
  input.json
  resultados.json
  memoria.html
  assets/
```

`[id]` may be numeric (`1`) or a safe project slug (`miniso-pr`) using letters, numbers, dots, underscores, and hyphens. Do not create or save runtime Renovacion project artifacts under this skill directory. `.pi/skills/renovacion/proyectos/` is reserved only for deliberate fixtures/examples.

`spec.json` may exist for future/manual equipment specification, but demand-only memory generation does not require it.

## Local commands

From the directory that should receive project outputs, run scripts by path:

```bash
python .pi/skills/renovacion/scripts/run-calc.py miniso-pr
bash .pi/skills/renovacion/scripts/run-memory.sh miniso-pr
bash .pi/skills/renovacion/scripts/run-project.sh miniso-pr
```

They compute `SKILL_ROOT` from their own location for engine/assets, but read and write project artifacts under the caller's `./proyectos/[id]/`.

For skill development tests only, from this skill root run:

```bash
uv run pytest -q tests
```

## Default workflow

1. Keep or create `./proyectos/[id]/input.json` in the current execution directory.
2. Run `python .pi/skills/renovacion/scripts/run-calc.py [id]` to write `./proyectos/[id]/resultados.json`.
3. Run `bash .pi/skills/renovacion/scripts/run-memory.sh [id]` to write `./proyectos/[id]/memoria.html`.
4. Or run `bash .pi/skills/renovacion/scripts/run-project.sh [id]` for calc → memory.

## Future/manual equipment specification

`python .pi/skills/renovacion/scripts/run-spec.py [id]` remains available for future/manual equipment selection and writes `./proyectos/[id]/spec.json` when explicitly requested. Default memory output does not load or render that artifact.

## Scope notes

This skill includes local engines, rules, contracts, CSS, vendored KaTeX, catalog images, examples, and fixture data. PDF output and final install instructions are out of scope for this change.
