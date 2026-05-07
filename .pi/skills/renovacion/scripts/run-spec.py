#!/usr/bin/env python3
import importlib
import importlib.util
import json
import sys

from _skill_paths import SKILL_ROOT, project_dir, require_project_file

PACKAGE_NAME = "renovacion_spec_engine"


def load_spec_runner():
    package_dir = SKILL_ROOT / "lib" / "spec-engine"
    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        package_dir / "__init__.py",
        submodule_search_locations=[str(package_dir)],
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load spec engine from {package_dir}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[PACKAGE_NAME] = module
    spec.loader.exec_module(module)
    return importlib.import_module(f"{PACKAGE_NAME}.runner")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/run-spec.py <project-id>", file=sys.stderr)
        return 2
    try:
        project_path = project_dir(argv[1])
        require_project_file(project_path, "input.json")
        require_project_file(project_path, "resultados.json")
        runner = load_spec_runner()
        catalog_path = SKILL_ROOT / "lib" / "spec-engine" / "catalog" / "models.json"
        spec_data = runner.run_spec_generation(project_path, catalog_path)
        output_path = project_path / "spec.json"
        output_path.write_text(json.dumps(spec_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {output_path}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
