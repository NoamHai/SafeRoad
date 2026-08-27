#!/usr/bin/env python3
"""
Final verification test script for Safe Roads project.
Tests backend imports, predictions, and overall functionality.
"""

import sys
import os
from pathlib import Path

# This script lives in scripts/; anchor to the project root so backend imports
# and relative file paths work regardless of where it is launched from.
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

VALID_PAYLOAD = {
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

def test_backend_imports() -> bool:
    """Test that all backend modules can be imported."""
    print("Testing backend imports...")

    try:
        from backend.app import app
        print("✅ Backend app imported successfully")
        print(f"   Routes: {len(app.routes)}")

        from backend.services.model_service import predict_probability
        print("✅ Model service imported successfully")

        from backend.models.schemas import PredictRequest, ModelResult
        print("✅ Schemas imported successfully")

        from backend.config import settings
        print("✅ Config imported successfully")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prediction_functionality() -> bool:
    """Test the prediction functionality."""
    print("\nTesting prediction functionality...")

    try:
        from backend.services.model_service import predict_probability

        # Test basic prediction
        result = predict_probability(VALID_PAYLOAD)

        # Validate result structure
        required_keys = {'prediction', 'prediction_label', 'light_probability', 'dangerous_probability'}
        if not set(result.keys()) == required_keys:
            print(f"❌ Missing keys in result: {result.keys()}")
            return False

        if result['prediction'] not in {0, 1}:
            print(f"❌ Invalid prediction class: {result['prediction']}")
            return False

        if not isinstance(result['prediction_label'], str):
            print(f"❌ Prediction label not string: {result['prediction_label']}")
            return False

        for key in ("light_probability", "dangerous_probability"):
            probability = result[key]
            if not isinstance(probability, (int, float)) or not 0.0 <= probability <= 1.0:
                print(f"❌ Invalid {key}: {probability}")
                return False

        print("✅ Prediction test successful")
        print(
            "   Result: "
            f"prediction={result['prediction']}, "
            f"light_probability={result['light_probability']:.3f}, "
            f"dangerous_probability={result['dangerous_probability']:.3f}"
        )

        return True
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_validation() -> bool:
    """Test Pydantic schema validation."""
    print("\nTesting schema validation...")

    try:
        from backend.models.schemas import PredictRequest, ModelResult
        from backend.services.model_service import predict_probability

        # Test valid input
        request = PredictRequest(**VALID_PAYLOAD)
        print("✅ Valid input accepted")

        # Test prediction with validated input
        payload = request.model_dump(mode="json")
        result = predict_probability(payload)
        response = ModelResult(**result)
        print("✅ Response validation successful")

        return True
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend_files() -> bool:
    """Test that frontend files exist and are readable."""
    print("\nTesting frontend files...")

    frontend_files = ['frontend/index.html', 'frontend/script.js', 'frontend/style.css']

    for file_path in frontend_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if len(content) > 0:
                        print(f"✅ {file_path} exists and readable ({len(content)} chars)")
                    else:
                        print(f"❌ {file_path} is empty")
                        return False
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
                return False
        else:
            print(f"❌ {file_path} not found")
            return False

    return True

def main() -> int:
    """Run all verification tests."""
    print("🔍 Safe Roads Project - Final Verification")
    print("=" * 50)

    tests = [
        test_backend_imports,
        test_prediction_functionality,
        test_schema_validation,
        test_frontend_files
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test.__name__}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All verification tests passed! Project is ready for submission.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
