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


def make_cwd_project(tmp_path: Path, project_id: str, source_id: str = "1") -> Path:
    project = tmp_path / "proyectos" / project_id
    project.mkdir(parents=True)
    shutil.copy2(SKILL_ROOT / f"proyectos/{source_id}/input.json", project / "input.json")
    return project


def test_run_calc_writes_resultados_under_cwd_project(tmp_path):
    project = make_cwd_project(tmp_path, "1")
    output = project / "resultados.json"
    skill_output = SKILL_ROOT / "proyectos/1/resultados.json"
    before = skill_output.read_text(encoding="utf-8") if skill_output.exists() else None

    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-calc.py"), "1"], cwd=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == 1
    assert data["summary"]["total_required_m3_h"] > 0
    assert "equipment_results" not in data
    assert "equipment_count" not in data["summary"]
    assert all("linked_equipment_ids" not in area for area in data["area_results"])
    if before is not None:
        assert skill_output.read_text(encoding="utf-8") == before


def test_run_spec_writes_spec_under_cwd_project(tmp_path):
    project = make_cwd_project(tmp_path, "1")
    calc_result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-calc.py"), "1"], cwd=tmp_path)
    assert calc_result.returncode == 0, calc_result.stdout + calc_result.stderr
    results_data = json.loads((project / "resultados.json").read_text(encoding="utf-8"))
    assert "equipment_results" not in results_data

    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-spec.py"), "1"], cwd=tmp_path)

    assert result.returncode == 0, result.stdout + result.stderr
    output = project / "spec.json"
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


def test_run_spec_selects_model_for_temp_project_with_manual_equipment(tmp_path):
    project_path = make_cwd_project(tmp_path, "991")
    input_data = json.loads((project_path / "input.json").read_text(encoding="utf-8"))
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

    calc_result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-calc.py"), "991"], cwd=tmp_path)
    assert calc_result.returncode == 0, calc_result.stdout + calc_result.stderr
    assert (project_path / "resultados.json").exists()

    result = run_cmd(["python", str(SKILL_ROOT / "scripts/run-spec.py"), "991"], cwd=tmp_path)
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


def test_run_calc_accepts_slug_project_ids_under_cwd_projects(tmp_path):
    project_path = make_cwd_project(tmp_path, "miniso-pr")
    input_data = json.loads((project_path / "input.json").read_text(encoding="utf-8"))
    input_data["project"]["id"] = "miniso-pr"
    input_data["project"]["name"] = "MINISO PR"
    (project_path / "input.json").write_text(
        json.dumps(input_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "miniso-pr"],
        cwd=tmp_path,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    output = project_path / "resultados.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["project"]["id"] == "miniso-pr"


def test_wrappers_reject_path_traversal_project_ids(tmp_path):
    result = run_cmd(
        ["python", str(SKILL_ROOT / "scripts/run-calc.py"), "../1"], cwd=tmp_path
    )
    assert result.returncode != 0
    assert "Project id must contain only letters, numbers, dots, underscores, and hyphens" in (
        result.stdout + result.stderr
    )
