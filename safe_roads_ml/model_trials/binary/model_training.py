# ------------------------------------------------------------
# Binary model trials on selected feature sets
# ------------------------------------------------------------
# For each feature list:
# 1. Load full dataset
# 2. Clean blanks -> NaN
# 3. Combine HAD_MASLUL + RAV_MASLUL into ROAD_STRUCTURE
# 4. Drop irrelevant columns
# 5. Drop columns with too much missing data
# 6. Convert target to binary:
#       1 = dangerous (fatal + severe)
#       0 = light
# 7. Keep only selected features
# 8. Compare 3 models:
#       - Logistic Regression  (one-hot)
#       - Random Forest        (ordinal encoding)
#       - HistGradientBoosting (one-hot)
# 9. Save logs and summaries per feature set
# ------------------------------------------------------------

import builtins
import os
from datetime import datetime

import numpy as np
import pandas as pd

from datetime import datetime
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score
)
from sklearn.utils.class_weight import compute_sample_weight

from typing import Any, Callable

print("Run started at:", datetime.now().strftime("%H:%M:%S"))

# ------------------------------------------------------------
# --- config ---
# ------------------------------------------------------------
INPUT_FILE = "accidents_full_copy.xlsx"
TARGET_COL = "HUMRAT_TEUNA"
BINARY_TARGET_COL = "TARGET_BINARY"

MISSING_THRESHOLD = 0.5
RANDOM_STATE = 42
N_SPLITS_CV = 5   # reduce to 3 if runtime is too long

# ------------------------------------------------------------
# --- feature sets to test ---
# ------------------------------------------------------------
# This experiment uses the ordered top-16 list with combined ROAD_STRUCTURE.
FEATURE_SETS = {
    "top16": [
        "SHAA",
        "HODESH_TEUNA",
        "YOM_BASHAVUA",
        "SUG_TEUNA",
        "ROAD_STRUCTURE",
        "ROHAV",
        "NAFA",
        "ZURAT_ISHUV",
        "MEHIRUT_MUTERET",
        "TEURA",
        "SUG_DEREH",
        "SIMUN_TIMRUR",
        "TKINUT",
        "PNE_KVISH",
        "MEZEG_AVIR",
        "YOM_LAYLA"
    ]
}

# ------------------------------------------------------------
# --- global run folder ---
# ------------------------------------------------------------
os.makedirs("runs", exist_ok=True)


# ------------------------------------------------------------
# --- helper: combine HAD_MASLUL + RAV_MASLUL ---
# ------------------------------------------------------------
def combine_road_structure(row: pd.Series) -> str:
    had = row["HAD_MASLUL"]
    rav = row["RAV_MASLUL"]

    # single-carriageway values
    if pd.notna(had) and had != 0:
        if had in [1, 2, 3]:
            return f"HAD_{int(had)}"
        else:
            return "OTHER"

    # multi-carriageway values
    if pd.notna(rav) and rav != 0:
        if rav in [1, 2, 3, 4]:
            return f"RAV_{int(rav)}"
        else:
            return "OTHER"

    return "OTHER"


# ------------------------------------------------------------
# --- helper: load and prepare base dataframe ---
# ------------------------------------------------------------
def load_and_prepare_base_df() -> pd.DataFrame:
    df = pd.read_excel(INPUT_FILE)

    # convert cells with only spaces to NaN
    df = df.replace(r"^\s*$", np.nan, regex=True)

    # combine road structure BEFORE dropping old columns
    df["ROAD_STRUCTURE"] = df.apply(combine_road_structure, axis=1)

    # remove old split columns
    df = df.drop(columns=["HAD_MASLUL", "RAV_MASLUL"], errors="ignore")

    # remove level-1 columns (identifiers / exact location / admin / time-specific)
    drop_cols_level1 = [
        "pk_teuna_fikt",
        "sug_tik",
        "SEMEL_YISHUV",
        "REHOV1",
        "REHOV2",
        "BAYIT",
        "KVISH1",
        "KVISH2",
        "KM",
        "YEHIDA",
        "X",
        "Y",
        "YEAR",
        "SHNAT_TEUNA",
    ]

    df = df.drop(columns=drop_cols_level1, errors="ignore")

    # drop columns with too many missing values
    missing_ratio = df.isnull().mean()
    cols_to_drop_missing = missing_ratio[missing_ratio > MISSING_THRESHOLD].index.tolist()

    if TARGET_COL in cols_to_drop_missing:
        cols_to_drop_missing.remove(TARGET_COL)

    df = df.drop(columns=cols_to_drop_missing, errors="ignore")

    # drop rows where target is missing
    df = df.dropna(subset=[TARGET_COL]).copy()

    # convert target to binary
    # 1 = dangerous (fatal + severe), 0 = light
    df[BINARY_TARGET_COL] = df[TARGET_COL].replace({
        1: 1,
        2: 1,
        3: 0
    })

    return df


