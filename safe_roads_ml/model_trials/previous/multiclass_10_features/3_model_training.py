# Historical 10-feature multiclass comparison with logistic-regression tuning.

import builtins
import os
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    f1_score
)


# --- log all prints to file only (no console output) ---
os.makedirs("runs", exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = f"runs/run_{stamp}.txt"
_log_f = open(LOG_PATH, "w", encoding="utf-8")

def print(*args: object, **kwargs: object) -> None:
    """Write experiment output to the log and flush it immediately."""
    builtins.print(*args, file=_log_f, **kwargs)
    _log_f.flush()

# --- config ---
INPUT_FILE = "accidents_10_feat.xlsx"
TARGET_COL = "HUMRAT_TEUNA"

print("LOG_PATH:", LOG_PATH)
print("INPUT_FILE:", INPUT_FILE)
print("TARGET_COL:", TARGET_COL)

# --- load data ---
df = pd.read_excel(INPUT_FILE)

X = df.drop(columns=[TARGET_COL])
y = df[TARGET_COL]

# --- split ---
X_trainVal, X_test, y_trainVal, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_trainVal, y_trainVal,
    test_size=0.25,
    random_state=42,
    stratify=y_trainVal
)

# --- feature groups ---
cat_cols = [
    "SUG_DEREH",
    "HODESH_TEUNA",
    "YOM_BASHAVUA",
    "SIMUN_TIMRUR",
    "TEURA",
    "PNE_KVISH",
    "MAHOZ",
    "SHAA"
]

ord_cols = ["MEHIRUT_MUTERET", "ROHAV"]

# --- ordinal: 0 -> NaN ---
for c in ord_cols:
    X_train[c] = X_train[c].astype(float)
    X_val[c]   = X_val[c].astype(float)
    X_test[c]  = X_test[c].astype(float)

for c in ord_cols:
    X_train.loc[:, c] = X_train[c].replace(0, np.nan)
    X_val.loc[:, c]   = X_val[c].replace(0, np.nan)
    X_test.loc[:, c]  = X_test[c].replace(0, np.nan)

# --- preprocessing ---
cat_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

ord_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

preprocess = ColumnTransformer(
    transformers=[
        ("cat", cat_transformer, cat_cols),
        ("ord", ord_transformer, ord_cols),
    ],
    remainder="drop"
)

# --- helpers ---
def eval_on_val(model: Pipeline, name: str) -> dict[str, str | float]:
    """Fit on training data and return validation metrics for the named model."""
    model.fit(X_train, y_train)
    pred = model.predict(X_val)

    bal_acc = balanced_accuracy_score(y_val, pred)
    f1_macro = f1_score(y_val, pred, average="macro")
    f1_weighted = f1_score(y_val, pred, average="weighted")

    print(f"\n=== {name} - VAL ===")
    print("VAL Balanced Accuracy:", bal_acc)
    print("VAL F1 macro:", f1_macro)
    print("VAL F1 weighted:", f1_weighted)
    print(classification_report(y_val, pred))
    print("Confusion matrix:\n", confusion_matrix(y_val, pred))

    return {
        "model": name,
        "val_bal_acc": float(bal_acc),
        "val_f1_macro": float(f1_macro),
        "val_f1_weighted": float(f1_weighted),
    }

def cv_on_train(model: Pipeline, name: str, cv: StratifiedKFold) -> dict[str, float]:
    """Return mean cross-validation metrics computed only on training data."""
    scoring = {
        "bal_acc": "balanced_accuracy",
        "f1_macro": "f1_macro",
        "f1_weighted": "f1_weighted"
    }
    cv_res = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)

    out = {
        "cv_bal_acc": float(cv_res["test_bal_acc"].mean()),
        "cv_f1_macro": float(cv_res["test_f1_macro"].mean()),
        "cv_f1_weighted": float(cv_res["test_f1_weighted"].mean())
    }

    print(f"\n=== {name} - CV on TRAIN ===")
    print("CV Balanced Acc:", out["cv_bal_acc"])
    print("CV F1 macro:", out["cv_f1_macro"])
    print("CV F1 weighted:", out["cv_f1_weighted"])
    return out

# --- CV splitter ---
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# --- models ---
log_reg = Pipeline(steps=[
    ("prep", preprocess),
    ("model", LogisticRegression(
        max_iter=3000,
        class_weight="balanced",
        random_state=42
    ))
])

rf = Pipeline(steps=[
    ("prep", preprocess),
    ("model", RandomForestClassifier(
        n_estimators=500,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    ))
])

hgb = Pipeline(steps=[
    ("prep", preprocess),
    ("model", HistGradientBoostingClassifier(
        random_state=42
    ))
])

models = {
    "LogisticRegression (baseline)": log_reg,
    "RandomForest (baseline)": rf,
    "HistGradientBoosting (baseline)": hgb
}

# --- 1) Baseline VAL for all models ---
results = []
for name, mdl in models.items():
    results.append(eval_on_val(mdl, name))

# --- 2) CV on TRAIN for all models ---
for r in results:
    name = r["model"]
    r.update(cv_on_train(models[name], name, cv))

# --- 3) GridSearch for Logistic Regression only ---
param_grid = {"model__C": [0.01, 0.1, 1, 3, 10]}

grid = GridSearchCV(
    log_reg,
    param_grid=param_grid,
    scoring="f1_macro",
    cv=cv,
    n_jobs=-1
)

grid.fit(X_train, y_train)

print("\n=== GridSearch (Logistic Regression) Results ===")
print("Best params:", grid.best_params_)
print("Best CV f1_macro:", float(grid.best_score_))

best_log_reg = grid.best_estimator_

tuned_res = eval_on_val(best_log_reg, "LogisticRegression (tuned)")
tuned_res.update(cv_on_train(best_log_reg, "LogisticRegression (tuned)", cv))
tuned_res["best_params"] = str(grid.best_params_)
tuned_res["best_cv_search_f1_macro"] = float(grid.best_score_)

results.append(tuned_res)

# --- 4) Summary table to CSV ---
res_df = pd.DataFrame(results)

order_cols = [
    "model",
    "val_bal_acc", "val_f1_macro", "val_f1_weighted",
    "cv_bal_acc", "cv_f1_macro", "cv_f1_weighted",
    "best_params", "best_cv_search_f1_macro"
]
for c in order_cols:
    if c not in res_df.columns:
        res_df[c] = np.nan

res_df = res_df[order_cols].sort_values(by="val_f1_macro", ascending=False)

print("\n=== SUMMARY (sorted by VAL F1 macro) ===")
print(res_df)

summary_csv = f"runs/summary_{stamp}.csv"
res_df.to_csv(summary_csv, index=False)
print("\nSaved summary to:", summary_csv)

# --- 5) Fit a chosen final model on TrainVal (no TEST here) ---
final_model = best_log_reg
final_model.fit(X_trainVal, y_trainVal)

print("\nFinal model trained on TrainVal (no TEST run in this script).")
print("Final model:", "LogisticRegression (tuned)")

_log_f.close()

# minimal console hint (does not use print override)
builtins.print("Done. Outputs saved to:", LOG_PATH)
builtins.print("Summary saved to:", summary_csv)
