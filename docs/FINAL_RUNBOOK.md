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

**Expected Result:** all collected prediction-contract tests pass. The exact count may increase as validation coverage is added.

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
```

### 5. Access the Application

- Open web browser to: `http://127.0.0.1:8000`
- Select driving conditions from dropdowns
- Click "Predict risk" button

**Expected Result:**
- Web page loads with form inputs
- After clicking predict: Shows the predicted class and Light/Dangerous probabilities

## API Testing

### Direct API Test

```powershell
# Test the prediction endpoint directly (requires backend running)
$body = @{
  SHAA = "08:00"
  HODESH_TEUNA = "january"
  YOM_BASHAVUA = "sunday"
  SUG_TEUNA = "front_to_side_collision"
  ROAD_STRUCTURE = "single_lane_1"
  ROHAV = "5_to_7_meters"
  NAFA = "tel_aviv"
  ZURAT_ISHUV = "jewish_city_100k_200k"
  MEHIRUT_MUTERET = "up_to_50_kmh"
  TEURA = "daylight"
  SUG_DEREH = "urban_intersection"
  SIMUN_TIMRUR = "no_defect"
  TKINUT = "no_defect"
  PNE_KVISH = "dry"
  MEZEG_AVIR = "clear"
  YOM_LAYLA = "day"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/predict" -ContentType "application/json" -Body $body
```

**Expected response contract:**

- `prediction`: integer class, `0` or `1`.
- `prediction_label`: `Light accident` or `Dangerous accident`.
- `light_probability`: floating-point probability in `[0, 1]`.
- `dangerous_probability`: floating-point probability in `[0, 1]`.

The exact prediction and probabilities come from the saved model and are not hard-coded in this runbook.

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
