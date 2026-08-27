# Safe Roads: Developer Quick Reference Card

## 🚀 30-Second Start

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

Then open: **http://127.0.0.1:8000**

---

## 📍 Critical Files

| File | Purpose | Key Function |
|------|---------|--------------|
| `frontend/index.html` | UI structure | `<form id="predictionForm">` |
| `frontend/script.js` | Logic + translations | `translations` dict |
| `backend/app.py` | FastAPI server | Serves frontend + API |
| `backend/routes/predict.py` | `/predict` endpoint | `predict()` function |
| `backend/services/data_mapper.py` | **16-feature mapping** | `prepare_model_array()` |
| `backend/services/model_service.py` | ML inference | `predict_probability()` |

---

## 🔄 Data Flow

```
HTML Form (Hebrew)
  ↓
form.values → JSON
  ↓
POST /predict
  ↓
PredictRequest (16 required current fields)
  ↓
prepare_model_frame() ← ordered model input
  ↓
predict_probability(payload)
  ↓
ModelResult (class + Light/Dangerous probabilities)
  ↓
Render class and probability display
```

---

## 🔑 Core Functions

### Backend Conversion
```python
from backend.services.data_mapper import prepare_model_array

ui_input = {
    "SHAA": "14:00",
    "MEHIRUT_MUTERET": "עד 80 קמ״ש",
    # ... 14 more features
}

model_array = prepare_model_array(ui_input)
# Returns: numpy array shape (16,) with integer codes
```

### Validation
```python
from backend.services.data_mapper import validate_ui_input

result = validate_ui_input(form_dict)
# result['valid'] → bool
# result['errors'] → list
# result['warnings'] → list
# result['suggestions'] → dict
```

### Feature Engineering
```python
from backend.services.data_mapper import engineer_road_structure

road_structure = engineer_road_structure(df)
# Creates ROAD_STRUCTURE from HAD_MASLUL + RAV_MASLUL
```

---

## 🗂️ Configuration

### Feature Mappings
```python
# backend/services/data_mapper.py
FEATURE_CONFIG = {
    'MEHIRUT_MUTERET': {
        'type': 'integer',
        'range': [0, 8],
        'mapping': {
            "לא ידוע": 0,
            "עד 50 קמ״ש": 1,
            "עד 80 קמ״ש": 4,
            "עד 120 קמ״ש": 8,  # ← EDGE CASE
        }
    },
    # ... 15 more features
}
```

### CORS Settings
```python
# backend/config.py
ALLOWED_ORIGINS = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
]
```

---

## 🧪 Quick Tests

### Full Integration
```bash
python integration_test.py    # 6 comprehensive tests
```

### System Check
```bash
python system_check.py        # Verification checklist
```

### API Test
```bash
pytest tests/test_predict.py -v
```

---

## 🐛 Debugging

### Frontend Issues
- Check browser console: `F12` → Console tab
- Check form values: `console.log(formData)` in script.js
- Check CSS: Run `system_check.py`

### Backend Issues
- Check logs: Terminal running uvicorn
- Check data mapping: `python integration_test.py`
- Check validation: Call `validate_ui_input()` directly

### API Issues
```bash
# Test endpoint with curl
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"SHAA":"08:00","HODESH_TEUNA":"january","YOM_BASHAVUA":"sunday","SUG_TEUNA":"front_to_side_collision","ROAD_STRUCTURE":"single_lane_1","ROHAV":"5_to_7_meters","NAFA":"tel_aviv","ZURAT_ISHUV":"jewish_city_100k_200k","MEHIRUT_MUTERET":"up_to_50_kmh","TEURA":"daylight","SUG_DEREH":"urban_intersection","SIMUN_TIMRUR":"no_defect","TKINUT":"no_defect","PNE_KVISH":"dry","MEZEG_AVIR":"clear","YOM_LAYLA":"day"}'
```

The response contains `prediction`, `prediction_label`, `light_probability`, and `dangerous_probability`. Exact values are produced by the saved model.

---

## 🔗 Data Mapping Cheat Sheet

### Speed Limit (MEHIRUT_MUTERET)
- `"לא ידוע"` → 0
- `"עד 50 קמ״ש"` → 1
- `"עד 80 קמ״ש"` → 4
- `"עד 120 קמ״ש"` → 8 ← **Custom**

### Road Type (SUG_DEREH)
- `"עירוני בצומת"` → 1
- `"עירוני לא בצומת"` → 2
- `"לא עירוני בצומת"` → 3
- `"לא עירוני לא בצומת"` → 4

### Surface (PNE_KVISH)
- `"יבש"` → 1
- `"רטוב ממים"` → 2
- `"מרוח בחומר דלק"` → 3
- `"מכוסה בבוץ"` → 4

---

## 📋 Prediction Request Fields (16 Required)

