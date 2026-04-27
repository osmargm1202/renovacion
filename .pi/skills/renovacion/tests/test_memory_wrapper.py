import os
import re
import subprocess
import unicodedata
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


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
    assert "3798.00 m3/h".lower() in normalized_html
    assert "2235.42 cfm" in normalized_html
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
        "2448.00 m3/h",
        "1440.84 CFM",
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
    assert_project_1_demand_only_values(html)
    assert "Selección de Equipos" not in html
    assert "80F / GreenBuilder" not in html
    assert "Delta Breez" not in html
    assert "assets/vendor/katex" in html
    assert "cdn.jsdelivr" not in html.lower()
    assert not (tmp_path / "proyectos" / "1" / "memoria.html").exists()
