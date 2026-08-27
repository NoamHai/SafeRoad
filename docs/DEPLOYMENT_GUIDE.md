# Safe Roads: Complete Deployment & Integration Guide

## 🎯 System Overview

**Safe Roads** is a production-ready web application that predicts accident risk using:
- **Frontend**: Bilingual HTML5/CSS3/JavaScript (Hebrew RTL + English LTR)
- **Backend**: FastAPI with 16-feature ML inference pipeline
- **Data Pipeline**: Hebrew↔Integer mapping system with feature engineering
- **UI Theme**: Professional navy government design with flat modern aesthetics

---

## 📋 Quick Start

### Prerequisites
```bash
python --version  # Python 3.8+
pip install -r requirements-dev.txt
```

### Start Backend (Port 8000)
```bash
uvicorn backend.app:app --reload --port 8000
```

Then access at: **http://127.0.0.1:8000**

---

## 🏗️ Architecture

### Component Hierarchy
```
frontend/ (Static UI)
├── index.html          # Bilingual structure (Hebrew/English)
├── script.js           # Translation dictionary, form handling
└── style.css           # Navy theme, RTL/LTR symmetry

backend/ (FastAPI)
├── app.py              # Main application & static file serving
├── config.py           # Settings & CORS configuration
├── routes/
│   └── predict.py      # POST /predict endpoint
├── models/
│   └── schemas.py      # Pydantic request/response models
└── services/
    ├── model_service.py           # Required saved-model loading and inference
    ├── data_mapper.py             # 16-feature mapping system ⭐
    └── README_DATA_MAPPER.md      # Complete documentation ⭐

tests/
├── test_predict.py            # API endpoint tests
scripts/integration_test.py    # End-to-end verification ⭐
scripts/system_check.py        # System readiness checklist ⭐
```

⭐ = Newly created high-value components

---

## 🔑 Critical Components

### 1. Data Mapper (`backend/services/data_mapper.py`)

**Purpose**: Convert Hebrew UI strings → Integer codes for ML model

**16 Features Implemented**:
```python
FEATURE_CONFIG = {
    'SHAA': {...},                    # Quarter-hour time code
    'HODESH_TEUNA': {...},            # Month
    'YOM_BASHAVUA': {...},            # Day of week
    'SUG_TEUNA': {...},               # Accident type
    'ROAD_STRUCTURE': {...},          # Road structure
    'ROHAV': {...},                   # Road width
    'NAFA': {...},                    # District
    'ZURAT_ISHUV': {...},             # Settlement form
    'MEHIRUT_MUTERET': {...},         # Speed limit
    'TEURA': {...},                   # Lighting conditions
    'SUG_DEREH': {...},               # Road type
    'SIMUN_TIMRUR': {...},            # Marking/signage condition
    'TKINUT': {...},                  # Road-condition integrity
    'PNE_KVISH': {...},               # Road surface
    'MEZEG_AVIR': {...},              # Weather
    'YOM_LAYLA': {...},               # Day/night indicator
}
```

**Key Functions**:
```python
# Convert single value
code = map_value_to_integer("עד 80 קמ״ש", SPEED_LIMIT_MAPPING)
# → 4

# Convert entire form
model_dict = prepare_model_input(ui_form_dict)
model_array = prepare_model_array(ui_form_dict)  # Returns numpy array shape (16,)

# Validate input
validation = validate_ui_input(ui_form_dict)
# Returns: {valid, errors, warnings, missing_features, suggestions}

# Engineer features
road_structure = engineer_road_structure(df)
# Creates ROAD_STRUCTURE from HAD_MASLUL + RAV_MASLUL columns
```

### 2. Frontend Integration (`frontend/script.js`)

**Translation Dictionary** (English ↔ Hebrew):
```javascript
const translations = {
  en: {
    "label_SUG_DEREH": "Road Type",
    "label_SHAA": "Time",
    // ... etc
  },
  he: {
    "label_SUG_DEREH": "סוג דרך",
    "label_SHAA": "שעה",
    // ... etc
  }
};
```

**Form Submission Flow**:
```javascript
// 1. User completes all 16 selectors
// 2. predict() builds the uppercase 16-field payload
// 3. Frontend sends POST /predict
// 4. Backend validates and maps the payload for the saved model
// 5. Frontend renders the returned class and probabilities
```

### 3. API Contract (`backend/routes/predict.py`)

**Request Schema**:
```python
class PredictRequest(BaseModel):
    SHAA: int | str
    HODESH_TEUNA: int | str
    YOM_BASHAVUA: int | str
    SUG_TEUNA: int | str
    ROAD_STRUCTURE: int | str
    ROHAV: int | str
    NAFA: int | str
    ZURAT_ISHUV: int | str
    MEHIRUT_MUTERET: int | str
    TEURA: int | str
    SUG_DEREH: int | str
    SIMUN_TIMRUR: int | str
    TKINUT: int | str
    PNE_KVISH: int | str
    MEZEG_AVIR: int | str
    YOM_LAYLA: int | str
```

