# Train and export the final 16-feature binary model used by the backend.

import json

import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.utils.class_weight import compute_sample_weight


INPUT_FILE = "accidents_full_copy.xlsx"
TARGET_COL = "HUMRAT_TEUNA"
BINARY_TARGET_COL = "TARGET_BINARY"

MODEL_PATH = "../saved_model/safe_roads_model.joblib"
METADATA_PATH = "../saved_model/model_metadata.json"
RESULTS_PATH = "../evaluation/final_model_results.txt"

RANDOM_STATE = 42
MISSING_THRESHOLD = 0.5

FINAL_FEATURES = [
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
    "YOM_LAYLA",
]


def combine_road_structure(row: pd.Series) -> str:
    had = row["HAD_MASLUL"]
    rav = row["RAV_MASLUL"]

    # Prefer a nonzero HAD_MASLUL value before checking RAV_MASLUL.
    if pd.notna(had) and had != 0:
        if had in [1, 2, 3]:
            return f"HAD_{int(had)}"
        return "OTHER"

    if pd.notna(rav) and rav != 0:
        if rav in [1, 2, 3, 4]:
            return f"RAV_{int(rav)}"
        return "OTHER"

    return "OTHER"


def load_and_prepare_data() -> pd.DataFrame:
    df = pd.read_excel(INPUT_FILE)
    df = df.replace(r"^\s*$", np.nan, regex=True)

    df["ROAD_STRUCTURE"] = df.apply(combine_road_structure, axis=1)
    df = df.drop(columns=["HAD_MASLUL", "RAV_MASLUL"], errors="ignore")

    drop_cols = [
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
    df = df.drop(columns=drop_cols, errors="ignore")

    missing_ratio = df.isnull().mean()
    cols_to_drop = missing_ratio[missing_ratio > MISSING_THRESHOLD].index.tolist()

    if TARGET_COL in cols_to_drop:
        cols_to_drop.remove(TARGET_COL)

    df = df.drop(columns=cols_to_drop, errors="ignore")
    df = df.dropna(subset=[TARGET_COL]).copy()

    df[BINARY_TARGET_COL] = df[TARGET_COL].replace({
        1: 1,
        2: 1,
        3: 0,
    })

    return df


def build_final_model() -> Pipeline:
    # Treat all final features as categorical, including numeric codes.
    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(
            handle_unknown="infrequent_if_exist",
            min_frequency=50,
            sparse_output=False,
        )),
    ])

    preprocessing = ColumnTransformer(
        transformers=[
            ("cat", categorical_transformer, FINAL_FEATURES),
        ],
        remainder="drop",
    )

    model = HistGradientBoostingClassifier(
        random_state=RANDOM_STATE,
    )

    return Pipeline(steps=[
        ("prep", preprocessing),
        ("model", model),
    ])


def main() -> None:
    df = load_and_prepare_data()

    X = df[FINAL_FEATURES].copy()
    y = df[BINARY_TARGET_COL].copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    sample_weights = compute_sample_weight(
        class_weight="balanced",
        y=y_train,
    )

    final_model = build_final_model()
    final_model.fit(X_train, y_train, model__sample_weight=sample_weights)

    y_pred = final_model.predict(X_test)

    if hasattr(final_model, "predict_proba"):
        y_proba = final_model.predict_proba(X_test)[:, 1]
    else:
        y_proba = None

    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, y_pred)),
        "f1_binary": float(f1_score(y_test, y_pred, pos_label=1)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "precision_dangerous": float(precision_score(y_test, y_pred, pos_label=1, zero_division=0)),
        "recall_dangerous": float(recall_score(y_test, y_pred, pos_label=1, zero_division=0)),
    }

    joblib.dump(final_model, MODEL_PATH)

    metadata = {
        "model_type": "HistGradientBoostingClassifier",
        "target_column": BINARY_TARGET_COL,
        "target_meaning": {
            "0": "Light accident",
            "1": "Dangerous accident",
        },
        "features": FINAL_FEATURES,
        "road_structure_values": [
            "HAD_1",
            "HAD_2",
            "HAD_3",
            "RAV_1",
            "RAV_2",
            "RAV_3",
            "RAV_4",
            "OTHER",
        ],
        "random_state": RANDOM_STATE,
        "metrics": metrics,
    }

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        f.write("Final Safe Roads Model\n")
        f.write("======================\n\n")
        f.write("Model: HistGradientBoostingClassifier\n")
        f.write(f"Samples: {len(df)}\n")
        f.write(f"Features: {len(FINAL_FEATURES)}\n\n")

        f.write("Metrics:\n")
        for name, value in metrics.items():
            f.write(f"{name}: {value:.4f}\n")

        f.write("\nClassification report:\n")
        f.write(classification_report(
            y_test,
            y_pred,
            target_names=["Light (0)", "Dangerous (1)"],
            digits=4,
        ))

        f.write("\nConfusion matrix:\n")
        f.write(str(confusion_matrix(y_test, y_pred)))

    print("Final model was trained and saved successfully.")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print(f"Results saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
