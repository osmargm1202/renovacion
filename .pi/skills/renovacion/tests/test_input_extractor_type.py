import importlib.util
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "lib" / "input-pipeline" / "validator.py"
PROJECT_INPUT_PATH = SKILL_ROOT / "proyectos" / "1" / "input.json"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("renovacion_input_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["renovacion_input_validator"] = module
    spec.loader.exec_module(module)
    return module


def load_project_input():
    return json.loads(PROJECT_INPUT_PATH.read_text(encoding="utf-8"))


def test_missing_area_extractor_type_fails_validation():
    validator_module = load_validator_module()
    validator = validator_module.InputValidator()
    data = load_project_input()
    data["areas"][0].pop("extractor_type", None)

    result = validator.validate(data)

    assert result["valid"] is False
    assert any("extractor_type" in error for error in result["errors"])



def test_invalid_area_extractor_type_fails_validation():
    validator_module = load_validator_module()
    validator = validator_module.InputValidator()
    data = load_project_input()
    data["areas"][0]["extractor_type"] = "industrial"

    result = validator.validate(data)

    assert result["valid"] is False
    assert any("extractor_type" in error or "industrial" in error for error in result["errors"])



def test_valid_area_extractor_type_values_pass_validation():
    validator_module = load_validator_module()
    validator = validator_module.InputValidator()

    for extractor_type in ["sencillo", "ducteable"]:
        data = load_project_input()
        data["areas"][0]["extractor_type"] = extractor_type

        result = validator.validate(data)

        assert result["valid"] is True
        assert result["errors"] == []
        assert result["critical_complete"] is True
