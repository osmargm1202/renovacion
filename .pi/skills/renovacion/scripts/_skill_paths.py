from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]
PROYECTOS_ROOT = SKILL_ROOT / "proyectos"


def parse_project_id(raw: str) -> str:
    if not raw.isdigit():
        raise ValueError("Project id must be numeric")
    return raw


def project_dir(raw: str) -> Path:
    project_id = parse_project_id(raw)
    return PROYECTOS_ROOT / project_id


def require_project_file(project_path: Path, filename: str) -> Path:
    path = project_path / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required project file: {path}")
    return path


def add_calc_engine_to_path() -> None:
    src = SKILL_ROOT / "lib" / "calc-engine" / "src"
    sys.path.insert(0, str(src))