# ------------------------------------------------------------
# --- helper: fit with optional sample_weight ---
# ------------------------------------------------------------
def fit_with_optional_sample_weight(
    pipeline_model: Pipeline,
    X_fit: pd.DataFrame,
    y_fit: pd.Series,
) -> bool:
    sw = compute_sample_weight(class_weight="balanced", y=y_fit)

    try:
        pipeline_model.fit(X_fit, y_fit, model__sample_weight=sw)
        return True
    except TypeError:
        pipeline_model.fit(X_fit, y_fit)
        return False


# ------------------------------------------------------------
# --- helper: build models for a given feature set ---
# ------------------------------------------------------------
def build_models(cat_cols: list[str]) -> dict[str, Pipeline]:
    # Logistic Regression and HistGB:
    # treat all selected features as categorical and one-hot encode them
    cat_transformer_onehot = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            min_frequency=50,
            sparse_output=False
        )),
    ])

    preprocess_onehot = ColumnTransformer(
        transformers=[
            ("cat", cat_transformer_onehot, cat_cols)
        ],
        remainder="drop"
    )

    # Random Forest:
    # keep one column per original feature using ordinal encoding
    cat_transformer_rf = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("ordinal", OrdinalEncoder(
            handle_unknown="use_encoded_value",
            unknown_value=-1
        )),
    ])

    preprocess_rf = ColumnTransformer(
        transformers=[
            ("cat", cat_transformer_rf, cat_cols)
        ],
        remainder="drop"
    )

    log_reg = Pipeline(steps=[
        ("prep", preprocess_onehot),
        ("model", LogisticRegression(
            max_iter=3000,
            class_weight="balanced",
            random_state=RANDOM_STATE
        ))
    ])

    rf = Pipeline(steps=[
        ("prep", preprocess_rf),
        ("model", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ))
    ])

    hgb = Pipeline(steps=[
        ("prep", preprocess_onehot),
        ("model", HistGradientBoostingClassifier(
            random_state=RANDOM_STATE
        ))
    ])

    return {
        "LogisticRegression": log_reg,
        "RandomForest": rf,
        "HistGradientBoosting": hgb
    }


# ------------------------------------------------------------
# --- helper: evaluation on validation set ---
# ------------------------------------------------------------
def eval_on_val(
    model: Pipeline,
    name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    print_fn: Callable[..., None],
) -> dict:
    used_sw = fit_with_optional_sample_weight(model, X_train, y_train)
    pred = model.predict(X_val)

    acc = accuracy_score(y_val, pred)
    bal_acc = balanced_accuracy_score(y_val, pred)
    f1_bin = f1_score(y_val, pred, average="binary", pos_label=1)
    f1_macro = f1_score(y_val, pred, average="macro")
    precision_pos = precision_score(y_val, pred, pos_label=1, zero_division=0)
    recall_pos = recall_score(y_val, pred, pos_label=1, zero_division=0)

    print_fn(f"\n=== {name} - VAL ===")
    print_fn("used_sample_weight:", used_sw)
    print_fn("VAL Accuracy:", acc)
    print_fn("VAL Balanced Accuracy:", bal_acc)
    print_fn("VAL F1 binary (class 1 = dangerous):", f1_bin)
    print_fn("VAL F1 macro:", f1_macro)
    print_fn("VAL Precision (class 1):", precision_pos)
    print_fn("VAL Recall (class 1):", recall_pos)
    print_fn("\nClassification report:")
    print_fn(classification_report(
        y_val,
        pred,
        target_names=["Light (0)", "Dangerous (1)"],
        digits=4
    ))
    print_fn("Confusion matrix:\n", confusion_matrix(y_val, pred))

    return {
        "model": name,
        "used_sample_weight": used_sw,
        "val_acc": float(acc),
        "val_bal_acc": float(bal_acc),
        "val_f1_binary": float(f1_bin),
        "val_f1_macro": float(f1_macro),
        "val_precision_pos": float(precision_pos),
        "val_recall_pos": float(recall_pos),
    }


