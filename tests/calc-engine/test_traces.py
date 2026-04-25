"""
Test traces module
"""
import pytest
from calc_engine.traces import (
    trace_rh_human,
    trace_rh_structured,
    trace_people_human,
    trace_people_structured,
    trace_not_applicable
)


def test_trace_rh_human():
    """Test RH human trace format"""
    trace = trace_rh_human(21.6, 6.0, 129.6)
    assert trace == "Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h"


def test_trace_rh_structured():
    """Test RH structured trace format"""
    trace = trace_rh_structured(21.6, 6.0, 129.6)
    
    assert trace['formula'] == "required_m3_h = volume_m3 * rh_target"
    assert trace['inputs']['volume_m3'] == 21.6
    assert trace['inputs']['rh_target'] == 6.0
    assert trace['operation'] == 'multiply'
    assert trace['output'] == 129.6
    assert trace['unit'] == 'm3/h'


def test_trace_people_human():
    """Test people human trace format"""
    trace = trace_people_human(4, 75.0, 300.0)
    assert trace == "Q_people = P * q = 4 * 75.00 = 300.00 m3/h"


def test_trace_people_structured():
    """Test people structured trace format"""
    trace = trace_people_structured(4, 75.0, 300.0)
    
    assert trace['formula'] == "required_m3_h = people * caudal_persona_target"
    assert trace['inputs']['people'] == 4
    assert trace['inputs']['caudal_persona_target'] == 75.0
    assert trace['operation'] == 'multiply'
    assert trace['output'] == 300.0
    assert trace['unit'] == 'm3/h'


def test_trace_not_applicable():
    """Test not-applicable trace format"""
    trace_h, trace_s = trace_not_applicable("people is null")
    
    assert trace_h == "Not applicable: people is null"
    assert trace_s['formula'] is None
    assert trace_s['operation'] is None
    assert trace_s['output'] is None
    assert trace_s['unit'] == 'm3/h'
