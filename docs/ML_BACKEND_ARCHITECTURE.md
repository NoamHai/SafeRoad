# ML Backend Architecture — Safe Roads

This document describes the implemented runtime architecture for accident-severity inference. Model training remains separate from the application backend.

## Constraints

- The backend does not train or modify the model.
- Every prediction requires the final 16-field request contract.
- The mapper preserves the model's verified feature order and mapping meanings.
- The real saved model is required; there is no heuristic fallback.

## Relevant Structure

```text
backend/
├── app.py                         # FastAPI application and static serving
├── routes/predict.py              # POST /predict
├── models/schemas.py              # PredictRequest and ModelResult
└── services/
    ├── data_mapper.py             # Current mappings and ordered model frame
    └── model_service.py           # Saved-model loading and inference

safe_roads_ml/final_model/saved_model/
├── safe_roads_model.joblib        # Final trained pipeline
└── model_metadata.json            # Feature and target metadata
```

## Responsibilities

### `backend/app.py`

- Creates the FastAPI application.
- Configures middleware, routes, logging, and static frontend serving.

### `backend/routes/predict.py`

- Receives `POST /predict` through `PredictRequest`.
- Serializes the validated 16-field request.
- Calls `predict_probability` and validates the returned `ModelResult`.
- Converts input errors to HTTP `422` and unexpected failures to HTTP `500`.

### `backend/models/schemas.py`

- Requires all 16 current fields.
- Forbids unexpected fields.
- Defines the four-field prediction response.

### `backend/services/data_mapper.py`

- Converts supported application values to the numeric representation expected by the model.
- Builds a one-row frame in `FEATURE_ORDER`.
- Validates the special `SHAA` time representation.

### `backend/services/model_service.py`

- Verifies the exact current feature-key set for direct service calls.
- Loads and caches `safe_roads_model.joblib` with Joblib.
- Calls `predict_proba` on the ordered frame.
- Aligns class `0`/`1` with Light/Dangerous probabilities.
- Returns `prediction`, `prediction_label`, `light_probability`, and `dangerous_probability`.
- Fails explicitly if the real model is unavailable.

## Request Flow

1. The frontend submits the current 16-field JSON payload.
2. FastAPI/Pydantic validates required and unexpected fields.
3. The route serializes the request and calls `predict_probability`.
4. The service verifies the key set and builds the ordered feature frame.
5. The cached final Joblib model is loaded if necessary.
6. The service calls `predict_proba` and aligns class probabilities.
7. The API returns the four-field `ModelResult`.

This boundary keeps application validation and mapping explicit while preserving the saved ML pipeline as the authority for inference.
