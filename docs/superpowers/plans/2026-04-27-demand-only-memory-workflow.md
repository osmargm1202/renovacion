# Demand-Only Memory Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Renovacion default workflow generate calculation results and a demand-only HTML memory without requiring or rendering equipment specification output.

**Architecture:** Keep the calculation engine as the upstream producer of `resultados.json`, keep `run-spec.py` and `lib/spec-engine/` available for future/manual equipment work, and disconnect the default project and memory workflow from `spec.json`. The memory engine will load only `input.json` and `resultados.json`, stage only project/logos assets, render calculation sections plus a final `Resumen de Necesidad por Área`, and omit `Selección de Equipos` from the document and index.

**Tech Stack:** Python 3.13, pytest, Bash wrappers, Node.js CommonJS memory engine, Markdown contracts.

---

## File Map

- Create `.pi/skills/renovacion/tests/test_demand_only_workflow.py`: RED/GREEN integration tests proving `run-memory.sh` and `run-project.sh` do not require or create `spec.json`, memory output has demand summary, and visible equipment selection is absent.
- Create `.pi/skills/renovacion/tests/test_demand_docs_contract.py`: RED/GREEN documentation tests for AGENTS, SKILL, and memory contracts.
- Create `.pi/skills/renovacion/lib/memory-engine/sections/resumen-necesidad-area.js`: final memory section renderer for per-area required m3/h plus CFM.
- Modify `.pi/skills/renovacion/scripts/run-project.sh`: run calc then memory only; do not invoke `run-spec.py`; validate `input.json`, `resultados.json`, and `memoria.html` only; remove equipment text smoke checks.
- Modify `.pi/skills/renovacion/scripts/run-memory.sh`: require only `input.json` and `resultados.json`; do not require `spec.json`.
- Modify `.pi/skills/renovacion/lib/memory-engine/index.js`: do not load `spec.json`; do not call equipment selection renderer; call the new demand summary renderer before `fin`.
- Modify `.pi/skills/renovacion/lib/memory-engine/assets.js`: make default `stageAll()` accept `inputData` only and stage logos/placeholders only for memory.
- Modify `.pi/skills/renovacion/lib/memory-engine/sections/indice.js`: replace `Selección de Equipos` entry with `Resumen de Necesidad por Área`.
- Modify `.pi/skills/renovacion/tests/test_memory_wrapper.py`: update smoke expectations to demand-only memory.
- Modify `.pi/skills/renovacion/tests/test_no_repo_root_dependency.py`: update isolated copy smoke expectations to calc + memory only.
- Modify `.pi/skills/renovacion/tests/test_skill_structure.py`: remove `proyectos/1/spec.json` as a required default fixture artifact while keeping `run-spec.py`, `docs/contracts/spec-json.md`, and `lib/spec-engine/` required for future use.
- Modify `.pi/skills/renovacion/tests/test_agents_contract.py`: update operator/default workflow expectations to calc + memory only.
- Modify `AGENTS.md`: remove default operator/client `run-spec` instructions and `spec.json` reporting from operator/default workflow; state spec engine remains available for future/manual use.
- Modify `.pi/skills/renovacion/SKILL.md`: describe demand-only default workflow; keep `run-spec.py` as optional future/manual command, not default.
- Modify `.pi/skills/renovacion/docs/contracts/memoria-html.md`: update memory contract to require only `input.json` and `resultados.json`, include demand summary, and exclude visible equipment selection.
- Modify `.pi/skills/renovacion/docs/contracts/memory-assets.md`: remove default memory dependency on `spec.json` equipment images; document logo/project assets only for demand memory.
- Preserve `.pi/skills/renovacion/scripts/run-spec.py`, `.pi/skills/renovacion/lib/spec-engine/`, `.pi/skills/renovacion/docs/contracts/spec-json.md`, and `.pi/skills/renovacion/proyectos/1/spec.json` if present.

## Constraints

- Use RED → GREEN → REFACTOR for each behavior change.
- Do not modify `agents/pdd-orgm/*`.
- Do not modify `/home/osmarg/.pi/agent/git/github.com/obra/superpowers/skills/*`.
- Do not delete or weaken `run-spec.py` or `.pi/skills/renovacion/lib/spec-engine/`; they remain future/manual capability.
- Do not require `spec.json` in `run-project.sh`, `run-memory.sh`, docs, SKILL default workflow, or memory engine.
- Do not render `Selección de Equipos` in generated `memoria.html` or the index.
- Preserve `.pi/skills/renovacion/proyectos/[id]/` convention and never write Renovacion artifacts outside it.
- Commit examples are implementation-phase suggestions; planner phase must not commit.

