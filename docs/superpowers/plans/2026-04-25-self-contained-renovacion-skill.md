# Self-Contained Renovacion Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained Pi skill at `.pi/skills/renovacion/` that runs the existing Renovacion pipeline without repository-root dependencies and keeps all project artifacts under `proyectos/[id]/` inside the skill.

**Architecture:** Treat the skill directory as a copied mini-root with existing engines/resources preserved. Add thin wrappers that compute `SKILL_ROOT`, validate numeric project ids, and invoke calc/spec/memory while forcing all reads/writes under skill-local `proyectos/[id]/`.

**Tech Stack:** Python 3.13, `uv`, `pytest`, `jsonschema`, Node.js CommonJS, Bash, Pi project skills.

---

## Parallel Execution Map

- `main` must run first. It creates only the bare skill test harness and failing structure contract.
- `build-package` creates/copies the self-contained resource tree and passes frontmatter/resource checks; script-existence checks pass after wrapper groups.
- After `build-package`, `build-python-wrappers` and `build-memory-wrapper` can run in parallel because they write different scripts/tests.
- `build-e2e-isolation` depends on both wrapper groups.
- Review groups mirror build groups and can run as soon as their build dependency finishes.

## File Responsibilities

Create/modify these files only:

- Create `.pi/skills/renovacion/SKILL.md`: Pi skill frontmatter and operational instructions; no final install instructions.
- Create `.pi/skills/renovacion/.python-version`: copy root Python version.
- Create `.pi/skills/renovacion/pyproject.toml`: skill-local test/runtime metadata with `jsonschema` and `pytest`.
- Copy `.pi/skills/renovacion/lib/input-pipeline/` from `lib/input-pipeline/`.
- Copy `.pi/skills/renovacion/lib/calc-engine/` from `lib/calc-engine/`.
- Copy `.pi/skills/renovacion/lib/spec-engine/` from `lib/spec-engine/`.
- Copy `.pi/skills/renovacion/lib/memory-engine/` from `lib/memory-engine/`.
- Copy `.pi/skills/renovacion/rules/renovacion.json` from `rules/renovacion.json`.
- Copy `.pi/skills/renovacion/assets/css/` from `assets/css/`.
- Copy `.pi/skills/renovacion/assets/vendor/katex/` from `assets/vendor/katex/`.
- Copy `.pi/skills/renovacion/assets/extractores/` from `assets/extractores/`.
- Copy `.pi/skills/renovacion/docs/contracts/` from `docs/contracts/`.
- Copy `.pi/skills/renovacion/examples/input-pipeline/` from `examples/input-pipeline/`.
- Copy `.pi/skills/renovacion/proyectos/1/` from `proyectos/1/`.
- Create `.pi/skills/renovacion/scripts/_skill_paths.py`: shared path helpers.
- Create `.pi/skills/renovacion/scripts/run-calc.py`: skill-local calc runner.
- Create `.pi/skills/renovacion/scripts/run-spec.py`: skill-local spec runner with alias import for hyphenated engine dir.
- Create `.pi/skills/renovacion/scripts/run-memory.sh`: cwd-stable memory runner.
- Create `.pi/skills/renovacion/scripts/run-project.sh`: end-to-end smoke runner.
- Create `.pi/skills/renovacion/scripts/validate-skill-structure.py`: manual structure validator.
- Create `.pi/skills/renovacion/tests/test_skill_structure.py`: frontmatter/resource contract tests.
- Create `.pi/skills/renovacion/tests/test_python_wrappers.py`: calc/spec wrapper tests.
- Create `.pi/skills/renovacion/tests/test_memory_wrapper.py`: memory wrapper test.
- Create `.pi/skills/renovacion/tests/test_no_repo_root_dependency.py`: temp-copy isolation test.

Do not modify `README.md` in this change.

---

### Task 1: Seed failing skill structure contract

**Files:**
- Create: `.pi/skills/renovacion/tests/test_skill_structure.py`
- Create: `.pi/skills/renovacion/pyproject.toml`
- Create: `.pi/skills/renovacion/.python-version`

