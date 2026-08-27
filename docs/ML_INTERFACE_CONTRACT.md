# ML Interface Contract — Safe Roads Backend

This document defines the clean interface between the FastAPI backend (`backend/services/model_service.py`) and a future trained ML model provided by the data/ML partner (Mor). The interface ensures seamless integration without modifying the backend code.

## 1. Expected Input Features

The model must accept input as a list of 6 string features representing driving conditions:

- `road_type`: String indicating road environment (e.g., "urban", "highway").
- `weather`: String describing weather conditions (e.g., "clear", "rain", "fog").
- `time_of_day`: String for time period (e.g., "day", "night").
- `lighting`: String for visibility conditions (e.g., "daylight", "dark_with_streetlights", "dark_no_streetlights").
- `junction`: String indicating junction presence (e.g., "no_junction", "junction").
- `road_surface`: String for surface condition (e.g., "dry", "wet", "unknown").

**Abstract Specification**: Input is a list of 6 categorical strings. No preprocessing required in backend; model handles encoding internally. Features are derived from user inputs and match frontend enum values.

## 2. Expected Output Format

The model must implement `predict_proba(input_list)` returning a 2-element array:

- `[prob_no_accident, prob_accident]`: NumPy array or list of floats summing to 1.0.
- Backend extracts `prob_accident` (index 1) as the accident probability.

**Abstract Specification**: Binary classification probabilities. Output must be a sequence of two floats (probabilities for classes 0 and 1, where 1 = accident). Backend clamps the accident probability to [0.0, 0.95] for consistency.

## 3. Model File Format Assumptions

- **File Name**: `model.pkl` (placed in project root).
- **Serialization**: Joblib (scikit-learn compatible) pickle format.
- **Requirements**: Model object must have `predict_proba` method accepting a list of lists (e.g., `[features]` for single prediction).
- **Dependencies**: Model may require scikit-learn, but backend only imports `joblib` for loading.
- **Version Compatibility**: Assume compatible with Python 3.8+ and joblib 1.0+.

**Abstract Specification**: Serialized model file loadable via `joblib.load()`. No specific ML library assumed, as long as interface matches.

## 4. Error Handling Strategy

- **Model Missing**: If `model.pkl` does not exist, backend falls back to rule-based prediction without error.
- **Loading Failure**: If `joblib.load()` raises exception (e.g., corrupted file, incompatible version), log error and fall back to rule-based.
- **Prediction Failure**: If `predict_proba()` raises exception (e.g., invalid input shape), log error and fall back to rule-based.
- **Logging**: Errors logged via Python `logging` (configured in `backend/app.py`); no crashes or user-visible errors.
- **Fallback Behavior**: Rule-based prediction ensures system always works; breakdown remains explainable.

**Abstract Specification**: Graceful degradation — ML enhances prediction if available, but system remains functional without it. Errors do not propagate to API responses.

## Integration Notes

- **Backend Changes**: No code changes needed when model is provided; just place `model.pkl` in root.
- **Testing**: Partner should test model locally with `backend/model_service.predict_probability(input_dict)` before deployment.
- **Performance**: Model should be lightweight for real-time inference; backend is synchronous.
- **Updates**: If model interface changes, update this contract and backend code accordingly.

This contract ensures clean separation: backend handles API/inference plumbing, ML partner provides the trained model.