## Task 0: Baseline and Safety

**Files:**
- Read-only check: repository state and required paths.

- [ ] **Step 0.1: Verify planner/implementation starting state**

Run:
```bash
git status --short
python .pi/skills/renovacion/scripts/validate-skill-structure.py
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
```

Expected:
```text
?? .pi-lens/
...
```
Validator exits `0`. Existing tests pass before edits, or any pre-existing failure is recorded before changing files.

- [ ] **Step 0.2: Verify forbidden paths are not edited by this plan**

Run:
```bash
test ! -d agents/pdd-orgm || git status --short -- agents/pdd-orgm
git -C /home/osmarg/.pi/agent/git/github.com/obra/superpowers status --short -- skills || true
```

Expected: no tracked modifications listed for either forbidden path.

## Task 1: RED runtime tests for demand-only workflow

**Files:**
- Create: `.pi/skills/renovacion/tests/test_demand_only_workflow.py`

- [ ] **Step 1.1: Create failing demand-only runtime tests**

Write `.pi/skills/renovacion/tests/test_demand_only_workflow.py`:

```python
import os
import shutil
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], cwd: Path):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, env=env, timeout=60)


def make_project(project_id: str, *, include_resultados: bool) -> Path:
    project = SKILL_ROOT / "proyectos" / project_id
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copy2(SKILL_ROOT / "proyectos/1/input.json", project / "input.json")
    if include_resultados:
        shutil.copy2(SKILL_ROOT / "proyectos/1/resultados.json", project / "resultados.json")
    spec = project / "spec.json"
    if spec.exists():
        spec.unlink()
    return project


def read_html(project: Path) -> str:
    return (project / "memoria.html").read_text(encoding="utf-8")


def test_run_memory_requires_input_and_resultados_only_not_spec(tmp_path):
    project = make_project("991", include_resultados=True)
    try:
        result = run_cmd(["bash", str(SKILL_ROOT / "scripts/run-memory.sh"), "991"], cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert (project / "memoria.html").exists()
        assert not (project / "spec.json").exists()
        html = read_html(project)
        assert "AURORA GMR" in html
        assert "Resumen de Necesidad por Área" in html
        assert "129.60 m3/h" in html
        assert "76.28 CFM" in html
        assert "Selección de Equipos" not in html
        assert "#seleccion-equipos" not in html
    finally:
        shutil.rmtree(project, ignore_errors=True)


def test_run_project_runs_calc_then_memory_only_and_does_not_create_spec(tmp_path):
    project = make_project("992", include_resultados=False)
    try:
        result = run_cmd(["bash", str(SKILL_ROOT / "scripts/run-project.sh"), "992"], cwd=tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert (project / "input.json").exists()
        assert (project / "resultados.json").exists()
        assert (project / "memoria.html").exists()
        assert not (project / "spec.json").exists()
        combined = result.stdout + result.stderr
        assert "run-spec" not in combined
        html = read_html(project)
        assert "Resumen de Necesidad por Área" in html
        assert "Selección de Equipos" not in html
        assert "80F / GreenBuilder" not in html
        assert "Delta Breez" not in html
    finally:
        shutil.rmtree(project, ignore_errors=True)


def test_run_spec_script_and_spec_engine_remain_available_for_future():
    assert (SKILL_ROOT / "scripts/run-spec.py").exists()
    assert (SKILL_ROOT / "lib/spec-engine/runner.py").exists()
    assert (SKILL_ROOT / "docs/contracts/spec-json.md").exists()
```

- [ ] **Step 1.2: Run RED tests**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_demand_only_workflow.py
```

Expected:
```text
FAILED .pi/skills/renovacion/tests/test_demand_only_workflow.py::test_run_memory_requires_input_and_resultados_only_not_spec
FAILED .pi/skills/renovacion/tests/test_demand_only_workflow.py::test_run_project_runs_calc_then_memory_only_and_does_not_create_spec
```
Failure reasons include current `run-memory.sh` requiring `spec.json`, current `run-project.sh` invoking `run-spec.py`, or current memory output containing `Selección de Equipos`.

## Task 2: GREEN wrapper scripts for calc + memory only

**Files:**
- Modify: `.pi/skills/renovacion/scripts/run-memory.sh`
- Modify: `.pi/skills/renovacion/scripts/run-project.sh`

- [ ] **Step 2.1: Replace `run-memory.sh` with input/resultados-only gate**

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

node lib/memory-engine/runner.js "$PROJECT_ID" "$PROJECT_PATH"
```

- [ ] **Step 2.2: Replace `run-project.sh` with calc + memory smoke**

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
echo "Workflow: calc -> memory"