- [ ] **Step 1: Create bare skill test directory**

Run:

```bash
mkdir -p .pi/skills/renovacion/tests
cp .python-version .pi/skills/renovacion/.python-version
```

- [ ] **Step 2: Create skill-local pyproject**

Write `.pi/skills/renovacion/pyproject.toml`:

```toml
[project]
name = "renovacion-skill"
version = "0.1.0"
description = "Self-contained Pi skill for Renovacion airflow calculation/spec/memory generation."
requires-python = ">=3.13"
dependencies = [
  "jsonschema>=4.23.0",
  "pytest>=8.3.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 3: Write failing structure/resource test**

Write `.pi/skills/renovacion/tests/test_skill_structure.py`:

```python
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.find("\n---", 4)
    assert end != -1, "SKILL.md must close YAML frontmatter"
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def test_skill_frontmatter_is_pi_discoverable():
    skill_md = SKILL_ROOT / "SKILL.md"
    assert skill_md.exists()
    frontmatter = parse_frontmatter(skill_md)
    assert frontmatter["name"] == SKILL_ROOT.name == "renovacion"
    assert frontmatter["description"]
    assert len(frontmatter["name"]) <= 64
    assert frontmatter["name"].replace("-", "").isalnum()
    assert not frontmatter["name"].startswith("-")
    assert not frontmatter["name"].endswith("-")
    assert "--" not in frontmatter["name"]


def test_required_runtime_resources_are_skill_local():
    required_paths = [
        "lib/input-pipeline/schema.json",
        "lib/input-pipeline/validator.py",
        "lib/input-pipeline/catalog_resolver.py",
        "lib/input-pipeline/project_id_allocator.py",
        "lib/calc-engine/pyproject.toml",
        "lib/calc-engine/src/calc_engine/runner.py",
        "lib/spec-engine/__init__.py",
        "lib/spec-engine/runner.py",
        "lib/spec-engine/catalog/models.json",
        "lib/memory-engine/index.js",
        "lib/memory-engine/runner.js",
        "lib/memory-engine/assets.js",
        "lib/memory-engine/formula.js",
        "lib/memory-engine/sections/portada.js",
        "rules/renovacion.json",
        "assets/css/memoria.css",
        "assets/css/memoria-sections.css",
        "assets/vendor/katex/katex.min.css",
        "assets/vendor/katex/katex.min.js",
        "assets/vendor/katex/auto-render.min.js",
        "assets/extractores/ex-150.png",
        "assets/extractores/ex-160.png",
        "assets/extractores/ex-200.png",
        "assets/extractores/ex-250.png",
        "docs/contracts/input-json.md",
        "docs/contracts/resultados-json.md",
        "docs/contracts/spec-json.md",
        "docs/contracts/memoria-html.md",
        "examples/input-pipeline/aurora-gmr.input.json",
        "proyectos/1/input.json",
        "proyectos/1/resultados.json",
        "proyectos/1/spec.json",
        "proyectos/1/memoria.html",
    ]
    missing = [rel for rel in required_paths if not (SKILL_ROOT / rel).exists()]
    assert missing == []


def test_scripts_expected_by_skill_exist_and_are_executable():
    scripts = [
        "scripts/run-calc.py",
        "scripts/run-spec.py",
        "scripts/run-memory.sh",
        "scripts/run-project.sh",
        "scripts/validate-skill-structure.py",
    ]
    missing = [rel for rel in scripts if not (SKILL_ROOT / rel).exists()]
    assert missing == []
```

- [ ] **Step 4: Run test and verify it fails for missing implementation**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_skill_structure.py
```

Expected: FAIL. First failure should mention missing `.pi/skills/renovacion/SKILL.md` or required resource paths.

- [ ] **Step 5: Commit checkpoint**

```bash
git add .pi/skills/renovacion/pyproject.toml .pi/skills/renovacion/.python-version .pi/skills/renovacion/tests/test_skill_structure.py
git commit -m "test: define renovacion skill structure contract"
```

