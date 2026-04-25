---
name: renovacion
description: Run the Renovacion airflow calculation, equipment specification, and HTML memory workflow from a self-contained project skill.
---

# Renovacion Skill

Use this skill for Renovacion ventilation projects.

## Project file rule

All project files must live under this skill directory using:

```text
proyectos/[id]/
  input.json
  resultados.json
  spec.json
  memoria.html
  assets/
```

Never create or save Renovacion project artifacts outside `proyectos/[id]/` relative to this skill root.

## Local commands

From this skill root, run:

```bash
uv run pytest -q tests
bash scripts/run-project.sh 1
```

From any other working directory, run the scripts by path. They compute `SKILL_ROOT` from their own location and still write under this skill's `proyectos/[id]/`.

## Workflow

1. Keep or create `proyectos/[id]/input.json`.
2. Run `python scripts/run-calc.py [id]` to write `proyectos/[id]/resultados.json`.
3. Run `python scripts/run-spec.py [id]` to write `proyectos/[id]/spec.json`.
4. Run `bash scripts/run-memory.sh [id]` to write `proyectos/[id]/memoria.html`.
5. Or run `bash scripts/run-project.sh [id]` for calc → spec → memory.

## Scope notes

This skill includes local engines, rules, contracts, CSS, vendored KaTeX, catalog images, examples, and the `proyectos/1` smoke fixture. PDF output and final install instructions are out of scope for this change.