# ------------------------------------------------------------
# --- helper: cross-validation on train set ---
# ------------------------------------------------------------
def cv_on_train(
    model: Pipeline,
    name: str,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    print_fn: Callable[..., None],
) -> dict:
    cv = StratifiedKFold(n_splits=N_SPLITS_CV, shuffle=True, random_state=RANDOM_STATE)

    scoring = {
        "accuracy": "accuracy",
        "bal_acc": "balanced_accuracy",
        "f1_binary": "f1",
        "f1_macro": "f1_macro",
        "precision": "precision",
        "recall": "recall"
    }

    cv_res = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)

    out = {
        "cv_acc": float(cv_res["test_accuracy"].mean()),
        "cv_bal_acc": float(cv_res["test_bal_acc"].mean()),
        "cv_f1_binary": float(cv_res["test_f1_binary"].mean()),
        "cv_f1_macro": float(cv_res["test_f1_macro"].mean()),
        "cv_precision_pos": float(cv_res["test_precision"].mean()),
        "cv_recall_pos": float(cv_res["test_recall"].mean()),
    }

    print_fn(f"\n=== {name} - CV on TRAIN ===")
    print_fn("CV Accuracy:", out["cv_acc"])
    print_fn("CV Balanced Acc:", out["cv_bal_acc"])
    print_fn("CV F1 binary:", out["cv_f1_binary"])
    print_fn("CV F1 macro:", out["cv_f1_macro"])
    print_fn("CV Precision (class 1):", out["cv_precision_pos"])
    print_fn("CV Recall (class 1):", out["cv_recall_pos"])

    return out


# ------------------------------------------------------------
# --- helper: evaluation on test set ---
# ------------------------------------------------------------
def eval_on_test(
    model: Pipeline,
    name: str,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    print_fn: Callable[..., None],
) -> dict:
    pred = model.predict(X_test)

    acc = accuracy_score(y_test, pred)
    bal_acc = balanced_accuracy_score(y_test, pred)
    f1_bin = f1_score(y_test, pred, average="binary", pos_label=1)
    f1_macro = f1_score(y_test, pred, average="macro")
    precision_pos = precision_score(y_test, pred, pos_label=1, zero_division=0)
    recall_pos = recall_score(y_test, pred, pos_label=1, zero_division=0)

    print_fn(f"\n=== {name} - TEST ===")
    print_fn("TEST Accuracy:", acc)
    print_fn("TEST Balanced Accuracy:", bal_acc)
    print_fn("TEST F1 binary (class 1 = dangerous):", f1_bin)
    print_fn("TEST F1 macro:", f1_macro)
    print_fn("TEST Precision (class 1):", precision_pos)
    print_fn("TEST Recall (class 1):", recall_pos)
    print_fn("\nClassification report:")
    print_fn(classification_report(
        y_test,
        pred,
        target_names=["Light (0)", "Dangerous (1)"],
        digits=4
    ))
    print_fn("Confusion matrix:\n", confusion_matrix(y_test, pred))

    return {
        "test_acc": float(acc),
        "test_bal_acc": float(bal_acc),
        "test_f1_binary": float(f1_bin),
        "test_f1_macro": float(f1_macro),
        "test_precision_pos": float(precision_pos),
        "test_recall_pos": float(recall_pos),
    }


