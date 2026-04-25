#!/usr/bin/env python3
import sys
from pathlib import Path

from _skill_paths import SKILL_ROOT, add_calc_engine_to_path, project_dir, require_project_file


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/run-calc.py <project-id>", file=sys.stderr)
        return 2
    try:
        project_path = project_dir(argv[1])
        input_path = require_project_file(project_path, "input.json")
        rules_path = SKILL_ROOT / "rules" / "renovacion.json"
        output_path = project_path / "resultados.json"
        add_calc_engine_to_path()
        from calc_engine.runner import run_calculation
        run_calculation(Path(input_path), Path(rules_path), Path(output_path))
        print(f"Wrote {output_path.relative_to(SKILL_ROOT)}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
