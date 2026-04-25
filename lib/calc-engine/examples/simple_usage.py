#!/usr/bin/env python3
"""
Simple usage example for calc_engine

This shows how calculator-agent will use the calc engine.
"""
from pathlib import Path
import sys

# In production, calc_engine will be installed as package
# For this example, add to path
calc_engine_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(calc_engine_src))

from calc_engine import run_calculation


def main():
    """Run calculation for a project"""
    
    # Paths (normally from calculator-agent context)
    project_id = 1
    base = Path(__file__).parent.parent.parent.parent
    
    input_path = base / "proyectos" / str(project_id) / "input.json"
    rules_path = base / "rules" / "renovacion.json"
    output_path = base / "proyectos" / str(project_id) / "resultados.json"
    
    print(f"🔧 Running calculation for project {project_id}...")
    print(f"   Input: {input_path.name}")
    print(f"   Rules: {rules_path.name}")
    
    try:
        # Main calculation
        result = run_calculation(
            input_path=input_path,
            rules_path=rules_path,
            output_path=output_path
        )
        
        # Success
        print(f"\n✅ Calculation completed!")
        print(f"\n📊 Summary:")
        print(f"   Total required: {result['summary']['total_required_m3_h']} m³/h")
        print(f"   Areas: {result['summary']['areas_count']}")
        print(f"   Equipment: {result['summary']['equipment_count']}")
        print(f"   Areas with people: {result['summary']['areas_with_people']}")
        print(f"   Areas without people: {result['summary']['areas_without_people']}")
        
        print(f"\n🎯 Governing methods:")
        for method, count in result['summary']['governing_method_counts'].items():
            if count > 0:
                print(f"   {method}: {count}")
        
        print(f"\n💾 Output saved to: {output_path}")
        
        # calculator-agent would return structured response here
        return {
            "status": "completed",
            "summary": "Calculation successful",
            "artifacts_created": [str(output_path)],
            "artifacts_updated": [],
            "questions_for_user": [],
            "next_recommended_agent": "spec-agent",
            "notes_for_orchestrator": [
                f"Calculated {result['summary']['areas_count']} areas",
                f"Total demand: {result['summary']['total_required_m3_h']} m³/h"
            ]
        }
        
    except ValueError as e:
        # Calculation error
        print(f"\n❌ Calculation failed: {e}")
        
        # calculator-agent would return error response
        return {
            "status": "failed",
            "summary": f"Calculation error: {e}",
            "artifacts_created": [],
            "artifacts_updated": [],
            "questions_for_user": [],
            "next_recommended_agent": None,
            "notes_for_orchestrator": [str(e)]
        }


if __name__ == "__main__":
    response = main()
    print(f"\n📋 Agent response:")
    print(f"   Status: {response['status']}")
    if response['next_recommended_agent']:
        print(f"   Next: {response['next_recommended_agent']}")
