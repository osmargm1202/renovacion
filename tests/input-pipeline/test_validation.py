#!/usr/bin/env python3
"""Tests for critical/non-critical validation and draft/calc_ready status."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib" / "input-pipeline"))

from validator import InputValidator


@pytest.fixture
def validator():
    return InputValidator()


@pytest.fixture
def base_data():
    """Base valid data for testing."""
    return {
        "project": {
            "id": 1,
            "name": "Test Project",
            "cliente": "Test Client",
            "ubicacion": "Test Location",
            "ingeniero": "Test Engineer",
            "codia": "12345",
            "empresa_calculo": "Test Company",
            "logo_empresa": "https://example.com/logo1.png",
            "logo_cliente": "https://example.com/logo2.png",
            "status": "calc_ready",
        },
        "validation": {
            "critical_complete": True,
            "missing_critical": [],
            "missing_non_critical": [],
            "notes": [],
        },
        "areas": [
            {
                "id": "A1",
                "alias": "Test Area",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {"area_m2": 8.0, "height_m": 2.7, "volume_m3": 21.6},
                "people": 2,
                "equipment_ids": ["E1"],
                "notes": [],
            }
        ],
        "equipment": [
            {
                "id": "E1",
                "alias": "Test Equipment",
                "kind": "extractor",
                "cantidad": 1,
                "serves_area_ids": ["A1"],
                "voltage": "220V",
                "frequency_hz": 60,
                "installation_type": "wall",
                "power_w": 100,
                "power_kw": 0.1,
                "airflow_cfm": 200,
                "airflow_m3_h": 340,
                "notes": [],
            }
        ],
        "defaults_applied": [],
    }


def test_critical_complete_all_present(validator, base_data):
    """Test critical_complete=True when all critical fields present."""
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is True
    assert len(missing_critical) == 0


def test_critical_missing_project_name(validator, base_data):
    """Test missing project.name is critical."""
    base_data["project"]["name"] = None
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "project.name" in missing_critical


def test_critical_missing_project_ubicacion(validator, base_data):
    """Test missing project.ubicacion is critical."""
    base_data["project"]["ubicacion"] = None
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "project.ubicacion" in missing_critical


def test_critical_no_areas(validator, base_data):
    """Test at least one area is critical."""
    base_data["areas"] = []
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "areas" in missing_critical


def test_critical_missing_area_id(validator, base_data):
    """Test missing area.id is critical."""
    base_data["areas"][0]["id"] = ""
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "areas[0].id" in missing_critical


def test_critical_missing_catalog_type(validator, base_data):
    """Test missing area.catalog_type is critical."""
    base_data["areas"][0]["catalog_type"] = ""
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "areas[0].catalog_type" in missing_critical


def test_critical_missing_height(validator, base_data):
    """Test missing height_m is critical."""
    del base_data["areas"][0]["dimensions"]["height_m"]
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert "areas[0].dimensions.height_m" in missing_critical


def test_critical_missing_both_area_and_length_width(validator, base_data):
    """Test missing both area_m2 and length+width is critical."""
    base_data["areas"][0]["dimensions"] = {"height_m": 2.7, "volume_m3": 21.6}
    critical_complete, missing_critical = validator.validate_critical_fields(base_data)
    assert critical_complete is False
    assert any("dimensions" in mc for mc in missing_critical)


def test_non_critical_metadata(validator, base_data):
    """Test non-critical metadata fields."""
    base_data["project"]["cliente"] = None
    base_data["project"]["ingeniero"] = None
    base_data["project"]["codia"] = None

    missing_non_critical = validator.validate_non_critical_fields(base_data)
    assert "project.cliente" in missing_non_critical
    assert "project.ingeniero" in missing_non_critical
    assert "project.codia" in missing_non_critical


def test_non_critical_people(validator, base_data):
    """Test people is non-critical."""
    base_data["areas"][0]["people"] = None
    missing_non_critical = validator.validate_non_critical_fields(base_data)
    assert "areas[0].people" in missing_non_critical


def test_non_critical_equipment_placeholders(validator, base_data):
    """Test equipment placeholders are non-critical."""
    base_data["equipment"][0]["voltage"] = None
    base_data["equipment"][0]["power_w"] = None

    missing_non_critical = validator.validate_non_critical_fields(base_data)
    assert "equipment[0].voltage" in missing_non_critical
    assert "equipment[0].power_w" in missing_non_critical


def test_full_validation_calc_ready(validator, base_data):
    """Test full validation with calc_ready status."""
    result = validator.validate(base_data, normalize=True)
    assert result["valid"] is True
    assert result["critical_complete"] is True
    assert len(result["missing_critical"]) == 0


def test_full_validation_draft(validator, base_data):
    """Test full validation in draft status with missing criticals."""
    base_data["project"]["name"] = None
    base_data["project"]["status"] = "draft"

    result = validator.validate(base_data, normalize=True)
    assert result["valid"] is True  # Still structurally valid
    assert result["critical_complete"] is False
    assert "project.name" in result["missing_critical"]


def test_cross_link_validation(validator, base_data):
    """Test area ↔ equipment cross-link validation."""
    # Valid: A1 → E1, E1 → A1
    errors = validator.validate_cross_links(base_data)
    assert len(errors) == 0

    # Invalid: A1 → E1, but E1 doesn't reference A1
    base_data["equipment"][0]["serves_area_ids"] = []
    errors = validator.validate_cross_links(base_data)
    assert len(errors) > 0
    assert "does not reference area" in errors[0]


def test_cross_link_missing_equipment(validator, base_data):
    """Test cross-link with missing equipment reference."""
    base_data["areas"][0]["equipment_ids"] = ["E1", "E999"]
    errors = validator.validate_cross_links(base_data)
    assert len(errors) > 0
    assert "non-existent equipment E999" in errors[0]


def test_unique_ids_duplicate_areas(validator, base_data):
    """Test duplicate area IDs fail validation."""
    base_data["areas"].append(base_data["areas"][0].copy())
    errors = validator.validate_unique_ids(base_data)
    assert len(errors) > 0
    assert "duplicate area" in errors[0].lower()


def test_unique_ids_duplicate_equipment(validator, base_data):
    """Test duplicate equipment IDs fail validation."""
    base_data["equipment"].append(base_data["equipment"][0].copy())
    errors = validator.validate_unique_ids(base_data)
    assert len(errors) > 0
    assert "duplicate equipment" in errors[0].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
