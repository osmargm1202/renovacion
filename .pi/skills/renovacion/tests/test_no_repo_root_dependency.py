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
