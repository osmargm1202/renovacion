"""
Test rule_loader module
"""
import json
import pytest
from pathlib import Path
from calc_engine.rule_loader import load_rules, resolve_rh_rule, resolve_people_rule


def test_resolve_rh_rule_min_max():
    """Test RH rule with min/max range"""
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
        ]
    }
    
    result = resolve_rh_rule(rules, "residencial_domestico", "Cuartos de baño")
    assert result == {"min": 5, "max": 7}


def test_resolve_rh_rule_aprox():
    """Test RH rule with aprox"""
    rules = {
        "tablas_renovaciones_aire": [
            {
                "sector": "terciario",
                "locales": [
                    {
                        "tipo_de_local": "Garages",
                        "renovaciones_aire_por_hora": {"aprox": 5}
                    }
                ]
            }
        ]
    }
    
    result = resolve_rh_rule(rules, "terciario", "Garages")
    assert result == {"aprox": 5}


def test_resolve_rh_rule_not_found():
    """Test RH rule lookup failure"""
    rules = {"tablas_renovaciones_aire": []}
    
    result = resolve_rh_rule(rules, "unknown", "Unknown")
    assert result is None


def test_resolve_people_rule_single():
    """Test people rule with single valor"""
    rules = {
        "tabla_caudal_por_persona": [
            {
                "tipo_de_local": "Escuelas",
                "caudal_por_persona_m3_h": {"valor": 50}
            }
        ]
    }
    
    result = resolve_people_rule(rules, "Escuelas")
    assert result == {"valor": 50}


def test_resolve_people_rule_range():
    """Test people rule with min/max"""
    rules = {
        "tabla_caudal_por_persona": [
            {
                "tipo_de_local": "Habitaciones",
                "caudal_por_persona_m3_h": {"min": 40, "max": 80}
            }
        ]
    }
    
    result = resolve_people_rule(rules, "Habitaciones")
    assert result == {"min": 40, "max": 80}


def test_resolve_people_rule_not_found():
    """Test people rule lookup failure"""
    rules = {"tabla_caudal_por_persona": []}
    
    result = resolve_people_rule(rules, "Unknown")
    assert result is None
