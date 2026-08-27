"""
Israel Road Accidents — Full ML Pipeline
=========================================
Dataset : accidents_raw_master.csv
Target  : HUMRAT_TEUNA  (1 = Fatal, 2 = Severe, 3 = Light)

Pipeline
--------
1. Load & column selection
2. Missing data imputation
3. Categorical encoding
4. Train / Test split (80 / 20, stratified)
5. Feature scaling (StandardScaler)
6. Model training (Random Forest)
7. Evaluation & visualisation
"""

# ─────────────────────────────────────────────────────────────
# 0. IMPORTS
# ─────────────────────────────────────────────────────────────
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless rendering
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection  import train_test_split
from sklearn.preprocessing    import StandardScaler, LabelEncoder
from sklearn.impute           import SimpleImputer
from sklearn.ensemble         import RandomForestClassifier
from sklearn.metrics          import (
    accuracy_score, classification_report, confusion_matrix
)

# ─────────────────────────────────────────────────────────────
# 1. LOAD & COLUMN SELECTION
# ─────────────────────────────────────────────────────────────
CSV_PATH = "accidents_raw_master.csv"
TARGET   = "HUMRAT_TEUNA"

df = pd.read_csv(CSV_PATH)
print(f"Raw shape: {df.shape}")

# Drop: identifiers, near-empty location fields, redundant geo keys
DROP_COLS = [
    "pk_teuna_fikt", "sug_tik",
    "REHOV1", "REHOV2", "BAYIT",
    "ZOMET_IRONI", "KVISH1", "KVISH2", "KM", "ZOMET_LO_IRONI",
    "SHNAT_TEUNA", "YEAR", "X", "Y",
    "YEHIDA", "NAFA", "SEMEL_YISHUV",
]
df = df.drop(columns=DROP_COLS)
print(f"After column drop: {df.shape}")

# ─────────────────────────────────────────────────────────────
# 2. FILL MISSING DATA
# ─────────────────────────────────────────────────────────────
NUM_COLS = ["HODESH_TEUNA", "SHAA"]

CAT_COLS = [
    "THUM_GEOGRAFI", "SUG_DEREH", "SUG_YOM", "YOM_LAYLA",
    "YOM_BASHAVUA", "SUG_TEUNA", "HAD_MASLUL", "RAV_MASLUL",
    "MEHIRUT_MUTERET", "TKINUT", "ROHAV", "SIMUN_TIMRUR",
    "TEURA", "MEZEG_AVIR", "PNE_KVISH", "SUG_EZEM",
    "MERHAK_EZEM", "LO_HAZA", "OFEN_HAZIYA", "MEKOM_HAZIYA",
    "KIVUN_HAZIYA", "MAHOZ", "EZOR_TIVI", "STATUS_IGUN",
    "MAAMAD_MINIZIPALI", "ZURAT_ISHUV",
]

# Numerical  → median  (robust to outliers)
num_imputer = SimpleImputer(strategy="median")
df[NUM_COLS] = num_imputer.fit_transform(df[NUM_COLS])

# Categorical → mode (most frequent valid code)
cat_imputer = SimpleImputer(strategy="most_frequent")
df[CAT_COLS] = cat_imputer.fit_transform(df[CAT_COLS])

assert df.isnull().sum().sum() == 0, "Still has missing values!"
print("Missing values after imputation: 0 ✅")

# ─────────────────────────────────────────────────────────────
# 3. ENCODE CATEGORICAL COLUMNS
# ─────────────────────────────────────────────────────────────
le = LabelEncoder()
for col in CAT_COLS:
    df[col] = le.fit_transform(df[col].astype(str))

print(f"Encoding done. Final shape: {df.shape} ✅")

# ─────────────────────────────────────────────────────────────
# 4. TRAIN / TEST SPLIT — 80 / 20
# ─────────────────────────────────────────────────────────────
FEATURES = [c for c in df.columns if c != TARGET]

X = df[FEATURES]
y = df[TARGET]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y          # keeps class proportions identical in both sets
)

print(f"\nTrain : {X_train.shape[0]:,} rows")
print(f"Test  : {X_test.shape[0]:,} rows")
print(f"\nClass distribution (train):\n{y_train.value_counts(normalize=True).round(3)}")
print(f"\nClass distribution (test):\n{y_test.value_counts(normalize=True).round(3)}")

# ─────────────────────────────────────────────────────────────
# 5. FEATURE SCALING
# ─────────────────────────────────────────────────────────────
scaler = StandardScaler()