python scripts/run-calc.py "$PROJECT_ID"
bash scripts/run-memory.sh "$PROJECT_ID"

for file in input.json resultados.json memoria.html; do
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

if ! grep -q "Resumen de Necesidad por Área" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html missing Resumen de Necesidad por Área" >&2
  exit 1
fi

if grep -q "Selección de Equipos" "${PROJECT_PATH}/memoria.html"; then
  echo "memoria.html contains Selección de Equipos" >&2
  exit 1
fi

echo "OK: ${PROJECT_PATH}"
```

- [ ] **Step 2.3: Run demand tests after wrapper changes**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_demand_only_workflow.py
```

Expected: still fails because `.pi/skills/renovacion/lib/memory-engine/index.js` still loads `spec.json` and renders equipment selection.

## Task 3: GREEN memory engine no spec load, no equipment section, final demand summary

**Files:**
- Create: `.pi/skills/renovacion/lib/memory-engine/sections/resumen-necesidad-area.js`
- Modify: `.pi/skills/renovacion/lib/memory-engine/index.js`
- Modify: `.pi/skills/renovacion/lib/memory-engine/assets.js`
- Modify: `.pi/skills/renovacion/lib/memory-engine/sections/indice.js`

- [ ] **Step 3.1: Add final demand summary section renderer**

Write `.pi/skills/renovacion/lib/memory-engine/sections/resumen-necesidad-area.js`:

```javascript
/**
 * Resumen de Necesidad por Área Section Renderer
 */

function m3hToCfm(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return null;
  return Number((Number(value) * 0.5885777702).toFixed(2));
}

function numberOrNull(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return null;
  return Number(value);
}

function formatM3h(value) {
  const numeric = numberOrNull(value);
  if (numeric === null) return 'N/A';
  return `${numeric.toFixed(2)} m3/h`;
}

function formatCfm(m3h, cfm) {
  const explicit = numberOrNull(cfm);
  const converted = explicit === null ? m3hToCfm(m3h) : explicit;
  if (converted === null) return 'N/A';
  return `${converted.toFixed(2)} CFM`;
}

function renderRows(areaResults) {
  if (!areaResults || areaResults.length === 0) {
    return `
      <tr>
        <td colspan="5" class="text-center">No hay áreas calculadas.</td>
      </tr>
    `;
  }

  return areaResults.map(area => {
    const requiredM3h = area.required_m3_h_final;
    const requiredCfm = area.required_cfm_final;
    const governing = {
      rh: 'Renovaciones por hora (RH)',
      people: 'Personas',
      tie: 'Empate'
    }[area.governing_method] || 'N/A';

    return `
      <tr>
        <td class="text-left">${area.area_id || 'N/A'}</td>
        <td class="text-left">${area.area_alias || 'N/A'}</td>
        <td class="text-left">${governing}</td>
        <td class="text-right"><strong>${formatM3h(requiredM3h)}</strong></td>
        <td class="text-right"><strong>${formatCfm(requiredM3h, requiredCfm)}</strong></td>
      </tr>
    `;
  }).join('');
}

function renderResumenNecesidadArea(resultadosData) {
  const areaResults = resultadosData.area_results || [];

  return `
<div id="resumen-necesidad-area" class="page">
  <h1>Resumen de Necesidad por Área</h1>
  <p>
    Esta sección consolida la demanda de renovación de aire requerida por área.
    Los valores provienen exclusivamente de <code>resultados.json</code> y expresan
    el caudal final requerido en m3/h y CFM.
  </p>

  <table class="equipment-alternatives-table">
    <thead>
      <tr>
        <th class="text-left">Área</th>
        <th class="text-left">Nombre</th>
        <th class="text-left">Método gobernante</th>
        <th class="text-right">Requerido (m3/h)</th>
        <th class="text-right">Requerido (CFM)</th>
      </tr>
    </thead>
    <tbody>
      ${renderRows(areaResults)}
    </tbody>
  </table>

  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

module.exports = { renderResumenNecesidadArea, formatM3h, formatCfm };
```

- [ ] **Step 3.2: Replace index renderer entries**

Write `.pi/skills/renovacion/lib/memory-engine/sections/indice.js`:

```javascript
/**
 * Índice (Table of Contents) Section Renderer
 */

