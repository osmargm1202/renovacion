import importlib.util
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = SKILL_ROOT / "lib" / "spec-engine" / "catalog_validator.py"


def load_catalog_validator_module():
    spec = importlib.util.spec_from_file_location("renovacion_catalog_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load catalog validator from {VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["renovacion_catalog_validator"] = module
    spec.loader.exec_module(module)
    return module


def commercial_model(**overrides):
    model = {
        "brand": "Delta Breez",
        "model": "80F / GreenBuilder",
        "kind": "extractor",
        "extractor_type": "sencillo",
        "airflow_cfm": 80.0,
        "airflow_m3_h": 135.9,
        "voltage": 120,
        "frequency_hz": 60,
        "power_w": 10.5,
        "power_kw": 0.0105,
        "installation_type": "ceiling_wall",
        "image_asset": "assets/extractores/sencillo.png",
        "source_url": "https://www.deltabreez.com/80F.php",
        "catalog_url": "https://www.deltabreez.com/80F.php",
        "image_source_url": "https://www.deltabreez.com/images/80f.png",
        "rating_basis": "HVI 0.1 in wg",
        "source_notes": "Product page airflow/power values.",
        "retrieved_at": "2026-04-25",
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
