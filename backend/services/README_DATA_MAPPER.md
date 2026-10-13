# Feature mapping reference

The runtime mapping source is `backend/services/feature_value_mappings.json`.
Frontend labels are bilingual; option keys stay in English. The JSON contains 15
categorical-field mappings. `SHAA` is converted separately into quarter-hour codes.
Do not edit mapping meanings independently of the saved model and official data dictionary.

## Runtime flow

`prepare_model_input` matches option keys exactly, then without case sensitivity.
Recognized raw codes are also accepted. `prepare_model_frame` returns one row in
`FEATURE_ORDER`, with the column names expected by the saved pipeline.
`prepare_model_array` is a supporting helper returning an object array `(1, 16)`.

| Field | Model representation |
| --- | --- |
| `SHAA` | Integer 1–96; `00:00` → 1, `08:00` → 33, `23:45` → 96 |
| `HODESH_TEUNA` | Integer month code |
| `YOM_BASHAVUA` | Integer weekday code |
| `SUG_TEUNA` | Integer accident-type code |
| `ROAD_STRUCTURE` | `HAD_1`–`HAD_3`, `RAV_1`–`RAV_4`, or `OTHER` |
| `ROHAV` | Integer road-width code |
| `NAFA` | Integer district code |
| `ZURAT_ISHUV` | Integer settlement-form code |
| `MEHIRUT_MUTERET` | Integer speed-limit code |
| `TEURA` | Integer lighting code |
| `SUG_DEREH` | Integer road-type code |
| `SIMUN_TIMRUR` | Integer marking code |
| `TKINUT` | Integer road-condition code |
| `PNE_KVISH` | Integer surface code |
| `MEZEG_AVIR` | Integer weather code |
| `YOM_LAYLA` | Integer day/night code |

The JSON file is the value reference; this guide does not maintain a second table
of category codes. Legitimate unknown categories remain supported as defined there.

## Errors and retained behavior

All 16 request keys are required and extra keys are rejected. `SHAA` accepts valid
1–96 codes or `HH:MM` with minutes 00, 15, 30, or 45. Unsupported times raise a
validation error. Other unrecognized values currently become default `0`;
`validate_ui_input` can report warnings but is not called by the prediction route.
This behavior has not been tightened during submission preparation.

The authoritative file is loaded once per process. If it is missing, unreadable,
malformed, or structurally invalid, no older mapping is substituted. Static serving
remains available and prediction reaches the existing controlled HTTP 500 handler.
Restore the tracked file and restart the process to recover.

## Historical helpers

`engineer_road_structure` and `preprocess_dataset` retain older numeric lane codes.
They are referenced by historical examples and `scripts/integration_test.py` and
are not used by `/predict` or the final training script. Do not use them to regenerate
the saved model. `REVERSE_MAPPINGS` returns option keys, not translated UI labels.

From the root, after installing development dependencies:

```powershell
.\.venv\Scripts\python.exe scripts/integration_test.py
.\.venv\Scripts\python.exe -m pytest
```

The first command checks conversions and the legacy helper. The second includes
real-model API, mapping-resource, and static-serving checks. Browser language and
layout verification is separate; see [the runbook](../../docs/FINAL_RUNBOOK.md).
