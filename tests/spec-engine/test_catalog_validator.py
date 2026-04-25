"""Tests for catalog_validator module."""

import pytest
from lib.spec_engine.catalog_validator import validate_model, validate_catalog


def test_validate_model_valid():
    """Valid model passes validation."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'kind': 'extractor',
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro'
    }
    
    is_valid, errors = validate_model(model)
    assert is_valid is True
    assert len(errors) == 0


def test_validate_model_missing_field():
    """Model missing required field fails."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        # missing 'kind'
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro'
    }
    
    is_valid, errors = validate_model(model)
    assert is_valid is False
    assert any('kind' in e for e in errors)


def test_validate_model_invalid_airflow():
    """Model with airflow <= 0 fails."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'kind': 'extractor',
        'airflow_m3_h': 0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro'
    }
    
    is_valid, errors = validate_model(model)
    assert is_valid is False
    assert any('airflow_m3_h' in e for e in errors)


def test_validate_model_power_inconsistency():
    """Model with inconsistent power_w and power_kw fails."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'kind': 'extractor',
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.999,  # should be 0.045
        'installation_type': 'muro'
    }
    
    is_valid, errors = validate_model(model)
    assert is_valid is False
    assert any('power_kw inconsistent' in e for e in errors)


def test_validate_catalog_all_valid():
    """Catalog with all valid models passes."""
    models = [
        {
            'brand': 'ORGM',
            'model': 'EX-100',
            'kind': 'extractor',
            'airflow_m3_h': 100.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 35,
            'power_kw': 0.035,
            'installation_type': 'muro'
        },
        {
            'brand': 'ORGM',
            'model': 'EX-150',
            'kind': 'extractor',
            'airflow_m3_h': 140.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 45,
            'power_kw': 0.045,
            'installation_type': 'muro'
        }
    ]
    
    is_valid, invalid_entries = validate_catalog(models)
    assert is_valid is True
    assert len(invalid_entries) == 0


def test_validate_catalog_some_invalid():
    """Catalog with invalid models returns errors."""
    models = [
        {
            'brand': 'ORGM',
            'model': 'EX-100',
            'kind': 'extractor',
            'airflow_m3_h': 100.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 35,
            'power_kw': 0.035,
            'installation_type': 'muro'
        },
        {
            'brand': 'ORGM',
            'model': 'EX-BAD',
            # missing airflow_m3_h
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 45,
            'power_kw': 0.045,
            'installation_type': 'muro'
        }
    ]
    
    is_valid, invalid_entries = validate_catalog(models)
    assert is_valid is False
    assert len(invalid_entries) == 1
    assert invalid_entries[0]['model'] == 'EX-BAD'
