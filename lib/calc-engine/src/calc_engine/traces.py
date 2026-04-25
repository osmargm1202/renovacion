"""
Trace generators: human-readable and machine-structured
"""
from typing import Optional


def trace_rh_human(volume_m3: float, rh_target: float, result_m3_h: float) -> str:
    """Generate human trace for RH method"""
    return f"Q_rh = V * RH = {volume_m3:.2f} * {rh_target:.2f} = {result_m3_h:.2f} m3/h"


def trace_rh_structured(volume_m3: float, rh_target: float, result_m3_h: float) -> dict:
    """Generate structured trace for RH method"""
    return {
        "formula": "required_m3_h = volume_m3 * rh_target",
        "inputs": {
            "volume_m3": volume_m3,
            "rh_target": rh_target
        },
        "operation": "multiply",
        "output": result_m3_h,
        "unit": "m3/h"
    }


def trace_people_human(people: int, caudal_target: float, result_m3_h: float) -> str:
    """Generate human trace for people method"""
    return f"Q_people = P * q = {people} * {caudal_target:.2f} = {result_m3_h:.2f} m3/h"


def trace_people_structured(people: int, caudal_target: float, result_m3_h: float) -> dict:
    """Generate structured trace for people method"""
    return {
        "formula": "required_m3_h = people * caudal_persona_target",
        "inputs": {
            "people": people,
            "caudal_persona_target": caudal_target
        },
        "operation": "multiply",
        "output": result_m3_h,
        "unit": "m3/h"
    }


def trace_not_applicable(reason: str) -> tuple[str, dict]:
    """Generate traces for non-applicable method"""
    human = f"Not applicable: {reason}"
    structured = {
        "formula": None,
        "inputs": {},
        "operation": None,
        "output": None,
        "unit": "m3/h"
    }
    return human, structured