# ------------------------------------------------------------
# --- main experiment function ---
# ------------------------------------------------------------
def run_feature_set(set_name: str, selected_features: list[str]) -> None:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    feature_count = len(selected_features)

    log_path = f"runs/run_binary_{feature_count}features_{set_name}_{stamp}.txt"
    summary_csv = f"runs/summary_binary_{feature_count}features_{set_name}_{stamp}.csv"
    test_csv = f"runs/test_results_binary_{feature_count}features_{set_name}_{stamp}.csv"

    log_f = open(log_path, "w", encoding="utf-8")

    def print_fn(*args: Any, **kwargs: Any) -> None:
        builtins.print(*args, **kwargs)
        builtins.print(*args, file=log_f, **kwargs)
        log_f.flush()

    print_fn("LOG_PATH:", log_path)
    print_fn("INPUT_FILE:", INPUT_FILE)
    print_fn("TARGET_COL:", TARGET_COL)
    print_fn("BINARY_TARGET_COL:", BINARY_TARGET_COL)
    print_fn("FEATURE_SET_NAME:", set_name)
    print_fn("FEATURE_COUNT:", feature_count)
    print_fn("SELECTED_FEATURES:", selected_features)

    # load cleaned base data
    df = load_and_prepare_base_df()

    # validate feature list
    existing_features = [col for col in selected_features if col in df.columns]
    missing_features = [col for col in selected_features if col not in df.columns]

    if missing_features:
        print_fn("\nWarning: these features were not found in the dataset:")
        print_fn(missing_features)

    if len(existing_features) == 0:
        print_fn("\nNo valid features found for this run. Skipping.")
        log_f.close()
        return

    # keep only selected features
    X = df[existing_features].copy()
    y = df[BINARY_TARGET_COL].copy()

    print_fn("\nSamples:", df.shape[0])
    print_fn("Features used:", X.shape[1])
    print_fn("Binary target distribution:")
    print_fn(y.value_counts())
    print_fn(y.value_counts(normalize=True).round(4))

    # split into Train / Val / Test
    X_trainVal, X_test, y_trainVal, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y
    )

    X_train, X_val, y_train, y_val = train_test_split(
        X_trainVal, y_trainVal,
        test_size=0.25,   # final = 60 / 20 / 20
        random_state=RANDOM_STATE,
        stratify=y_trainVal
    )

    print_fn("\nTrain:", X_train.shape, "Val:", X_val.shape, "Test:", X_test.shape)
    print_fn("Train distribution:\n", y_train.value_counts(normalize=True).round(4))
    print_fn("Val distribution:\n", y_val.value_counts(normalize=True).round(4))
    print_fn("Test distribution:\n", y_test.value_counts(normalize=True).round(4))

    # all selected features are treated as categorical in this project
    cat_cols = X.columns.tolist()

    # build models
    models = build_models(cat_cols)

    # 1) validation run for all models
    results = []
    for name, mdl in models.items():
        results.append(eval_on_val(mdl, name, X_train, y_train, X_val, y_val, print_fn))

    # 2) CV on train for all models
    for r in results:
        name = r["model"]
        r.update(cv_on_train(models[name], name, X_train, y_train, print_fn))

    # 3) summary csv
    res_df = pd.DataFrame(results)

    order_cols = [
        "model",
        "used_sample_weight",
        "val_acc",
        "val_bal_acc",
        "val_f1_binary",
        "val_f1_macro",
        "val_precision_pos",
        "val_recall_pos",
        "cv_acc",
        "cv_bal_acc",
        "cv_f1_binary",
        "cv_f1_macro",
        "cv_precision_pos",
        "cv_recall_pos"
    ]

    for c in order_cols:
        if c not in res_df.columns:
            res_df[c] = np.nan

    res_df = res_df[order_cols].sort_values(by="val_f1_binary", ascending=False)

    print_fn("\n=== SUMMARY (sorted by VAL F1 binary) ===")
    print_fn(res_df)

    res_df.to_csv(summary_csv, index=False)
    print_fn("\nSaved summary to:", summary_csv)

    # 4) train best model on TrainVal and evaluate on Test
    best_model_name = res_df.iloc[0]["model"]
    final_model = models[best_model_name]

    fit_with_optional_sample_weight(final_model, X_trainVal, y_trainVal)
    print_fn(f"\nFinal model trained on TrainVal: {best_model_name}")

    test_results = eval_on_test(final_model, best_model_name, X_test, y_test, print_fn)

    pd.DataFrame([{
        "feature_set_name": set_name,
        "feature_count": feature_count,
        "model": best_model_name,
        **test_results
    }]).to_csv(test_csv, index=False)

    print_fn("\nSaved test results to:", test_csv)

    log_f.close()

    builtins.print("Done. Outputs saved to:", log_path)
    builtins.print("Summary saved to:", summary_csv)
    builtins.print("Test results saved to:", test_csv)


# ------------------------------------------------------------
# --- run all requested feature sets ---
# ------------------------------------------------------------
if __name__ == "__main__":
    for set_name, selected_features in FEATURE_SETS.items():
        run_feature_set(set_name, selected_features)

    print("Run finished at:", datetime.now().strftime("%H:%M:%S"))