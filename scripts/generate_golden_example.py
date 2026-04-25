#!/usr/bin/env python3
"""Generate golden example resultados.json for AURORA GMR"""
import sys
from pathlib import Path

# Add lib/calc-engine/src to path
calc_engine_path = Path(__file__).parent.parent / "lib" / "calc-engine" / "src"
sys.path.insert(0, str(calc_engine_path))

from calc_engine.runner import run_calculation

def main():
    base = Path(__file__).parent.parent
    
    input_path = base / "proyectos" / "1" / "input.json"
    rules_path = base / "rules" / "renovacion.json"
    output_path = base / "proyectos" / "1" / "resultados.json"
    
    print(f"Input: {input_path}")
    print(f"Rules: {rules_path}")
    print(f"Output: {output_path}")
    
    result = run_calculation(input_path, rules_path, output_path)
    
    print("\n✅ Golden example generated!")
    print(f"\nSummary:")
    print(f"  Total required: {result['summary']['total_required_m3_h']} m³/h")
    print(f"  Areas: {result['summary']['areas_count']}")
    print(f"  Equipment: {result['summary']['equipment_count']}")
    print(f"  Governing: {result['summary']['governing_method_counts']}")

if __name__ == "__main__":
    main()
