from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_default_workflow_is_calc_memory_only():
    skill = text(SKILL_ROOT / "SKILL.md")
    assert "demand-only" in skill.lower() or "solo demanda" in skill.lower()
    assert "calc → memory" in skill or "calc -> memory" in skill
    assert (
        "Run `python scripts/run-spec.py [id]` to write `proyectos/[id]/spec.json`"
        not in skill
    )
    assert (
        "Run `bash scripts/run-memory.sh [id]` to write `proyectos/[id]/memoria.html`"
        in skill
    )
    assert "run-spec.py" in skill
    assert "future/manual" in skill.lower() or "manual/future" in skill.lower()


def test_root_agents_operator_default_workflow_omits_run_spec_and_spec_report():
    agents = text(REPO_ROOT / "AGENTS.md")
    operator_section = agents.split("## Operator mode", 1)[1].split(
        "## Client calculation workflow", 1
    )[0]
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
