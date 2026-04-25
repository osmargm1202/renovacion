"""Runner - orchestrate full spec generation pipeline."""

import json
from pathlib import Path
from typing import Dict, Any, List

from . import catalog_loader, catalog_validator, filters, selector, assembler


def run_spec_generation(
    project_path: Path,
    catalog_path: Path
) -> Dict[str, Any]:
    """
    Run full spec generation pipeline.
    
    Args:
        project_path: path to project directory (contains input.json, resultados.json)
        catalog_path: path to catalog models.json
        
    Returns:
        Complete spec.json dict
        
    Raises:
        FileNotFoundError: if input files missing
        ValueError: if catalog invalid or data inconsistent
    """
    # Load input files
    input_path = project_path / 'input.json'
    results_path = project_path / 'resultados.json'
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    with open(results_path, 'r', encoding='utf-8') as f:
        results_data = json.load(f)
    
    # Load and validate catalog
    catalog_data = catalog_loader.load_catalog(catalog_path)
    models = catalog_loader.get_models(catalog_data)
    catalog_metadata = catalog_loader.get_catalog_metadata(catalog_data)
    
    is_valid, invalid_entries = catalog_validator.validate_catalog(models)
    if not is_valid:
        raise ValueError(f"Catalog validation failed: {invalid_entries}")
    
    # Process each equipment
    equipment_selections = []
    
    for equipment in input_data['equipment']:
        equipment_id = equipment['id']
        
        # Find required airflow from results
        required_m3_h = find_required_airflow(equipment_id, results_data)
        if required_m3_h is None:
            raise ValueError(f"Required airflow not found for equipment {equipment_id}")
        
        # Apply filters
        filtered_models = filters.apply_filters(
            models,
            kind=equipment['kind'],
            installation_type=equipment.get('installation_type'),
            voltage=equipment.get('voltage'),
            frequency_hz=equipment.get('frequency_hz')
        )
        
        # Get eligible models
        eligible_models = filters.get_eligible_models(filtered_models, required_m3_h)
        
        # Select model
        selected_model, reason = selector.select_model(eligible_models, required_m3_h)
        
        # Get alternatives
        alternatives = selector.get_alternatives(eligible_models, selected_model, required_m3_h, max_count=3)
        
        # Build constraints used
        constraints_used = {
            'kind': equipment['kind']
        }
        if equipment.get('installation_type'):
            constraints_used['installation_type'] = equipment['installation_type']
        if equipment.get('voltage'):
            constraints_used['voltage'] = equipment['voltage']
        if equipment.get('frequency_hz'):
            constraints_used['frequency_hz'] = equipment['frequency_hz']
        
        # Create spec entry
        spec_entry = assembler.create_equipment_spec(
            equipment,
            required_m3_h,
            selected_model,
            alternatives,
            reason,
            constraints_used
        )
        
        equipment_selections.append(spec_entry)
    
    # Assemble final spec
    project_context = {
        'id': input_data['project']['id'],
        'name': input_data['project']['name'],
        'source_input': str(input_path),
        'source_results': str(results_path)
    }
    
    spec = assembler.assemble_spec_json(
        project_context,
        input_data,
        results_data,
        equipment_selections,
        catalog_metadata
    )
    
    return spec


def find_required_airflow(equipment_id: str, results_data: Dict[str, Any]) -> float:
    """
    Find required airflow for equipment from results.
    
    Args:
        equipment_id: equipment ID
        results_data: resultados.json content
        
    Returns:
        Required m3/h or None if not found
    """
    for eq_result in results_data.get('equipment_results', []):
        if eq_result['equipment_id'] == equipment_id:
            return eq_result.get('required_m3_h_assigned')
    
    return None