---

### Task 2: Add self-contained skill package resources

**Files:**
- Create: `.pi/skills/renovacion/SKILL.md`
- Copy: `.pi/skills/renovacion/lib/**`
- Copy: `.pi/skills/renovacion/rules/renovacion.json`
- Copy: `.pi/skills/renovacion/assets/{css,extractores,vendor/katex}/**`
- Copy: `.pi/skills/renovacion/docs/contracts/**`
- Copy: `.pi/skills/renovacion/examples/input-pipeline/**`
- Copy: `.pi/skills/renovacion/proyectos/1/**`
- Create: `.pi/skills/renovacion/scripts/validate-skill-structure.py`

- [ ] **Step 1: Copy resource tree**

Run:

```bash
mkdir -p .pi/skills/renovacion/lib .pi/skills/renovacion/rules .pi/skills/renovacion/assets .pi/skills/renovacion/docs .pi/skills/renovacion/examples .pi/skills/renovacion/proyectos .pi/skills/renovacion/scripts
cp -R lib/input-pipeline .pi/skills/renovacion/lib/input-pipeline
cp -R lib/calc-engine .pi/skills/renovacion/lib/calc-engine
cp -R lib/spec-engine .pi/skills/renovacion/lib/spec-engine
cp -R lib/memory-engine .pi/skills/renovacion/lib/memory-engine
cp rules/renovacion.json .pi/skills/renovacion/rules/renovacion.json
mkdir -p .pi/skills/renovacion/assets/css .pi/skills/renovacion/assets/vendor .pi/skills/renovacion/assets/extractores
cp -R assets/css/. .pi/skills/renovacion/assets/css/
cp -R assets/vendor/katex .pi/skills/renovacion/assets/vendor/katex
cp -R assets/extractores/. .pi/skills/renovacion/assets/extractores/
cp -R docs/contracts .pi/skills/renovacion/docs/contracts
cp -R examples/input-pipeline .pi/skills/renovacion/examples/input-pipeline
cp -R proyectos/1 .pi/skills/renovacion/proyectos/1
```

- [ ] **Step 2: Create Pi-valid SKILL.md**

Write `.pi/skills/renovacion/SKILL.md`:

```markdown
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
```

- [ ] **Step 3: Add structure validator script**

Write `.pi/skills/renovacion/scripts/validate-skill-structure.py`:

```python
#!/usr/bin/env python3
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "SKILL.md",
    "pyproject.toml",
    "lib/input-pipeline/schema.json",
    "lib/calc-engine/src/calc_engine/runner.py",
    "lib/spec-engine/runner.py",
    "lib/spec-engine/catalog/models.json",
    "lib/memory-engine/runner.js",
    "rules/renovacion.json",
    "assets/css/memoria.css",
    "assets/vendor/katex/katex.min.css",
    "assets/extractores/ex-150.png",
    "docs/contracts/input-json.md",
    "examples/input-pipeline/aurora-gmr.input.json",
    "proyectos/1/input.json",
]


def frontmatter() -> dict[str, str]:
    path = SKILL_ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("SKILL.md missing opening frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise SystemExit("SKILL.md missing closing frontmatter")
    parsed = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"')
    return parsed


def main() -> int:
    meta = frontmatter()
    errors = []
    if meta.get("name") != "renovacion":
        errors.append("SKILL.md name must be renovacion")
    if not meta.get("description"):
        errors.append("SKILL.md description is required")
    for rel in REQUIRED:
        if not (SKILL_ROOT / rel).exists():
            errors.append(f"missing {rel}")
    if errors:
        print("Skill structure invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Skill structure OK: {SKILL_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Run:

```bash
chmod +x .pi/skills/renovacion/scripts/validate-skill-structure.py
```

- [ ] **Step 4: Run structure tests and validator**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_skill_structure.py
python .pi/skills/renovacion/scripts/validate-skill-structure.py
```

Expected: PASS for frontmatter/resources. If script existence assertion still fails for wrappers, continue after Task 3/4 or temporarily expect only script-list failures. Final pass required after all scripts exist.

