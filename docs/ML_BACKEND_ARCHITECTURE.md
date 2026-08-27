# ML Backend Architecture — Safe Roads

This document designs the backend architecture focused solely on ML inference. It assumes the ML model is pre-trained and provided externally, with no training or data preprocessing responsibilities in the backend.

## Constraints

- **No Model Training**: Backend does not train models; models are loaded from disk.
- **Minimal Preprocessing**: Only basic input validation (e.g., presence of required fields); no feature engineering or encoding.
- **Runtime Loading**: Model loaded on-demand or at startup; cached for performance.

## Folder Structure

```
backend/
├── app.py                 # FastAPI application, routes, middleware
├── model_service.py       # ML inference service, model loading, prediction
└── models/                # Directory for model files (optional, for organization)
    └── model.pkl          # Trained model file (placed here or root)
```

- `backend/`: Core backend code.
- `models/`: Optional subfolder for model artifacts (e.g., `model.pkl`, config files).
- No changes to `frontend/`, `tools/`, `data/` — inference-only scope.

## Responsibility of Each File

### `backend/app.py`
- **Purpose**: Main FastAPI application entry point.
- **Responsibilities**:
  - Define FastAPI app instance, middleware (CORS, logging).
  - Define Pydantic models (`PredictRequest`, `ModelResult`) for API schema.
  - Implement `/predict` route: validate input, call `model_service.predict_probability()`, return JSON response.
  - Handle HTTP-level errors (e.g., 500 with sanitized messages).
  - Configure logging for errors.
- **Interactions**: Calls `model_service.predict_probability()` with validated input dict.

### `backend/services/model_service.py`
- **Purpose**: Abstraction layer for ML inference.
- **Responsibilities**:
  - Load trained model from disk (`model.pkl`) using `joblib`.
  - Implement `predict_probability(input_dict)`: prepare features, run model prediction, return standardized output.
  - Provide fallback to rule-based logic if model unavailable/invalid.
  - Generate explainable `breakdown` (rule-based, not ML-derived).
  - Clamp probabilities to [0.0, 0.95] for consistency.
- **Interactions**: Called by `app.py`; loads model at first inference or startup.

### `backend/models/` (Optional)
- **Purpose**: Storage for model files and metadata.
- **Responsibilities**: Hold `model.pkl` and any config (e.g., feature order). Not code, just assets.

## How the FastAPI Route Interacts with the Model Layer

1. **Request Reception**: `/predict` route receives JSON, parses via `PredictRequest` (Pydantic validation).
2. **Input Preparation**: `req.model_dump(mode="json")` converts enums to strings, creating input dict.
3. **Inference Call**: Route calls `model_service.predict_probability(input_dict)`.
4. **Model Loading**: If not cached, `model_service` loads `model.pkl` via `joblib.load()`.
5. **Prediction**: Model runs `predict_proba([features])`, extracts accident probability.
6. **Fallback**: On error, uses rule-based calculation.
7. **Response**: Returns `ModelResult` with probability, percent, breakdown.
8. **Error Handling**: Logs issues; API returns generic 500 if unrecoverable.

This architecture keeps inference decoupled, allowing easy model swaps without API changes.