function renderIndice() {
  const sections = [
    { number: '1', title: 'Portada', anchor: 'portada' },
    { number: '2', title: 'Índice', anchor: 'indice' },
    { number: '3', title: 'Teoría de Cálculo', anchor: 'teoria-calculo' },
    { number: '4', title: 'Resultados de Cálculo', anchor: 'resultados-calculo' },
    { number: '5', title: 'Resumen de Necesidad por Área', anchor: 'resumen-necesidad-area' },
    { number: '6', title: 'Fin del Documento', anchor: 'fin' }
  ];

  const items = sections.map(s => `
    <li class="indice-item">
      <span class="section-number">${s.number}.</span>
      <a href="#${s.anchor}">${s.title}</a>
    </li>
  `).join('');

  return `
<div id="indice" class="page">
  <div class="indice">
    <h1 class="indice-titulo">Índice</h1>
    <ul class="indice-list">
      ${items}
    </ul>
  </div>
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

module.exports = { renderIndice };
```

- [ ] **Step 3.3: Replace `assets.js` `stageAll()` method only**

In `.pi/skills/renovacion/lib/memory-engine/assets.js`, replace the existing `stageAll(inputData, specData)` method with this exact method:

```javascript
  /**
   * Stage all assets required by demand-only memory.
   */
  async stageAll(inputData) {
    await this.init();

    const stagedAssets = {
      logo_empresa: null,
      logo_cliente: null,
      equipment: []
    };

    if (inputData.project) {
      stagedAssets.logo_empresa = await this.resolveLogo(
        inputData.project.logo_empresa,
        'empresa'
      );
      stagedAssets.logo_cliente = await this.resolveLogo(
        inputData.project.logo_cliente,
        'cliente'
      );
    }

    return stagedAssets;
  }
```

- [ ] **Step 3.4: Replace `index.js` with demand-only orchestration**

Write `.pi/skills/renovacion/lib/memory-engine/index.js`:

```javascript
/**
 * Memory Engine - Main Renderer
 * Orchestrates demanda-only memoria.html generation
 */

const fs = require('fs').promises;
const path = require('path');
const { AssetManager } = require('./assets');
const { getKaTeXIncludes } = require('./formula');
const { renderPortada } = require('./sections/portada');
const { renderIndice } = require('./sections/indice');
const { renderTeoriaCalculo } = require('./sections/teoria-calculo');
const { renderResultadosCalculo } = require('./sections/resultados-calculo');
const { renderResumenNecesidadArea } = require('./sections/resumen-necesidad-area');
const { renderFin } = require('./sections/fin');

class MemoryEngine {
  constructor(projectId, projectPath) {
    this.projectId = projectId;
    this.projectPath = projectPath;
    this.assetManager = new AssetManager(projectId, projectPath);
  }

  async loadJSON(filePath) {
    const content = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  }

  async loadCSS() {
    const cssPath = path.join(__dirname, '../../assets/css');
    const memoriaCSS = await fs.readFile(path.join(cssPath, 'memoria.css'), 'utf-8');
    const sectionsCSS = await fs.readFile(path.join(cssPath, 'memoria-sections.css'), 'utf-8');
    return `${memoriaCSS}\n\n${sectionsCSS}`;
  }

  async generate() {
    try {
      const inputPath = path.join(this.projectPath, 'input.json');
      const resultadosPath = path.join(this.projectPath, 'resultados.json');

      const inputData = await this.loadJSON(inputPath);
      const resultadosData = await this.loadJSON(resultadosPath);

      const stagedAssets = await this.assetManager.stageAll(inputData);
      const css = await this.loadCSS();

      const portada = renderPortada(inputData.project, stagedAssets);
      const indice = renderIndice();
      const teoriaCalculo = renderTeoriaCalculo(resultadosData.calculation_trace);
      const resultadosCalculo = renderResultadosCalculo(resultadosData);
      const resumenNecesidadArea = renderResumenNecesidadArea(resultadosData);
      const fin = renderFin(inputData.project);

      const html = this.assembleHTML({
        project: inputData.project,
        css,
        sections: {
          portada,
          indice,
          teoriaCalculo,
          resultadosCalculo,
          resumenNecesidadArea,
          fin
        }
      });

      const outputPath = path.join(this.projectPath, 'memoria.html');
      await fs.writeFile(outputPath, html, 'utf-8');

      return {
        status: 'completed',
        output_path: outputPath,
        warnings: this.assetManager.getWarnings()
      };
    } catch (err) {
      return {
        status: 'failed',
        error: err.message,
        stack: err.stack
      };
    }
  }

  assembleHTML({ project, css, sections }) {
    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Memoria de Cálculo - ${project.name}</title>
  
  <!-- KaTeX -->
  ${getKaTeXIncludes()}
  
  <!-- Embedded CSS -->
  <style>
${css}
  </style>
</head>
<body>
  <!-- PORTADA -->
  ${sections.portada}
  
  <!-- ÍNDICE -->
  ${sections.indice}
  
  <!-- TEORÍA DE CÁLCULO -->
  ${sections.teoriaCalculo}
  
  <!-- RESULTADOS DE CÁLCULO -->
  ${sections.resultadosCalculo}
  
  <!-- RESUMEN DE NECESIDAD POR ÁREA -->
  ${sections.resumenNecesidadArea}
  
  <!-- FIN -->
  ${sections.fin}
</body>
</html>
`;
  }
}

