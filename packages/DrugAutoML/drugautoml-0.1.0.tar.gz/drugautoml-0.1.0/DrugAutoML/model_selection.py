"""
Model Selection Module for DrugAutoML
-------------------------------------

This module:
1. Loads training feature and label datasets.
2. Runs hyperparameter optimization for multiple ML algorithms using Optuna.
3. Evaluates each algorithm via repeated stratified k-fold CV.
4. Saves a leaderboard of the best-performing models.
5. Plots a violin chart of CV score distributions, ranked from best to worst.

Supported Algorithms:
- Random Forest (RF)
- Extra Trees (ET)
- Logistic Regression (LR)
- Linear SVC (LSVC)
- XGBoost (XGB)
- LightGBM (LGBM)

Dependencies:
- pandas, numpy, optuna
- scikit-learn
- seaborn, matplotlib (for plotting)
"""

from __future__ import annotations
from typing import Dict, Any
import os, glob, warnings
from datetime import datetime
import numpy as np
import pandas as pd
import optuna
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import make_scorer, matthews_corrcoef, balanced_accuracy_score, recall_score, precision_score, roc_auc_score, f1_score
from sklearn.exceptions import ConvergenceWarning
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Suppress warnings
warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", message="X does not have valid feature names")
warnings.filterwarnings("ignore", message="l1_ratio parameter is only used when penalty is 'elasticnet'")

# ---------- Custom Specificity ----------
def specificity_score(y_true, y_pred):
    from sklearn.metrics import confusion_matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0

# ---------- Scorer Map ----------
SCORERS = {
    "mcc": make_scorer(matthews_corrcoef),
    "balanced_accuracy": make_scorer(balanced_accuracy_score),
    "recall": make_scorer(recall_score),
    "specificity": make_scorer(specificity_score),
    "precision": make_scorer(precision_score),
    "roc_auc": make_scorer(roc_auc_score, needs_threshold=True),
    "f1_macro": make_scorer(f1_score, average="macro"),
}

SCORE_NAME_DISPLAY = {
    "mcc": "MCC",
    "balanced_accuracy": "Balanced Accuracy",
    "recall": "Recall",
    "specificity": "Specificity",
    "precision": "Precision",
    "roc_auc": "ROC-AUC",
    "f1_macro": "F1-Macro"
}

# ---------- Helper: find latest split files ----------
def _find_latest_file(results_dir: str, pattern: str) -> str:
    files = glob.glob(os.path.join(results_dir, pattern))
    if not files:
        raise FileNotFoundError(f"No file found matching pattern '{pattern}' in '{results_dir}'.")
    return max(files, key=os.path.getmtime)

# ---------- Objective Function Wrapper ----------
def _wrap_objective(build_model_func, algo_name, X_df, y, rskf, scoring, results_dir, timestamp):
    def obj(trial):
        clf = build_model_func(trial)
        scores = cross_val_score(clf, X_df, y, cv=rskf, scoring=scoring, n_jobs=-1, error_score=np.nan)
        trial.set_user_attr("cv_scores", scores.tolist())

        # Save CV fold scores
        scores_path = os.path.join(results_dir, f"cv_scores_{algo_name}_trial{trial.number}_{timestamp}.csv")
        pd.DataFrame({"Fold": list(range(1, len(scores) + 1)), "Score": scores}).to_csv(scores_path, index=False)

        return float(np.nanmean(scores))
    return obj

# ---------- Model Builder Functions ----------
def build_rf(trial, random_state):
    n_estimators = trial.suggest_int("n_estimators", 400, 1200, step=100)
    max_depth = trial.suggest_int("max_depth", 6, 24, step=2)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20, step=2)
    min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 12)
    max_features_opt = trial.suggest_categorical("max_features", ["sqrt", "log2", 0.2, 0.4, 0.6, 0.8])
    bootstrap = trial.suggest_categorical("bootstrap", [True, False])
    return RandomForestClassifier(
        n_estimators=n_estimators, max_depth=max_depth if max_depth > 0 else None,
        min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
        max_features=max_features_opt, class_weight="balanced_subsample",
        bootstrap=bootstrap,
        n_jobs=-1, random_state=random_state
    )

