#!/usr/bin/env python3
"""Tests for input.json schema validation."""

import json
import pytest
from pathlib import Path
import sys

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib" / "input-pipeline"))

from validator import InputValidator


@pytest.fixture
def validator():
    return InputValidator()


@pytest.fixture
def minimal_valid():
    """Minimal valid input.json structure."""
    return {
        "project": {
            "id": 1,
            "name": "Test Project",
            "cliente": None,
            "ubicacion": "Test Location",
            "ingeniero": None,
            "codia": None,
            "empresa_calculo": None,
            "logo_empresa": None,
            "logo_cliente": None,
            "status": "draft",
        },
        "validation": {
            "critical_complete": False,
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
                "dimensions": {"height_m": 2.7, "area_m2": 8.0, "volume_m3": 21.6},
                "people": None,
                "equipment_ids": [],
                "notes": [],
            }
        ],
        "equipment": [],
        "defaults_applied": [],
    }


def test_schema_valid_minimal(validator, minimal_valid):
    """Test minimal valid structure passes schema validation."""
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) == 0


def test_schema_missing_top_level_key(validator, minimal_valid):
    """Test missing top-level required key fails."""
    del minimal_valid["areas"]
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0
    assert "areas" in errors[0].lower()


def test_schema_invalid_status(validator, minimal_valid):
    """Test invalid project status fails."""
    minimal_valid["project"]["status"] = "invalid_status"
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0
    assert "status" in errors[0].lower()


def test_schema_extra_top_level_key(validator, minimal_valid):
    """Test extra top-level key fails (additionalProperties: false)."""
    minimal_valid["extra_key"] = "should not be here"
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0


def test_schema_invalid_project_id(validator, minimal_valid):
    """Test invalid project ID (not integer or < 1) fails."""
    minimal_valid["project"]["id"] = 0
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0

    minimal_valid["project"]["id"] = "not_an_int"
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0


def test_schema_invalid_catalog_sector(validator, minimal_valid):
    """Test invalid catalog_sector fails."""
    minimal_valid["areas"][0]["catalog_sector"] = "invalid_sector"
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0
    assert "catalog_sector" in errors[0].lower()


def test_schema_negative_dimensions(validator, minimal_valid):
    """Test negative dimensions fail."""
    minimal_valid["areas"][0]["dimensions"]["height_m"] = -2.7
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0


def test_schema_dimensions_shape_a(validator, minimal_valid):
    """Test dimensions shape A (area_m2 + height_m) is valid."""
    minimal_valid["areas"][0]["dimensions"] = {
        "area_m2": 10.0,
        "height_m": 3.0,
        "volume_m3": 30.0,
    }
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) == 0


def test_schema_dimensions_shape_b(validator, minimal_valid):
    """Test dimensions shape B (length_m + width_m + height_m) is valid."""
    minimal_valid["areas"][0]["dimensions"] = {
        "length_m": 2.0,
        "width_m": 5.0,
        "height_m": 3.0,
        "area_m2": 10.0,
        "volume_m3": 30.0,
    }
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) == 0


def test_schema_dimensions_missing_required(validator, minimal_valid):
    """Test dimensions missing height_m or area/length+width fails."""
    # Missing height_m
    minimal_valid["areas"][0]["dimensions"] = {"area_m2": 10.0, "volume_m3": 30.0}
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0

    # Missing both area_m2 and length/width combo
    minimal_valid["areas"][0]["dimensions"] = {"height_m": 3.0, "volume_m3": 30.0}
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) > 0


def test_schema_equipment_placeholders_nullable(validator, minimal_valid):
    """Test equipment placeholders can be null."""
    minimal_valid["equipment"] = [
        {
            "id": "E1",
            "alias": "Test Equipment",
            "kind": None,
            "cantidad": None,
            "serves_area_ids": ["A1"],
            "voltage": None,
            "frequency_hz": None,
            "installation_type": None,
            "power_w": None,
            "power_kw": None,
            "airflow_cfm": None,
            "airflow_m3_h": None,
            "notes": [],
        }
    ]
    errors = validator.validate_schema(minimal_valid)
    assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
