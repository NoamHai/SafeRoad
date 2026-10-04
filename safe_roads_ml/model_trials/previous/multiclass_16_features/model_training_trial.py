# ------------------------------------------------------------
# Historical multiclass comparison on 16 features
# ------------------------------------------------------------
# Compare Logistic Regression, Random Forest, and HistGradientBoosting.
# One-hot encode all features and group rare categories.
# ------------------------------------------------------------

import builtins
import os
from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
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
from sklearn.utils.class_weight import compute_sample_weight

from typing import Any

# ------------------------------------------------------------
# --- logging setup: writes experiment prints to the log file ---
# ------------------------------------------------------------
os.makedirs("runs", exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_PATH = f"runs/run_{stamp}.txt"
_log_f = open(LOG_PATH, "w", encoding="utf-8")

def print(*args: Any, **kwargs: Any) -> None:
    # write to log file
    builtins.print(*args, file=_log_f, **kwargs)
    _log_f.flush()

# ------------------------------------------------------------
# --- config ---
# ------------------------------------------------------------
INPUT_FILE = "accidents_full_copy.xlsx"
TARGET_COL = "HUMRAT_TEUNA"
RANDOM_STATE = 42

print("LOG_PATH:", LOG_PATH)
print("INPUT_FILE:", INPUT_FILE)
print("TARGET_COL:", TARGET_COL)
print("RANDOM_STATE:", RANDOM_STATE)

# ------------------------------------------------------------
# --- load data ---
# ------------------------------------------------------------
df = pd.read_excel(INPUT_FILE)

# drop rows where target is missing, if any
df = df.dropna(subset=[TARGET_COL])

selected_features = [
    "SHAA",
    "HODESH_TEUNA",
    "YOM_BASHAVUA",
    "EZOR_TIVI",
    "SUG_TEUNA",
    "ROHAV",
    "MEHIRUT_MUTERET",
    "HAD_MASLUL",
    "NAFA",
    "ZURAT_ISHUV",
    "SUG_DEREH",
    "TEURA",
    "RAV_MASLUL",
    "MAHOZ",
    "SIMUN_TIMRUR",
    "PNE_KVISH"
]

X = df[selected_features]
y = df[TARGET_COL]

print("\nSamples:", df.shape[0])
print("Features:", X.shape[1])
print("Target distribution:\n", y.value_counts())

# ------------------------------------------------------------
# --- split into Train/Val/Test (stratified) ---
# ------------------------------------------------------------
X_trainVal, X_test, y_trainVal, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_trainVal, y_trainVal,
    test_size=0.25,   # 0.25 of 80% = 20% -> final splits: 60% train, 20% val, 20% test
    random_state=RANDOM_STATE,
    stratify=y_trainVal
)

print("\nTrain:", X_train.shape, "Val:", X_val.shape, "Test:", X_test.shape)
print("Train distribution:\n", y_train.value_counts(normalize=True))
print("Val distribution:\n", y_val.value_counts(normalize=True))
print("Test distribution:\n", y_test.value_counts(normalize=True))

# ------------------------------------------------------------
# --- preprocessing ---
# ------------------------------------------------------------
# treat all remaining features as categorical
cat_cols = X.columns.tolist()
ord_cols = []  # none, since all treated as categorical in this run

# imputing + one-hot for all categorical
# handle_unknown='infrequent_if_exist' + min_frequency avoids explosion of dummy columns
cat_transformer = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(
        handle_unknown="infrequent_if_exist",
        min_frequency=50,      # adjust if needed; currently groups categories appearing <50 times
        sparse_output=False
    )),
])

# assemble
preprocess = ColumnTransformer(
    transformers=[
        ("cat", cat_transformer, cat_cols)
    ],
    remainder="drop"
)

# ------------------------------------------------------------
# --- CV splitter ---
# ------------------------------------------------------------
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

# ------------------------------------------------------------
# --- models ---
# ------------------------------------------------------------
log_reg = Pipeline(steps=[
    ("prep", preprocess),
    ("model", LogisticRegression(
        max_iter=3000,          # enough iterations for convergence
        class_weight="balanced",
        random_state=RANDOM_STATE
    ))
])

