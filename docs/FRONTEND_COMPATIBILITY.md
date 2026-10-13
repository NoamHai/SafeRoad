# Frontend and Prediction-API Compatibility — Safe Roads

## Interface Summary

The current frontend and backend use the same final 16-field prediction contract. The frontend constructs the uppercase payload in `frontend/script.js`, and `PredictRequest` requires those fields while rejecting unexpected keys.

## Request Contract

The frontend submits:

`SHAA`, `HODESH_TEUNA`, `YOM_BASHAVUA`, `SUG_TEUNA`, `ROAD_STRUCTURE`, `ROHAV`, `NAFA`, `ZURAT_ISHUV`, `MEHIRUT_MUTERET`, `TEURA`, `SUG_DEREH`, `SIMUN_TIMRUR`, `TKINUT`, `PNE_KVISH`, `MEZEG_AVIR`, and `YOM_LAYLA`.

All fields are required. Unsupported extra keys and incomplete payloads are rejected rather than converted to defaults.

## Response Contract

The frontend consumes exactly:

- `prediction`: `0` for Light accident or `1` for Dangerous accident.
- `prediction_label`: corresponding English class label.
- `light_probability`: model probability for class `0`.
- `dangerous_probability`: model probability for class `1`.

The UI derives displayed percentages and probability display bands from the returned probabilities. The API does not return a factor breakdown.

## Integration Checks

- `frontend/script.js` sends all 16 current fields to `POST /predict`.
- The backend mapping keys correspond to the values supplied by the current selectors.
- The frontend verifies that the class and both probabilities are numeric before rendering.
- Network or response-contract failures are shown through the existing error state.
- The backend requires the real saved model and does not provide rule-based predictions.

## Conclusion

The current frontend is aligned with the final ML inference contract. Future changes to request keys, feature order, target meaning, or response fields must be coordinated across frontend, schemas, mapper, service, tests, and documentation.
