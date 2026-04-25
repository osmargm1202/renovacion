"""Tests for assembler module."""

import pytest
from lib.spec_engine.assembler import (
    create_equipment_spec,
    format_model,
    assemble_spec_json
)


def test_format_model():
    """Format model extracts relevant fields."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'kind': 'extractor',
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro',
        'image_asset': 'assets/ex-150.png',
        'notes': ['internal note']
    }
    
    formatted = format_model(model)
    
    assert 'brand' in formatted
    assert 'model' in formatted
    assert 'airflow_m3_h' in formatted
    assert 'image_asset' in formatted
    assert 'notes' not in formatted
    assert 'kind' not in formatted


def test_format_model_no_image():
    """Format model without optional image."""
    model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro'
    }
    
    formatted = format_model(model)
    assert 'image_asset' not in formatted


def test_create_equipment_spec_selected():
    """Create spec entry for selected equipment."""
    equipment = {
        'id': 'E1',
        'alias': 'Extractor baño',
        'kind': 'extractor'
    }
    
    selected_model = {
        'brand': 'ORGM',
        'model': 'EX-150',
        'airflow_m3_h': 140.0,
        'voltage': 120,
        'frequency_hz': 60,
        'power_w': 45,
        'power_kw': 0.045,
        'installation_type': 'muro'
    }
    
    alternatives = []
    
    spec = create_equipment_spec(
        equipment,
        required_m3_h=129.6,
        selected_model=selected_model,
        alternatives=alternatives,
        selection_reason='Selected smallest airflow above required.',
        constraints_used={'kind': 'extractor'}
    )
    
    assert spec['equipment_id'] == 'E1'
    assert spec['selection_status'] == 'selected'
    assert spec['selected_model']['model'] == 'EX-150'
    assert spec['required_m3_h'] == 129.6


def test_create_equipment_spec_failed():
    """Create spec entry for failed selection."""
    equipment = {
        'id': 'E1',
        'alias': 'Extractor baño',
        'kind': 'extractor'
    }
    
    spec = create_equipment_spec(
        equipment,
        required_m3_h=500.0,
        selected_model=None,
        alternatives=[],
        selection_reason='No eligible model with sufficient airflow',
        constraints_used={'kind': 'extractor'}
    )
    
    assert spec['equipment_id'] == 'E1'
    assert spec['selection_status'] == 'failed'
    assert spec['selected_model'] is None


def test_assemble_spec_json_completed():
    """Assemble complete spec.json."""
    project_data = {
        'id': 1,
        'name': 'Test Project',
        'source_input': '/path/input.json',
        'source_results': '/path/results.json'
    }
    
    equipment_selections = [
        {
            'equipment_id': 'E1',
            'selection_status': 'selected'
        }
    ]
    
    catalog_metadata = {
        'version': '1',
        'source': 'local-catalog-v1'
    }
    
    spec = assemble_spec_json(
        project_data,
        {},
        {},
        equipment_selections,
        catalog_metadata
    )
    
    assert spec['project']['id'] == 1
    assert spec['project']['spec_status'] == 'completed'
    assert spec['summary']['equipment_count'] == 1
    assert spec['summary']['selected_models_count'] == 1
    assert spec['summary']['failed_selections_count'] == 0


def test_assemble_spec_json_partial():
    """Assemble spec.json with mixed results."""
    project_data = {
        'id': 1,
        'name': 'Test Project',
        'source_input': '/path/input.json',
        'source_results': '/path/results.json'
    }
    
    equipment_selections = [
        {'equipment_id': 'E1', 'selection_status': 'selected'},
        {'equipment_id': 'E2', 'selection_status': 'failed'}
    ]
    
    catalog_metadata = {
        'version': '1',
        'source': 'local-catalog-v1'
    }
    
    spec = assemble_spec_json(
        project_data,
        {},
        {},
        equipment_selections,
        catalog_metadata
    )
    
    assert spec['project']['spec_status'] == 'partial'
    assert spec['summary']['selected_models_count'] == 1
    assert spec['summary']['failed_selections_count'] == 1


def test_assemble_spec_json_all_failed():
    """Assemble spec.json with all failed selections."""
    project_data = {
        'id': 1,
        'name': 'Test Project',
        'source_input': '/path/input.json',
        'source_results': '/path/results.json'
    }
    
    equipment_selections = [
        {'equipment_id': 'E1', 'selection_status': 'failed'}
    ]
    
    catalog_metadata = {
        'version': '1',
        'source': 'local-catalog-v1'
    }
    
    spec = assemble_spec_json(
        project_data,
        {},
        {},
        equipment_selections,
        catalog_metadata
    )
    
    assert spec['project']['spec_status'] == 'failed'
