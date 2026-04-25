"""
Calculation policies: midpoint, aprox->same, max-of-both
"""
from typing import Optional, Tuple


def compute_rh_target(rule: dict) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Compute rh_min, rh_max, rh_target from rule
    
    Policy:
    - min/max: rh_target = (min + max) / 2
    - aprox: rh_min = rh_max = aprox
    
    Returns:
        (rh_min, rh_max, rh_target) or (None, None, None) if invalid
    """
    if 'min' in rule and 'max' in rule:
        rh_min = float(rule['min'])
        rh_max = float(rule['max'])
        rh_target = round((rh_min + rh_max) / 2, 2)
        return rh_min, rh_max, rh_target
    
    if 'aprox' in rule:
        aprox = float(rule['aprox'])
        return aprox, aprox, aprox
    
    return None, None, None


def compute_people_target(rule: dict) -> Optional[float]:
    """
    Compute caudal_persona_target from people rule
    
    Policy:
    - valor: use direct
    - min/max: use midpoint (same-as-rh-policy)
    
    Returns:
        float target or None if invalid
    """
    if 'valor' in rule:
        return float(rule['valor'])
    
    if 'min' in rule and 'max' in rule:
        pmin = float(rule['min'])
        pmax = float(rule['max'])
        return round((pmin + pmax) / 2, 2)
    
    return None


def select_governing_method(
    rh_result: Optional[float],
    people_result: Optional[float]
) -> str:
    """
    Select governing method using max-of-both policy
    
    Returns:
        'rh', 'people', or 'tie'
    """
    if rh_result is None and people_result is None:
        return 'rh'  # fallback
    
    if rh_result is None:
        return 'people'
    
    if people_result is None:
        return 'rh'
    
    if rh_result > people_result:
        return 'rh'
    elif people_result > rh_result:
        return 'people'
    else:
        return 'tie'