def build_et(trial, random_state):
    n_estimators = trial.suggest_int("n_estimators", 500, 1500, step=100)
    max_depth = trial.suggest_int("max_depth", 6, 24, step=2)
    min_samples_split = trial.suggest_int("min_samples_split", 2, 20, step=2)
    min_samples_leaf = trial.suggest_int("min_samples_leaf", 1, 12)
    max_features_opt = trial.suggest_categorical("max_features", ["sqrt", "log2", 0.2, 0.4, 0.6, 0.8])
    bootstrap = trial.suggest_categorical("bootstrap", [True, False])
    kwargs = dict(
        n_estimators=n_estimators, max_depth=max_depth,
        min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
        max_features=max_features_opt, bootstrap=bootstrap,
        class_weight="balanced", n_jobs=-1, random_state=random_state
    )
    if bootstrap:
        kwargs["max_samples"] = trial.suggest_float("et_max_samples", 0.5, 1.0)
    return ExtraTreesClassifier(**kwargs)

def build_logreg(trial):
    C = trial.suggest_float("C", 1e-4, 1e3, log=True)
    penalty = trial.suggest_categorical("penalty", ["l1", "l2", "elasticnet"])
    if penalty == "elasticnet":
        solver = "saga"
        l1_ratio = trial.suggest_float("l1_ratio", 0.0, 1.0)
    elif penalty == "l1":
        solver = "liblinear"
        l1_ratio = None
    else:  # l2
        solver = "lbfgs"
        l1_ratio = None
    return Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", LogisticRegression(
            max_iter=20000, class_weight="balanced", solver=solver, penalty=penalty,
            C=C, l1_ratio=l1_ratio
        ))
    ])

def build_lsvc(trial, random_state):
    C = trial.suggest_float("C", 1e-3, 100, log=True)
    max_iter = trial.suggest_int("max_iter", 5000, 20000, step=1000)
    dual = trial.suggest_categorical("dual", [True, False])
    return Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", LinearSVC(
            C=C, class_weight="balanced", max_iter=max_iter,
            loss="squared_hinge", dual=dual, random_state=random_state
        ))
    ])

def build_xgb(trial, random_state, y):
    from xgboost import XGBClassifier
    counter = Counter(y)
    neg, pos = counter[0], counter[1]
    base_spw = neg / pos
    spw_mult = trial.suggest_float("spw_mult", 0.25, 4.0, log=True)
    return XGBClassifier(
        n_estimators=trial.suggest_int("n_estimators", 400, 1500, step=100),
        max_depth=trial.suggest_int("max_depth", 3, 10),
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.30, log=True),
        subsample=trial.suggest_float("subsample", 0.6, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-6, 100.0, log=True),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        min_child_weight=trial.suggest_float("min_child_weight", 1.0, 10.0, log=True),
        gamma=trial.suggest_float("gamma", 1e-8, 5.0),
        scale_pos_weight=base_spw * spw_mult, eval_metric="logloss", tree_method="hist",
        n_jobs=-1, random_state=random_state, verbosity=0
    )

def build_lgbm(trial, random_state, y):
    import lightgbm as lgb
    counter = Counter(y)
    neg, pos = counter[0], counter[1]
    base_spw = neg / pos
    spw_mult = trial.suggest_float("spw_mult", 0.25, 4.0, log=True)

    max_depth = trial.suggest_categorical("max_depth", [-1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    num_leaves = trial.suggest_int("num_leaves", 31, 255)
    if isinstance(max_depth, int) and max_depth > 0:
        num_leaves = min(num_leaves, 2 ** max_depth)
    return lgb.LGBMClassifier(
        n_estimators=trial.suggest_int("n_estimators", 400, 2000, step=100),
        num_leaves=num_leaves,
        max_depth=max_depth,
        learning_rate=trial.suggest_float("learning_rate", 0.01, 0.20, log=True),
        subsample=trial.suggest_float("subsample", 0.6, 1.0),
        colsample_bytree=trial.suggest_float("colsample_bytree", 0.6, 1.0),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-6, 100.0, log=True),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-8, 10.0, log=True),
        min_child_weight=trial.suggest_float("min_child_weight", 1e-3, 10.0, log=True),
        scale_pos_weight=base_spw * spw_mult,
        objective="binary", n_jobs=-1, random_state=random_state, verbosity=-1
    )

