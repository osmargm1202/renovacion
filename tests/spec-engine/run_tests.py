#!/usr/bin/env python3
"""
Simple test runner without pytest dependency.
Run with: python3 tests/spec-engine/run_tests.py
"""

import sys
import importlib.util
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def load_module_from_path(module_name, file_path):
    """Load Python module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load spec-engine modules
base_path = project_root / 'lib' / 'spec-engine'
catalog_validator = load_module_from_path('catalog_validator', base_path / 'catalog_validator.py')
filters_mod = load_module_from_path('filters', base_path / 'filters.py')
selector = load_module_from_path('selector', base_path / 'selector.py')
assembler = load_module_from_path('assembler', base_path / 'assembler.py')

def run_tests():
    """Run all tests and report results."""
    
    passed = 0
    failed = 0
    errors = []
    
    # Catalog validator tests
    print("Running catalog_validator tests...")
    try:
        # Test valid model
        model_valid = {
            'brand': 'ORGM',
            'model': 'EX-150',
            'kind': 'extractor',
            'airflow_m3_h': 140.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 45,
            'power_kw': 0.045,
            'installation_type': 'muro'
        }
        is_valid, errs = catalog_validator.validate_model(model_valid)
        assert is_valid, f"Valid model should pass: {errs}"
        passed += 1
        print("  ✓ validate_model_valid")
        
        # Test missing field
        model_missing = {
            'brand': 'ORGM',
            'model': 'EX-150',
            'airflow_m3_h': 140.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 45,
            'power_kw': 0.045,
            'installation_type': 'muro'
        }
        is_valid, errs = catalog_validator.validate_model(model_missing)
        assert not is_valid, "Model with missing field should fail"
        passed += 1
        print("  ✓ validate_model_missing_field")
        
        # Test power inconsistency
        model_bad_power = model_valid.copy()
        model_bad_power['power_kw'] = 0.999
        is_valid, errs = catalog_validator.validate_model(model_bad_power)
        assert not is_valid, "Model with inconsistent power should fail"
        passed += 1
        print("  ✓ validate_model_power_inconsistency")
        
    except Exception as e:
        failed += 3
        errors.append(f"catalog_validator tests: {e}")
        print(f"  ✗ Error: {e}")
    
    # Filters tests
    print("\nRunning filters tests...")
    try:
        # Test kind filter
        models = [
            {'kind': 'extractor', 'model': 'EX-1'},
            {'kind': 'inyector', 'model': 'INY-1'},
            {'kind': 'extractor', 'model': 'EX-2'}
        ]
        filtered = filters_mod.apply_filters(models, kind='extractor')
        assert len(filtered) == 2, "Should filter by kind"
        passed += 1
        print("  ✓ apply_filters_kind")
        
        # Test eligibility
        models = [
            {'airflow_m3_h': 100.0, 'model': 'EX-1'},
            {'airflow_m3_h': 140.0, 'model': 'EX-2'},
            {'airflow_m3_h': 160.0, 'model': 'EX-3'}
        ]
        eligible = filters_mod.get_eligible_models(models, required_m3_h=130.0)
        assert len(eligible) == 2, "Should get eligible models"
        assert {m['model'] for m in eligible} == {'EX-2', 'EX-3'}
        passed += 1
        print("  ✓ get_eligible_models")
        
    except Exception as e:
        failed += 2
        errors.append(f"filters tests: {e}")
        print(f"  ✗ Error: {e}")
    
    # Selector tests
    print("\nRunning selector tests...")
    try:
        # Test selection
        models = [
            {'airflow_m3_h': 200.0, 'power_w': 60, 'model': 'EX-200'},
            {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150'},
            {'airflow_m3_h': 160.0, 'power_w': 50, 'model': 'EX-160'}
        ]
        selected, reason = selector.select_model(models, required_m3_h=130.0)
        assert selected['model'] == 'EX-150', "Should select closest airflow"
        passed += 1
        print("  ✓ select_model_closest")
        
        # Test tie-break
        models_tie = [
            {'airflow_m3_h': 140.0, 'power_w': 50, 'model': 'EX-150-HP'},
            {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150-LP'}
        ]
        selected, reason = selector.select_model(models_tie, required_m3_h=130.0)
        assert selected['model'] == 'EX-150-LP', "Should tie-break by power"
        passed += 1
        print("  ✓ select_model_tiebreak")
        
        # Test alternatives
        models_alt = [
            {'airflow_m3_h': 140.0, 'power_w': 45, 'model': 'EX-150'},
            {'airflow_m3_h': 160.0, 'power_w': 50, 'model': 'EX-160'},
            {'airflow_m3_h': 200.0, 'power_w': 60, 'model': 'EX-200'}
        ]
        selected = models_alt[0]
        alternatives = selector.get_alternatives(models_alt, selected, required_m3_h=130.0)
        assert len(alternatives) == 2, "Should get alternatives"
        assert selected['model'] not in {m['model'] for m in alternatives}
        passed += 1
        print("  ✓ get_alternatives")
        
    except Exception as e:
        failed += 3
        errors.append(f"selector tests: {e}")
        print(f"  ✗ Error: {e}")
    
    # Assembler tests
    print("\nRunning assembler tests...")
    try:
        # Test format model
        model = {
            'brand': 'ORGM',
            'model': 'EX-150',
            'kind': 'extractor',
            'airflow_m3_h': 140.0,
            'voltage': 120,
            'frequency_hz': 60,
            'power_w': 45,
            'power_kw': 0.045,
            'installation_type': 'muro',
            'notes': ['internal']
        }
        formatted = assembler.format_model(model)
        assert 'brand' in formatted
        assert 'notes' not in formatted
        assert 'kind' not in formatted
        passed += 1
        print("  ✓ format_model")
        
        # Test create spec
        equipment = {
            'id': 'E1',
            'alias': 'Test',
            'kind': 'extractor'
        }
        selected = model
        spec = assembler.create_equipment_spec(
            equipment,
            required_m3_h=129.6,
            selected_model=selected,
            alternatives=[],
            selection_reason='Test reason',
            constraints_used={'kind': 'extractor'}
        )
        assert spec['equipment_id'] == 'E1'
        assert spec['selection_status'] == 'selected'
        passed += 1
        print("  ✓ create_equipment_spec")
        
        # Test assemble
        project_data = {
            'id': 1,
            'name': 'Test',
            'source_input': '/path/input.json',
            'source_results': '/path/results.json'
        }
        equipment_selections = [
            {'equipment_id': 'E1', 'selection_status': 'selected'}
        ]
        catalog_metadata = {'version': '1', 'source': 'test'}
        spec_json = assembler.assemble_spec_json(
            project_data,
            {},
            {},
            equipment_selections,
            catalog_metadata
        )
        assert spec_json['project']['id'] == 1
        assert spec_json['project']['spec_status'] == 'completed'
        passed += 1
        print("  ✓ assemble_spec_json")
        
    except Exception as e:
        failed += 3
        errors.append(f"assembler tests: {e}")
        print(f"  ✗ Error: {e}")
    
    # Summary
    print("\n" + "="*60)
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {failed}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(run_tests())
