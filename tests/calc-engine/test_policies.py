"""
Test policies module
"""
import pytest
from calc_engine.policies import (
    compute_rh_target,
    compute_people_target,
    select_governing_method
)


def test_compute_rh_target_midpoint():
    """Test RH target computation with min/max uses midpoint"""
    rule = {"min": 5, "max": 7}
    rh_min, rh_max, rh_target = compute_rh_target(rule)
    
    assert rh_min == 5.0
    assert rh_max == 7.0
    assert rh_target == 6.0


def test_compute_rh_target_aprox():
    """Test RH target with aprox sets min=max=aprox"""
    rule = {"aprox": 5}
    rh_min, rh_max, rh_target = compute_rh_target(rule)
    
    assert rh_min == 5.0
    assert rh_max == 5.0
    assert rh_target == 5.0


def test_compute_rh_target_invalid():
    """Test RH target with invalid rule"""
    rule = {}
    rh_min, rh_max, rh_target = compute_rh_target(rule)
    
    assert rh_min is None
    assert rh_max is None
    assert rh_target is None


def test_compute_people_target_single():
    """Test people target with single valor"""
    rule = {"valor": 50}
    target = compute_people_target(rule)
    
    assert target == 50.0


def test_compute_people_target_midpoint():
    """Test people target with range uses midpoint (same-as-rh-policy)"""
    rule = {"min": 40, "max": 80}
    target = compute_people_target(rule)
    
    assert target == 60.0


def test_compute_people_target_invalid():
    """Test people target with invalid rule"""
    rule = {}
    target = compute_people_target(rule)
    
    assert target is None


def test_select_governing_rh_wins():
    """Test max-of-both: RH wins"""
    governing = select_governing_method(150.0, 100.0)
    assert governing == 'rh'


def test_select_governing_people_wins():
    """Test max-of-both: people wins"""
    governing = select_governing_method(100.0, 150.0)
    assert governing == 'people'


def test_select_governing_tie():
    """Test max-of-both: tie"""
    governing = select_governing_method(100.0, 100.0)
    assert governing == 'tie'


def test_select_governing_only_rh():
    """Test max-of-both: only RH applicable"""
    governing = select_governing_method(100.0, None)
    assert governing == 'rh'


def test_select_governing_only_people():
    """Test max-of-both: only people applicable"""
    governing = select_governing_method(None, 100.0)
    assert governing == 'people'
