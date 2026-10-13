# Application overview

Safe Roads is an educational accident-severity classifier with a static bilingual
frontend and a FastAPI backend. It uses the included HistGradientBoosting pipeline
to classify a described accident as Light or Dangerous (fatal or severe).
The class probabilities do not predict whether an accident will occur.

The application accepts 16 required features. Stable frontend option keys are
mapped through the authoritative JSON file; `SHAA` is converted to a quarter-hour
code, and `ROAD_STRUCTURE` retains the model's string categories. The API returns
a class, class label, and two probabilities. No factor-impact explanation is
computed. The frontend supports English/LTR and Hebrew/RTL.

The saved model, metadata, datasets, experiments, evaluation results, and mentor
examples remain in the repository. Historical preprocessing helpers are retained
but do not define the final model's input transformation.

Use the [README](../README.md) for setup, [runbook](FINAL_RUNBOOK.md) for checks,
and [ML guide](../safe_roads_ml/README.md) for research and training instructions.
Verification must be performed against the exact commit being submitted; this
page is a component overview, not a claim of production or submission readiness.