**Response Schema**:
```python
class ModelResult(BaseModel):
    prediction: int
    prediction_label: str
    light_probability: float
    dangerous_probability: float
```

**Endpoint**: `POST http://127.0.0.1:8000/predict`

---

## 🔄 Integration Steps

### Step 1: Verify Backend Structure
```bash
python system_check.py
```
Expected output: All checks PASS

### Step 2: Run Integration Tests
```bash
python scripts/integration_test.py
```
Expected output: All 6 tests PASS

### Step 3: Start Backend
```bash
uvicorn backend.app:app --reload --port 8000
```

### Step 5: Test Full Pipeline
```bash
# Open browser to http://127.0.0.1:8000
# Fill form in Hebrew or English
# Submit and verify prediction response
```

---

## 🔧 Key Implementation Details

### Application-Key-to-Model Mapping Example

**Frontend sends**:
```json
{
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
  "YOM_LAYLA": "day"
}
```

**Backend converts to**:
```python
model_input = prepare_model_input(request_payload)
model_frame = prepare_model_frame(request_payload, FEATURE_ORDER)

# model_frame has one row and the exact 16 columns in FEATURE_ORDER.
```

Here, `request_payload` is the validated 16-field request shown above.

### Edge Cases Handled

| Scenario | Handling |
|----------|----------|
| `None` or `NaN` values | → Default to 0 (לא ידוע) |
| Unmapped Hebrew string | → Default to 0, add warning |
| Case sensitivity | → Automatic case-insensitive matching |
| Custom 120 km/h speed | → Code 8 (not 50/80/100) |
| Missing form fields | → Validation error, suggestions provided |

### URL Query Parameters Conversion

Frontend HTML `<option value>` must match the descriptive keys in the backend mapping:
```html
<!-- frontend/index.html -->
<option value="urban_intersection">Urban at Junction</option>
<option value="urban_non_intersection">Urban Not at Junction</option>
```

The authoritative `SUG_DEREH` mapping is loaded from:

```text
backend/services/feature_value_mappings.json
```

---

## 📊 Feature Engineering

### ROAD_STRUCTURE Creation

Many row-level features require "engineering" from raw columns:

```python
# Input columns from CSV
HAD_MASLUL = [0, 1, 0, 1]    # Single lane indicator
RAV_MASLUL = [0, 0, 1, 1]    # Multi-lane indicator

# Engineering logic
def engineer(had, rav):
    if had == 0 and rav == 0: return 2  # Unknown/both false → same direction
    if had == 1 and rav == 0: return 1  # Single lane → one-way
    if had == 0 and rav == 1: return 4  # Multi-lane → both directions
    if had == 1 and rav == 1: return 3  # Multi-lane one-way
    return 2  # Default

# Output
ROAD_STRUCTURE = [2, 1, 4, 3]  # 4 integer codes
```

Dataset preprocessing helpers live in `backend/services/data_mapper.py`.

---

## 🧪 Testing & Verification

### Run Full Integration Tests
```bash
python integration_test.py
```
Tests:
- ✓ All 16 features configured
- ✓ Critical mappings (speed limit, road type, surface)
- ✓ UI → Model conversion pipeline
- ✓ Input validation & error handling
- ✓ Edge cases (None, NaN, unmapped values)
- ✓ Feature engineering (ROAD_STRUCTURE)

### Run API Tests
```bash
pytest tests/test_predict.py -v
```

### Verify System Readiness
```bash
python system_check.py
```

### Run Full End-to-End Verification
```bash
python verify_final.py
```

---

## 🚀 Production Deployment

### 1. Prepare Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Prepare ML Model
```bash
# Final saved model used by the application:
safe_roads_ml/final_model/saved_model/safe_roads_model.joblib

# The model must:
# - Accept input shape (n, 16) where n = num samples
# - Implement predict_proba() returning (n, 2) array
# - Return probabilities aligned to classes 0 (Light) and 1 (Dangerous)
# - Be loadable with joblib under the declared scikit-learn dependency
```

