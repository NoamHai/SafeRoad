# Application setup and deployment notes

For local submission verification, use the [root README](../README.md) and
[runbook](FINAL_RUNBOOK.md). Supported Python versions are 3.10–3.12. Install
runtime packages from `requirements.txt`; testing also requires
`requirements-dev.txt`. There is one server, run from the repository root on port
8000. The static frontend has no build step.

## Required resources

- `safe_roads_ml/final_model/saved_model/safe_roads_model.joblib`
- `safe_roads_ml/final_model/saved_model/model_metadata.json` (class labels)
- `backend/services/feature_value_mappings.json`
- `frontend/index.html`, `frontend/script.js`, and `frontend/style.css`

The saved model is included. Datasets, a processed-data pickle, external APIs,
credentials, and retraining are not required for inference. The metadata has
built-in label defaults; the real model and authoritative mappings are required
for prediction. Missing or invalid mappings allow static serving but cause
prediction to return the existing controlled HTTP 500 error.

## Optional configuration

The root `.env` can set `APP_NAME`, `DEBUG`, and `CORS_ORIGINS`. Use the JSON-list
syntax in `.env.example`. There is no environment setting for the saved-model path.
For local same-origin use, keep the defaults. Do not expose debug mode publicly.

This repository does not establish production hosting, TLS, authentication, load
capacity, or operational monitoring. Passing local checks is evidence for the
submission workflow, not a production-readiness guarantee.
