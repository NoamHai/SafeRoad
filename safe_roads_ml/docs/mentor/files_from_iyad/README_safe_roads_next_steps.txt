Historical mentor guidance for the comparison script only.
Use safe_roads_ml/README.md for the full dependency setup and working directory.
This experiment does not export the saved model used by the application.

Israel Road Accidents — Improved ML Pipeline
============================================

What this script does
---------------------
This script compares 3 versions of the model:

1. Baseline Random Forest
2. Random Forest with class_weight='balanced'
3. SMOTENC + Random Forest with class_weight='balanced'

The goal is to check whether handling class imbalance improves the
performance on the minority classes (Fatal / Severe), especially in
terms of F1-macro and recall.

Why SMOTENC and not regular SMOTE?
----------------------------------
Most of the features in this project are categorical.
Regular SMOTE is more suitable for continuous numerical features.
SMOTENC is designed for mixed data and categorical columns, so it is
more appropriate for this dataset.

Important logic in the pipeline
-------------------------------
1. Load the dataset
2. Drop irrelevant / near-empty / identifier columns
3. Split into train and test using stratify
4. Fit imputers only on train, then transform test
5. Fit encoder only on train, then transform test
6. Train baseline model
7. Train balanced model
8. Apply SMOTENC only on the train set
9. Train RF on the resampled train set
10. Compare the results

Important note
--------------
SMOTENC must be applied ONLY on the training data.
Never apply oversampling before the train/test split.
Never apply oversampling on the test set.

Files created by the script
---------------------------
1. model_comparison_results.csv
   Summary table with:
   - model_name
   - accuracy
   - f1_macro

2. feature_importance_smotenc_rf.csv
   Feature importance values from the RF model trained after SMOTENC

3. full_model_reports.txt
   Full classification reports and confusion matrices for all 3 models

How to run
----------
1. Put the file accidents_raw_master.csv in the same folder as the script
2. Install the required package:
   pip install imbalanced-learn
3. Run:
   python accidents_ml_pipeline_improved.py

What to check in the results
----------------------------
Do not focus only on accuracy.

Main things to compare:
- F1-macro
- Recall for Fatal
- Recall for Severe
- Confusion matrix behavior
- Whether the model still performs reasonably on Light accidents

Interpretation
--------------
A lower accuracy is not necessarily worse.
If accuracy drops a little, but F1-macro and minority-class recall improve,
that can actually mean the model is better and more useful.

About feature importance
------------------------
The feature importance from the old Random Forest can still be used as a baseline.
However, once the training method changes (class_weight / SMOTENC),
the learned model changes too, so feature importance should be recalculated.

Therefore:
- old feature ranking = baseline comparison
- new feature ranking = better candidate for final presentation

Suggested next steps
--------------------
1. Run the script and compare the 3 models
2. Check whether F1-macro improves
3. Check whether Fatal / Severe recall improves
4. If the improved model is better, use its feature importance table
5. Optionally later:
   - try binary classification
   - try XGBoost / LightGBM
   - tune Random Forest hyperparameters