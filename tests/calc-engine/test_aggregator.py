"""
Test aggregator module
"""
import pytest
from calc_engine.aggregator import aggregate_equipment, compute_summary


def test_aggregate_equipment_single_area():
    """Test equipment aggregation with single area"""
    equipment_list = [
        {
            "id": "E1",
            "alias": "Extractor 1",
            "kind": "extractor",
            "cantidad": 1,
            "serves_area_ids": ["A1"]
        }
    ]
    
    area_results = [
        {
            "area_id": "A1",
            "required_m3_h_final": 129.6
        }
    ]
    
    result = aggregate_equipment(equipment_list, area_results)
    
    assert len(result) == 1
    assert result[0]['equipment_id'] == 'E1'
    assert result[0]['required_m3_h_assigned'] == 129.6
    assert result[0]['sizing_status'] == 'not_sized_v1'


def test_aggregate_equipment_multiple_areas():
    """Test equipment aggregation with multiple areas"""
    equipment_list = [
        {
            "id": "E1",
            "alias": "Fan central",
            "kind": "fan",
            "cantidad": 1,
            "serves_area_ids": ["A1", "A2"]
        }
    ]
    
    area_results = [
        {"area_id": "A1", "required_m3_h_final": 100.0},
        {"area_id": "A2", "required_m3_h_final": 150.0}
    ]
    
    result = aggregate_equipment(equipment_list, area_results)
    
    assert result[0]['required_m3_h_assigned'] == 250.0


def test_aggregate_equipment_no_areas():
    """Test equipment with no assigned areas"""
    equipment_list = [
        {
            "id": "E1",
            "alias": "Spare",
            "kind": "extractor",
            "cantidad": 1,
            "serves_area_ids": []
        }
    ]
    
    area_results = []
    
    result = aggregate_equipment(equipment_list, area_results)
    
    assert result[0]['required_m3_h_assigned'] == 0.0


def test_compute_summary():
    """Test project summary computation"""
    area_results = [
        {
            "area_id": "A1",
            "required_m3_h_final": 129.6,
            "governing_method": "rh",
            "inputs": {"people": None}
        },
        {
            "area_id": "A2",
            "required_m3_h_final": 200.0,
            "governing_method": "people",
            "inputs": {"people": 4}
        },
        {
            "area_id": "A3",
            "required_m3_h_final": 100.0,
            "governing_method": "tie",
            "inputs": {"people": None}
        }
    ]
    
    equipment_results = [
        {"equipment_id": "E1"},
        {"equipment_id": "E2"}
    ]
    
    summary = compute_summary(area_results, equipment_results)
    
    assert summary['total_required_m3_h'] == 429.6
    assert summary['areas_count'] == 3
    assert summary['equipment_count'] == 2
    assert summary['areas_with_people'] == 1
    assert summary['areas_without_people'] == 2
    assert summary['governing_method_counts']['rh'] == 1
    assert summary['governing_method_counts']['people'] == 1
    assert summary['governing_method_counts']['tie'] == 1
