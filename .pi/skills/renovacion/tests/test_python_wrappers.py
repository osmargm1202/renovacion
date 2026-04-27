import json
import os
import shutil
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
    result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "1"], cwd=SKILL_ROOT.parent
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == 1
    assert data["summary"]["total_required_m3_h"] > 0
    assert "equipment_results" not in data
    assert "equipment_count" not in data["summary"]
    assert all("linked_equipment_ids" not in area for area in data["area_results"])
    if before is not None:
        assert (
            json.loads(output.read_text(encoding="utf-8"))["project"][
                "calculation_status"
            ]
            == "completed"
        )


def test_run_spec_writes_spec_under_skill_project():
    calc_result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "1"], cwd=SKILL_ROOT.parent
    )
    assert calc_result.returncode == 0, calc_result.stdout + calc_result.stderr
    results_data = json.loads(
        (SKILL_ROOT / "proyectos/1/resultados.json").read_text(encoding="utf-8")
    )
    assert "equipment_results" not in results_data

    result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-spec.py"), "1"], cwd=SKILL_ROOT.parent
    )
    assert result.returncode == 0, result.stdout + result.stderr
    output = SKILL_ROOT / "proyectos/1/spec.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == 1
    assert data["project"]["spec_status"] == "completed"
    assert data["summary"] == {
        "equipment_count": 0,
        "selected_models_count": 0,
        "failed_selections_count": 0,
    }
    assert data["equipment_specs"] == []


def test_run_spec_selects_model_for_temp_project_with_manual_equipment():
    project_path = SKILL_ROOT / "proyectos/991"
    if project_path.exists():
        shutil.rmtree(project_path)
    project_path.mkdir(parents=True)

    input_data = json.loads(
        (SKILL_ROOT / "proyectos/1/input.json").read_text(encoding="utf-8")
    )
    input_data["project"]["id"] = 991
    input_data["project"]["name"] = "Manual Spec Wrapper"
    input_data["areas"][0]["extractor_type"] = "sencillo"
    input_data["areas"][0]["equipment_ids"] = ["E1"]
    input_data["equipment"] = [
        {
            "id": "E1",
            "alias": "Extractor principal",
            "kind": "extractor",
            "serves_area_ids": ["EX1"],
            "installation_type": None,
            "voltage": None,
            "frequency_hz": None,
        }
    ]
    (project_path / "input.json").write_text(
        json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    try:
        calc_result = run_cmd(
            ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "991"],
            cwd=SKILL_ROOT.parent,
        )
        assert calc_result.returncode == 0, calc_result.stdout + calc_result.stderr
        assert (project_path / "resultados.json").exists()

        result = run_cmd(
            ["python", str(SKILL_ROOT / "scripts/run-spec.py"), "991"],
            cwd=SKILL_ROOT.parent,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        output = project_path / "spec.json"
        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert data["project"]["id"] == 991
        assert data["project"]["spec_status"] == "completed"
        assert data["summary"] == {
            "equipment_count": 1,
            "selected_models_count": 1,
            "failed_selections_count": 0,
        }
        equipment_spec = data["equipment_specs"][0]
        assert equipment_spec["equipment_id"] == "E1"
        assert equipment_spec["selection_status"] == "selected"
        selected = equipment_spec["selected_model"]
        assert selected["brand"]
        assert selected["model"]
        assert selected["extractor_type"] == "sencillo"
        assert selected["source_url"]
    finally:
        shutil.rmtree(project_path, ignore_errors=True)


def test_wrappers_reject_non_numeric_project_ids():
    result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "../1"], cwd=SKILL_ROOT
    )
    assert result.returncode != 0
    assert "Project id must be numeric" in (result.stdout + result.stderr)
