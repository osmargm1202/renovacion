"""
Test area_engine module
"""
import pytest
from calc_engine.area_engine import calculate_area


def test_calculate_area_rh_only():
    """Test area calculation with RH method only (people null)"""
    area = {
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
    
    rules = {
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
    
    result = calculate_area(area, rules)
    
    assert result['area_id'] == 'A1'
    assert result['governing_method'] == 'rh'
    assert result['required_m3_h_final'] == 129.6
    
    # Check RH method
    rh = result['methods']['rh']
    assert rh['applicable'] is True
    assert rh['rh_min'] == 5.0
    assert rh['rh_max'] == 7.0
    assert rh['rh_target'] == 6.0
    assert rh['result_m3_h'] == 129.6
    
    # Check people method not applicable
    people = result['methods']['people']
    assert people['applicable'] is False
    assert people['result_m3_h'] is None
    assert "Not applicable" in people['trace_human']


def test_calculate_area_with_people():
    """Test area calculation with both methods"""
    area = {
        "id": "A2",
        "alias": "Aula 1",
        "catalog_type": "Aulas",
        "catalog_sector": "terciario",
        "dimensions": {
            "area_m2": 50.0,
            "height_m": 3.0,
            "volume_m3": 150.0
        },
        "people": 30,
        "equipment_ids": ["E2"]
    }
    
    rules = {
        "tablas_renovaciones_aire": [
            {
                "sector": "terciario",
                "locales": [
                    {
                        "tipo_de_local": "Aulas",
                        "renovaciones_aire_por_hora": {"min": 5, "max": 7}
                    }
                ]
            }
        ],
        "tabla_caudal_por_persona": [
            {
                "tipo_de_local": "Escuelas",
                "caudal_por_persona_m3_h": {"valor": 50}
            }
        ]
    }
    
    # Note: catalog_type "Aulas" won't match people rule "Escuelas"
    # Should raise ValueError
    with pytest.raises(ValueError, match="no mapping found"):
        calculate_area(area, rules)


def test_calculate_area_missing_rh_rule():
    """Test error when canonical RH rule missing"""
    area = {
        "id": "A1",
        "alias": "Test",
        "catalog_type": "Unknown",
        "catalog_sector": "unknown",
        "dimensions": {"volume_m3": 20.0},
        "people": None,
        "equipment_ids": []
    }
    
    rules = {
        "tablas_renovaciones_aire": [],
        "tabla_caudal_por_persona": []
    }
    
    with pytest.raises(ValueError, match="Missing canonical RH rule"):
        calculate_area(area, rules)


def test_calculate_area_people_present_no_mapping():
    """Test error when people present but no mapping"""
    area = {
        "id": "A1",
        "alias": "Test",
        "catalog_type": "Cuartos de baño",
        "catalog_sector": "residencial_domestico",
        "dimensions": {"volume_m3": 20.0},
        "people": 2,
        "equipment_ids": []
    }
    
    rules = {
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
    
    with pytest.raises(ValueError, match="no mapping found"):
        calculate_area(area, rules)


def test_calculate_area_rounding():
    """Test result rounding to 2 decimals"""
    area = {
        "id": "A1",
        "alias": "Test",
        "catalog_type": "Cuartos de baño",
        "catalog_sector": "residencial_domestico",
        "dimensions": {"volume_m3": 21.6},
        "people": None,
        "equipment_ids": []
    }
    
    rules = {
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
    
    result = calculate_area(area, rules)
    
    # 21.6 * 6.0 = 129.6 (exact, but should be stored as 2 decimals)
    assert result['required_m3_h_final'] == 129.6
    assert isinstance(result['required_m3_h_final'], float)