# CRITICAL: fit ONLY on train, then transform both
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

print(f"\nScaling done ✅")
print(f"  Post-scale mean (first 3): {X_train_scaled.mean(axis=0)[:3].round(4)}")
print(f"  Post-scale std  (first 3): {X_train_scaled.std(axis=0)[:3].round(4)}")

# ─────────────────────────────────────────────────────────────
# 6. MODEL TRAINING — Random Forest
# ─────────────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=150,
    random_state=42,
    n_jobs=-1            # use all CPU cores
)
model.fit(X_train_scaled, y_train)

y_pred = model.predict(X_test_scaled)
acc    = accuracy_score(y_test, y_pred)

print(f"\n{'='*50}")
print(f"Overall Accuracy : {acc:.4f}  ({acc:.1%})")
print(f"{'='*50}\n")
print(classification_report(
    y_test, y_pred,
    target_names=["Fatal (1)", "Severe (2)", "Light (3)"]
))

# ─────────────────────────────────────────────────────────────
# 7. VISUALISATION
# ─────────────────────────────────────────────────────────────
feat_imp    = pd.Series(model.feature_importances_, index=FEATURES).sort_values(ascending=False)
cm          = confusion_matrix(y_test, y_pred)
report_dict = classification_report(
    y_test, y_pred,
    target_names=["Fatal", "Severe", "Light"],
    output_dict=True
)

# ── Palette ──────────────────────────────────────────────────
BG     = "#0f1117"
PANEL  = "#1a1d27"
ACC    = "#6c63ff"
ACC2   = "#ff6584"
ACC3   = "#43e97b"
GRID   = "#2a2d3a"
TEXT   = "#e0e0e0"
MUTED  = "#888"
COLORS = [ACC, ACC2, ACC3]

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    PANEL,
    "axes.edgecolor":    GRID,
    "axes.labelcolor":   TEXT,
    "xtick.color":       TEXT,
    "ytick.color":       TEXT,
    "text.color":        TEXT,
    "grid.color":        GRID,
    "font.family":       "DejaVu Sans",
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

fig = plt.figure(figsize=(22, 26), facecolor=BG)
gs  = gridspec.GridSpec(4, 2, figure=fig, hspace=0.55, wspace=0.38)

# ── Plot 1: Target distribution ──────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
labels = ["Fatal (1)", "Severe (2)", "Light (3)"]
sizes  = df[TARGET].value_counts().sort_index().values
wedges, texts, autotexts = ax1.pie(
    sizes, labels=labels, colors=COLORS, autopct="%1.1f%%",
    startangle=140, pctdistance=0.78,
    wedgeprops=dict(width=0.55, edgecolor=BG, linewidth=2)
)
for at in autotexts:
    at.set(color=BG, fontsize=11, fontweight="bold")
ax1.set_title("Target Distribution\n(HUMRAT_TEUNA)",
              fontsize=14, fontweight="bold", pad=14, color=TEXT)

# ── Plot 2: Confusion Matrix ──────────────────────────────────
ax2   = fig.add_subplot(gs[0, 1])
cm_pct = cm.astype(float) / cm.sum(axis=1, keepdims=True) * 100
im = ax2.imshow(cm_pct, cmap="Blues", vmin=0, vmax=100)
for i in range(3):
    for j in range(3):
        ax2.text(j, i, f"{cm[i,j]:,}\n({cm_pct[i,j]:.1f}%)",
                 ha="center", va="center",
                 color="white" if cm_pct[i, j] > 50 else TEXT,
                 fontsize=10, fontweight="bold")
ax2.set_xticks([0, 1, 2]); ax2.set_yticks([0, 1, 2])
ax2.set_xticklabels(["Fatal", "Severe", "Light"])
ax2.set_yticklabels(["Fatal", "Severe", "Light"])
ax2.set_xlabel("Predicted", fontsize=12)
ax2.set_ylabel("Actual",    fontsize=12)
ax2.set_title("Confusion Matrix (%)", fontsize=14, fontweight="bold", pad=14)
plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04)

# ── Plot 3: Top 15 Feature Importances ───────────────────────
ax3   = fig.add_subplot(gs[1, :])
top_n = 15
top_fi = feat_imp.head(top_n)
bar_colors = [ACC if i < 5 else (ACC2 if i < 10 else ACC3) for i in range(top_n)]
bars = ax3.barh(top_fi.index[::-1], top_fi.values[::-1],
                color=bar_colors[::-1], edgecolor="none", height=0.65)
