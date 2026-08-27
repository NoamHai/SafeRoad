# Data Mapper & Preprocessing Pipeline
## Safe Roads Traffic Accidents Prediction Model

Complete data preprocessing and UI-to-Backend mapping system for the Safe Roads accident risk prediction model.

---

## 📋 Overview

This system provides:

1. **Data Preprocessing** - Prepare raw accidents dataset for model training
2. **Feature Engineering** - Create new features from existing data
3. **UI-to-Backend Mapping** - Convert Hebrew UI strings to integer codes for the model
4. **Validation & Error Handling** - Robust edge case management and user feedback
5. **Integration Examples** - Show how to use with FastAPI, model_service, etc.

### Key Statistics
- **16 Required Features** for the model
- **16 Comprehensive Feature Mappings** (Hebrew ↔ Integer codes)
- **Edge Case Handling** for missing values and unknown inputs
- **Full RTL/LTR Support** for Hebrew UI strings

---

## 📁 Files

### Core Modules

| File | Purpose |
|------|---------|
| `data_mapper.py` | Main mapping dictionaries and conversion functions |

### Usage

```
backend/services/
├── data_mapper.py                          # ✓ Mapping dictionaries
├── model_service.py                        # (existing model service)
└── README_DATA_MAPPER.md                   # ✓ This file
```

---

## 🎯 The 16 Required Features

The model uses exactly these 16 features:

| Hebrew Name | English Description | Code |
|-------------|-------------------|------|
| SHAA | Quarter-hour time code | Integer |
| HODESH_TEUNA | Month of accident | Integer |
| YOM_BASHAVUA | Day of week | Integer |
| SUG_TEUNA | Type of accident | Integer |
| ROAD_STRUCTURE | Road structure (engineered) | Integer |
| ROHAV | Road width | Integer |
| NAFA | District | Integer |
| ZURAT_ISHUV | Settlement type | Integer |
| MEHIRUT_MUTERET | Speed limit | Integer |
| TEURA | Lighting conditions | Integer |
| SUG_DEREH | Road type | Integer |
| SIMUN_TIMRUR | Traffic signal/marking | Integer |
| TKINUT | Road-condition integrity | Integer |
| PNE_KVISH | Road surface condition | Integer |
| MEZEG_AVIR | Weather | Integer |
| YOM_LAYLA | Day/night indicator | Integer |

---

## 🔄 Feature Mappings

### 1. MEHIRUT_MUTERET (Speed Limit)

```python
0 = "לא ידוע"              # Unknown
1 = "עד 50 קמ״ש"           # Up to 50 km/h
2 = "עד 60 קמ״ש"           # Up to 60 km/h
3 = "עד 70 קמ״ש"           # Up to 70 km/h
4 = "עד 80 קמ״ש"           # Up to 80 km/h
5 = "עד 90 קמ״ש"           # Up to 90 km/h
6 = "עד 100 קמ״ש"          # Up to 100 km/h
7 = "עד 110 קמ״ש"          # Up to 110 km/h
8 = "עד 120 קמ״ש"          # Up to 120 km/h (custom edge case)
```

### 2. SUG_DEREH (Road Type)

```python
0 = "לא ידוע"              # Unknown
1 = "עירוני בצומת"         # Urban at junction
2 = "עירוני לא בצומת"      # Urban not at junction
3 = "לא עירוני בצומת"      # Non-urban at junction
4 = "לא עירוני לא בצומת"   # Non-urban not at junction
```

### 3. PNE_KVISH (Road Surface)

```python
0 = "לא ידוע"              # Unknown
1 = "יבש"                  # Dry
2 = "רטוב ממים"            # Wet from water
3 = "מרוח בחומר דלק"       # Covered with fuel
4 = "מכוסה בבוץ"           # Covered in mud
```

### 4. SUG_TEUNA (Accident Type)

```python
0 = "לא ידוע"              # Unknown
1 = "חזיתי"                # Frontal
2 = "אחורי"                # Rear-end
3 = "צדדי"                 # Side
4 = "הולך רגל"             # Pedestrian
```

