"""Filters - apply eligibility filters to models."""

from typing import Dict, Any, List, Optional


def apply_filters(
    models: List[Dict[str, Any]],
    kind: str,
    installation_type: Optional[str] = None,
    voltage: Optional[int] = None,
    frequency_hz: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Filter models by compatibility constraints.
    
    Args:
        models: list of model dicts
        kind: equipment kind (required)
        installation_type: installation type filter (optional)
        voltage: voltage filter (optional)
        frequency_hz: frequency filter (optional)
        
    Returns:
        Filtered list of models
    """
    filtered = []
    
    for model in models:
        # Kind filter (required)
        if model.get('kind') != kind:
            continue
        
        # Installation type filter (if specified)
        if installation_type is not None:
            if model.get('installation_type') != installation_type:
                continue
        
        # Voltage filter (if specified)
        if voltage is not None:
            if model.get('voltage') != voltage:
                continue
        
        # Frequency filter (if specified)
        if frequency_hz is not None:
            if model.get('frequency_hz') != frequency_hz:
                continue
        
        filtered.append(model)
    
    return filtered


def get_eligible_models(
    models: List[Dict[str, Any]],
    required_m3_h: float
) -> List[Dict[str, Any]]:
    """
    Get models meeting minimum airflow requirement.
    
    Args:
        models: filtered model list
        required_m3_h: minimum required airflow
        
    Returns:
        Models with airflow_m3_h >= required_m3_h
    """
    eligible = []
    
    for model in models:
        airflow = model.get('airflow_m3_h', 0)
        if airflow >= required_m3_h:
            eligible.append(model)
    
    return eligible
