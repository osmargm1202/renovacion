"""Tests for filters module."""

import pytest
from lib.spec_engine.filters import apply_filters, get_eligible_models


def test_apply_filters_kind_only():
    """Filter by kind only."""
    models = [
        {'kind': 'extractor', 'model': 'EX-1'},
        {'kind': 'inyector', 'model': 'INY-1'},
        {'kind': 'extractor', 'model': 'EX-2'}
    ]
    
    filtered = apply_filters(models, kind='extractor')
    assert len(filtered) == 2
    assert all(m['kind'] == 'extractor' for m in filtered)


def test_apply_filters_installation_type():
    """Filter by kind and installation_type."""
    models = [
        {'kind': 'extractor', 'installation_type': 'muro', 'model': 'EX-1'},
        {'kind': 'extractor', 'installation_type': 'techo', 'model': 'EX-2'},
        {'kind': 'extractor', 'installation_type': 'muro', 'model': 'EX-3'}
    ]
    
    filtered = apply_filters(models, kind='extractor', installation_type='muro')
    assert len(filtered) == 2
    assert all(m['installation_type'] == 'muro' for m in filtered)


def test_apply_filters_voltage():
    """Filter by voltage."""
    models = [
        {'kind': 'extractor', 'voltage': 120, 'model': 'EX-1'},
        {'kind': 'extractor', 'voltage': 240, 'model': 'EX-2'},
        {'kind': 'extractor', 'voltage': 120, 'model': 'EX-3'}
    ]
    
    filtered = apply_filters(models, kind='extractor', voltage=120)
    assert len(filtered) == 2
    assert all(m['voltage'] == 120 for m in filtered)


def test_apply_filters_frequency():
    """Filter by frequency_hz."""
    models = [
        {'kind': 'extractor', 'frequency_hz': 60, 'model': 'EX-1'},
        {'kind': 'extractor', 'frequency_hz': 50, 'model': 'EX-2'},
        {'kind': 'extractor', 'frequency_hz': 60, 'model': 'EX-3'}
    ]
    
    filtered = apply_filters(models, kind='extractor', frequency_hz=60)
    assert len(filtered) == 2
    assert all(m['frequency_hz'] == 60 for m in filtered)


def test_apply_filters_all_constraints():
    """Filter with all constraints."""
    models = [
        {
            'kind': 'extractor',
            'installation_type': 'muro',
            'voltage': 120,
            'frequency_hz': 60,
            'model': 'EX-1'
        },
        {
            'kind': 'extractor',
            'installation_type': 'techo',
            'voltage': 120,
            'frequency_hz': 60,
            'model': 'EX-2'
        },
        {
            'kind': 'extractor',
            'installation_type': 'muro',
            'voltage': 240,
            'frequency_hz': 60,
            'model': 'EX-3'
        },
        {
            'kind': 'extractor',
            'installation_type': 'muro',
            'voltage': 120,
            'frequency_hz': 50,
            'model': 'EX-4'
        },
        {
            'kind': 'extractor',
            'installation_type': 'muro',
            'voltage': 120,
            'frequency_hz': 60,
            'model': 'EX-5'
        }
    ]
    
    filtered = apply_filters(
        models,
        kind='extractor',
        installation_type='muro',
        voltage=120,
        frequency_hz=60
    )
    assert len(filtered) == 2
    assert {m['model'] for m in filtered} == {'EX-1', 'EX-5'}


def test_get_eligible_models_sufficient():
    """Get models meeting airflow requirement."""
    models = [
        {'airflow_m3_h': 100.0, 'model': 'EX-1'},
        {'airflow_m3_h': 140.0, 'model': 'EX-2'},
        {'airflow_m3_h': 160.0, 'model': 'EX-3'}
    ]
    
    eligible = get_eligible_models(models, required_m3_h=130.0)
    assert len(eligible) == 2
    assert {m['model'] for m in eligible} == {'EX-2', 'EX-3'}


def test_get_eligible_models_none_sufficient():
    """No models meet airflow requirement."""
    models = [
        {'airflow_m3_h': 100.0, 'model': 'EX-1'},
        {'airflow_m3_h': 120.0, 'model': 'EX-2'}
    ]
    
    eligible = get_eligible_models(models, required_m3_h=150.0)
    assert len(eligible) == 0


def test_get_eligible_models_exact_match():
    """Model with exact airflow is eligible."""
    models = [
        {'airflow_m3_h': 100.0, 'model': 'EX-1'},
        {'airflow_m3_h': 130.0, 'model': 'EX-2'},
        {'airflow_m3_h': 160.0, 'model': 'EX-3'}
    ]
    
    eligible = get_eligible_models(models, required_m3_h=130.0)
    assert len(eligible) == 2
    assert 'EX-2' in {m['model'] for m in eligible}
