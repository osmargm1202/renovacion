"""
Aggregation logic: equipment results and project summary
"""
from typing import List
from .policies import m3_h_to_cfm


def aggregate_equipment(
    equipment_list: List[dict],
    area_results: List[dict]
) -> List[dict]:
    """
    Aggregate required m3/h per equipment from area results
    
    In v1: direct sum of areas served
    """
    equipment_results = []
    
    for equip in equipment_list:
        equip_id = equip['id']
        serves_area_ids = equip.get('serves_area_ids', [])
        
        # Sum demand from served areas
        total_assigned = 0.0
        for area_res in area_results:
            if area_res['area_id'] in serves_area_ids:
                total_assigned += area_res['required_m3_h_final']
        
        total_assigned = round(total_assigned, 2)
        
        equipment_results.append({
            "equipment_id": equip_id,
            "equipment_alias": equip['alias'],
            "kind": equip.get('kind'),
            "cantidad": equip.get('cantidad'),
            "serves_area_ids": serves_area_ids,
            "required_m3_h_assigned": total_assigned,
            "required_cfm_assigned": m3_h_to_cfm(total_assigned),
            "sizing_status": "not_sized_v1",
            "notes": []
        })
    
    return equipment_results


def compute_summary(
    area_results: List[dict],
    equipment_results: List[dict]
) -> dict:
    """
    Compute project summary
    """
    total_m3_h = sum(ar['required_m3_h_final'] for ar in area_results)
    total_m3_h = round(total_m3_h, 2)
    
    areas_count = len(area_results)
    equipment_count = len(equipment_results)
    
    areas_with_people = sum(
        1 for ar in area_results
        if ar['inputs']['people'] is not None
    )
    areas_without_people = areas_count - areas_with_people
    
    # Count governing methods
    gov_counts = {"rh": 0, "people": 0, "tie": 0}
    for ar in area_results:
        method = ar['governing_method']
        if method in gov_counts:
            gov_counts[method] += 1
    
    return {
        "total_required_m3_h": total_m3_h,
        "total_required_cfm": m3_h_to_cfm(total_m3_h),
        "areas_count": areas_count,
        "equipment_count": equipment_count,
        "areas_with_people": areas_with_people,
        "areas_without_people": areas_without_people,
        "governing_method_counts": gov_counts
    }