- [ ] **Step 5: Commit checkpoint**

```bash
git add .pi/skills/renovacion
git commit -m "feat: add self-contained renovacion skill resources"
```

---

### Task 3: Add Python path helpers and calc/spec wrappers

**Dependencies:** Task 2 resource copy.

**Files:**
- Create: `.pi/skills/renovacion/scripts/_skill_paths.py`
- Create: `.pi/skills/renovacion/scripts/run-calc.py`
- Create: `.pi/skills/renovacion/scripts/run-spec.py`
- Create: `.pi/skills/renovacion/tests/test_python_wrappers.py`

- [ ] **Step 1: Write failing wrapper tests**

Write `.pi/skills/renovacion/tests/test_python_wrappers.py`:

```python
import json
import os
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], cwd: Path):
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=env)


def test_run_calc_writes_resultados_under_skill_project():
    output = SKILL_ROOT / "proyectos/1/resultados.json"
    before = output.read_text(encoding="utf-8") if output.exists() else None
    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-calc.py"), "1"], cwd=SKILL_ROOT.parent)
    assert result.returncode == 0, result.stdout + result.stderr
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == 1
    assert data["summary"]["total_required_m3_h"] > 0
    if before is not None:
        assert json.loads(output.read_text(encoding="utf-8"))["project"]["calculation_status"] == "completed"


def test_run_spec_writes_spec_under_skill_project():
    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-spec.py"), "1"], cwd=SKILL_ROOT.parent)
    assert result.returncode == 0, result.stdout + result.stderr
    output = SKILL_ROOT / "proyectos/1/spec.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == 1
    selected = data["equipment_specs"][0]["selected_model"]
    assert selected["model"] == "EX-150"


def test_wrappers_reject_non_numeric_project_ids():
    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-calc.py"), "../1"], cwd=SKILL_ROOT)
    assert result.returncode != 0
    assert "Project id must be numeric" in (result.stdout + result.stderr)
```

- [ ] **Step 2: Run tests and verify they fail for missing wrappers**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_python_wrappers.py
```

Expected: FAIL with `can't open file` or missing script errors.

- [ ] **Step 3: Implement shared path helper**

Write `.pi/skills/renovacion/scripts/_skill_paths.py`:

```python
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROYECTOS_ROOT = SKILL_ROOT / "proyectos"


def parse_project_id(raw: str) -> str:
    if not raw.isdigit():
        raise ValueError("Project id must be numeric")
    return raw


def project_dir(raw: str) -> Path:
    project_id = parse_project_id(raw)
    return PROYECTOS_ROOT / project_id


def require_project_file(project_path: Path, filename: str) -> Path:
    path = project_path / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required project file: {path}")
    return path


def add_calc_engine_to_path() -> None:
    src = SKILL_ROOT / "lib" / "calc-engine" / "src"
    sys.path.insert(0, str(src))
```

- [ ] **Step 4: Implement calc wrapper**

Write `.pi/skills/renovacion/scripts/run-calc.py`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path

