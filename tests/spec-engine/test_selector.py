"""Tests for selector module."""

import pytest
from lib.spec_engine.selector import select_model, get_alternatives


def test_select_model_single_eligible():
    """Select only eligible model."""
    models = [
        {
            'airflow_m3_h': 140.0,
            'power_w': 45,
            'model': 'EX-150'
        }
    ]
    
    selected, reason = select_model(models, required_m3_h=130.0)
    assert selected['model'] == 'EX-150'
    assert 'smallest airflow above' in reason.lower()


def test_select_model_closest_airflow():
    """Select model with smallest excess."""
    models = [
        {
            'airflow_m3_h': 200.0,
            'power_w': 60,
            'model': 'EX-200'
        },
        {
            'airflow_m3_h': 140.0,
            'power_w': 45,
            'model': 'EX-150'
        },
        {
            'airflow_m3_h': 160.0,
            'power_w': 50,
            'model': 'EX-160'
        }
    ]
    
    selected, reason = select_model(models, required_m3_h=130.0)
    assert selected['model'] == 'EX-150'


def test_select_model_tie_break_power():
    """Tie-break by lower power."""
    models = [
        {
            'airflow_m3_h': 140.0,
            'power_w': 50,
            'model': 'EX-150-HP'
        },
        {
            'airflow_m3_h': 140.0,
            'power_w': 45,
            'model': 'EX-150-LP'
        },
        {
            'airflow_m3_h': 160.0,
            'power_w': 40,
            'model': 'EX-160'
        }
    ]
    
    selected, reason = select_model(models, required_m3_h=130.0)
    assert selected['model'] == 'EX-150-LP'
    assert 'tie broken by lower power' in reason.lower()


def test_select_model_no_eligible():
    """Return None when no eligible models."""
    models = [
        {
            'airflow_m3_h': 100.0,
            'power_w': 35,
            'model': 'EX-100'
        }
    ]
    
    selected, reason = select_model(models, required_m3_h=130.0)
    assert selected is None
    assert 'no eligible' in reason.lower()


def test_select_model_empty_list():
    """Return None for empty model list."""
    selected, reason = select_model([], required_m3_h=130.0)
    assert selected is None


def test_get_alternatives_excludes_selected():
    """Alternatives exclude selected model."""
    models = [
        {
            'airflow_m3_h': 140.0,
            'power_w': 45,
            'model': 'EX-150'
        },
        {
            'airflow_m3_h': 160.0,
            'power_w': 50,
            'model': 'EX-160'
        },
        {
            'airflow_m3_h': 200.0,
            'power_w': 60,
            'model': 'EX-200'
        }
    ]
    
    selected = models[0]
    alternatives = get_alternatives(models, selected, required_m3_h=130.0)
    
    assert len(alternatives) == 2
    assert selected['model'] not in {m['model'] for m in alternatives}


def test_get_alternatives_ordered():
    """Alternatives ordered by selection criterion."""
    models = [
        {
            'airflow_m3_h': 140.0,
            'power_w': 45,
            'model': 'EX-150'
        },
        {
            'airflow_m3_h': 250.0,
            'power_w': 75,
            'model': 'EX-250'
        },
        {
            'airflow_m3_h': 200.0,
            'power_w': 60,
            'model': 'EX-200'
        },
        {
            'airflow_m3_h': 160.0,
            'power_w': 50,
            'model': 'EX-160'
        }
    ]
    
    selected = models[0]
    alternatives = get_alternatives(models, selected, required_m3_h=130.0, max_count=3)
    
    assert len(alternatives) == 3
    assert alternatives[0]['model'] == 'EX-160'
    assert alternatives[1]['model'] == 'EX-200'
    assert alternatives[2]['model'] == 'EX-250'


def test_get_alternatives_max_count():
    """Respect max_count limit."""
    models = [
        {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150'},
        {'airflow_m3_h': 160.0, 'power_w': 50, 'model': 'EX-160'},
        {'airflow_m3_h': 200.0, 'power_w': 60, 'model': 'EX-200'},
        {'airflow_m3_h': 250.0, 'power_w': 75, 'model': 'EX-250'},
        {'airflow_m3_h': 300.0, 'power_w': 90, 'model': 'EX-300'}
    ]
    
    selected = models[0]
    alternatives = get_alternatives(models, selected, required_m3_h=130.0, max_count=2)
    
    assert len(alternatives) == 2


def test_get_alternatives_no_selected():
    """Return empty list when no model selected."""
    models = [
        {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150'}
    ]
    
    alternatives = get_alternatives(models, selected_model=None, required_m3_h=130.0)
    assert len(alternatives) == 0


def test_get_alternatives_only_selected_eligible():
    """Return empty list when only selected model is eligible."""
    models = [
        {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150'}
    ]
    
    selected = models[0]
    alternatives = get_alternatives(models, selected, required_m3_h=130.0)
    assert len(alternatives) == 0
