# Safe Roads — Accident Severity Classifier

[GitHub repository](https://github.com/NoamHai/SafeRoad)

Safe Roads classifies the severity of a described road accident using 16 features.
The included scikit-learn model returns **Light** (`0`) or **Dangerous** (`1`, fatal
or severe), with a model probability for each class. These probabilities do not
estimate whether an accident will occur. The English/Hebrew interface supports RTL.

## Requirements

- Python 3.10–3.12 (Python 3.12 is recommended for the Windows commands below).
- A modern browser and internet access for the initial dependency installation.
- No database, API credentials, Node.js build, or model retraining is required.

## Windows setup

Open PowerShell in the repository root. If `py` does not find Python 3.12, use the
full path to an installed Python 3.12 interpreter for the first command.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Start

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --reload --port 8000
```

Open **http://127.0.0.1:8000**. One server serves both the frontend and `POST /predict`.
Select the accident scenario, including accident type, then click **Classify Severity**.
The gauge shows display bands of the Dangerous-class probability; it is not a
validated driving-safety scale. Stop the server with `Ctrl+C`.

## Included resources and optional configuration

Keep `safe_roads_ml/final_model/saved_model/safe_roads_model.joblib`, its
`model_metadata.json`, and `backend/services/feature_value_mappings.json` in place.
The application uses the included model without training. If the model or required
mappings cannot be loaded, prediction returns an error instead of substitute results.

No `.env` file is required. To customize `APP_NAME`, `DEBUG`, or `CORS_ORIGINS`, copy
`.env.example` to `.env` in the root. `CORS_ORIGINS` uses a JSON list. Same-origin
startup needs no CORS changes. Google Fonts is optional; CSS provides fallback fonts.

## Verify

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest
```

The tests cover the API contract, actual saved-model predictions, mappings,
required-resource failures, configuration, and static frontend serving. If Node.js
is available, run `node --test tests/frontend.test.cjs` for UI logic regressions.
Browser checks remain separate; see [the runbook](docs/FINAL_RUNBOOK.md).

For data preparation, experiments, and training instructions, see the
[ML guide](safe_roads_ml/README.md). See [the API contract](docs/ML_INTERFACE_CONTRACT.md)
for request and response details.