### 5. ROAD_STRUCTURE (Engineered Feature)

```python
0 = "לא ידוע"              # Unknown
1 = "חד-כיווני"            # Single lane
2 = "דו-כיווני"            # Two-way
3 = "רב-נתיבים דו-כיווני"  # Multi-lane two-way
4 = "רב-נתיבים חד-כיווני"  # Multi-lane one-way
```

Engineered from:
- `HAD_MASLUL` (Single-lane indicator)
- `RAV_MASLUL` (Multi-lane indicator)

**Other Mappings**: See `feature_value_mappings.json` and `data_mapper.py` for every field in `FEATURE_ORDER`.

---

## 🚀 Quick Start

### 1. Basic Value Conversion

Convert a single supported descriptive key to its model code:

```python
from backend.services.data_mapper import map_value_to_integer, ROAD_SURFACE_MAPPING

# Map "dry" → 1
code = map_value_to_integer("dry", ROAD_SURFACE_MAPPING, "PNE_KVISH")
print(code)  # Output: 1
```

### 2. Convert User Form to Model Input

Convert complete UI input to model-ready integers:

```python
from backend.services.data_mapper import prepare_model_input

ui_data = {
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

model_input = prepare_model_input(ui_data)
# The returned dictionary follows FEATURE_ORDER and contains the mapped integer values.
```

### 3. Create the Ordered Model Frame

Build the one-row DataFrame used by the saved pipeline:

```python
from backend.services.data_mapper import FEATURE_ORDER, prepare_model_frame

model_frame = prepare_model_frame(ui_data, FEATURE_ORDER)
print(model_frame.shape)  # (1, 16)
```

### 4. Validate User Input

Check for errors and missing values:

```python
from backend.services.data_mapper import validate_ui_input

validation = validate_ui_input(ui_data)
print(validation)
# {
#     'valid': True,
#     'errors': [],
#     'warnings': [],
#     'missing_features': []
# }
```

---

## 🔧 Integration with FastAPI Backend

### Current `backend/routes/predict.py` flow:

```python
@router.post("/predict", response_model=ModelResult)
def predict(req: PredictRequest) -> ModelResult:
    payload = req.model_dump(mode="json")
    result = predict_probability(payload)
    return ModelResult(**result)
```

`PredictRequest` requires all fields in `FEATURE_ORDER` and forbids unexpected fields. `predict_probability` builds the ordered frame, runs the real saved model, and returns `prediction`, `prediction_label`, `light_probability`, and `dangerous_probability`.

---

## 📊 Dataset Preprocessing

### In Python Script

```python
from backend.services.data_mapper import preprocess_dataset
import pandas as pd

# Load raw data
df_raw = pd.read_csv("data/accidents_raw_master.csv")

# Preprocess
df_processed = preprocess_dataset(df_raw)

# Use for training
# X = df_processed[features]
# y = df_processed['target']
```

---

## ⚙️ Feature Engineering: ROAD_STRUCTURE

The `ROAD_STRUCTURE` feature doesn't exist in the raw dataset. It's engineered from:
- `HAD_MASLUL`: Single-lane indicator (binary)
- `RAV_MASLUL`: Multi-lane indicator (binary)

### Logic

```python
from backend.services.data_mapper import engineer_road_structure

road_structure = engineer_road_structure(df)

# Result mapping:
# 0 = Unknown (missing data)
# 1 = Single lane (HAD_MASLUL = 1)
# 2 = Two-way (default, no multi-lane indicator)
# 3 = Multi-lane one-way (RAV_MASLUL = 1 AND HAD_MASLUL = 1)
# 4 = Multi-lane two-way (RAV_MASLUL = 1 only)
```

---

## 🛡️ Error Handling & Edge Cases

### Automatic Defaults

The system automatically handles missing/invalid values:

