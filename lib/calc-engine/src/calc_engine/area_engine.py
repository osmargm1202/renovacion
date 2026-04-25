"""
Area calculation engine: RH + people methods per area
"""
from typing import Optional
from .rule_loader import resolve_rh_rule, resolve_people_rule
from .policies import compute_rh_target, compute_people_target, select_governing_method
from .traces import (
    trace_rh_human, trace_rh_structured,
    trace_people_human, trace_people_structured,
    trace_not_applicable
)


def calculate_area(
    area: dict,
    rules: dict
) -> dict:
    """
    Calculate required m3/h for one area
    
    Returns:
        area_result dict matching resultados.json schema
    
    Raises:
        ValueError if canonical RH rule missing or people mapping failed
    """
    area_id = area['id']
    area_alias = area['alias']
    catalog_type = area['catalog_type']
    catalog_sector = area['catalog_sector']
    volume_m3 = area['dimensions']['volume_m3']
    people = area.get('people')
    equipment_ids = area.get('equipment_ids', [])
    
    # RH method (always applicable)
    rh_rule = resolve_rh_rule(rules, catalog_sector, catalog_type)
    if rh_rule is None:
        raise ValueError(
            f"Area {area_id}: Missing canonical RH rule for "
            f"catalog_sector={catalog_sector}, catalog_type={catalog_type}"
        )
    
    rh_min, rh_max, rh_target = compute_rh_target(rh_rule)
    if rh_target is None:
        raise ValueError(f"Area {area_id}: Invalid RH rule format")
    
    result_rh = round(volume_m3 * rh_target, 2)
    
    rh_method = {
        "applicable": True,
        "source": "rules/renovacion.json.tablas_renovaciones_aire",
        "rh_min": rh_min,
        "rh_max": rh_max,
        "rh_target": rh_target,
        "result_m3_h": result_rh,
        "trace_human": trace_rh_human(volume_m3, rh_target, result_rh),
        "trace_structured": trace_rh_structured(volume_m3, rh_target, result_rh)
    }
    
    # People method
    people_method = None
    result_people = None
    
    if people is None:
        # Not applicable: people null
        trace_h, trace_s = trace_not_applicable("people is null")
        people_method = {
            "applicable": False,
            "source": "rules/renovacion.json.tabla_caudal_por_persona",
            "caudal_persona_target": None,
            "result_m3_h": None,
            "trace_human": trace_h,
            "trace_structured": trace_s
        }
    else:
        # Lookup people rule
        people_rule = resolve_people_rule(rules, catalog_type)
        
        if people_rule is None:
            raise ValueError(
                f"Area {area_id}: People present ({people}) but no mapping found "
                f"for catalog_type={catalog_type}"
            )
        
        caudal_target = compute_people_target(people_rule)
        if caudal_target is None:
            raise ValueError(f"Area {area_id}: Invalid people rule format")
        
        result_people = round(people * caudal_target, 2)
        
        people_method = {
            "applicable": True,
            "source": "rules/renovacion.json.tabla_caudal_por_persona",
            "caudal_persona_target": caudal_target,
            "result_m3_h": result_people,
            "trace_human": trace_people_human(people, caudal_target, result_people),
            "trace_structured": trace_people_structured(people, caudal_target, result_people)
        }
    
    # Governing method
    governing = select_governing_method(result_rh, result_people)
    
    if governing == 'rh':
        final_m3_h = result_rh
    elif governing == 'people':
        final_m3_h = result_people
    else:  # tie
        final_m3_h = result_rh  # both equal
    
    return {
        "area_id": area_id,
        "area_alias": area_alias,
        "catalog_type": catalog_type,
        "catalog_sector": catalog_sector,
        "inputs": {
            "dimensions": area['dimensions'],
            "volume_m3": volume_m3,
            "people": people
        },
        "methods": {
            "rh": rh_method,
            "people": people_method
        },
        "governing_method": governing,
        "required_m3_h_final": final_m3_h,
        "linked_equipment_ids": equipment_ids,
        "notes": []
    }
