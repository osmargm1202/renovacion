import importlib.util
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "lib" / "spec-engine" / "catalog_validator.py"
CATALOG_PATH = SKILL_ROOT / "lib" / "spec-engine" / "catalog" / "models.json"


def load_catalog_validator_module():
    spec = importlib.util.spec_from_file_location("renovacion_catalog_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load catalog validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["renovacion_catalog_validator"] = module
    spec.loader.exec_module(module)
    return module


def load_actual_catalog_models():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["models"]



def commercial_model(**overrides):
    model = {
        "brand": "Delta Breez",
        "model": "80F / GreenBuilder",
        "kind": "extractor",
        "extractor_type": "sencillo",
        "airflow_cfm": 80.0,
        "airflow_m3_h": 135.9,
        "airflow_unit_original": "CFM",
        "voltage": 120,
        "frequency_hz": 60,
        "power_w": 10.5,
        "power_kw": 0.0105,
        "power_unit_original": "W",
        "installation_type": "ceiling_wall",
        "image_asset": "assets/extractores/sencillo.png",
        "source_url": "https://www.deltabreez.com/80F.php",
        "catalog_url": "https://www.deltabreez.com/80F.php",
        "image_source_url": "https://www.deltabreez.com/images/80f.png",
        "rating_basis": "HVI 0.1 in wg",
        "source_notes": "Product page airflow/power values.",
        "retrieved_at": "2026-04-25",
        "notes": [],
    }
    model.update(overrides)
    return model


def test_valid_commercial_model_with_source_fields_passes():
    validator = load_catalog_validator_module()

    is_valid, errors = validator.validate_model(commercial_model())

    assert is_valid is True
    assert errors == []



def test_missing_extractor_type_and_source_url_fail():
    validator = load_catalog_validator_module()
    model = commercial_model()
    del model["extractor_type"]
    del model["source_url"]

    is_valid, errors = validator.validate_model(model)

    assert is_valid is False
    assert "Missing required field: extractor_type" in errors
    assert "Missing required field: source_url" in errors



def test_remote_image_asset_fails():
    validator = load_catalog_validator_module()
    model = commercial_model(image_asset="https://cdn.example.com/extractor.png")

    is_valid, errors = validator.validate_model(model)

    assert is_valid is False
    assert any("image_asset" in error for error in errors)



def test_invalid_extractor_type_fails():
    validator = load_catalog_validator_module()
    model = commercial_model(extractor_type="industrial")

    is_valid, errors = validator.validate_model(model)

    assert is_valid is False
    assert any("extractor_type" in error for error in errors)



def test_string_voltage_and_frequency_are_accepted():
    validator = load_catalog_validator_module()
    model = commercial_model(
        voltage="220-240",
        frequency_hz="50/60",
        extractor_type="ducteable",
        image_asset="assets/extractores/ducteable.png",
    )

    is_valid, errors = validator.validate_model(model)

    assert is_valid is True
    assert errors == []



def test_missing_design_required_fields_fail_validation():
    validator = load_catalog_validator_module()
    model = commercial_model()
    del model["airflow_unit_original"]
    del model["power_unit_original"]
    del model["notes"]

    is_valid, errors = validator.validate_model(model)

    assert is_valid is False
    assert "Missing required field: airflow_unit_original" in errors
    assert "Missing required field: power_unit_original" in errors
    assert "Missing required field: notes" in errors



def test_actual_catalog_rows_include_design_required_fields():
    required_fields = {"airflow_unit_original", "power_unit_original", "notes"}

    missing_fields_by_model = {
        model["model"]: sorted(required_fields - model.keys())
        for model in load_actual_catalog_models()
        if required_fields - model.keys()
    }

    assert missing_fields_by_model == {}



def test_actual_catalog_includes_required_sodeca_seed_rows():
    sodeca_models = {
        model["model"]
        for model in load_actual_catalog_models()
        if model.get("brand") == "Sodeca"
    }

    assert {"CA/LINE-15", "CA/LINE-20", "CA/LINE-31", "TUB-250", "TUB-315"} <= sodeca_models