rf = Pipeline(steps=[
    ("prep", preprocess),
    ("model", RandomForestClassifier(
        n_estimators=300,       # fewer than 500 for speed; adjust if needed
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1
    ))
])

hgb = Pipeline(steps=[
    ("prep", preprocess),
    ("model", HistGradientBoostingClassifier(
        random_state=RANDOM_STATE
    ))
])

models = {
    "LogisticRegression": log_reg,
    "RandomForest": rf,
    "HistGradientBoosting": hgb
}

# ------------------------------------------------------------
# --- helper functions ---
# ------------------------------------------------------------
def fit_with_optional_sample_weight(
    pipeline_model: Pipeline,
    X_fit: pd.DataFrame,
    y_fit: pd.Series,
) -> bool:
    """
    Try to fit with sample_weight if the model supports it,
    otherwise fit without it.
    """
    sw = compute_sample_weight(class_weight="balanced", y=y_fit)

    try:
        # pass sample_weight to the final estimator in pipeline if supported
        pipeline_model.fit(X_fit, y_fit, model__sample_weight=sw)
        return True
    except TypeError:
        # if the model does not accept sample_weight named parameter
        pipeline_model.fit(X_fit, y_fit)
        return False

def eval_on_val(model: Pipeline, name: str) -> dict:
    used_sw = fit_with_optional_sample_weight(model, X_train, y_train)
    pred = model.predict(X_val)

    bal_acc = balanced_accuracy_score(y_val, pred)
    f1_macro = f1_score(y_val, pred, average="macro")
    f1_weighted = f1_score(y_val, pred, average="weighted")

    print(f"\n=== {name} - VAL ===")
    print("used_sample_weight:", used_sw)
    print("VAL Balanced Accuracy:", bal_acc)
    print("VAL F1 macro:", f1_macro)
    print("VAL F1 weighted:", f1_weighted)
    print(classification_report(y_val, pred))
    print("Confusion matrix:\n", confusion_matrix(y_val, pred))

    return {
        "model": name,
        "used_sample_weight": used_sw,
        "val_bal_acc": float(bal_acc),
        "val_f1_macro": float(f1_macro),
        "val_f1_weighted": float(f1_weighted),
    }

def cv_on_train(model: Pipeline, name: str, cv_obj: StratifiedKFold) -> dict:
    scoring = {
        "bal_acc": "balanced_accuracy",
        "f1_macro": "f1_macro",
        "f1_weighted": "f1_weighted"
    }
    cv_res = cross_validate(model, X_train, y_train, cv=cv_obj, scoring=scoring, n_jobs=-1)

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

# ------------------------------------------------------------
# --- 1) Baseline VAL for all models ---
# ------------------------------------------------------------
results = []
for name, mdl in models.items():
    results.append(eval_on_val(mdl, name))

# ------------------------------------------------------------
# --- 2) CV on TRAIN for all models ---
# ------------------------------------------------------------
for r in results:
    name = r["model"]
    r.update(cv_on_train(models[name], name, cv))

# ------------------------------------------------------------
# --- 3) Summary table to CSV ---
# ------------------------------------------------------------
res_df = pd.DataFrame(results)

order_cols = [
    "model",
    "used_sample_weight",
    "val_bal_acc", "val_f1_macro", "val_f1_weighted",
    "cv_bal_acc", "cv_f1_macro", "cv_f1_weighted"
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

# ------------------------------------------------------------
# --- 4) Train the selected model on TrainVal ---
# ------------------------------------------------------------
# Select by validation F1 macro; this experiment does not save a model.
best_model_name = res_df.iloc[0]["model"]
final_model = models[best_model_name]

# train on full TrainVal set
fit_with_optional_sample_weight(final_model, X_trainVal, y_trainVal)
print(f"\nFinal model trained on TrainVal: {best_model_name}")

# ------------------------------------------------------------
# --- close log ---
# ------------------------------------------------------------
_log_f.close()

builtins.print("Done. Outputs saved to:", LOG_PATH)
builtins.print("Summary saved to:", summary_csv)
