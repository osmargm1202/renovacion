"""Catalog validator - validates commercial extractor model entries."""

from typing import Any, Dict, List, Tuple


REQUIRED_FIELDS = [
    "brand",
    "model",
    "kind",
    "extractor_type",
    "airflow_cfm",
    "airflow_m3_h",
    "voltage",
    "frequency_hz",
    "power_w",
    "power_kw",
    "installation_type",
    "image_asset",
    "source_url",
    "catalog_url",
    "image_source_url",
    "rating_basis",
    "source_notes",
    "retrieved_at",
]

ALLOWED_EXTRACTOR_TYPES = {"sencillo", "ducteable"}
ALLOWED_IMAGE_ASSETS = {
    "assets/extractores/sencillo.png",
    "assets/extractores/ducteable.png",
}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def _is_non_negative_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0


def _is_positive_number_or_non_empty_string(value: Any) -> bool:
    return _is_positive_number(value) or _is_non_empty_string(value)


def validate_model(model: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate single catalog model entry."""
    errors: List[str] = []

    for field in REQUIRED_FIELDS:
        if field not in model:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    if not _is_non_empty_string(model["brand"]):
        errors.append("brand must be non-empty string")

    if not _is_non_empty_string(model["model"]):
        errors.append("model must be non-empty string")

    if not _is_non_empty_string(model["kind"]):
        errors.append("kind must be non-empty string")

    extractor_type = model["extractor_type"]
    if extractor_type not in ALLOWED_EXTRACTOR_TYPES:
        errors.append("extractor_type must be one of: sencillo, ducteable")

    if not _is_positive_number(model["airflow_cfm"]):
        errors.append("airflow_cfm must be > 0")

    if not _is_positive_number(model["airflow_m3_h"]):
        errors.append("airflow_m3_h must be > 0")

    if not _is_positive_number_or_non_empty_string(model["voltage"]):
        errors.append("voltage must be positive number or non-empty string")

    if not _is_positive_number_or_non_empty_string(model["frequency_hz"]):
        errors.append("frequency_hz must be positive number or non-empty string")

    if not _is_non_negative_number(model["power_w"]):
        errors.append("power_w must be >= 0")

    if not _is_non_negative_number(model["power_kw"]):
        errors.append("power_kw must be >= 0")

    expected_kw = round(model["power_w"] / 1000.0, 6)
    actual_kw = round(model["power_kw"], 6)
    if abs(expected_kw - actual_kw) > 1e-5:
        errors.append(f"power_kw inconsistent with power_w: {model['power_kw']} != {model['power_w']}/1000")

    if not _is_non_empty_string(model["installation_type"]):
        errors.append("installation_type must be non-empty string")

    image_asset = model["image_asset"]
    if image_asset not in ALLOWED_IMAGE_ASSETS:
        errors.append("image_asset must be local category image: assets/extractores/sencillo.png or assets/extractores/ducteable.png")

    for field in ["source_url", "catalog_url", "image_source_url", "rating_basis", "source_notes", "retrieved_at"]:
        if not _is_non_empty_string(model[field]):
            errors.append(f"{field} must be non-empty string")

    if "power_hp" in model and model["power_hp"] is not None and not _is_non_negative_number(model["power_hp"]):
        errors.append("power_hp must be >= 0 when provided")

    return len(errors) == 0, errors


def validate_catalog(models: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """Validate entire catalog."""
    invalid_entries: List[Dict[str, Any]] = []

    for idx, model in enumerate(models):
        is_valid, errors = validate_model(model)
        if not is_valid:
            invalid_entries.append(
                {
                    "index": idx,
                    "model": model.get("model", "UNKNOWN"),
                    "errors": errors,
                }
            )

    return len(invalid_entries) == 0, invalid_entries
