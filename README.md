# Safe Roads – Accident Risk Predictor

A web application that predicts the **severity of a road accident** – *light* vs *dangerous* –
from 16 conditions describing the time, place, road and weather of the accident.

It has a **FastAPI** backend that serves a trained machine-learning model, and a static
**bilingual (English / Hebrew RTL)** frontend.

- **Model:** `HistGradientBoostingClassifier` (scikit-learn), trained on ~66,000 Israeli road
  accident records (2018–2023, data.gov.il).
- **Prediction:** `0 = Light accident`, `1 = Dangerous accident`, with probabilities for each class.

> The full machine-learning work (data preparation, feature selection, training, evaluation)
> lives under `safe_roads_ml/`.

## Requirements

- Python 3.10+
- A modern web browser

## Installation

```powershell
# from the project root
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt          # runtime
pip install -r requirements-dev.txt       # optional: adds pandas + test tools
```

## Running the app

```powershell
venv\Scripts\python.exe -m uvicorn backend.app:app --reload --port 8000
```

Then open **http://127.0.0.1:8000** – the frontend is served by the backend on the same origin.
Fill in the conditions, click **Predict Risk**, and the estimated risk is shown.

## API

### `POST /predict`

Send the 16 features. Values are the option keys used by the frontend (the backend maps them to
the numeric codes the model expects via `backend/services/feature_value_mappings.json`).

**Request:**

```json
{
  "SHAA": "21:30",
  "HODESH_TEUNA": "december",
  "YOM_BASHAVUA": "sunday",
  "SUG_TEUNA": "pedestrian_collision",
  "ROAD_STRUCTURE": "single_lane_1",
  "ROHAV": "unknown_road_width",
  "NAFA": "unknown",
  "ZURAT_ISHUV": "urban_refugee_camps",
  "MEHIRUT_MUTERET": "unknown_speed_limit",
  "TEURA": "daylight",
  "SUG_DEREH": "urban_intersection",
  "SIMUN_TIMRUR": "defective_or_missing_road_marking",
  "TKINUT": "unknown_road_condition",
  "PNE_KVISH": "dry",
  "MEZEG_AVIR": "clear",
  "YOM_LAYLA": "day"
}
```

**Response:**

```json
{
  "prediction": 0,
  "prediction_label": "Light accident",
  "light_probability": 0.5946,
  "dangerous_probability": 0.4054
}
```

## Project structure

```
final_project/
├── backend/                     # FastAPI backend
│   ├── app.py                   # App, CORS, serves the frontend
│   ├── config.py                # Settings
│   ├── models/schemas.py        # Request/response models (16-feature PredictRequest, ModelResult)
│   ├── routes/predict.py        # POST /predict
│   └── services/
│       ├── model_service.py     # Loads the model, runs prediction
│       ├── data_mapper.py       # Maps UI values -> numeric feature codes
│       └── feature_value_mappings.json   # Authoritative value mappings
├── frontend/                    # Static UI (bilingual, RTL/LTR)
│   ├── index.html
│   ├── script.js
│   └── style.css
├── safe_roads_ml/               # Machine-learning work (data, training, model, evaluation)
├── tests/                       # Pytest tests
├── requirements.txt
└── requirements-dev.txt
```

## Testing

```powershell
pip install -r requirements-dev.txt
venv\Scripts\python.exe -m pytest -v
```

## Notes

- The 16 feature names, their order, and the mapping values are fixed by the trained model and
  must not be changed independently of the model.
- If the model file (`safe_roads_ml/final_model/saved_model/safe_roads_model.joblib`) is missing,
  the API returns an error instead of guessing – there is no rule-based fallback.

---

*Academic final project – Tel-Hai Academic College, Department of Computer Science.*