async function generateMemoria(projectId, projectPath) {
  const engine = new MemoryEngine(projectId, projectPath);
  return await engine.generate();
}

module.exports = {
  MemoryEngine,
  generateMemoria
};
```

- [ ] **Step 3.5: Run GREEN demand runtime tests**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_demand_only_workflow.py
```

Expected:
```text
3 passed
```

## Task 4: RED docs and existing tests for default workflow contract

**Files:**
- Create: `.pi/skills/renovacion/tests/test_demand_docs_contract.py`
- Modify later: `.pi/skills/renovacion/tests/test_agents_contract.py`

- [ ] **Step 4.1: Create failing docs contract tests**

Write `.pi/skills/renovacion/tests/test_demand_docs_contract.py`:

```python
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_default_workflow_is_calc_memory_only():
    skill = text(SKILL_ROOT / "SKILL.md")
    assert "demand-only" in skill.lower() or "solo demanda" in skill.lower()
    assert "calc → memory" in skill or "calc -> memory" in skill
    assert "Run `python scripts/run-spec.py [id]` to write `proyectos/[id]/spec.json`" not in skill
    assert "Run `bash scripts/run-memory.sh [id]` to write `proyectos/[id]/memoria.html`" in skill
    assert "run-spec.py" in skill
    assert "future/manual" in skill.lower() or "manual/future" in skill.lower()


def test_root_agents_operator_default_workflow_omits_run_spec_and_spec_report():
    agents = text(REPO_ROOT / "AGENTS.md")
    operator_section = agents.split("## Operator mode", 1)[1].split("## Client calculation workflow", 1)[0]
    client_section = agents.split("## Client calculation workflow", 1)[1]
    assert ".pi/skills/renovacion/scripts/run-calc.py [id]" in operator_section
    assert ".pi/skills/renovacion/scripts/run-memory.sh [id]" in operator_section
    assert ".pi/skills/renovacion/scripts/run-spec.py [id]" not in operator_section
    assert ".pi/skills/renovacion/proyectos/[id]/spec.json" not in operator_section
    assert "Run calc, then memory" in client_section
    assert "run-spec.py [id]" not in client_section
    assert "spec.json" not in client_section
    assert "Spec engine remains available" in agents


def test_memory_contract_requires_results_not_spec_and_has_demand_summary():
    contract = text(SKILL_ROOT / "docs/contracts/memoria-html.md")
    assert "input.json" in contract
    assert "resultados.json" in contract
    assert "spec.json" not in contract
    assert "resumen-necesidad-area" in contract
    assert "Resumen de Necesidad por Área" in contract
    assert "seleccion-equipos" not in contract
    assert "Selección de equipos" not in contract


def test_memory_assets_contract_has_no_spec_equipment_dependency():
    contract = text(SKILL_ROOT / "docs/contracts/memory-assets.md")
    assert "demand-only" in contract.lower() or "solo demanda" in contract.lower()
    assert "spec.json" not in contract
    assert "equipment_specs" not in contract
    assert "HTML final sin URLs externas" in contract
```

- [ ] **Step 4.2: Run RED docs tests plus existing agent contract**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests/test_demand_docs_contract.py .pi/skills/renovacion/tests/test_agents_contract.py
```

Expected: failures because current AGENTS/SKILL/contracts still describe default `run-spec.py`, `spec.json`, and equipment selection.

## Task 5: GREEN docs, SKILL, AGENTS, and existing test expectations

**Files:**
- Modify: `AGENTS.md`
- Modify: `.pi/skills/renovacion/SKILL.md`
- Modify: `.pi/skills/renovacion/docs/contracts/memoria-html.md`
- Modify: `.pi/skills/renovacion/docs/contracts/memory-assets.md`
- Modify: `.pi/skills/renovacion/tests/test_agents_contract.py`
- Modify: `.pi/skills/renovacion/tests/test_memory_wrapper.py`
- Modify: `.pi/skills/renovacion/tests/test_no_repo_root_dependency.py`
- Modify: `.pi/skills/renovacion/tests/test_skill_structure.py`

- [ ] **Step 5.1: Replace root AGENTS default workflow text**

Write `AGENTS.md`:

```markdown
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
- Review top-level keys `project`, `validation`, `areas`, `equipment`, `defaults_applied`.
- Update `.pi/skills/renovacion/proyectos/[id]/input.json` with collected client data.
- Run `python .pi/skills/renovacion/scripts/run-calc.py [id]`.
- Run `bash .pi/skills/renovacion/scripts/run-memory.sh [id]`.
- Report outputs from `.pi/skills/renovacion/proyectos/[id]/resultados.json` and `.pi/skills/renovacion/proyectos/[id]/memoria.html`.