for bar, val in zip(bars, top_fi.values[::-1]):
    ax3.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
             f"{val:.3f}", va="center", fontsize=9, color=MUTED)
ax3.set_xlabel("Importance Score", fontsize=12)
ax3.set_title(f"Top {top_n} Feature Importances (Random Forest)",
              fontsize=14, fontweight="bold", pad=14)
ax3.axvline(top_fi.values.mean(), color=ACC2, ls="--", lw=1.5, alpha=0.7,
            label=f"Mean = {top_fi.values.mean():.3f}")
ax3.legend(fontsize=10)
ax3.grid(axis="x", alpha=0.3)

# ── Plot 4: Per-class Metrics ─────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
metrics      = ["precision", "recall", "f1-score"]
class_names  = ["Fatal", "Severe", "Light"]
x = np.arange(len(class_names))
width = 0.25
for i, (met, col) in enumerate(zip(metrics, COLORS)):
    vals = [report_dict[c][met] for c in class_names]
    ax4.bar(x + i * width, vals, width, label=met.capitalize(),
            color=col, edgecolor="none")
ax4.set_xticks(x + width)
ax4.set_xticklabels(class_names)
ax4.set_ylim(0, 1.15)
ax4.set_ylabel("Score", fontsize=12)
ax4.set_title("Precision / Recall / F1 by Class",
              fontsize=14, fontweight="bold", pad=14)
ax4.legend(fontsize=10)
ax4.axhline(0.5, color=MUTED, ls=":", lw=1)
ax4.grid(axis="y", alpha=0.3)

# ── Plot 5: Before vs After Scaling ──────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
N = 2000
fa_raw = X_train.iloc[:N, 0].values
fb_raw = X_train.iloc[:N, 1].values
fa_sc  = X_train_scaled[:N, 0]
fb_sc  = X_train_scaled[:N, 1]
ax5.scatter(fa_raw, fb_raw, alpha=0.15, s=8, color=ACC2, label="Before Scaling")
ax5.scatter(fa_sc,  fb_sc,  alpha=0.15, s=8, color=ACC3, label="After Scaling")
ax5.set_xlabel(f"Feature: {FEATURES[0]}", fontsize=11)
ax5.set_ylabel(f"Feature: {FEATURES[1]}", fontsize=11)
ax5.set_title("Before vs After StandardScaler\n(sample 2 000 points)",
              fontsize=13, fontweight="bold", pad=14)
ax5.legend(fontsize=10)
ax5.grid(alpha=0.2)

# ── Plot 6: Summary Card ──────────────────────────────────────
ax6 = fig.add_subplot(gs[3, :])
ax6.set_xlim(0, 10); ax6.set_ylim(0, 2)
ax6.axis("off")
summary = [
    ("Overall Accuracy",  f"{acc:.1%}",                                 ACC),
    ("Fatal — F1",        f"{report_dict['Fatal']['f1-score']:.2f}",    ACC2),
    ("Severe — F1",       f"{report_dict['Severe']['f1-score']:.2f}",   ACC),
    ("Light — F1",        f"{report_dict['Light']['f1-score']:.2f}",    ACC3),
    ("Train Samples",     "53,513",                                      MUTED),
    ("Test Samples",      "13,379",                                      MUTED),
]
for idx, (label, value, color) in enumerate(summary):
    col_x = (idx % 3) * 3.4 + 0.3
    row_y = 1.5 - (idx // 3) * 0.9
    rect = mpatches.FancyBboxPatch(
        (col_x - 0.15, row_y - 0.52), 3.1, 0.72,
        boxstyle="round,pad=0.08", linewidth=1.5,
        edgecolor=color, facecolor=PANEL
    )
    ax6.add_patch(rect)
    ax6.text(col_x + 1.4, row_y, value,
             ha="center", va="center", fontsize=20,
             fontweight="bold", color=color)
    ax6.text(col_x + 1.4, row_y - 0.33, label,
             ha="center", va="center", fontsize=10, color=MUTED)
ax6.set_title("Model Performance Summary",
              fontsize=15, fontweight="bold", pad=6, color=TEXT)

fig.suptitle("Israel Road Accidents — Full ML Pipeline Analysis",
             fontsize=18, fontweight="bold", color=TEXT, y=0.98)

OUTPUT_PNG = "accidents_analysis.png"
plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"\nPlot saved to {OUTPUT_PNG} ✅")
plt.close()
