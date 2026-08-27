# Safe Roads Project - Final Runbook

This document provides exact commands and expected results for running the Safe Roads accident risk predictor application.

## Prerequisites

- Windows 10/11 with PowerShell
- Python 3.8+ installed and available in PATH
- Internet connection for initial dependency installation

## Quick Start (One-Command)

```powershell
# From project root directory
python -m uvicorn backend.app:app --reload --port 8000
```

**Expected Result:**
```
INFO:     Will watch for changes in these directories: ['C:\path\to\project']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:backend.services.model_service:model.pkl not found, will use rule-based prediction
```

Then open `http://127.0.0.1:8000` in your web browser.

## Complete Setup and Run

### 1. Environment Setup

```powershell
# Navigate to project directory
cd path\to\safe-roads-project

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

**Expected Result:**
```
(venv) PS C:\path\to\safe-roads-project>
```

### 2. Install Dependencies

```powershell
# Install core dependencies
pip install -r requirements.txt
```

**Expected Result:**
```
Collecting fastapi>=0.104.0 (from -r requirements.txt (line 2))
...
Successfully installed fastapi-0.128.0 uvicorn-0.40.0 pydantic-2.12.5 pydantic-settings-2.12.0 joblib-1.5.3
```

### 3. Run Tests (Optional but Recommended)

```powershell
# Run all tests
python -m pytest tests/ -v
```

**Expected Result:**
```
============================= test session starts ==============================
...
tests/test_predict.py::TestPredictOutputStructure::test_output_keys PASSED
tests/test_predict.py::TestPredictOutputStructure::test_output_types PASSED
tests/test_predict.py::TestPredictOutputStructure::test_breakdown_item_types PASSED
tests/test_predict.py::TestPredictSanityCases::test_low_risk_scenario PASSED
tests/test_predict.py::TestPredictSanityCases::test_high_risk_scenario PASSED
tests/test_predict.py::TestPredictSanityCases::test_rainy_conditions PASSED
tests/test_predict.py::TestPredictSanityCases::test_night_driving PASSED
tests/test_predict.py::TestPredictSanityCases::test_all_factors_present PASSED
tests/test_predict.py::TestPredictEdgeCases::test_missing_input_keys PASSED
tests/test_predict.py::TestPredictEdgeCases::test_invalid_input_values PASSED
tests/test_predict.py::TestPredictConsistency::test_same_input_same_output PASSED

============================== 11 passed in 0.26s =============================
```

### 4. Start the Application

```powershell
# Start the server
python -m uvicorn backend.app:app --reload --port 8000
```

**Expected Result:**
```
INFO:     Will watch for changes in these directories: ['C:\path\to\project']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:backend.services.model_service:model.pkl not found, will use rule-based prediction
```

### 5. Access the Application

- Open web browser to: `http://127.0.0.1:8000`
- Select driving conditions from dropdowns
- Click "Predict risk" button

**Expected Result:**
- Web page loads with form inputs
- After clicking predict: Shows risk percentage, color-coded display, and breakdown of factors

## API Testing

### Direct API Test

```powershell
# Test the prediction endpoint directly (requires backend running)
curl -X POST "http://127.0.0.1:8000/predict" ^
  -H "Content-Type: application/json" ^
  -d "{\"road_type\":\"urban\",\"weather\":\"clear\",\"time_of_day\":\"day\",\"lighting\":\"daylight\",\"junction\":\"no_junction\",\"road_surface\":\"dry\"}"
```

**Expected Result:**
```json
{
  "probability": 0.14,
  "risk_percent": 14,
  "breakdown": [
    {
      "factor": "road_type",
      "value": "urban",
      "delta": 0.04,
      "note": "Urban driving has many interactions"
    },
    {
      "factor": "weather",
      "value": "clear",
      "delta": 0.0,
      "note": "Good conditions"
    },
    {
      "factor": "time_of_day",
      "value": "day",
      "delta": 0.0,
      "note": "Daytime"
    },
    {
      "factor": "lighting",
      "value": "daylight",
      "delta": 0.0,
      "note": "Good lighting"
    },
    {
      "factor": "junction",
      "value": "no_junction",
      "delta": 0.0,
      "note": "No junction"
    },
    {
      "factor": "road_surface",
      "value": "dry",
      "delta": 0.0,
      "note": "Dry surface"
    }
  ]
}
```

## Alternative Frontend Serving

If you prefer to serve frontend separately:

```powershell
# Terminal 1: Start backend
python -m uvicorn backend.app:app --reload --port 8000

# Terminal 2: Serve frontend (from project root)
cd frontend
python -m http.server 5500
```

Then access: `http://127.0.0.1:5500` (backend must allow CORS)

## Development Commands

```powershell
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
python -m pytest tests/ --cov=backend --cov-report=html

# Run specific test
python -m pytest tests/test_predict.py::TestPredictOutputStructure::test_output_keys -v

# Format code (if black installed)
black backend/ frontend/ tests/

# Type checking (if mypy installed)
mypy backend/
```

## Troubleshooting

### Backend Won't Start
- Ensure virtual environment is activated: `venv\Scripts\activate`
- Check dependencies: `pip list | findstr fastapi`
- Verify Python version: `python --version` (should be 3.8+)

### Frontend Not Loading
- Check browser console for JavaScript errors
- Ensure backend is running on port 8000
- Try refreshing the page

### Tests Failing
- Ensure development dependencies installed: `pip install -r requirements-dev.txt`
- Check Python path: `python -c "import sys; print(sys.path)"`

### Import Errors
- Run from project root directory
- Ensure virtual environment is activated
- Check for missing dependencies

## File Structure Verification

After setup, verify these files exist:

```
safe-roads/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── predict.py
│   └── services/
│       ├── __init__.py
│       └── model_service.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── tests/
│   ├── __init__.py
│   └── test_predict.py
├── docs/
│   └── ... (documentation files)
├── data/
│   └── accidents_raw_master.csv
└── tools/
    └── accidents_analysis.py
```

## Success Criteria

✅ **Application starts** with `uvicorn` command
✅ **Web interface loads** at `http://127.0.0.1:8000`
✅ **Form submission works** and shows prediction results
✅ **API returns valid JSON** with expected structure
✅ **All tests pass** with `pytest`
✅ **No import errors** or missing dependencies

The application is ready for submission when all commands execute successfully and produce the expected results above.