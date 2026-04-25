# Self-Contained Renovacion Pi Skill Design

## Goal
Package `renovacion` as a self-contained project Pi skill at `.pi/skills/renovacion/` so Pi can discover it and the calculation/spec/memory workflow can run without depending on repository-root files.

## Approved Scope
Includes:
- Create `.pi/skills/renovacion/SKILL.md` with Pi-valid frontmatter: `name: renovacion` matching parent directory and a non-empty `description`.
- Copy/include all runtime resources needed by the skill:
  - `lib/input-pipeline/`
  - `lib/calc-engine/`
  - `lib/spec-engine/`
  - `lib/memory-engine/`
  - `rules/renovacion.json`
  - `assets/css/`
  - `assets/vendor/katex/`
  - `assets/extractores/`
  - `docs/contracts/`
  - `examples/input-pipeline/`
  - `proyectos/1/` golden fixture
- Add skill-local wrapper scripts that compute `SKILL_ROOT` from script location and always read/write under skill root.
- Preserve artifact convention: every created or saved project file lives under `.pi/skills/renovacion/proyectos/[id]/`.
- Add tests proving structure, resources, skill-local smoke behavior, no repository-root dependency, and output location.

Excludes:
- Final README install instructions.
- Redesign of engines.
- PDF generation.
- New business logic beyond wrappers/path stabilization.
- Root package restructuring.

## Evidence
Exploration artifact: `pdd/self-contained-renovacion-skill/explore`.

Key findings:
- Repo has no `.pi/skills/` today.
- Pi discovers skills under `.pi/skills/**/SKILL.md`; `name` must match parent directory and `description` is required.
- Existing artifacts consistently use `proyectos/[id]/input.json`, `resultados.json`, `spec.json`, `memoria.html`, optional `memoria.pdf`, and `assets/`.
- Golden fixture exists at `proyectos/1/`.
- `memory-engine/runner.js` and `assets.js` are cwd-sensitive; wrappers must `cd` to `SKILL_ROOT` or pass explicit project paths.
- `spec-engine` lives in hyphenated directory; wrapper needs importlib package alias to preserve relative imports.
- Root `pyproject.toml` lacks `jsonschema`; skill-local test metadata must include test/runtime deps.
- Existing memory Jest-style tests are not usable without adding a runner; new skill tests should use Python subprocess assertions and plain shell/node commands.

## Architecture
Treat `.pi/skills/renovacion/` as a copied mini-root. Inside that directory, existing engines keep their current relative layout so copied code that already climbs to root still resolves to the skill root.

Runtime entrypoints live under `.pi/skills/renovacion/scripts/`:
- `_skill_paths.py`: shared path helpers and safe project-id validation.
- `run-calc.py`: invokes copied `calc_engine.runner.run_calculation()` and writes `proyectos/[id]/resultados.json`.
- `run-spec.py`: imports copied hyphenated `lib/spec-engine` through a package alias and writes `proyectos/[id]/spec.json`.
- `run-memory.sh`: `cd`s to `SKILL_ROOT`, runs copied Node memory runner, and writes `proyectos/[id]/memoria.html`.
- `run-project.sh`: runs calc → spec → memory for one numeric project id and validates local outputs.
- `validate-skill-structure.py`: validates frontmatter and required resource presence.

Testing is skill-local and TDD-first. Builders first add failing tests under `.pi/skills/renovacion/tests/`, then add resources/wrappers until those tests pass.

## File Layout
Target layout:

```text
.pi/skills/renovacion/
  SKILL.md
  .python-version
  pyproject.toml
  lib/
    input-pipeline/
    calc-engine/
    spec-engine/
    memory-engine/
  rules/renovacion.json
  assets/
    css/
    extractores/
    vendor/katex/
  docs/contracts/
  examples/input-pipeline/
  proyectos/1/
  scripts/
    _skill_paths.py
    run-calc.py
    run-spec.py
    run-memory.sh
    run-project.sh
    validate-skill-structure.py
  tests/
    test_skill_structure.py
    test_python_wrappers.py
    test_memory_wrapper.py
    test_no_repo_root_dependency.py
```

