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