`SHAA`, `HODESH_TEUNA`, `YOM_BASHAVUA`, `SUG_TEUNA`, `ROAD_STRUCTURE`,
`ROHAV`, `NAFA`, `ZURAT_ISHUV`, `MEHIRUT_MUTERET`, `TEURA`, `SUG_DEREH`,
`SIMUN_TIMRUR`, `TKINUT`, `PNE_KVISH`, `MEZEG_AVIR`, and `YOM_LAYLA`.

⚠️ **Important**: All 16 fields are required, and request keys must match the backend contract exactly.

---

## 🌐 Bilingual Support

### Translation Setup
```javascript
// frontend/script.js
const translations = {
  en: { "label_SUG_DEREH": "Road Type", ... },
  he: { "label_SUG_DEREH": "סוג דרך", ... }
};

// Switch language (in console)
setLanguage('he');  // Hebrew (RTL)
setLanguage('en');  // English (LTR)
```

### Data i18n Attributes
```html
<label data-i18n="label_SUG_DEREH"></label>
<!-- Automatically translates based on current language -->
```

---

## 🎨 CSS Important Classes

```css
.linear-gauge      /* Horizontal 24px bar with 3 colors */
.gauge-indicator   /* Navy needle (3px width) */
.risk-badge        /* Risk percentage display */
.form-group        /* Form field container (RTL symmetry) */
```

---

## 🚨 Common Mistakes

| ❌ Wrong | ✅ Correct |
|---------|-----------|
| Feature name "SPEED_LIMIT" | Feature name "MEHIRUT_MUTERET" |
| Frontend value "Urban" | Frontend value "עירוני בצומת" |
| Hard-coded color #FF0000 | Use variable from CSS theme |
| SQL in backend | Use model prediction only |
| String "8" for speed code | Integer 8 |

---

## 📚 Key Documentation

| Doc | Location | Purpose |
|-----|----------|---------|
| **API Reference** | `backend/services/README_DATA_MAPPER.md` | 16 features, mappings, functions |
| **Deployment** | `DEPLOYMENT_GUIDE.md` | Production setup, checklists |
| **Final Summary** | `FINAL_SUMMARY.md` | Project completion overview |
| **Integration Check** | `scripts/integration_test.py` | End-to-end verification |

---

## ⚡ Performance Notes

- **Model Loading**: Cached in memory (singleton pattern)
- **Request Handling**: Direct array conversion, no database
- **Response Time**: <200ms typical (depends on model)
- **Concurrent Requests**: ASGI supports multiple workers

---

## 🔐 Security Checklist

- [x] No hardcoded credentials
- [x] CORS properly restricted
- [x] Input validation on every endpoint
- [x] No SQL injection (no database)
- [x] No path traversal (static files only)
- [x] No exposed model internals

---

## 📦 Dependencies

### Core (production)
```
fastapi==0.104.0
uvicorn==0.24.0
pydantic==2.0+
numpy==1.24+
```

### Dev (testing)
```
pandas==2.0+
pytest==7.0+
httpx==0.25+
```

Install all: `pip install -r requirements-dev.txt`

---

## 🎯 Testing Checklist Before Deployment

- [ ] `python integration_test.py` → All PASS
- [ ] `python system_check.py` → All PASS
- [ ] `pytest tests/test_predict.py -v` → All PASS
- [ ] Frontend loads at http://127.0.0.1:8000
- [ ] Form submits successfully
- [ ] Gauge animates smoothly
- [ ] Language toggle works (English ↔ Hebrew)
- [ ] Light and Dangerous percentages display correctly
- [ ] Predicted class matches the larger returned probability
- [ ] No console errors (F12)
- [ ] RTL layout perfect for Hebrew
- [ ] LTR layout perfect for English

---

## 🚀 Deployment (One-Liner)

```bash
pip install -r requirements.txt && \
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

Then access: `http://YOUR_IP:8000`

---

## 💡 Pro Tips

1. **Use integration_test.py** - Verify all components work together
2. **Check validation first** - See what's wrong before debugging
3. **Mirror frontend/backend** - Keep option values in sync
4. **Test with curl first** - Verify API before checking UI
5. **Read README_DATA_MAPPER.md** - Most questions answered there
6. **Run system_check.py** - Verify structure before starting

---

## 📞 When Stuck

1. Run `python system_check.py` → See what's missing
2. Run `python integration_test.py` → Which test fails?
3. Check browser console → JS errors?
4. Check backend logs → API errors?
5. Read `backend/services/README_DATA_MAPPER.md` → Feature reference
6. Check `DEPLOYMENT_GUIDE.md` → Integration details

---

**Quick Links**:
- 🎨 Frontend: `frontend/`
- ⚙️ Backend: `backend/`
- 🧪 Tests: `integration_test.py`, `system_check.py`
- 📖 Docs: `backend/services/README_DATA_MAPPER.md`

**Status**: ✅ Production Ready
