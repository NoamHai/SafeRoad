# Local runbook

Use Python 3.10–3.12. Run all commands from the repository root. Follow the
[Windows setup and startup commands](../README.md) first. The frontend and backend
share one server at **http://127.0.0.1:8000**; no separate frontend server is needed.
Use the included model and mappings. Do not train a model to start the application.

## Automated checks

After installing `requirements-dev.txt` in the isolated environment:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/integration_test.py
.\.venv\Scripts\python.exe scripts/verify_final.py
.\.venv\Scripts\python.exe scripts/system_check.py
```

`pytest` includes actual saved-model checks and controlled failure tests. The
integration utility checks mapper conversions and a retained legacy numeric road
helper. `verify_final.py` checks imports, real inference, and frontend file presence.
`system_check.py` inspects files and imports. None of these utilities tests browser
layout or proves deployment readiness.

With Node.js available, also run:

```powershell
node --check frontend/script.js
node --test tests/frontend.test.cjs
```

These JavaScript tests use a small DOM substitute; they are not browser tests.

## Browser checks

- Load the page with no false error alert.
- Submit with a missing field and check the field-specific message.
- Fill every field and obtain a class plus Light/Dangerous probabilities.
- Switch English/Hebrew after a result; check retained values, translated output,
  and LTR/RTL layout.
- After a missing-field error, fill the form, stop the backend, and submit again.
  Check that the alert shows a network error, not the earlier validation message.
- Restart the backend and submit successfully again.

The output classifies accident severity, not accident occurrence. Probability
bands and explanatory text do not provide driving instructions.

## Troubleshooting

- Run from the root: static serving uses the relative `frontend` directory.
- Use the environment's Python executable directly; activation is optional and
  PowerShell script execution policy does not need to be changed.
- Use port 8000: the frontend's alternate-origin URL also targets this port.
- If Python is missing, install Python 3.12 manually, then repeat setup.
- For prediction HTTP 500, inspect the server log and restore the tracked model
  or authoritative mapping file if unavailable. Restart after resource restoration;
  resources are cached per process. Do not replace them with example data.
- HTTP 422 indicates an invalid request shape or time; consult the API contract.
