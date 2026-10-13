"""Retain the mentor comparison of Random Forest weighting and SMOTENC sampling."""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OrdinalEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score
)

from imblearn.over_sampling import SMOTENC



# ============================================================
# SETTINGS
# ============================================================
CSV_PATH = "accidents_raw_master.csv"
TARGET = "HUMRAT_TEUNA"
RANDOM_STATE = 42


# ============================================================
# 1. LOAD DATA
# ============================================================
df = pd.read_csv(CSV_PATH)
print(f"Raw shape: {df.shape}")

# Drop identifiers, near-empty location fields, and redundant geographic fields.
DROP_COLS = [
    "pk_teuna_fikt", "sug_tik",
    "REHOV1", "REHOV2", "BAYIT",
    "ZOMET_IRONI", "KVISH1", "KVISH2", "KM", "ZOMET_LO_IRONI",
    "SHNAT_TEUNA", "YEAR", "X", "Y",
    "YEHIDA", "NAFA", "SEMEL_YISHUV",
]

existing_drop_cols = [col for col in DROP_COLS if col in df.columns]
df = df.drop(columns=existing_drop_cols)
print(f"After column drop: {df.shape}")


# ============================================================
# 2. DEFINE COLUMN TYPES
# ============================================================
# Retain the feature groups used by the historical baseline.
NUM_COLS = [col for col in ["HODESH_TEUNA", "SHAA"] if col in df.columns]

CAT_COLS = [
    "THUM_GEOGRAFI", "SUG_DEREH", "SUG_YOM", "YOM_LAYLA",
    "YOM_BASHAVUA", "SUG_TEUNA", "HAD_MASLUL", "RAV_MASLUL",
    "MEHIRUT_MUTERET", "TKINUT", "ROHAV", "SIMUN_TIMRUR",
    "TEURA", "MEZEG_AVIR", "PNE_KVISH", "SUG_EZEM",
    "MERHAK_EZEM", "LO_HAZA", "OFEN_HAZIYA", "MEKOM_HAZIYA",
    "KIVUN_HAZIYA", "MAHOZ", "EZOR_TIVI", "STATUS_IGUN",
    "MAAMAD_MINIZIPALI", "ZURAT_ISHUV",
]
CAT_COLS = [col for col in CAT_COLS if col in df.columns]

# Safety: make sure target exists
if TARGET not in df.columns:
    raise ValueError(f"Target column '{TARGET}' not found in dataset.")

FEATURES = [col for col in df.columns if col != TARGET]


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================
X = df[FEATURES].copy()
y = df[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=RANDOM_STATE
)

print(f"\nTrain shape: {X_train.shape}")
print(f"Test shape : {X_test.shape}")

print("\nTrain target distribution:")
print(y_train.value_counts(normalize=True).sort_index().round(4))

print("\nTest target distribution:")
print(y_test.value_counts(normalize=True).sort_index().round(4))


# ============================================================
# 4. IMPUTATION
# IMPORTANT: fit only on train, then transform test
# ============================================================
if NUM_COLS:
    num_imputer = SimpleImputer(strategy="median")
    X_train[NUM_COLS] = num_imputer.fit_transform(X_train[NUM_COLS])
    X_test[NUM_COLS] = num_imputer.transform(X_test[NUM_COLS])

if CAT_COLS:
    cat_imputer = SimpleImputer(strategy="most_frequent")
    X_train[CAT_COLS] = cat_imputer.fit_transform(X_train[CAT_COLS])
    X_test[CAT_COLS] = cat_imputer.transform(X_test[CAT_COLS])

print("\nMissing values after imputation:")
print("Train:", int(X_train.isnull().sum().sum()))
print("Test :", int(X_test.isnull().sum().sum()))


# ============================================================
# 5. ENCODING
# We use OrdinalEncoder so we can fit on train and transform test safely.
# For Random Forest this is acceptable as a baseline approach.
# ============================================================
encoder = OrdinalEncoder(
    handle_unknown="use_encoded_value",
    unknown_value=-1
)

if CAT_COLS:
    X_train[CAT_COLS] = encoder.fit_transform(X_train[CAT_COLS].astype(str))
    X_test[CAT_COLS] = encoder.transform(X_test[CAT_COLS].astype(str))

# Make sure everything is numeric
X_train = X_train.astype(float)
X_test = X_test.astype(float)


