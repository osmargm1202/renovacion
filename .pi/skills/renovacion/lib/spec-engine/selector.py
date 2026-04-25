"""Selector - select best model using closest-airflow-above + lower-power tie-break."""

from typing import Dict, Any, List, Optional, Tuple


def select_model(
    eligible_models: List[Dict[str, Any]],
    required_m3_h: float
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Select best model using closest-airflow-above policy.
    
    Policy:
    - Select model with minimum excess over required_m3_h
    - Tie-break: lower power_w
    
    Args:
        eligible_models: models with airflow >= required
        required_m3_h: required airflow
        
    Returns:
        (selected_model, reason) or (None, reason) if no eligible
    """
    if not eligible_models:
        return None, "No eligible model with sufficient airflow"
    
    # Calculate excess for each model
    candidates = []
    for model in eligible_models:
        airflow = model['airflow_m3_h']
        excess = airflow - required_m3_h
        power = model['power_w']
        candidates.append((excess, power, model))
    
    # Sort by excess (ascending), then power (ascending)
    candidates.sort(key=lambda x: (x[0], x[1]))
    
    # Select first candidate
    selected = candidates[0][2]
    
    # Build reason
    excess = candidates[0][0]
    if len(candidates) > 1 and candidates[0][0] == candidates[1][0]:
        reason = f"Selected smallest airflow above required demand ({selected['airflow_m3_h']} m³/h vs {required_m3_h} m³/h required); tie broken by lower power ({selected['power_w']}W)."
    else:
        reason = f"Selected smallest airflow above required demand ({selected['airflow_m3_h']} m³/h vs {required_m3_h} m³/h required)."
    
    return selected, reason


def get_alternatives(
    eligible_models: List[Dict[str, Any]],
    selected_model: Optional[Dict[str, Any]],
    required_m3_h: float,
    max_count: int = 3
) -> List[Dict[str, Any]]:
    """
    Get top alternative models excluding selected.
    
    Args:
        eligible_models: all eligible models
        selected_model: the selected model (to exclude)
        required_m3_h: required airflow
        max_count: max alternatives to return
        
    Returns:
        Up to max_count alternative models, ordered by selection criterion
    """
    if selected_model is None:
        return []
    
    # Filter out selected model
    alternatives = [m for m in eligible_models if m['model'] != selected_model['model']]
    
    # Sort by same criterion as selection
    candidates = []
    for model in alternatives:
        airflow = model['airflow_m3_h']
        excess = airflow - required_m3_h
        power = model['power_w']
        candidates.append((excess, power, model))
    
    candidates.sort(key=lambda x: (x[0], x[1]))
    
    # Take top max_count
    result = [c[2] for c in candidates[:max_count]]
    
    return result
