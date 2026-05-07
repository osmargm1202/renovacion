import json
import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], cwd: Path):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run(
        args, cwd=cwd, text=True, capture_output=True, env=env, timeout=60
    )


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text).replace("³", "3")
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def assert_area_summary(
    normalized_html: str, area_id: str, area_alias: str, m3_h: str, cfm: str
):
    pattern = (
        rf"{re.escape(normalize_text(area_id))}.*?"
        rf"{re.escape(normalize_text(area_alias))}.*?"
        rf"{re.escape(normalize_text(m3_h))}.*?"
        rf"{re.escape(normalize_text(cfm))}"
    )
    assert re.search(pattern, normalized_html, re.DOTALL), pattern


def assert_project_1_demand_only_values(html: str):
    normalized_html = normalize_text(html)
    assert "aurora gmr" in normalized_html
    assert "resumen de necesidad por area" in normalized_html
    assert "3,798.00 m3/h".lower() in normalized_html
    assert "2,235.42 cfm" in normalized_html
    assert_area_summary(normalized_html, "EX1", "BAÑO", "54.00 m3/h", "31.78 CFM")
    assert_area_summary(
        normalized_html,
        "EX2",
        "Almacén 2do Nivel",
        "292.50 m3/h",
        "172.16 CFM",
    )
    assert_area_summary(
        normalized_html,
        "EX3",
        "TALLER 2do NIVEL",
        "2,448.00 m3/h",
        "1,440.84 CFM",
    )
    assert_area_summary(
        normalized_html,
        "EX4",
        "TALLER 3er NIVEL",
        "936.00 m3/h",
        "550.91 CFM",
    )
    assert_area_summary(
        normalized_html,
        "EX5",
        "Almacén 3er Nivel",
        "67.50 m3/h",
        "39.73 CFM",
    )


def make_project(root: Path, project_id: str, *, include_resultados: bool) -> Path:
    project = root / "proyectos" / project_id
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copy2(SKILL_ROOT / "proyectos/1/input.json", project / "input.json")
    if include_resultados:
        shutil.copy2(
            SKILL_ROOT / "proyectos/1/resultados.json", project / "resultados.json"
        )
    return project


def read_html(project: Path) -> str:
    return (project / "memoria.html").read_text(encoding="utf-8")


def test_run_memory_requires_input_and_resultados_only_not_spec(tmp_path):
    project = make_project(tmp_path, "991", include_resultados=True)
    result = run_cmd(
        ["bash", str(SKILL_ROOT / "scripts/run-memory.sh"), "991"], cwd=tmp_path
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "memoria.html").exists()
    assert not (project / "spec.json").exists()
    html = read_html(project)
    assert_project_1_demand_only_values(html)
    assert "Selección de Equipos" not in html
    assert "#seleccion-equipos" not in html


def test_run_project_runs_calc_then_memory_only_and_does_not_create_spec(tmp_path):
    project = make_project(tmp_path, "992", include_resultados=False)
    result = run_cmd(
        ["bash", str(SKILL_ROOT / "scripts/run-project.sh"), "992"], cwd=tmp_path
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "input.json").exists()
    assert (project / "resultados.json").exists()
    assert (project / "memoria.html").exists()
    assert not (project / "spec.json").exists()
    combined = result.stdout + result.stderr
    assert "run-spec" not in combined
    html = read_html(project)
    assert_project_1_demand_only_values(html)
    assert "Equipos Requeridos" not in html
    assert "Selección de Equipos" not in html
    assert "80F / GreenBuilder" not in html
    assert "Delta Breez" not in html


def test_run_project_accepts_slug_ids_without_fixture_name_assumption(tmp_path):
    project = make_project(tmp_path, "miniso-pr", include_resultados=False)
    input_path = project / "input.json"
    data = json.loads(input_path.read_text(encoding="utf-8"))
    data["project"]["id"] = "miniso-pr"
    data["project"]["name"] = "MINISO PR"
    input_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    result = run_cmd(
        ["bash", str(SKILL_ROOT / "scripts/run-project.sh"), "miniso-pr"],
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "resultados.json").exists()
    assert (project / "memoria.html").exists()
    assert "MINISO PR" in read_html(project)


def test_run_spec_script_and_spec_engine_remain_available_for_future():
    assert (SKILL_ROOT / "scripts/run-spec.py").exists()
    assert (SKILL_ROOT / "lib/spec-engine/runner.py").exists()
    assert (SKILL_ROOT / "docs/contracts/spec-json.md").exists()