# ---------- Main Class ----------
class ModelSelector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.leaderboard = None
        self.best_params = None
        self.train_smiles = None

    def run(self):
        results_dir = self.config.get("results_dir", "results")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        train_X_path = self.config.get("train_X_path") or _find_latest_file(results_dir, "split_train_X_*.csv")
        train_y_path = self.config.get("train_y_path") or _find_latest_file(results_dir, "split_train_y_*.csv")

        train_X_df = pd.read_csv(train_X_path)
        self.train_smiles = train_X_df["SMILES"].tolist()
        X_df = train_X_df.drop(columns=["SMILES"], errors="ignore")

        y_df = pd.read_csv(train_y_path)
        y = y_df["y"].values

        if len(X_df) != len(y):
            raise ValueError(f"X_train ({len(X_df)}) and y_train ({len(y)}) have different lengths!")

        algos = self.config.get("algos", "auto")
        scoring_name = self.config.get("scoring", "mcc").lower()
        n_trials_per_algo = self.config.get("n_trials_per_algo", 20)
        cv_splits = self.config.get("cv_splits", 5)
        cv_repeats = self.config.get("cv_repeats", 3)
        random_state = self.config.get("random_state", 42)

        if algos == "auto":
            algos = ["RF", "ET", "XGB", "LGBM", "LR", "LSVC"]

        if scoring_name not in SCORERS:
            raise ValueError(f"Invalid scoring '{scoring_name}'. Choose from {list(SCORERS.keys())}")
        scoring = SCORERS[scoring_name]
        display_metric = SCORE_NAME_DISPLAY.get(scoring_name, scoring_name)

        rskf = RepeatedStratifiedKFold(n_splits=cv_splits, n_repeats=cv_repeats, random_state=random_state)

        algo_builders = {
            "RF": lambda trial: build_rf(trial, random_state),
            "ET": lambda trial: build_et(trial, random_state),
            "LR": lambda trial: build_logreg(trial),
            "LSVC": lambda trial: build_lsvc(trial, random_state),
            "XGB": lambda trial: build_xgb(trial, random_state, y),
            "LGBM": lambda trial: build_lgbm(trial, random_state, y),
        }

        leaderboard_rows = []
        violin_data = []

        for algo in algos:
            print(f"\n=== Running {algo} optimization ===")
            study = optuna.create_study(direction="maximize")
            study.optimize(
                _wrap_objective(algo_builders[algo], algo, X_df, y, rskf, scoring, results_dir, timestamp),
                n_trials=n_trials_per_algo, n_jobs=1
            )

            scores_list = study.best_trial.user_attrs.get("cv_scores", [])
            leaderboard_rows.append({
                "Algorithm": algo,
                f"Best {display_metric} Mean": np.mean(scores_list) if scores_list else study.best_value,
                f"Best {display_metric} Std": np.std(scores_list) if scores_list else np.nan,
                "Best Params": study.best_params
            })

            for score in scores_list:
                violin_data.append({"Algorithm": algo, "Score": score})

        leaderboard_df = pd.DataFrame(leaderboard_rows).sort_values(
            by=f"Best {display_metric} Mean", ascending=False
        ).reset_index(drop=True)

        leaderboard_path = os.path.join(results_dir, f"leaderboard_{timestamp}.csv")
        leaderboard_df.to_csv(leaderboard_path, index=False)

        self.leaderboard = leaderboard_df
        self.best_params = leaderboard_df.iloc[0]["Best Params"]

        print(f"Leaderboard saved to: {leaderboard_path}")

        # ---------- Violin Plot ----------
        violin_df = pd.DataFrame(violin_data)
        order = leaderboard_df["Algorithm"].tolist()

        base_palette = sns.color_palette("crest", len(order))
        palette = dict(zip(order, base_palette))

        plt.figure(figsize=(8, 5))
        ax = sns.violinplot(
            data=violin_df,
            x="Algorithm", y="Score",
            hue="Algorithm",
            order=order,
            palette=palette,
            cut=0,
            dodge=False
        )
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()

        plt.title(f"{display_metric} Distribution per Algorithm", fontsize=14)
        plt.ylabel(display_metric)
        plt.xlabel("Algorithm")
        plt.grid(axis="y", linestyle="--", alpha=0.6)
        plt.tight_layout()

        violin_path = os.path.join(results_dir, f"violinplot_{timestamp}.png")
        plt.savefig(violin_path, dpi=300)
        plt.close()

        print(f"Violin plot saved to: {violin_path}")

        return self
