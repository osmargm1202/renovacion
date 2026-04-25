#!/usr/bin/env python3
"""Tests for dimensions normalization (flexible shape A/B)."""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib" / "input-pipeline"))

from validator import InputValidator


@pytest.fixture
def validator():
    return InputValidator()


def test_normalize_shape_a(validator):
    """Test shape A: area_m2 + height_m → derive volume_m3."""
    data = {
        "project": {
            "id": 1,
            "name": "Test",
            "cliente": None,
            "ubicacion": "Test",
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
                "alias": "Test",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {"area_m2": 10.0, "height_m": 2.5},
                "people": None,
                "equipment_ids": [],
                "notes": [],
            }
        ],
        "equipment": [],
        "defaults_applied": [],
    }

    normalized, notes = validator.normalize_dimensions(data)
    dims = normalized["areas"][0]["dimensions"]

    assert dims["area_m2"] == 10.0
    assert dims["height_m"] == 2.5
    assert dims["volume_m3"] == 25.0
    assert any("volume_m3 derived" in n for n in notes)


def test_normalize_shape_b(validator):
    """Test shape B: length_m + width_m + height_m → derive area_m2 and volume_m3."""
    data = {
        "project": {
            "id": 1,
            "name": "Test",
            "cliente": None,
            "ubicacion": "Test",
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
                "alias": "Test",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {"length_m": 2.0, "width_m": 5.0, "height_m": 3.0},
                "people": None,
                "equipment_ids": [],
                "notes": [],
            }
        ],
        "equipment": [],
        "defaults_applied": [],
    }

    normalized, notes = validator.normalize_dimensions(data)
    dims = normalized["areas"][0]["dimensions"]

    assert dims["length_m"] == 2.0
    assert dims["width_m"] == 5.0
    assert dims["height_m"] == 3.0
    assert dims["area_m2"] == 10.0
    assert dims["volume_m3"] == 30.0
    assert any("area_m2 derived" in n for n in notes)
    assert any("volume_m3 derived" in n for n in notes)


def test_normalize_preserve_existing_values(validator):
    """Test normalization preserves existing values when already complete."""
    data = {
        "project": {
            "id": 1,
            "name": "Test",
            "cliente": None,
            "ubicacion": "Test",
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
                "alias": "Test",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {
                    "length_m": 2.0,
                    "width_m": 4.0,
                    "height_m": 2.7,
                    "area_m2": 8.0,
                    "volume_m3": 21.6,
                },
                "people": None,
                "equipment_ids": [],
                "notes": [],
            }
        ],
        "equipment": [],
        "defaults_applied": [],
    }

    normalized, notes = validator.normalize_dimensions(data)
    dims = normalized["areas"][0]["dimensions"]

    # All values should be preserved
    assert dims["length_m"] == 2.0
    assert dims["width_m"] == 4.0
    assert dims["height_m"] == 2.7
    assert dims["area_m2"] == 8.0
    assert dims["volume_m3"] == 21.6


def test_normalize_conflict_resolution(validator):
    """Test conflict when provided area_m2 doesn't match length*width."""
    data = {
        "project": {
            "id": 1,
            "name": "Test",
            "cliente": None,
            "ubicacion": "Test",
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
                "alias": "Test",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {
                    "length_m": 2.0,
                    "width_m": 5.0,
                    "height_m": 3.0,
                    "area_m2": 999.0,  # Conflict: should be 10.0
                },
                "people": None,
                "equipment_ids": [],
                "notes": [],
            }
        ],
        "equipment": [],
        "defaults_applied": [],
    }

    normalized, notes = validator.normalize_dimensions(data)
    dims = normalized["areas"][0]["dimensions"]

    # Should use derived value (length * width)
    assert dims["area_m2"] == 10.0
    assert any("mismatch" in n.lower() for n in notes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