Spec engine remains available for future/manual equipment specification through `.pi/skills/renovacion/scripts/run-spec.py`, but it is not part of the default operator workflow.

## Client calculation workflow

1. Start from `.pi/skills/renovacion/proyectos/[id]/input.json`.
2. If client information is missing, ask one focused question at a time and align answers to `.pi/skills/renovacion/docs/contracts/input-json.md`.
3. Fill required data under top-level keys `project`, `validation`, `areas`, `equipment`, `defaults_applied`.
4. Update `.pi/skills/renovacion/proyectos/[id]/input.json`.
5. Run calc, then memory.
6. Report outputs and file locations for `.pi/skills/renovacion/proyectos/[id]/resultados.json` and `.pi/skills/renovacion/proyectos/[id]/memoria.html`.
```

- [ ] **Step 5.2: Replace Renovacion SKILL default workflow**

Write `.pi/skills/renovacion/SKILL.md`:

```markdown
---
name: renovacion
description: Run the Renovacion airflow calculation and demand-only HTML memory workflow from a self-contained project skill.
---

# Renovacion Skill

Use this skill for Renovacion ventilation projects.

## Project file rule

All default project files must live under this skill directory using:

```text
proyectos/[id]/
  input.json
  resultados.json
  memoria.html
  assets/
```

Never create or save Renovacion project artifacts outside `proyectos/[id]/` relative to this skill root.

`spec.json` may exist for future/manual equipment specification, but demand-only memory generation does not require it.

## Local commands

From this skill root, run:

```bash
uv run pytest -q tests
bash scripts/run-project.sh 1
```

From any other working directory, run the scripts by path. They compute `SKILL_ROOT` from their own location and still write under this skill's `proyectos/[id]/`.

## Default workflow

1. Keep or create `proyectos/[id]/input.json`.
2. Run `python scripts/run-calc.py [id]` to write `proyectos/[id]/resultados.json`.
3. Run `bash scripts/run-memory.sh [id]` to write `proyectos/[id]/memoria.html`.
4. Or run `bash scripts/run-project.sh [id]` for calc → memory.

## Future/manual equipment specification

`python scripts/run-spec.py [id]` remains available for future/manual equipment selection and writes `proyectos/[id]/spec.json` when explicitly requested. Default memory output does not load or render that artifact.

## Scope notes

This skill includes local engines, rules, contracts, CSS, vendored KaTeX, catalog images, examples, and the `proyectos/1` smoke fixture. PDF output and final install instructions are out of scope for this change.
```

- [ ] **Step 5.3: Replace memory HTML contract**

Write `.pi/skills/renovacion/docs/contracts/memoria-html.md`:

```markdown
# Contract: memoria.html

## Purpose

Memoria HTML final de cálculo y necesidad de renovación de aire por área. Este contrato es demand-only: documenta demanda calculada, no selección comercial de equipos.

## Location

`.pi/skills/renovacion/proyectos/[id]/memoria.html`

## Inputs required

- `input.json`
- `resultados.json`
- `assets/` del proyecto

## Required sections

1. `portada`
2. `indice`
3. `teoria-calculo`
4. `resultados-calculo`
5. `resumen-necesidad-area`
6. `fin`

## Resumen de Necesidad por Área

Contenido requerido por área:

- id de área
- alias de área
- método gobernante
- caudal requerido final en `m3/h`
- caudal requerido final en `CFM`

Salida visible esperada:

- título `Resumen de Necesidad por Área`
- tabla o bloque equivalente con valores por área
- para AURORA GMR área A1: `129.60 m3/h` y `76.28 CFM`

## Content exclusions

Default memory output must not show:

- `Selección de Equipos`
- fichas comerciales de equipos
- modelo seleccionado
- alternativas comerciales
- datos eléctricos de equipos comerciales

## Asset policy

- usar assets locales del proyecto
- sin CDN ni URLs externas en HTML final
- fórmulas usan KaTeX vendorizado local

## Expected output for AURORA GMR project 1

### Resultados

- área A1: Baño principal
- RH: `129.6 m³/h`

