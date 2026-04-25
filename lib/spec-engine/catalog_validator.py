"""Catalog validator - validates model entries against contract."""

from typing import Dict, Any, List, Tuple


REQUIRED_FIELDS = [
    'brand',
    'model',
    'kind',
    'airflow_m3_h',
    'voltage',
    'frequency_hz',
    'power_w',
    'power_kw',
    'installation_type',
]


def validate_model(model: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate single model entry.
    
    Args:
        model: model dict
        
    Returns:
        (is_valid, errors) tuple
    """
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in model:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Type and value constraints
    if not isinstance(model['airflow_m3_h'], (int, float)) or model['airflow_m3_h'] <= 0:
        errors.append("airflow_m3_h must be > 0")
    
    if not isinstance(model['voltage'], int) or model['voltage'] <= 0:
        errors.append("voltage must be int > 0")
    
    if not isinstance(model['frequency_hz'], int) or model['frequency_hz'] <= 0:
        errors.append("frequency_hz must be int > 0")
    
    if not isinstance(model['power_w'], (int, float)) or model['power_w'] < 0:
        errors.append("power_w must be >= 0")
    
    if not isinstance(model['power_kw'], (int, float)) or model['power_kw'] < 0:
        errors.append("power_kw must be >= 0")
    
    # Consistency check: power_kw == power_w / 1000
    if 'power_w' in model and 'power_kw' in model:
        expected_kw = round(model['power_w'] / 1000.0, 6)
        actual_kw = round(model['power_kw'], 6)
        if abs(expected_kw - actual_kw) > 1e-5:
            errors.append(f"power_kw inconsistent with power_w: {model['power_kw']} != {model['power_w']}/1000")
    
    return len(errors) == 0, errors


def validate_catalog(models: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate entire catalog.
    
    Args:
        models: list of model dicts
        
    Returns:
        (all_valid, invalid_entries) where invalid_entries contains models with errors
    """
    invalid_entries = []
    
    for idx, model in enumerate(models):
        is_valid, errors = validate_model(model)
        if not is_valid:
            invalid_entries.append({
                'index': idx,
                'model': model.get('model', 'UNKNOWN'),
                'errors': errors
            })
    
    return len(invalid_entries) == 0, invalid_entries
