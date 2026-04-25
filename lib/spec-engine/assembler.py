"""Assembler - assemble spec.json structure from selection results."""

from typing import Dict, Any, List, Optional
from pathlib import Path


def assemble_spec_json(
    project_data: Dict[str, Any],
    input_data: Dict[str, Any],
    results_data: Dict[str, Any],
    equipment_selections: List[Dict[str, Any]],
    catalog_metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Assemble complete spec.json structure.
    
    Args:
        project_data: project context
        input_data: input.json content
        results_data: resultados.json content
        equipment_selections: list of selection results per equipment
        catalog_metadata: catalog metadata
        
    Returns:
        Complete spec.json dict
    """
    # Count selections
    selected_count = sum(1 for s in equipment_selections if s['selection_status'] == 'selected')
    failed_count = sum(1 for s in equipment_selections if s['selection_status'] == 'failed')
    
    # Determine overall spec status
    if failed_count == 0:
        spec_status = 'completed'
    elif selected_count > 0:
        spec_status = 'partial'
    else:
        spec_status = 'failed'
    
    spec = {
        'project': {
            'id': project_data['id'],
            'name': project_data['name'],
            'source_input': str(project_data.get('source_input', '')),
            'source_results': str(project_data.get('source_results', '')),
            'spec_status': spec_status
        },
        'summary': {
            'equipment_count': len(equipment_selections),
            'selected_models_count': selected_count,
            'failed_selections_count': failed_count
        },
        'equipment_specs': equipment_selections,
        'catalog_trace': {
            'catalog_source': catalog_metadata.get('source', 'local-catalog-v1'),
            'catalog_version': catalog_metadata.get('version', '1'),
            'local_only': True,
            'selection_mode': 'auto-select-model'
        }
    }
    
    return spec


def create_equipment_spec(
    equipment: Dict[str, Any],
    required_m3_h: float,
    selected_model: Optional[Dict[str, Any]],
    alternatives: List[Dict[str, Any]],
    selection_reason: str,
    constraints_used: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create single equipment spec entry.
    
    Args:
        equipment: equipment node from input.json
        required_m3_h: required airflow from resultados.json
        selected_model: selected model or None
        alternatives: alternative models list
        selection_reason: human-readable reason
        constraints_used: filters applied
        
    Returns:
        Equipment spec dict
    """
    spec = {
        'equipment_id': equipment['id'],
        'equipment_alias': equipment['alias'],
        'kind': equipment['kind'],
        'required_m3_h': required_m3_h,
        'selection_status': 'selected' if selected_model else 'failed',
        'selection_policy': 'closest-airflow-above',
        'selection_reason': selection_reason,
        'selected_model': format_model(selected_model) if selected_model else None,
        'alternatives': [format_model(m) for m in alternatives],
        'constraints_used': constraints_used,
        'notes': []
    }
    
    return spec


def format_model(model: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format model for output (extract relevant fields only).
    
    Args:
        model: full model dict
        
    Returns:
        Formatted model dict
    """
    formatted = {
        'brand': model['brand'],
        'model': model['model'],
        'airflow_m3_h': model['airflow_m3_h'],
        'voltage': model['voltage'],
        'frequency_hz': model['frequency_hz'],
        'power_w': model['power_w'],
        'power_kw': model['power_kw'],
        'installation_type': model['installation_type']
    }
    
    if 'image_asset' in model:
        formatted['image_asset'] = model['image_asset']
    
    return formatted
