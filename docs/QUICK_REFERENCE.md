# Developer quick reference

See the [README](../README.md) for installation and single-server startup, and the
[runbook](FINAL_RUNBOOK.md) for verification commands and browser checks.

## Prediction path

`frontend/script.js` → `POST /predict` → `PredictRequest` →
`predict_probability` → `prepare_model_frame` → saved pipeline → `ModelResult`.

- `backend/models/schemas.py`: 16 required fields; extra keys are forbidden.
- `backend/services/feature_value_mappings.json`: authoritative option-key mappings.
- `backend/services/data_mapper.py`: `SHAA` conversion and ordered input frame.
- `backend/services/model_service.py`: cached model loading and inference.
- `frontend/script.js`: `i18n`, stable option keys, language switching, and results.

`ROAD_STRUCTURE` maps to strings such as `HAD_1`, not numeric lane codes.
`prepare_model_array` returns an object array of shape `(1, 16)`; inference uses
the named DataFrame instead. The retained legacy dataset helpers are not the
final training pipeline. See [the mapper reference](../backend/services/README_DATA_MAPPER.md).

The response has exactly `prediction`, `prediction_label`, `light_probability`,
and `dangerous_probability`. There is no factor-impact breakdown. The frontend
shows display bands of Dangerous-class probability, not accident-occurrence risk.

## Configuration and errors

Use `.env.example` for optional application settings. CORS lists use JSON.
Missing mappings or an unloadable model disable inference and return HTTP 500.
Invalid request shape or time returns HTTP 422. Unrecognized category values
currently map to default `0`; this retained behavior is separate from resource
errors and should not be confused with legitimate unknown categories.
