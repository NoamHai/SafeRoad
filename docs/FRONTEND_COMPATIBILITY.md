# Frontend Compatibility — Safe Roads

## Verification Summary

The frontend (`frontend/script.js`) does **not require any changes** when switching from rule-based logic to ML-based inference in the backend. The API response format remains identical, ensuring full backward compatibility.

## Detailed Analysis

### Expected Response Structure
The frontend expects the `/predict` API to return a JSON object with exactly these keys:

- `probability`: A number (0.0 to 1.0) representing accident risk.
- `risk_percent`: An integer (0 to 100), though the frontend recalculates it from `probability` for display.
- `breakdown`: An array of objects, each with:
  - `factor`: String (e.g., "weather")
  - `value`: String (e.g., "rain")
  - `delta`: Number (fractional risk increase, e.g., 0.18)
  - `note`: String (human-readable explanation)

### Backend Response with ML Inference
The updated `backend/services/model_service.py` preserves this structure:
- `probability`: Clamped float from ML `predict_proba` or rule-based fallback.
- `risk_percent`: Calculated as `int(round(probability * 100))`.
- `breakdown`: Generated using rule-based logic (not ML-derived), providing consistent explainability.

### Code Compatibility Check
- **Probability Handling**: `const p = Number(data.probability);` works with ML or rule-based values.
- **Breakdown Rendering**: `breakdown.map(x => \`${x.factor} (+${Math.round(Number(x.delta) * 100)}%)\`)` assumes `factor` and `delta` fields, which are unchanged.
- **Error Handling**: No changes to error display; backend errors are handled at API level.
- **UI Logic**: Risk classification, advice, and bar display depend only on `probability`, unaffected by inference method.

### Why No Changes Are Needed
- The API contract is strictly preserved (as documented in `docs/ML_INTERFACE_CONTRACT.md`).
- ML inference only affects the `probability` value; structure remains the same.
- Fallback to rule-based ensures the system works without ML, maintaining compatibility.
- No redesign of UI is required, as per constraints.

## Conclusion
The frontend is fully compatible with ML-based inference. No code changes are necessary. The switch is seamless: place `model.pkl` in the project root, and the backend will use it automatically while keeping the UI experience identical.