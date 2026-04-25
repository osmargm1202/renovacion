#!/usr/bin/env python3
from pathlib import Path
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "SKILL.md",
    "pyproject.toml",
    "lib/input-pipeline/schema.json",
    "lib/calc-engine/src/calc_engine/runner.py",
    "lib/spec-engine/runner.py",
    "lib/spec-engine/catalog/models.json",
    "lib/memory-engine/runner.js",
    "rules/renovacion.json",
    "assets/css/memoria.css",
    "assets/vendor/katex/katex.min.css",
    "assets/extractores/ex-150.png",
    "docs/contracts/input-json.md",
    "examples/input-pipeline/aurora-gmr.input.json",
    "proyectos/1/input.json",
]


def frontmatter() -> dict[str, str]:
    path = SKILL_ROOT / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise SystemExit("SKILL.md missing opening frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise SystemExit("SKILL.md missing closing frontmatter")
    parsed = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"')
    return parsed


def main() -> int:
    meta = frontmatter()
    errors = []
    if meta.get("name") != "renovacion":
        errors.append("SKILL.md name must be renovacion")
    if not meta.get("description"):
        errors.append("SKILL.md description is required")
    for rel in REQUIRED:
        if not (SKILL_ROOT / rel).exists():
            errors.append(f"missing {rel}")
    if errors:
        print("Skill structure invalid:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Skill structure OK: {SKILL_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
