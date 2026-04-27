from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.find("\n---", 4)
    assert end != -1, "SKILL.md must close YAML frontmatter"
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def test_skill_frontmatter_is_pi_discoverable():
    skill_md = SKILL_ROOT / "SKILL.md"
    assert skill_md.exists()
    frontmatter = parse_frontmatter(skill_md)
    assert frontmatter["name"] == SKILL_ROOT.name == "renovacion"
    assert frontmatter["description"]
    assert len(frontmatter["name"]) <= 64
    assert frontmatter["name"].replace("-", "").isalnum()
    assert not frontmatter["name"].startswith("-")
    assert not frontmatter["name"].endswith("-")
    assert "--" not in frontmatter["name"]


def test_required_runtime_resources_are_skill_local():
    required_paths = [
        "lib/input-pipeline/schema.json",
        "lib/input-pipeline/validator.py",
        "lib/input-pipeline/catalog_resolver.py",
        "lib/input-pipeline/project_id_allocator.py",
        "lib/calc-engine/pyproject.toml",
        "lib/calc-engine/src/calc_engine/runner.py",
        "lib/spec-engine/__init__.py",
        "lib/spec-engine/runner.py",
        "lib/spec-engine/catalog/models.json",
        "lib/memory-engine/index.js",
        "lib/memory-engine/runner.js",
        "lib/memory-engine/assets.js",
        "lib/memory-engine/formula.js",
        "lib/memory-engine/sections/portada.js",
        "lib/memory-engine/sections/resumen-necesidad-area.js",
        "rules/renovacion.json",
        "assets/css/memoria.css",
        "assets/css/memoria-sections.css",
        "assets/vendor/katex/katex.min.css",
        "assets/vendor/katex/katex.min.js",
        "assets/vendor/katex/auto-render.min.js",
        "assets/extractores/ex-150.png",
        "assets/extractores/ex-160.png",
        "assets/extractores/ex-200.png",
        "assets/extractores/ex-250.png",
        "docs/contracts/input-json.md",
        "docs/contracts/resultados-json.md",
        "docs/contracts/spec-json.md",
        "docs/contracts/memoria-html.md",
        "examples/input-pipeline/aurora-gmr.input.json",
        "proyectos/1/input.json",
        "proyectos/1/resultados.json",
        "proyectos/1/memoria.html",
    ]
    missing = [rel for rel in required_paths if not (SKILL_ROOT / rel).exists()]
    assert missing == []


def test_scripts_expected_by_skill_exist_and_are_executable():
    scripts = [
        "scripts/run-calc.py",
        "scripts/run-spec.py",
        "scripts/run-memory.sh",
        "scripts/run-project.sh",
        "scripts/validate-skill-structure.py",
    ]
    missing = [rel for rel in scripts if not (SKILL_ROOT / rel).exists()]
    assert missing == []
