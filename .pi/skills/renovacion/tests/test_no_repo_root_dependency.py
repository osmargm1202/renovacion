import os
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def ignore_noise(_dir, names):
    return {".venv", "__pycache__", ".pytest_cache", "uv.lock"}.intersection(names)


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


def test_skill_copy_runs_outside_repo_and_writes_only_inside_cwd_project(tmp_path):
    copied_skill = tmp_path / "renovacion"
    shutil.copytree(SKILL_ROOT, copied_skill, ignore=ignore_noise)
    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()

    source_project = copied_skill / "proyectos/1"
    project = outside_cwd / "proyectos/1"
    project.mkdir(parents=True)
    shutil.copy2(source_project / "input.json", project / "input.json")
    skill_resultados = source_project / "resultados.json"
    skill_memoria = source_project / "memoria.html"
    before_resultados = skill_resultados.read_text(encoding="utf-8") if skill_resultados.exists() else None
    before_memoria = skill_memoria.read_text(encoding="utf-8") if skill_memoria.exists() else None

    result = subprocess.run(
        ["bash", str(copied_skill / "scripts/run-project.sh"), "1"],
        cwd=outside_cwd,
        text=True,
        capture_output=True,
        env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"},
        timeout=60,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert (project / "resultados.json").exists()
    assert (project / "memoria.html").exists()
    assert not (project / "spec.json").exists()
    if before_resultados is not None:
        assert skill_resultados.read_text(encoding="utf-8") == before_resultados
    if before_memoria is not None:
        assert skill_memoria.read_text(encoding="utf-8") == before_memoria
    html = (project / "memoria.html").read_text(encoding="utf-8")
    assert_project_1_demand_only_values(html)
    assert "Selección de Equipos" not in html
    assert "80F / GreenBuilder" not in html
    assert "cdn.jsdelivr" not in html.lower()