### Resumen demand-only

- área A1: Baño principal
- requerido: `129.60 m3/h`
- requerido: `76.28 CFM`
- no aparece `Selección de Equipos`
```

- [ ] **Step 5.4: Replace memory assets contract**

Write `.pi/skills/renovacion/docs/contracts/memory-assets.md`:

```markdown
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
<img src="assets/logos/empresa-orgm.png" alt="Logo empresa">
```

Ejemplo logo cliente:

```html
<img src="assets/logos/cliente-bohc.png" alt="Logo cliente">
```
```

- [ ] **Step 5.5: Replace relevant `test_agents_contract.py` function**

In `.pi/skills/renovacion/tests/test_agents_contract.py`, replace `test_false_mode_is_operator_only_runs_pipeline_and_reports_outputs()` with:

```python
def test_false_mode_is_operator_only_runs_pipeline_and_reports_outputs():
    text = read_agents()
    lowered = text.lower()
    assert "developer_mode = false" in text
    assert "operator-only" in lowered
    assert ".pi/skills/renovacion/proyectos/[id]/input.json" in text
    assert ".pi/skills/renovacion/scripts/run-calc.py [id]" in text
    assert ".pi/skills/renovacion/scripts/run-memory.sh [id]" in text
    operator_section = text.split("## Operator mode", 1)[1].split("## Client calculation workflow", 1)[0]
    client_section = text.split("## Client calculation workflow", 1)[1]
    assert ".pi/skills/renovacion/scripts/run-spec.py [id]" not in operator_section
    assert ".pi/skills/renovacion/proyectos/[id]/spec.json" not in operator_section
    assert "run-spec.py [id]" not in client_section
    assert "spec.json" not in client_section
    assert ".pi/skills/renovacion/proyectos/[id]/resultados.json" in text
    assert ".pi/skills/renovacion/proyectos/[id]/memoria.html" in text
    assert "report outputs" in lowered
    assert "Spec engine remains available" in text
```

- [ ] **Step 5.6: Replace memory wrapper smoke test expectations**

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
    assert "Resumen de Necesidad por Área" in html
    assert "129.60 m3/h" in html
    assert "76.28 CFM" in html
    assert "Selección de Equipos" not in html
    assert "80F / GreenBuilder" not in html
    assert "Delta Breez" not in html
    assert "assets/vendor/katex" in html
    assert "cdn.jsdelivr" not in html.lower()
    assert not (tmp_path / "proyectos" / "1" / "memoria.html").exists()
```

- [ ] **Step 5.7: Replace no-root-dependency smoke expectations**

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

    project = copied_skill / "proyectos/1"
    spec = project / "spec.json"
    if spec.exists():
        spec.unlink()

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
    assert (copied_skill / "proyectos/1/memoria.html").exists()
    assert not (copied_skill / "proyectos/1/spec.json").exists()
    assert not (outside_cwd / "proyectos").exists()
    html = (copied_skill / "proyectos/1/memoria.html").read_text(encoding="utf-8")
    assert "AURORA GMR" in html
    assert "Resumen de Necesidad por Área" in html
    assert "129.60 m3/h" in html
    assert "76.28 CFM" in html
    assert "Selección de Equipos" not in html
    assert "80F / GreenBuilder" not in html
    assert "cdn.jsdelivr" not in html.lower()
```

- [ ] **Step 5.8: Replace required resource list in `test_skill_structure.py`**

In `.pi/skills/renovacion/tests/test_skill_structure.py`, replace the `required_paths` list inside `test_required_runtime_resources_are_skill_local()` with:

```python
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
        "lib/memory-engine/sections/resumen-necesidad-area.js",
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
        "proyectos/1/memoria.html",
    ]
```

- [ ] **Step 5.9: Run docs and updated tests GREEN**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q \
  .pi/skills/renovacion/tests/test_demand_docs_contract.py \
  .pi/skills/renovacion/tests/test_agents_contract.py \
  .pi/skills/renovacion/tests/test_memory_wrapper.py \
  .pi/skills/renovacion/tests/test_no_repo_root_dependency.py \
  .pi/skills/renovacion/tests/test_skill_structure.py
