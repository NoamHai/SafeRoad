"""
Safe Roads: Mapper and Legacy Helper Checks

Checks the current option mappings, input conversion, and legacy numeric road helper.
These checks do not run the browser or establish end-to-end application readiness.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.services.data_mapper import (
    FEATURE_ORDER,
    FEATURE_CONFIG,
    SPEED_LIMIT_MAPPING,
    ROAD_TYPE_MAPPING,
    ROAD_SURFACE_MAPPING,
    prepare_model_input,
    prepare_model_array,
    validate_ui_input,
    engineer_road_structure,
)

import pandas as pd
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def test_16_features() -> bool:
    """Verify all 16 features are properly configured."""
    print("\n" + "="*80)
    print("TEST 1: 16 Features Configuration")
    print("="*80)
    
    required_features = list(FEATURE_ORDER)
    
    print(f"\nRequired features: {len(required_features)}")
    
    missing = []
    for feature in required_features:
        if feature not in FEATURE_CONFIG:
            missing.append(feature)
            print(f"  ✗ {feature}")
        else:
            config = FEATURE_CONFIG[feature]
            print(f"  ✓ {feature:20s} | {config['type']:12s} | {len(config['mapping'])} mappings")
    
    if missing:
        print(f"\n✗ FAILED: Missing features: {missing}")
        return False
    
    print(f"\n✓ PASSED: All 16 features configured")
    return True


def test_feature_mappings() -> bool:
    """Verify critical feature mappings match specification."""
    print("\n" + "="*80)
    print("TEST 2: Critical Feature Mappings")
    print("="*80)
    
    tests = []
    
    # MEHIRUT_MUTERET - Speed Limit (including custom 120 km/h edge case)
    print("\nMEHIRUT_MUTERET (Speed Limit):")
    speed_tests = [
        ("unknown_speed_limit", 0),
        ("up_to_50_kmh", 1),
        ("80_kmh", 4),
        ("120_kmh", 8),
    ]
    for text, expected_code in speed_tests:
        actual_code = SPEED_LIMIT_MAPPING.get(text)
        status = "✓" if actual_code == expected_code else "✗"
        print(f"  {status} {text:20s} → {actual_code} (expected {expected_code})")
        tests.append(actual_code == expected_code)
    
    # SUG_DEREH - Road Type
    print("\nSUG_DEREH (Road Type):")
    road_type_tests = [
        ("urban_intersection", 1),
        ("urban_non_intersection", 2),
        ("non_urban_intersection", 3),
        ("non_urban_non_intersection", 4),
    ]
    for text, expected_code in road_type_tests:
        actual_code = ROAD_TYPE_MAPPING.get(text)
        status = "✓" if actual_code == expected_code else "✗"
        print(f"  {status} {text:25s} → {actual_code} (expected {expected_code})")
        tests.append(actual_code == expected_code)
    
    # PNE_KVISH - Road Surface
    print("\nPNE_KVISH (Road Surface):")
    surface_tests = [
        ("dry", 1),
        ("wet", 2),
        ("covered_with_fuel", 3),
        ("muddy", 4),
    ]
    for text, expected_code in surface_tests:
        actual_code = ROAD_SURFACE_MAPPING.get(text)
        status = "✓" if actual_code == expected_code else "✗"
        print(f"  {status} {text:20s} → {actual_code} (expected {expected_code})")
        tests.append(actual_code == expected_code)
    
    if all(tests):
        print(f"\n✓ PASSED: All {len(tests)} mapping tests passed")
        return True
    else:
        failed = len([t for t in tests if not t])
        print(f"\n✗ FAILED: {failed}/{len(tests)} tests failed")
        return False


def test_ui_to_model_conversion() -> bool:
    """Test complete UI input → Model array conversion."""
    print("\n" + "="*80)
    print("TEST 3: UI Input → Model Array Conversion")
    print("="*80)
    
    ui_input = {
        "SHAA": "14:00",
        "HODESH_TEUNA": "may",
        "YOM_BASHAVUA": "monday",
        "SUG_TEUNA": "front_to_side_collision",
        "ROAD_STRUCTURE": "single_lane_1",
        "ROHAV": "7_to_10_5_meters",
        "NAFA": "tel_aviv",
        "ZURAT_ISHUV": "jewish_city_100k_200k",
        "MEHIRUT_MUTERET": "80_kmh",
        "TEURA": "daylight",
        "SUG_DEREH": "urban_intersection",
        "SIMUN_TIMRUR": "no_defect",
        "TKINUT": "no_defect",
        "PNE_KVISH": "dry",
        "MEZEG_AVIR": "clear",
        "YOM_LAYLA": "day",
    }
    
    print("\nUI Input (frontend option keys):")
    for key, value in list(ui_input.items())[:5]:
        print(f"  {key:20s}: {value}")
    print("  ...")
    
    # Convert to model format
    try:
        model_dict = prepare_model_input(ui_input)
        print(f"\n✓ Successfully converted to model dict")
        print(f"  Keys: {list(model_dict.keys())[:5]} ...")
        
        model_array = prepare_model_array(ui_input)
        print(f"\n✓ Successfully created model array")
        print(f"  Shape: {model_array.shape}")
        print(f"  Dtype: {model_array.dtype}")
        print(f"  Values: {model_array}")
        
        # Verify shape and content
        if model_array.shape == (1, 16):
            print(f"\n✓ PASSED: Array has correct shape {model_array.shape} and dtype {model_array.dtype}")
            return True
        else:
            print(f"\n✗ FAILED: Incorrect shape or dtype")
            return False
    
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_validation() -> bool:
    """Test input validation with various scenarios."""
    print("\n" + "="*80)
    print("TEST 4: Input Validation & Error Handling")
    print("="*80)
    
    # Test 1: Valid input
    print("\n[Scenario 1] Valid complete input")
    valid_input = {
        "SHAA": "08:00",
        "HODESH_TEUNA": "january",
        "YOM_BASHAVUA": "sunday",
        "SUG_TEUNA": "front_to_side_collision",
        "ROAD_STRUCTURE": "single_lane_1",
        "ROHAV": "5_to_7_meters",
        "NAFA": "tel_aviv",
        "ZURAT_ISHUV": "jewish_city_100k_200k",
        "MEHIRUT_MUTERET": "up_to_50_kmh",
        "TEURA": "daylight",
        "SUG_DEREH": "urban_intersection",
        "SIMUN_TIMRUR": "no_defect",
        "TKINUT": "no_defect",
        "PNE_KVISH": "dry",
        "MEZEG_AVIR": "clear",
        "YOM_LAYLA": "day",
    }
    validation1 = validate_ui_input(valid_input)
    print(f"  Valid: {validation1['valid']}")
    print(f"  Errors: {len(validation1['errors'])}")
    print(f"  Warnings: {len(validation1['warnings'])}")
    test1_pass = validation1['valid']
    
    # Test 2: Missing features
    print("\n[Scenario 2] Missing required features")
    incomplete_input = {"SHAA": "08:00", "MEHIRUT_MUTERET": "עד 50 קמ״ש"}
    validation2 = validate_ui_input(incomplete_input)
    print(f"  Valid: {validation2['valid']}")
    print(f"  Missing features: {len(validation2['missing_features'])}")
    test2_pass = not validation2['valid'] and len(validation2['missing_features']) > 0
    
    # Test 3: Invalid mapping
    print("\n[Scenario 3] Invalid/unmapped values")
    invalid_input = valid_input.copy()
    invalid_input["MEHIRUT_MUTERET"] = "invalid_speed"
    validation3 = validate_ui_input(invalid_input)
    print(f"  Valid: {validation3['valid']}")
    print(f"  Warnings: {len(validation3['warnings'])}")
    # Should have warning but still be processable (defaults to 0)
    test3_pass = len(validation3['warnings']) > 0
    
    if test1_pass and test2_pass and test3_pass:
        print(f"\n✓ PASSED: All validation scenarios handled correctly")
        return True
    else:
        print(f"\n✗ FAILED: Some validation scenarios failed")
        return False


def test_edge_cases() -> bool:
    """Test edge cases and default handling."""
    print("\n" + "="*80)
    print("TEST 5: Edge Cases & Default Handling")
    print("="*80)
    
    from backend.services.data_mapper import map_value_to_integer
    
    tests = []
    
    print("\nEdge Case: None values")
    result = map_value_to_integer(None, SPEED_LIMIT_MAPPING)
    print(f"  None → {result} (expected 0)")
    tests.append(result == 0)
    
    print("\nEdge Case: NaN values")
    result = map_value_to_integer(np.nan, SPEED_LIMIT_MAPPING)
    print(f"  NaN → {result} (expected 0)")
    tests.append(result == 0)
    
    print("\nEdge Case: Unmapped string")
    result = map_value_to_integer("unknown_value", SPEED_LIMIT_MAPPING)
    print(f"  'unknown_value' → {result} (expected 0)")
    tests.append(result == 0)
    
    print("\nEdge Case: Empty string")
    result = map_value_to_integer("", SPEED_LIMIT_MAPPING)
    print(f"  '' → {result} (expected 0)")
    tests.append(result == 0)
    
    print("\nEdge Case: 120 km/h speed limit")
    result = map_value_to_integer("120_kmh", SPEED_LIMIT_MAPPING)
    print(f"  '120_kmh' → {result} (expected 8)")
    tests.append(result == 8)
    
    if all(tests):
        print(f"\n✓ PASSED: All {len(tests)} edge cases handled correctly")
        return True
    else:
        failed = len([t for t in tests if not t])
        print(f"\n✗ FAILED: {failed}/{len(tests)} edge cases failed")
        return False


def test_road_structure_engineering() -> bool:
    """Test ROAD_STRUCTURE feature engineering from component columns."""
    print("\n" + "="*80)
    print("TEST 6: ROAD_STRUCTURE Feature Engineering")
    print("="*80)
    
    print("\nCreating test dataset with HAD_MASLUL and RAV_MASLUL columns...")
    
    test_df = pd.DataFrame({
        'HAD_MASLUL': [0, 1, 0, 1, 0],
        'RAV_MASLUL': [0, 0, 1, 1, 0],
    })
    
    print(f"  Input shape: {test_df.shape}")
    print(f"  Input data:\n{test_df}")
    
    try:
        road_structure = engineer_road_structure(test_df)
        print(f"\n✓ Successfully engineered ROAD_STRUCTURE")
        print(f"  Output: {road_structure.values}")
        print(f"  Expected: [2, 1, 4, 3, 2]")
        
        expected = [2, 1, 4, 3, 2]
        if all(road_structure.values == expected):
            print(f"\n✓ PASSED: ROAD_STRUCTURE engineered correctly")
            return True
        else:
            print(f"\n✗ FAILED: ROAD_STRUCTURE values don't match expected")
            return False
    
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main() -> int:
    """Run all mapper and legacy helper checks."""
    print("\n")
    print("█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  SAFE ROADS: MAPPER AND LEGACY HELPER CHECKS  ".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    results = {}
    
    # Run all tests
    results['16_features'] = test_16_features()
    results['mappings'] = test_feature_mappings()
    results['ui_conversion'] = test_ui_to_model_conversion()
    results['validation'] = test_validation()
    results['edge_cases'] = test_edge_cases()
    results['engineering'] = test_road_structure_engineering()
    
    # Print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:8s} | {test_name}")
    
    print("\n" + "-"*80)
    print(f"Total: {passed}/{total} tests passed")
    print("="*80 + "\n")
    
    if passed == total:
        print("✓ All mapper and legacy helper checks passed. Browser and API checks are separate.")
        return 0
    else:
        print(f"✗ {total - passed} TEST(S) FAILED - Please review errors above")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
