from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[2]
AGENTS_MD = REPO_ROOT / "AGENTS.md"


def read_agents() -> str:
    assert AGENTS_MD.exists(), f"Missing {AGENTS_MD.relative_to(REPO_ROOT)}"
    return AGENTS_MD.read_text(encoding="utf-8")


def test_root_agents_md_exists():
    assert AGENTS_MD.exists(), f"Missing {AGENTS_MD.relative_to(REPO_ROOT)}"


def test_agents_sets_manual_developer_mode_true():
    lines = read_agents().splitlines()
    assert "developer_mode = true" in lines


def test_agents_declares_skill_source_of_truth_and_project_artifact_path():
    text = read_agents()
    lowered = text.lower()
    assert ".pi/skills/renovacion/" in text
    assert "source of truth" in lowered
    assert ".pi/skills/renovacion/proyectos/[id]/" in text
    assert "preserve" in lowered


def test_true_mode_allows_skill_changes_with_tdd_red_green_refactor():
    text = read_agents()
    lowered = text.lower()
    assert "developer_mode = true" in text
    assert "red → green → refactor" in text or "red-green-refactor" in lowered
    assert "tdd" in lowered
    for required_path in [
        ".pi/skills/renovacion/assets/",
        ".pi/skills/renovacion/lib/",
        ".pi/skills/renovacion/lib/spec-engine/catalog/",
        ".pi/skills/renovacion/docs/",
        ".pi/skills/renovacion/tests/",
    ]:
        assert required_path in text
    assert "may modify" in lowered or "can modify" in lowered


def test_false_mode_is_operator_only_runs_pipeline_and_reports_outputs():
    text = read_agents()
    lowered = text.lower()
    assert "developer_mode = false" in text
    assert "operator-only" in lowered
    assert ".pi/skills/renovacion/proyectos/[id]/input.json" in text
    assert ".pi/skills/renovacion/scripts/run-calc.py [id]" in text
    assert ".pi/skills/renovacion/scripts/run-spec.py [id]" in text
    assert ".pi/skills/renovacion/scripts/run-memory.sh [id]" in text
    assert ".pi/skills/renovacion/proyectos/[id]/resultados.json" in text
    assert ".pi/skills/renovacion/proyectos/[id]/spec.json" in text
    assert ".pi/skills/renovacion/proyectos/[id]/memoria.html" in text
    assert "report outputs" in lowered


def test_false_mode_prohibits_modifying_skill_implementation_paths():
    text = read_agents()
    lowered = text.lower()
    assert "must not modify" in lowered or "do not modify" in lowered
    for required_path in [
        ".pi/skills/renovacion/assets/",
        ".pi/skills/renovacion/lib/",
        ".pi/skills/renovacion/lib/spec-engine/catalog/",
        ".pi/skills/renovacion/docs/",
        ".pi/skills/renovacion/tests/",
    ]:
        assert required_path in text


def test_missing_info_workflow_asks_one_question_uses_input_contract_and_mentions_top_level_keys():
    text = read_agents()
    lowered = text.lower()
    assert "one focused question at a time" in lowered
    assert ".pi/skills/renovacion/docs/contracts/input-json.md" in text
    assert "top-level keys" in lowered
    for key in ["project", "validation", "areas", "equipment", "defaults_applied"]:
        assert f"`{key}`" in text
