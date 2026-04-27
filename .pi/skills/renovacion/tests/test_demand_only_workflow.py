import os
import shutil
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def run_cmd(args: list[str], cwd: Path):
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    return subprocess.run(
        args, cwd=cwd, text=True, capture_output=True, env=env, timeout=60
    )


def make_project(project_id: str, *, include_resultados: bool) -> Path:
    project = SKILL_ROOT / "proyectos" / project_id
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copy2(SKILL_ROOT / "proyectos/1/input.json", project / "input.json")
    if include_resultados:
        shutil.copy2(
            SKILL_ROOT / "proyectos/1/resultados.json", project / "resultados.json"
        )
    spec = project / "spec.json"
    if spec.exists():
        spec.unlink()
    return project


def read_html(project: Path) -> str:
    return (project / "memoria.html").read_text(encoding="utf-8")


def test_run_memory_requires_input_and_resultados_only_not_spec(tmp_path):
    project = make_project("991", include_resultados=True)
    try:
        result = run_cmd(
            ["bash", str(SKILL_ROOT / "scripts/run-memory.sh"), "991"], cwd=tmp_path
        )
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
        assert "Resumen de Necesidad por Área" in html
        assert "Equipos Requeridos" not in html
        assert "Selección de Equipos" not in html
        assert "80F / GreenBuilder" not in html
        assert "Delta Breez" not in html
    finally:
        shutil.rmtree(project, ignore_errors=True)


def test_run_spec_script_and_spec_engine_remain_available_for_future():
    assert (SKILL_ROOT / "scripts/run-spec.py").exists()
    assert (SKILL_ROOT / "lib/spec-engine/runner.py").exists()
    assert (SKILL_ROOT / "docs/contracts/spec-json.md").exists()
