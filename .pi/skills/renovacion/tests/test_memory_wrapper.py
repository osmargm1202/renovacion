import os
import subprocess
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


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
    assert "AURORA GMR" in html
    assert "129.6" in html
    assert "EX-150" in html
    assert "assets/vendor/katex" in html
    assert "cdn.jsdelivr" not in html.lower()
    assert not (tmp_path / "proyectos" / "1" / "memoria.html").exists()
