"""Tests for runner module."""

import json
import pytest
from pathlib import Path
from lib.spec_engine.runner import run_spec_generation, find_required_airflow


def test_find_required_airflow():
    """Find required airflow from results data."""
    results_data = {
        'equipment_results': [
            {
                'equipment_id': 'E1',
                'required_m3_h_assigned': 129.6
            },
            {
                'equipment_id': 'E2',
                'required_m3_h_assigned': 85.0
            }
        ]
    }
    
    airflow = find_required_airflow('E1', results_data)
    assert airflow == 129.6
    
    airflow = find_required_airflow('E2', results_data)
    assert airflow == 85.0


def test_find_required_airflow_not_found():
    """Return None when equipment not found."""
    results_data = {
        'equipment_results': [
            {
                'equipment_id': 'E1',
                'required_m3_h_assigned': 129.6
            }
        ]
    }
    
    airflow = find_required_airflow('E999', results_data)
    assert airflow is None


def test_run_spec_generation_integration(tmp_path):
    """Full integration test for spec generation."""
    # Create test project directory
    project_path = tmp_path / 'proyecto-test'
    project_path.mkdir()
    
    # Create input.json
    input_data = {
        'project': {
            'id': 1,
            'name': 'Test Project'
        },
        'equipment': [
            {
                'id': 'E1',
                'alias': 'Extractor test',
                'kind': 'extractor',
                'installation_type': 'muro',
                'voltage': 120,
                'frequency_hz': 60
            }
        ]
    }
    
    with open(project_path / 'input.json', 'w') as f:
        json.dump(input_data, f)
    
    # Create resultados.json
    results_data = {
        'equipment_results': [
            {
                'equipment_id': 'E1',
                'required_m3_h_assigned': 129.6
            }
        ]
    }
    
    with open(project_path / 'resultados.json', 'w') as f:
        json.dump(results_data, f)
    
    # Create test catalog
    catalog_path = tmp_path / 'catalog.json'
    catalog_data = {
        'catalog': {
            'version': '1',
            'source': 'test-catalog'
        },
        'models': [
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
            },
            {
                'brand': 'ORGM',
                'model': 'EX-200',
                'kind': 'extractor',
                'airflow_m3_h': 200.0,
                'voltage': 120,
                'frequency_hz': 60,
                'power_w': 60,
                'power_kw': 0.06,
                'installation_type': 'muro'
            }
        ]
    }
    
    with open(catalog_path, 'w') as f:
        json.dump(catalog_data, f)
    
    # Run spec generation
    spec = run_spec_generation(project_path, catalog_path)
    
    # Verify results
    assert spec['project']['id'] == 1
    assert spec['project']['spec_status'] == 'completed'
    assert spec['summary']['equipment_count'] == 1
    assert spec['summary']['selected_models_count'] == 1
    assert len(spec['equipment_specs']) == 1
    
    eq_spec = spec['equipment_specs'][0]
    assert eq_spec['equipment_id'] == 'E1'
    assert eq_spec['selection_status'] == 'selected'
    assert eq_spec['selected_model']['model'] == 'EX-150'
    assert len(eq_spec['alternatives']) == 1
    assert eq_spec['alternatives'][0]['model'] == 'EX-200'


def test_run_spec_generation_no_eligible_model(tmp_path):
    """Test when no model meets requirement."""
    project_path = tmp_path / 'proyecto-fail'
    project_path.mkdir()
    
    input_data = {
        'project': {
            'id': 1,
            'name': 'Fail Project'
        },
        'equipment': [
            {
                'id': 'E1',
                'alias': 'Extractor high demand',
                'kind': 'extractor'
            }
        ]
    }
    
    with open(project_path / 'input.json', 'w') as f:
        json.dump(input_data, f)
    
    results_data = {
        'equipment_results': [
            {
                'equipment_id': 'E1',
                'required_m3_h_assigned': 500.0  # No model can meet this
            }
        ]
    }
    
    with open(project_path / 'resultados.json', 'w') as f:
        json.dump(results_data, f)
    
    catalog_path = tmp_path / 'catalog-fail.json'
    catalog_data = {
        'catalog': {
            'version': '1',
            'source': 'test-catalog'
        },
        'models': [
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
    }
    
    with open(catalog_path, 'w') as f:
        json.dump(catalog_data, f)
    
    spec = run_spec_generation(project_path, catalog_path)
    
    assert spec['project']['spec_status'] == 'failed'
    assert spec['summary']['failed_selections_count'] == 1
    eq_spec = spec['equipment_specs'][0]
    assert eq_spec['selection_status'] == 'failed'
    assert eq_spec['selected_model'] is None
