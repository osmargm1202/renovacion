"""
Test runner module (integration test)
"""
import json
import pytest
from pathlib import Path
from calc_engine.runner import run_calculation


def test_run_calculation_aurora_gmr(tmp_path):
    """Integration test with AURORA GMR fixture"""
    # Create input.json
    input_data = {
        "project": {
            "id": 1,
            "name": "AURORA GMR",
            "cliente": "BOHC SRL",
            "status": "calc_ready"
        },
        "areas": [
            {
                "id": "A1",
                "alias": "Baño principal",
                "catalog_type": "Cuartos de baño",
                "catalog_sector": "residencial_domestico",
                "dimensions": {
                    "length_m": 2.0,
                    "width_m": 4.0,
                    "height_m": 2.7,
                    "area_m2": 8.0,
                    "volume_m3": 21.6
                },
                "people": None,
                "equipment_ids": ["E1"]
            }
        ],
        "equipment": [
            {
                "id": "E1",
                "alias": "Extractor baño principal",
                "kind": "extractor",
                "cantidad": 1,
                "serves_area_ids": ["A1"]
            }
        ]
    }
    
    input_path = tmp_path / "input.json"
    with open(input_path, 'w') as f:
        json.dump(input_data, f)
    
    # Create minimal rules
    rules_data = {
        "tablas_renovaciones_aire": [
            {
                "sector": "residencial_domestico",
                "locales": [
                    {
                        "tipo_de_local": "Cuartos de baño",
                        "renovaciones_aire_por_hora": {"min": 5, "max": 7}
                    }
                ]
            }
        ],
        "tabla_caudal_por_persona": []
    }
    
    rules_path = tmp_path / "rules.json"
    with open(rules_path, 'w') as f:
        json.dump(rules_data, f)
    
    output_path = tmp_path / "resultados.json"
    
    # Run calculation
    result = run_calculation(input_path, rules_path, output_path)
    
    # Verify output file created
    assert output_path.exists()
    
    # Verify result structure
    assert result['project']['id'] == 1
    assert result['project']['name'] == 'AURORA GMR'
    assert result['project']['calculation_status'] == 'completed'
    
    # Verify summary
    assert result['summary']['total_required_m3_h'] == 129.6
    assert result['summary']['areas_count'] == 1
    assert result['summary']['equipment_count'] == 1
    assert result['summary']['areas_with_people'] == 0
    assert result['summary']['governing_method_counts']['rh'] == 1
    
    # Verify area result
    area_res = result['area_results'][0]
    assert area_res['area_id'] == 'A1'
    assert area_res['governing_method'] == 'rh'
    assert area_res['required_m3_h_final'] == 129.6
    
    # Verify equipment result
    equip_res = result['equipment_results'][0]
    assert equip_res['equipment_id'] == 'E1'
    assert equip_res['required_m3_h_assigned'] == 129.6
    assert equip_res['sizing_status'] == 'not_sized_v1'
    
    # Verify calculation trace
    trace = result['calculation_trace']
    assert trace['rounding_policy'] == 'round-2-decimals'
    assert trace['range_policy'] == 'midpoint'
    assert trace['governing_policy'] == 'max-of-both'


def test_run_calculation_not_calc_ready(tmp_path):
    """Test error when input status != calc_ready"""
    input_data = {
        "project": {"status": "draft"}
    }
    
    input_path = tmp_path / "input.json"
    with open(input_path, 'w') as f:
        json.dump(input_data, f)
    
    rules_path = tmp_path / "rules.json"
    with open(rules_path, 'w') as f:
        json.dump({}, f)
    
    with pytest.raises(ValueError, match="calc_ready"):
        run_calculation(input_path, rules_path)
