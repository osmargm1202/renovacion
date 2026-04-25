"""
Main calculation runner: orchestrates full calc flow
"""
import json
from pathlib import Path
from typing import Optional
from .rule_loader import load_rules
from .area_engine import calculate_area
from .aggregator import aggregate_equipment, compute_summary


def run_calculation(
    input_path: Path,
    rules_path: Path,
    output_path: Optional[Path] = None
) -> dict:
    """
    Run full calculation from input.json to resultados.json
    
    Args:
        input_path: Path to input.json
        rules_path: Path to rules/renovacion.json
        output_path: Optional path to save resultados.json
    
    Returns:
        resultados dict
    
    Raises:
        ValueError: If input status != calc_ready or calculation fails
    """
    # Load input
    with open(input_path, 'r', encoding='utf-8') as f:
        input_data = json.load(f)
    
    # Validate status
    if input_data.get('project', {}).get('status') != 'calc_ready':
        raise ValueError("Input status must be 'calc_ready'")
    
    # Load rules
    rules = load_rules(rules_path)
    
    # Calculate areas
    area_results = []
    for area in input_data.get('areas', []):
        area_result = calculate_area(area, rules)
        area_results.append(area_result)
    
    # Aggregate equipment
    equipment_results = aggregate_equipment(
        input_data.get('equipment', []),
        area_results
    )
    
    # Compute summary
    summary = compute_summary(area_results, equipment_results)
    
    # Build resultados
    project_info = input_data.get('project', {})
    resultados = {
        "project": {
            "id": project_info.get('id'),
            "name": project_info.get('name'),
            "source_input": str(input_path),
            "calculation_status": "completed"
        },
        "summary": summary,
        "area_results": area_results,
        "equipment_results": equipment_results,
        "calculation_trace": {
            "rounding_policy": "round-2-decimals",
            "range_policy": "midpoint",
            "governing_policy": "max-of-both"
        }
    }
    
    # Save if output path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    return resultados