```python
from backend.services.data_mapper import map_value_to_integer, SPEED_LIMIT_MAPPING

# None automatically becomes 0 (unknown)
code1 = map_value_to_integer(None, SPEED_LIMIT_MAPPING)
print(code1)  # 0

# NaN automatically becomes 0 (unknown)
import numpy as np
code2 = map_value_to_integer(np.nan, SPEED_LIMIT_MAPPING)
print(code2)  # 0

# Unknown string becomes default (0)
code3 = map_value_to_integer("invalid value", SPEED_LIMIT_MAPPING)
print(code3)  # 0

# Case-insensitive matching works
code4 = map_value_to_integer("יבש", SPEED_LIMIT_MAPPING)  # Still works
```

### Custom Edge Cases

Example: Speed Limit 120 km/h (custom addition):

```python
from backend.services.data_mapper import SPEED_LIMIT_MAPPING

# Custom edge case supported
print(SPEED_LIMIT_MAPPING["עד 120 קמ״ש"])  # 8
```

---

## 📝 Usage Examples

### Example 1: Single Prediction Request

User submits form → Convert → Predict → Return result

```python
# Frontend sends:
frontend_json = {
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

# Backend converts and predicts
model_input = prepare_model_input(frontend_json)
model_frame = prepare_model_frame(frontend_json, FEATURE_ORDER)
```

---

## 🧪 Testing

### Run Integration Tests

```bash
python scripts/integration_test.py

# Output:
# Testing Data Mapper Conversion Pipeline
# ================================================================================
# [Test 1] Basic conversion with prepare_model_input()
#   ✓ Conversion successful
#   ✓ Output keys: 16
# [Test 2] Frame conversion with prepare_model_frame()
#   ✓ Frame shape: (1, 16)
# ...
```

### Manual Testing

```python
from backend.services.data_mapper import *

# Test mapping a value
assert map_value_to_integer("dry", ROAD_SURFACE_MAPPING) == 1
assert map_value_to_integer(None, ROAD_SURFACE_MAPPING) == 0

# Test feature config
assert len(FEATURE_CONFIG) == 16

# Test reverse maps
reverse = REVERSE_MAPPINGS["PNE_KVISH"]
assert reverse[1] == "dry"

print("✓ All tests passed!")
```

---

## 📚 API Reference

### Core Functions

#### `map_value_to_integer(value, mapping_dict, feature_name, default=0)`
Convert a single value to its integer code.

#### `engineer_road_structure(df, had_maslul_col, rav_maslul_col)`
Create ROAD_STRUCTURE feature from components.

#### `prepare_model_input(ui_input, feature_order=None)`
Convert full UI input dict to model input dict.

#### `prepare_model_array(ui_input, feature_order=None)`
Convert UI input dict to numpy array for model.

#### `validate_ui_input(ui_input)`
Validate input and return error/warning report.

#### `preprocess_dataset(df, selected_features, target_column)`
Preprocess raw dataset for model training.

---

## 🔐 Design Principles

1. **Robustness**: Graceful handling of missing data, unknown values
2. **Clarity**: Hebrew strings ↔ Integer codes mapping visible and documented
3. **Extensibility**: Easy to add new features or mappings
4. **Type Safety**: Clear types for all functions (Dict, Array, etc.)
5. **Localization**: Full RTL/LTR support for Hebrew UI

---

## 📖 Additional Resources

- See `data_mapper.py` for complete mapping dictionaries
- Check `FEATURE_CONFIG` for per-feature documentation

---

## ✅ Checklist: Getting Started

- [ ] Copy `data_mapper.py` to `backend/services/`
- [ ] Import in your route: `from backend.services.data_mapper import prepare_model_array`
- [ ] Use in predict function: `model_array = prepare_model_array(ui_input)`
- [ ] Test with: `python scripts/integration_test.py`
- [ ] Run end-to-end test with your model

---

## 🤝 Support

For questions or issues:

1. Check the mapping dictionaries in `data_mapper.py`
2. Run the integration tests
3. Check validation results with `validate_ui_input()`

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Status**: Production Ready ✓
