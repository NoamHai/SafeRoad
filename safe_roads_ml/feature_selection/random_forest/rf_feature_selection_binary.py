# Rank features for the binary target and export the top-N lists.

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer

# =====================
# Config
# =====================
INPUT_FILE = "accidents_full_copy.xlsx"
TARGET_COL = "HUMRAT_TEUNA"
BINARY_TARGET_COL = "TARGET_BINARY"
MISSING_THRESHOLD = 0.5   # remove columns with >50% missing
RANDOM_STATE = 42

# =====================
# Load data
# =====================
df = pd.read_excel(INPUT_FILE)

# count missing before replacing blank strings
missing_before = df.isnull().sum().sum()

# convert cells with only spaces to NaN
df = df.replace(r"^\s*$", np.nan, regex=True)

# =====================
# Combine HAD_MASLUL and RAV_MASLUL into one feature
# =====================
def combine_road_structure(row: pd.Series) -> str:
    had = row["HAD_MASLUL"]
    rav = row["RAV_MASLUL"]

    # Prefer a nonzero HAD_MASLUL value before checking RAV_MASLUL.
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

df["ROAD_STRUCTURE"] = df.apply(combine_road_structure, axis=1)

# remove old split columns
df = df.drop(columns=["HAD_MASLUL", "RAV_MASLUL"], errors="ignore")

missing_after = df.isnull().sum().sum()

print("Missing before:", missing_before)
print("Missing after:", missing_after)
print("New missing added:", missing_after - missing_before)
print("Original shape:", df.shape)

# =====================
# Remove level-1 columns
# identifiers / exact location / non-user-friendly / non-generalizable
# =====================
drop_cols_level1 = [
    "pk_teuna_fikt",   # synthetic accident id
    "sug_tik",         # administrative record type
    "SEMEL_YISHUV",    # locality symbol - high cardinality / not user friendly
    "REHOV1",          # exact street
    "REHOV2",          # exact street
    "BAYIT",           # house number
    "KVISH1",          # exact road number
    "KVISH2",          # exact road number
    "KM",              # exact kilometer point
    "YEHIDA",          # police/admin unit
    "X",               # exact coordinate
    "Y",               # exact coordinate
    "YEAR",            # duplicate / time-specific
    "SHNAT_TEUNA"      # year of accident
]

df = df.drop(columns=drop_cols_level1, errors="ignore")

print("After level-1 drop:", df.shape)

# =====================
# Remove columns with too many missing values
# =====================
missing_ratio = df.isnull().mean()

cols_to_drop_missing = missing_ratio[missing_ratio > MISSING_THRESHOLD].index.tolist()

# do not remove target by mistake
if TARGET_COL in cols_to_drop_missing:
    cols_to_drop_missing.remove(TARGET_COL)

df = df.drop(columns=cols_to_drop_missing)

print("Dropped due to missing (>{:.0%}):".format(MISSING_THRESHOLD), cols_to_drop_missing)
print("After missing drop:", df.shape)

# =====================
# Remove rows where target is missing
# =====================
df = df.dropna(subset=[TARGET_COL])

print("After dropping rows with missing target:", df.shape)

# =====================
# Convert multiclass target to binary
# 1 = dangerous (fatal or severe)
# 0 = light
# =====================
df[BINARY_TARGET_COL] = df[TARGET_COL].replace({
    1: 1,  # fatal
    2: 1,  # severe
    3: 0   # light
})

print("\nOriginal target distribution:")
print(df[TARGET_COL].value_counts(dropna=False).sort_index())

print("\nBinary target distribution:")
print(df[BINARY_TARGET_COL].value_counts(dropna=False).sort_index())
print(df[BINARY_TARGET_COL].value_counts(normalize=True).sort_index().round(4))

# =====================
# Split X / y
# =====================
X = df.drop(columns=[TARGET_COL, BINARY_TARGET_COL])
y = df[BINARY_TARGET_COL]

print("\nFinal feature count:", X.shape[1])
print("Feature names:")
print(list(X.columns))

# =====================
# Impute remaining missing values
# Using most_frequent because features here are mostly categorical/coded
# =====================
imputer = SimpleImputer(strategy="most_frequent")
X_imputed = imputer.fit_transform(X)

# convert back to DataFrame so feature names are preserved clearly
X_imputed = pd.DataFrame(X_imputed, columns=X.columns)

# =====================
# Encode object columns to numeric codes
# (keep one column per original feature)
# =====================
for col in X_imputed.columns:
    if X_imputed[col].dtype == "object":
        X_imputed[col], _ = pd.factorize(X_imputed[col])

# =====================
# Train / Test split
# Only for stable feature importance calculation on train data
# =====================
X_train, X_test, y_train, y_test = train_test_split(
    X_imputed,
    y,
    test_size=0.2,
    stratify=y,
    random_state=RANDOM_STATE
)

print("\nTrain shape:", X_train.shape)
print("Test shape:", X_test.shape)

print("\nTrain binary distribution:")
print(y_train.value_counts(normalize=True).sort_index().round(4))

print("\nTest binary distribution:")
print(y_test.value_counts(normalize=True).sort_index().round(4))

# =====================
# Random Forest for feature importance
# =====================
rf = RandomForestClassifier(
    n_estimators=300,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)

print("\nTraining Random Forest for binary feature importance...")
rf.fit(X_train, y_train)

# =====================
# Feature importance
# =====================
importances = rf.feature_importances_
feature_names = X_train.columns

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

print("\nTop 20 features:")
print(importance_df.head(20))

# =====================
# Save full ranking
# =====================
importance_df.to_csv("rf_feature_importance_binary_full.csv", index=False)
print("\nSaved full ranking to rf_feature_importance_binary_full.csv")

# =====================
# Save top-N lists for later experiments
# =====================
for n in [5, 10, 15, 20]:
    top_n_df = importance_df.head(n).copy()
    out_name = f"rf_top_{n}_binary.csv"
    top_n_df.to_csv(out_name, index=False)
    print(f"Saved top {n} features to {out_name}")

# =====================
# Save feature names in simple txt form
# =====================
for n in [5, 10, 15, 20]:
    top_n_features = importance_df["feature"].head(n).tolist()
    out_name = f"rf_top_{n}_binary_features.txt"
    with open(out_name, "w", encoding="utf-8") as f:
        for feat in top_n_features:
            f.write(feat + "\n")
    print(f"Saved top {n} feature names to {out_name}")

# =====================
# Save feature lists ready for copy-paste into future code
# =====================
for n in [5, 10, 15, 20]:
    top_features = importance_df["feature"].head(n).tolist()

    feature_list_str = "SELECTED_FEATURES = [\n"
    for feat in top_features:
        feature_list_str += f'    "{feat}",\n'
    feature_list_str += "]\n"

    out_name = f"rf_top_{n}_features_for_code.txt"

    with open(out_name, "w", encoding="utf-8") as f:
        f.write(feature_list_str)

    print(f"Saved feature list for top {n} to {out_name}")

print("\nDone.")