## Data Flow
1. Pi discovers `.pi/skills/renovacion/SKILL.md`.
2. Skill instructions tell agents to keep all generated project artifacts under `proyectos/[id]/` relative to skill root.
3. For project `1`, `run-project.sh 1` computes `SKILL_ROOT`, changes into it, then runs:
   - `run-calc.py 1`: reads `proyectos/1/input.json`, `rules/renovacion.json`; writes `proyectos/1/resultados.json`.
   - `run-spec.py 1`: reads `input.json`, `resultados.json`, `lib/spec-engine/catalog/models.json`; writes `proyectos/1/spec.json`.
   - `run-memory.sh 1`: reads all three project JSON files and writes `proyectos/1/memoria.html`.
4. Validation asserts no output is written to caller cwd or repo-root `proyectos/`.

## Path Rules
- `SKILL_ROOT = Path(__file__).resolve().parents[1]` for Python scripts in `scripts/`.
- `SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"` for shell scripts.
- Project id must be numeric only; reject values containing `/`, `..`, or non-digits.
- All default project paths must be `SKILL_ROOT / "proyectos" / project_id`.
- Memory wrapper must `cd "$SKILL_ROOT"` before invoking Node because memory assets are cwd-sensitive.

## Skill Instructions
`SKILL.md` should be short and operational. It must:
- Declare this as the `renovacion` skill.
- State artifact convention: all project files under `proyectos/[id]/` inside the skill.
- List local commands for validating and running project 1.
- Avoid final install instructions in root `README.md` or any promise that install steps are final.
- Avoid promising PDF output.

## Acceptance Criteria
- `.pi/skills/renovacion/SKILL.md` exists with `name: renovacion` and non-empty `description`.
- Required copied resources exist under the skill, including engines, rules, CSS, vendored KaTeX, extractor images, docs/contracts, examples, and `proyectos/1`.
- `uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests` passes.
- `bash .pi/skills/renovacion/scripts/run-project.sh 1` passes from repo root.
- Running the copied skill from a temp directory outside the repo passes and writes only under temp skill `proyectos/1/`.
- Generated/updated outputs remain under `.pi/skills/renovacion/proyectos/[id]/`.
- Root `README.md` is not modified for install instructions in this change.

## Validation Strategy
- Structure test: frontmatter validity and required resource paths.
- Python wrapper tests: calc/spec wrappers write expected JSON outputs under skill project directory.
- Memory wrapper test: memory wrapper renders `memoria.html`, uses vendored KaTeX, and contains expected project values.
- Isolation test: copy `.pi/skills/renovacion/` to a temporary directory, run from outside the repo with no `PYTHONPATH`, assert no external `proyectos/` is created.
- Manual smoke: run `bash .pi/skills/renovacion/scripts/run-project.sh 1` from repo root and from within `.pi/skills/renovacion/`.

## Risks
- Resource copies can drift from root engines. Mitigation: keep copy step explicit and test required files/resources.
- Memory engine cwd sensitivity can silently write/read caller paths. Mitigation: wrapper always `cd`s to skill root and tests run from foreign cwd.
- Spec engine import can fail because of hyphenated directory. Mitigation: wrapper loads package alias with `submodule_search_locations`.
- Missing catalog images may produce placeholders. Mitigation: include extractor images referenced by golden fixture and accept existing placeholder behavior.
- Skill-local deps can drift from root deps. Mitigation: include skill-local `pyproject.toml` with `jsonschema` and `pytest`.

## Non-Goals
- No final README install instructions.
- No Pi package publishing flow.
- No new project creation UX beyond preserving `proyectos/[id]/` convention and safe path helpers.
- No engine behavior changes except path-stable wrappers.