# ============================================================
# 6. HELPER FUNCTION FOR EVALUATION
# ============================================================
def evaluate_model(model: RandomForestClassifier, X_tr: pd.DataFrame, y_tr: pd.Series, X_te: pd.DataFrame, y_te: pd.Series, model_name: str) -> dict[str, str | float | np.ndarray | RandomForestClassifier]:
    """Fit a Random Forest and return its predictions, metrics, and fitted estimator."""
    model.fit(X_tr, y_tr)
    y_pred = model.predict(X_te)

    acc = accuracy_score(y_te, y_pred)
    f1_macro = f1_score(y_te, y_pred, average="macro")

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)
    print(f"Accuracy : {acc:.4f}")
    print(f"F1-macro : {f1_macro:.4f}")
    print("\nClassification report:")
    print(classification_report(y_te, y_pred, digits=4))
    print("Confusion matrix:")
    print(confusion_matrix(y_te, y_pred))

    return {
        "model_name": model_name,
        "accuracy": acc,
        "f1_macro": f1_macro,
        "y_pred": y_pred,
        "model": model
    }


results = []


# ============================================================
# 7. MODEL 1 — BASELINE RANDOM FOREST
# ============================================================
rf_baseline = RandomForestClassifier(
    n_estimators=150,
    random_state=RANDOM_STATE,
    n_jobs=-1
)

res_baseline = evaluate_model(
    rf_baseline,
    X_train,
    y_train,
    X_test,
    y_test,
    "Baseline Random Forest"
)
results.append(res_baseline)


# ============================================================
# 8. MODEL 2 — RANDOM FOREST WITH CLASS WEIGHT
# ============================================================
rf_balanced = RandomForestClassifier(
    n_estimators=150,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

res_balanced = evaluate_model(
    rf_balanced,
    X_train,
    y_train,
    X_test,
    y_test,
    "Random Forest + class_weight='balanced'"
)
results.append(res_balanced)


# ============================================================
# 9. MODEL 3 — SMOTENC + RANDOM FOREST
# IMPORTANT:
# We apply SMOTENC only on the TRAIN set, never on the test set.
# ============================================================
categorical_feature_indices = [X_train.columns.get_loc(col) for col in CAT_COLS]

smote_nc = SMOTENC(
    categorical_features=categorical_feature_indices,
    random_state=RANDOM_STATE,
    k_neighbors=5
)

X_train_res, y_train_res = smote_nc.fit_resample(X_train, y_train)

print("\nAfter SMOTENC resampling:")
print(pd.Series(y_train_res).value_counts().sort_index())

rf_smote = RandomForestClassifier(
    n_estimators=150,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

res_smote = evaluate_model(
    rf_smote,
    X_train_res,
    y_train_res,
    X_test,
    y_test,
    "SMOTENC + Random Forest + class_weight='balanced'"
)
results.append(res_smote)


# ============================================================
# 10. SAVE MODEL COMPARISON TABLE
# ============================================================
comparison_df = pd.DataFrame([
    {
        "model_name": r["model_name"],
        "accuracy": r["accuracy"],
        "f1_macro": r["f1_macro"]
    }
    for r in results
])

comparison_df = comparison_df.sort_values(by="f1_macro", ascending=False)
comparison_df.to_csv("model_comparison_results.csv", index=False)

print("\nSaved: model_comparison_results.csv")
print(comparison_df)


# ============================================================
# 11. SAVE FEATURE IMPORTANCE OF THE SMOTENC MODEL
# This report uses rf_smote regardless of the comparison ranking.
# ============================================================
fi_df = pd.DataFrame({
    "feature": X_train.columns,
    "importance": rf_smote.feature_importances_
}).sort_values(by="importance", ascending=False)

fi_df.to_csv("feature_importance_smotenc_rf.csv", index=False)

print("\nSaved: feature_importance_smotenc_rf.csv")
print("\nTop 20 features from SMOTENC model:")
print(fi_df.head(20))


# ============================================================
# 12. OPTIONAL: SAVE FULL REPORTS TO TXT FILE
# ============================================================
with open("full_model_reports.txt", "w", encoding="utf-8") as f:
    for r in results:
        f.write("=" * 70 + "\n")
        f.write(r["model_name"] + "\n")
        f.write("=" * 70 + "\n")
        f.write(f"Accuracy : {r['accuracy']:.4f}\n")
        f.write(f"F1-macro : {r['f1_macro']:.4f}\n\n")
        f.write("Classification report:\n")
        f.write(classification_report(y_test, r["y_pred"], digits=4))
        f.write("\n")
        f.write("Confusion matrix:\n")
        f.write(str(confusion_matrix(y_test, r["y_pred"])))
        f.write("\n\n")

print("\nSaved: full_model_reports.txt")
print("\nDone.")