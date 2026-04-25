"""
Regression tests for CFM outputs in calc-engine.
RED first: these keys must not exist until CFM support is implemented.
"""
from calc_engine.area_engine import calculate_area
from calc_engine.aggregator import aggregate_equipment, compute_summary


def _rules():
    return {
        "tablas_renovaciones_aire": [
            {
                "sector": "residencial_domestico",
                "locales": [
                    {
                        "tipo_de_local": "Cuartos de baño",
                        "renovaciones_aire_por_hora": {"min": 5, "max": 7},
                    }
                ],
            }
        ],
        "tabla_caudal_por_persona": [],
    }


def _area():
    return {
        "id": "A1",
        "alias": "Baño principal",
        "catalog_type": "Cuartos de baño",
        "catalog_sector": "residencial_domestico",
        "dimensions": {
            "length_m": 2.0,
            "width_m": 4.0,
            "height_m": 2.7,
            "area_m2": 8.0,
            "volume_m3": 21.6,
        },
        "people": None,
        "equipment_ids": ["E1"],
    }


def test_area_result_includes_cfm_for_final_and_methods():
    result = calculate_area(_area(), _rules())

    assert result["required_m3_h_final"] == 129.6
    assert result["required_cfm_final"] == 76.28
    assert result["methods"]["rh"]["result_cfm"] == 76.28
    assert result["methods"]["people"]["result_cfm"] is None


def test_equipment_and_summary_include_cfm_totals():
    area_result = calculate_area(_area(), _rules())
    equipment = [
        {
            "id": "E1",
            "alias": "Extractor baño principal",
            "kind": "extractor",
            "cantidad": 1,
            "serves_area_ids": ["A1"],
        }
    ]

    equipment_results = aggregate_equipment(equipment, [area_result])
    summary = compute_summary([area_result], equipment_results)

    assert equipment_results[0]["required_m3_h_assigned"] == 129.6
    assert equipment_results[0]["required_cfm_assigned"] == 76.28
    assert summary["total_required_m3_h"] == 129.6
    assert summary["total_required_cfm"] == 76.28
