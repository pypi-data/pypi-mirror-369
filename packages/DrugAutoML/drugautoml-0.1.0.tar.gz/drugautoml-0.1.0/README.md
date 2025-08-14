# DrugAutoML

**DrugAutoML** is an **end-to-end Automated Machine Learning (AutoML) pipeline** for **bioactivity prediction** in drug discovery.  
It automates every stage — from reading raw datasets to generating predictions for new molecules — and produces both **high-performance models** and **explainable outputs**.

---

## 🚀 Features

- **Data Preprocessing**  
  Reads raw datasets, cleans and standardizes SMILES, removes invalid molecules, and labels compounds as *active* or *inactive* based on pChEMBL cutoffs or existing binary labels.

- **Molecular Featurization**  
  Generates **ECFP (Extended-Connectivity Fingerprints)** using RDKit with customizable radius, bit size, and count-based features.

- **Data Splitting**  
  Splits data into training and testing sets using:
  - **Scaffold Split** (structure-aware)
  - **Stratified Random Split** (class-proportion preserving)

- **Model Selection**  
  Hyperparameter optimization with **Optuna** for:
  - Random Forest, Extra Trees, Logistic Regression, Linear SVC, XGBoost, LightGBM  
  Uses repeated stratified k-fold CV and produces a ranked **leaderboard**.

- **Model Finalization**  
  Trains the best model, applies **probability calibration**, selects optimal classification threshold, evaluates on the test set, and saves the model.

- **Explainability**  
  - **SHAP** global importance plots (beeswarm, bar, signed bar)  
  - **Bit Gallery** visualizations: highlights ECFP bits in test molecules that strongly influence predictions.

- **Prediction on New Data**  
  Scores unlabeled or labeled molecules, outputs probabilities and predictions, and computes metrics if labels are available.