from _skill_paths import SKILL_ROOT, add_calc_engine_to_path, project_dir, require_project_file


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/run-calc.py <project-id>", file=sys.stderr)
        return 2
    try:
        project_path = project_dir(argv[1])
        input_path = require_project_file(project_path, "input.json")
        rules_path = SKILL_ROOT / "rules" / "renovacion.json"
        output_path = project_path / "resultados.json"
        add_calc_engine_to_path()
        from calc_engine.runner import run_calculation
        run_calculation(Path(input_path), Path(rules_path), Path(output_path))
        print(f"Wrote {output_path.relative_to(SKILL_ROOT)}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 5: Implement spec wrapper**

Write `.pi/skills/renovacion/scripts/run-spec.py`:

```python
#!/usr/bin/env python3
import importlib
import importlib.util
import json
import sys

from _skill_paths import SKILL_ROOT, project_dir, require_project_file

PACKAGE_NAME = "renovacion_spec_engine"


def load_spec_runner():
    package_dir = SKILL_ROOT / "lib" / "spec-engine"
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec engine from {package_dir}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return importlib.import_module(f"{PACKAGE_NAME}.runner")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/run-spec.py <project-id>", file=sys.stderr)
        return 2
    try:
        project_path = project_dir(argv[1])
        require_project_file(project_path, "input.json")
        require_project_file(project_path, "resultados.json")
        runner = load_spec_runner()
        catalog_path = SKILL_ROOT / "lib" / "spec-engine" / "catalog" / "models.json"
        spec_data = runner.run_spec_generation(project_path, catalog_path)
        output_path = project_path / "spec.json"
        output_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {output_path.relative_to(SKILL_ROOT)}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Run:

```bash
chmod +x .pi/skills/renovacion/scripts/run-calc.py .pi/skills/renovacion/scripts/run-spec.py
```

- [ ] **Step 6: Run Python wrapper tests**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_python_wrappers.py
```

Expected: PASS.

- [ ] **Step 7: Commit checkpoint**

```bash
git add .pi/skills/renovacion/scripts/_skill_paths.py .pi/skills/renovacion/scripts/run-calc.py .pi/skills/renovacion/scripts/run-spec.py .pi/skills/renovacion/tests/test_python_wrappers.py .pi/skills/renovacion/proyectos/1/resultados.json .pi/skills/renovacion/proyectos/1/spec.json
git commit -m "feat: add skill-local python pipeline wrappers"
```

---

### Task 4: Add memory wrapper

**Dependencies:** Task 2 resource copy.

**Files:**
- Create: `.pi/skills/renovacion/scripts/run-memory.sh`
- Create: `.pi/skills/renovacion/tests/test_memory_wrapper.py`

- [ ] **Step 1: Write failing memory wrapper test**

Write `.pi/skills/renovacion/tests/test_memory_wrapper.py`:

```python
import os
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def test_run_memory_from_foreign_cwd_writes_skill_local_html(tmp_path):
    output = SKILL_ROOT / "proyectos/1/memoria.html"
    result = subprocess.run(
        ["bash", str(SKILL_ROOT / "scripts/run-memory.sh"), "1"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert output.exists()
    html = output.read_text(encoding="utf-8")
    assert "AURORA GMR" in html
    assert "129.6" in html
    assert "EX-150" in html
    assert "assets/vendor/katex" in html
    assert "cdn.jsdelivr" not in html.lower()
    assert not (tmp_path / "proyectos" / "1" / "memoria.html").exists()
```

- [ ] **Step 2: Run test and verify it fails for missing wrapper**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_memory_wrapper.py
```

Expected: FAIL with missing `run-memory.sh`.

- [ ] **Step 3: Implement memory wrapper**

Write `.pi/skills/renovacion/scripts/run-memory.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/run-memory.sh <project-id>" >&2
  exit 2
fi

PROJECT_ID="$1"
if ! [[ "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
  echo "Project id must be numeric" >&2
  exit 1
fi

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_PATH="proyectos/${PROJECT_ID}"

cd "$SKILL_ROOT"

if [ ! -f "${PROJECT_PATH}/input.json" ]; then
  echo "Missing ${PROJECT_PATH}/input.json" >&2
  exit 1
fi
if [ ! -f "${PROJECT_PATH}/resultados.json" ]; then
  echo "Missing ${PROJECT_PATH}/resultados.json" >&2
  exit 1
fi
if [ ! -f "${PROJECT_PATH}/spec.json" ]; then
  echo "Missing ${PROJECT_PATH}/spec.json" >&2
  exit 1
fi

node lib/memory-engine/runner.js "$PROJECT_ID" "$PROJECT_PATH"
```

Run:

```bash
chmod +x .pi/skills/renovacion/scripts/run-memory.sh
```

- [ ] **Step 4: Run memory wrapper test**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_memory_wrapper.py
```

Expected: PASS.

- [ ] **Step 5: Commit checkpoint**

```bash
git add .pi/skills/renovacion/scripts/run-memory.sh .pi/skills/renovacion/tests/test_memory_wrapper.py .pi/skills/renovacion/proyectos/1/memoria.html .pi/skills/renovacion/proyectos/1/assets
git commit -m "feat: add skill-local memory wrapper"
```

---

### Task 5: Add end-to-end smoke and no-root-dependency test

**Dependencies:** Task 3 and Task 4.

**Files:**
- Create: `.pi/skills/renovacion/scripts/run-project.sh`
- Create: `.pi/skills/renovacion/tests/test_no_repo_root_dependency.py`

- [ ] **Step 1: Write failing isolation test**

Write `.pi/skills/renovacion/tests/test_no_repo_root_dependency.py`:

```python
import os
import shutil
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def ignore_noise(_dir, names):
    return {".venv", "__pycache__", ".pytest_cache", "uv.lock"}.intersection(names)


def test_skill_copy_runs_outside_repo_and_writes_only_inside_skill(tmp_path):
    copied_skill = tmp_path / "renovacion"
    shutil.copytree(SKILL_ROOT, copied_skill, ignore=ignore_noise)
    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()

    result = subprocess.run(
        ["bash", str(copied_skill / "scripts/run-project.sh"), "1"],
        cwd=outside_cwd,
        text=True,
        capture_output=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (copied_skill / "proyectos/1/resultados.json").exists()
    assert (copied_skill / "proyectos/1/spec.json").exists()
    assert (copied_skill / "proyectos/1/memoria.html").exists()
    assert not (outside_cwd / "proyectos").exists()
    html = (copied_skill / "proyectos/1/memoria.html").read_text(encoding="utf-8")
    assert "AURORA GMR" in html
    assert "EX-150" in html
    assert "cdn.jsdelivr" not in html.lower()
```

- [ ] **Step 2: Run test and verify it fails for missing end-to-end script**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_no_repo_root_dependency.py
```

Expected: FAIL with missing `run-project.sh`.

- [ ] **Step 3: Implement end-to-end smoke wrapper**

Write `.pi/skills/renovacion/scripts/run-project.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: bash scripts/run-project.sh <project-id>" >&2
  exit 2
fi

PROJECT_ID="$1"
if ! [[ "$PROJECT_ID" =~ ^[0-9]+$ ]]; then
  echo "Project id must be numeric" >&2
  exit 1
fi

SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_PATH="proyectos/${PROJECT_ID}"

cd "$SKILL_ROOT"

echo "Renovacion skill smoke: project ${PROJECT_ID}"

python scripts/run-calc.py "$PROJECT_ID"
python scripts/run-spec.py "$PROJECT_ID"
bash scripts/run-memory.sh "$PROJECT_ID"

for file in input.json resultados.json spec.json memoria.html; do
  if [ ! -f "${PROJECT_PATH}/${file}" ]; then
    echo "Missing ${PROJECT_PATH}/${file}" >&2
    exit 1
  fi
done

if grep -qi "cdn.jsdelivr\|unpkg.com" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html contains CDN references" >&2
  exit 1
fi

if ! grep -q "AURORA GMR" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html missing AURORA GMR" >&2
  exit 1
fi

if ! grep -q "EX-150" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html missing EX-150" >&2
  exit 1
fi

echo "OK: ${PROJECT_PATH}"
```

Run:

```bash
chmod +x .pi/skills/renovacion/scripts/run-project.sh
```

- [ ] **Step 4: Run isolation and full test suite**

Run:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_no_repo_root_dependency.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

Expected: PASS. No `proyectos/` directory should appear in caller cwd when scripts are invoked by absolute path.

- [ ] **Step 5: Commit checkpoint**

```bash
git add .pi/skills/renovacion/scripts/run-project.sh .pi/skills/renovacion/tests/test_no_repo_root_dependency.py .pi/skills/renovacion/proyectos/1/resultados.json .pi/skills/renovacion/proyectos/1/spec.json .pi/skills/renovacion/proyectos/1/memoria.html .pi/skills/renovacion/proyectos/1/assets
git commit -m "test: verify renovacion skill is self-contained"
```

---

### Task 6: Final validation and scope audit

**Files:**
- Modify only files needed to fix review failures under `.pi/skills/renovacion/`.
- Do not modify `README.md`.

- [ ] **Step 1: Run complete skill validation**

Run:

```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

Expected: all PASS.

- [ ] **Step 2: Verify root README unchanged**

Run:

```bash
git diff -- README.md
```

Expected: no output.

- [ ] **Step 3: Verify generated outputs are skill-local**

Run:

```bash
find .pi/skills/renovacion/proyectos/1 -maxdepth 2 -type f | sort
```

Expected includes:

```text
.pi/skills/renovacion/proyectos/1/input.json
.pi/skills/renovacion/proyectos/1/resultados.json
.pi/skills/renovacion/proyectos/1/spec.json
.pi/skills/renovacion/proyectos/1/memoria.html
```

- [ ] **Step 4: Final commit checkpoint**

```bash
git status --short
git add .pi/skills/renovacion
git commit -m "feat: package renovacion as self-contained pi skill"
```

---

## Review Groups

### review-package

**Depends on:** Task 2

Reviewer must verify:
- `SKILL.md` frontmatter name exactly equals `renovacion` and description is present.
- Required resources are copied into `.pi/skills/renovacion/` and not referenced from root by docs/instructions.
- `SKILL.md` says all project artifacts stay under `proyectos/[id]/`.
- `SKILL.md` does not finalize README install instructions and does not promise PDF generation.

Commands:

```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_skill_structure.py
```

### review-python-wrappers

**Depends on:** Task 3

Reviewer must verify:
- `_skill_paths.py` computes `SKILL_ROOT` from script location.
- Non-numeric project ids are rejected.
- `run-calc.py` writes `proyectos/[id]/resultados.json` under skill root.
- `run-spec.py` uses package alias import for `lib/spec-engine` and writes `proyectos/[id]/spec.json` under skill root.

Commands:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_python_wrappers.py
```

### review-memory-wrapper

**Depends on:** Task 4

Reviewer must verify:
- `run-memory.sh` changes to `SKILL_ROOT` before invoking Node.
- Memory output is `.pi/skills/renovacion/proyectos/[id]/memoria.html` even when called from another cwd.
- HTML uses vendored KaTeX and has no CDN references.

Commands:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_memory_wrapper.py
```

### review-e2e-isolation

**Depends on:** Task 5

Reviewer must verify:
- A copied skill runs from a temp directory outside the repo.
- No caller-cwd `proyectos/` directory is created.
- `run-project.sh 1` completes calc → spec → memory.

Commands:

```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_no_repo_root_dependency.py
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

## Validation Strategy

Primary gate:

```bash
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
bash .pi/skills/renovacion/scripts/run-project.sh 1
git diff -- README.md
```

Expected:
- validator exits 0
- all pytest tests pass
- smoke script exits 0
- README diff empty

## Rollback or Mitigation Notes

- If copied resources are too large/noisy, keep required runtime resources and golden fixture only; do not remove any file required by tests or wrappers.
- If `run-spec.py` import alias fails, debug with `python -c` inside skill root; do not rename `lib/spec-engine` in this change.
- If memory rendering writes outside skill root, fix `run-memory.sh` first by ensuring `cd "$SKILL_ROOT"` happens before Node starts.
- If network-dependent logo behavior flakes, rely on committed `proyectos/1/assets/` fixture and existing placeholder behavior; do not add new network requirements.
- If root and skill copies drift during implementation, recopy from root once, rerun tests, then avoid modifying engines unless a wrapper cannot solve the issue.

## Handoff Instructions for Builders

- Follow TDD order: write/run failing tests before adding each wrapper or resource group.
- Keep production changes inside `.pi/skills/renovacion/` only.
- Do not edit root `README.md`.
- Do not redesign engines; add wrappers/path helpers only.
- Use numeric project ids only and preserve `proyectos/[id]/` convention.
- Commit at each checkpoint shown above.