```

Expected:
```text
passed
```
All selected tests pass; pytest may print the exact count.

## Task 6: Full verification and refactor checks

**Files:**
- Generated by smoke: `.pi/skills/renovacion/proyectos/1/resultados.json`
- Generated by smoke: `.pi/skills/renovacion/proyectos/1/memoria.html`
- Preserved if present: `.pi/skills/renovacion/proyectos/1/spec.json`

- [ ] **Step 6.1: Run full skill test suite**

Run:
```bash
uv run --project .pi/skills/renovacion pytest -q .pi/skills/renovacion/tests
```

Expected:
```text
passed
```
No test requires `run-project.sh` or `run-memory.sh` to create/read `spec.json`.

- [ ] **Step 6.2: Run default project smoke**

Run:
```bash
bash .pi/skills/renovacion/scripts/run-project.sh 1
```

Expected:
```text
Renovacion skill smoke: project 1
Workflow: calc -> memory
...
OK: proyectos/1
```
No output line mentions `run-spec.py`.

- [ ] **Step 6.3: Verify generated memory has demand summary and no equipment selection**

Run:
```bash
grep -n "Resumen de Necesidad por Área" .pi/skills/renovacion/proyectos/1/memoria.html
grep -n "129.60 m3/h" .pi/skills/renovacion/proyectos/1/memoria.html
grep -n "76.28 CFM" .pi/skills/renovacion/proyectos/1/memoria.html
! grep -n "Selección de Equipos" .pi/skills/renovacion/proyectos/1/memoria.html
! grep -n "80F / GreenBuilder" .pi/skills/renovacion/proyectos/1/memoria.html
! grep -n "Delta Breez" .pi/skills/renovacion/proyectos/1/memoria.html
```

Expected: first three commands print matching lines; last three commands print nothing and exit `0` because `! grep` inverts the no-match status.

- [ ] **Step 6.4: Verify default docs no longer instruct run-spec in default workflow**

Run:
```bash
python - <<'PY'
from pathlib import Path
agents = Path('AGENTS.md').read_text(encoding='utf-8')
skill = Path('.pi/skills/renovacion/SKILL.md').read_text(encoding='utf-8')
operator = agents.split('## Operator mode', 1)[1].split('## Client calculation workflow', 1)[0]
client = agents.split('## Client calculation workflow', 1)[1]
default = skill.split('## Default workflow', 1)[1].split('## Future/manual equipment specification', 1)[0]
assert 'run-spec.py [id]' not in operator
assert 'spec.json' not in operator
assert 'run-spec.py [id]' not in client
assert 'spec.json' not in client
assert 'run-spec.py [id]' not in default
assert 'spec.json' not in default
print('OK: default docs are calc + memory only')
PY
```

Expected:
```text
OK: default docs are calc + memory only
```

- [ ] **Step 6.5: Verify spec engine remains available for future/manual use**

Run:
```bash
test -f .pi/skills/renovacion/scripts/run-spec.py
test -d .pi/skills/renovacion/lib/spec-engine
test -f .pi/skills/renovacion/docs/contracts/spec-json.md
echo "OK: spec engine preserved"
```

Expected:
```text
OK: spec engine preserved
```

- [ ] **Step 6.6: Verify forbidden paths remain untouched**

Run:
```bash
git status --short -- agents/pdd-orgm || true
git -C /home/osmarg/.pi/agent/git/github.com/obra/superpowers status --short -- skills || true
```

Expected: no modified files listed.

## Safety Proof Commands for Plan Artifact

Run after saving this plan:

```bash
grep -R "agents/pdd-orgm" docs/superpowers/plans/2026-04-27-demand-only-memory-workflow.md
grep -R "/home/osmarg/.pi/agent/git/github.com/obra/superpowers/skills/" docs/superpowers/plans/2026-04-27-demand-only-memory-workflow.md
python - <<'PY'
from pathlib import Path
plan = Path('docs/superpowers/plans/2026-04-27-demand-only-memory-workflow.md').read_text(encoding='utf-8')
for path in [
    'agents/pdd-orgm',
    '/home/osmarg/.pi/agent/git/github.com/obra/superpowers/skills/',
]:
    for verb in ['Create', 'Modify', 'Delete']:
        forbidden = verb + ': `' + path
        assert forbidden not in plan, forbidden
print('OK: no forbidden edit targets in plan')
PY
```

Expected: first two grep commands only show constraint/proof mentions; Python prints:

```text
OK: no forbidden edit targets in plan
```

## Self-Review Checklist

- [ ] Spec coverage: RED tests first, default calc + memory only, memory input/resultados only, no spec load, no equipment selection render, demand summary per area with m3/h + CFM, index updated, docs/AGENTS/SKILL updated, spec engine preserved, verification commands included.
- [ ] Placeholder scan: no unresolved implementation markers remain in this plan.
- [ ] Consistency: task names, paths, commands, and handoff contracts use the same demand-only workflow language.
- [ ] Safety: plan does not target forbidden paths for modification and keeps `.pi/skills/renovacion/proyectos/[id]/` convention.