### 3. Start Server
```bash
# Development
uvicorn backend.app:app --reload --port 8000

# Production
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Update CORS if Needed
Edit `backend/config.py`:
```python
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://your-domain.com",  # Add production domain
]
```

---

## 📁 File Structure Reference

```
project_root/
├── requirements.txt          # Core dependencies
├── requirements-dev.txt      # + dev tools (pytest, pandas)
│
├── frontend/
│   ├── index.html           # [PRODUCTION] Bilingual UI
│   ├── style.css            # [PRODUCTION] Navy theme
│   └── script.js            # [PRODUCTION] JS logic + translations
│
├── backend/
│   ├── app.py               # [PRODUCTION] FastAPI entry point
│   ├── config.py            # [PRODUCTION] Settings
│   ├── services/
│   │   ├── model_service.py              # [PRODUCTION] ML inference
│   │   ├── data_mapper.py                # [NEW] 16-feature mapping
│   │   └── README_DATA_MAPPER.md         # [NEW] Documentation
│   ├── routes/
│   │   └── predict.py                    # [PRODUCTION] /predict endpoint
│   └── models/
│       └── schemas.py                    # [PRODUCTION] Pydantic schemas
│
├── tests/
│   └── test_predict.py      # [TESTING] API endpoint tests
│
├── data/
│   └── accidents_raw_master.csv # [DATA] Raw dataset
│
└── [NEW TOOLS]
    ├── integration_test.py   # Comprehensive integration test
    ├── system_check.py       # System verification checklist
    └── verify_final.py       # Final verification script
```

---

## ⚠️ Common Issues & Solutions

| Problem | Solution |
|---------|----------|
| **CORS Error** | Update `ALLOWED_ORIGINS` in `backend/config.py` |
| **Model not loading** | Verify `safe_roads_ml/final_model/saved_model/safe_roads_model.joblib` and its runtime dependencies |
| **Hebrew characters garbled** | Verify `encoding='utf-8'` in file reads |
| **Feature mismatch** | Check frontend `<option value>` matches `*_MAPPING` keys |
| **Runtime "unknown value"** | Value not in mapping dict; returns 0 (default) + warning |
| **Gauge not animating** | Check CSS `.gauge-indicator` has `transition: left 0.7s` |

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `backend/services/README_DATA_MAPPER.md` | Complete data mapper reference (500+ lines) |
| `docs/ML_INTERFACE_CONTRACT.md` | Model input/output specification |
| `docs/FRONTEND_COMPATIBILITY.md` | UI requirements & i18n setup |
| `docs/REQUIREMENTS_CHECKLIST.md` | Submission checklist |
| `integration_test.py` | Automated system verification |

---

## 🔍 API Examples

### cURL Request
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"SHAA":"08:00","HODESH_TEUNA":"january","YOM_BASHAVUA":"sunday","SUG_TEUNA":"front_to_side_collision","ROAD_STRUCTURE":"single_lane_1","ROHAV":"5_to_7_meters","NAFA":"tel_aviv","ZURAT_ISHUV":"jewish_city_100k_200k","MEHIRUT_MUTERET":"up_to_50_kmh","TEURA":"daylight","SUG_DEREH":"urban_intersection","SIMUN_TIMRUR":"no_defect","TKINUT":"no_defect","PNE_KVISH":"dry","MEZEG_AVIR":"clear","YOM_LAYLA":"day"}'
```

### Python Request
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/predict",
    json={
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
)

result = response.json()
print(result["prediction_label"])
print(result["light_probability"], result["dangerous_probability"])
```

### Response Contract

- `prediction`: integer class `0` or `1`.
- `prediction_label`: `Light accident` or `Dangerous accident`.
- `light_probability`: model probability for class `0`.
- `dangerous_probability`: model probability for class `1`.

Exact prediction values depend on the saved model and request; this guide does not hard-code an example result.

---

## ✅ Deployment Checklist

- [ ] All 16 features configured in `FEATURE_CONFIG`
- [ ] `frontend/index.html` options match backend mappings
- [ ] `safe_roads_ml/final_model/saved_model/safe_roads_model.joblib` present and loadable
- [ ] Dataset preprocessed: `data/accidents_processed.pkl`
- [ ] Backend runs without errors: `uvicorn backend.app:app --reload --port 8000`
- [ ] Integration tests pass: `python integration_test.py`
- [ ] System checks pass: `python system_check.py`
- [ ] Frontend accessible at `http://127.0.0.1:8000`
- [ ] Form submission produces valid prediction
- [ ] Response contains the class label and Light/Dangerous probabilities
- [ ] Hebrew and English both functional
- [ ] Linear gauge displays correctly
- [ ] No JavaScript errors in browser console

---

## 📞 Support

For debugging:
1. Check browser console for JS errors: `F12` → Console tab
2. Check backend logs: Terminal running uvicorn
3. Run integration test: `python integration_test.py`
4. Review data mapper docs: `backend/services/README_DATA_MAPPER.md`
5. Check validation errors: `validate_ui_input()` returns detailed feedback

---

**Status: ✓ Production Ready**

All components integrated and tested. System ready for deployment.
