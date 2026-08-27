# ML Interface Contract — Safe Roads Backend

This document defines the implemented interface between the FastAPI application and Mor's final saved accident-severity model.

## 1. Prediction Request

`POST /predict` accepts exactly the following 16 required fields, in the model feature order:

1. `SHAA`
2. `HODESH_TEUNA`
3. `YOM_BASHAVUA`
4. `SUG_TEUNA`
5. `ROAD_STRUCTURE`
6. `ROHAV`
7. `NAFA`
8. `ZURAT_ISHUV`
9. `MEHIRUT_MUTERET`
10. `TEURA`
11. `SUG_DEREH`
12. `SIMUN_TIMRUR`
13. `TKINUT`
14. `PNE_KVISH`
15. `MEZEG_AVIR`
16. `YOM_LAYLA`

Values may be supported descriptive mapping keys or valid encoded values. The API rejects missing or unexpected fields; it does not translate older request formats or synthesize missing current fields.

## 2. Model Input and Output

`backend/services/data_mapper.py` maps the validated request to a one-row `pandas.DataFrame` ordered by `FEATURE_ORDER`. The saved pipeline implements `predict_proba(frame)` and returns class probabilities. Class `0` means `Light accident`; class `1` means `Dangerous accident`.

The API response contains exactly:

- `prediction`: integer class, `0` or `1`.
- `prediction_label`: `Light accident` or `Dangerous accident`.
- `light_probability`: floating-point probability in `[0, 1]`.
- `dangerous_probability`: floating-point probability in `[0, 1]`.

Exact probabilities are produced by the saved model and are not fixed by this contract.

## 3. Saved Model Artifacts

- Model: `safe_roads_ml/final_model/saved_model/safe_roads_model.joblib`
- Metadata: `safe_roads_ml/final_model/saved_model/model_metadata.json`
- Loading: `joblib.load()` through `backend/services/model_service.py`
- Required method: `predict_proba`

The metadata supplies the target labels, while `FEATURE_ORDER` controls the application-to-model column order.

## 4. Failure Behavior

- Invalid request shape or keys: rejected before inference.
- Invalid `SHAA`: rejected as a validation error.
- Missing or unloadable saved model: prediction is disabled and the API returns an error.
- Model inference failure: logged and returned as an API error.

There is no rule-based or dummy prediction fallback.

## Integration Notes

- The route validates `PredictRequest`, serializes it, and calls `predict_probability(payload)`.
- `predict_probability` builds the ordered feature frame, loads the cached real model, aligns Light/Dangerous probabilities, and formats the response.
- Model training is outside the runtime backend; this contract covers inference only.
- Changes to feature order, mapping meaning, target semantics, or response fields require coordinated changes to the model and application.
