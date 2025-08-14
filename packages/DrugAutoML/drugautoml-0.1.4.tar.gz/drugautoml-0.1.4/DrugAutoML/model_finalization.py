"""
Model Finalization Module for DrugAutoML
---------------------------------------

This module:
1) Loads latest split files (train/test).
2) Picks best model (from leaderboard or via config) and fits on TRAIN.
3) Applies probability calibration (default: isotonic; also supports 'sigmoid' or 'none').
4) Selects a decision threshold on TRAIN calibrated probabilities.
5) Evaluates on TEST and saves metrics, plots (ROC/PR/Calibration/CM), predictions, and confusion matrices (raw & normalized).
6) Saves the calibrated model + chosen threshold as a .pkl.

Dependencies:
- pandas, numpy, joblib
- scikit-learn
- xgboost, lightgbm (if used)
- matplotlib, seaborn
"""

from __future__ import annotations
from typing import Dict, Any, Optional, Tuple
import os, glob, json, warnings
from datetime import datetime

import numpy as np
import pandas as pd

from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    roc_auc_score, average_precision_score, brier_score_loss,
    precision_recall_curve, roc_curve, confusion_matrix,
    f1_score, matthews_corrcoef, precision_score, recall_score,
    balanced_accuracy_score, classification_report
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.exceptions import ConvergenceWarning

import matplotlib.pyplot as plt
import seaborn as sns
import joblib

warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", message="X does not have valid feature names")
warnings.filterwarnings("ignore", message="l1_ratio parameter is only used when penalty is 'elasticnet'")

# ---------------------- File helpers ----------------------
def _find_latest(results_dir: str, pattern: str) -> str:
    files = glob.glob(os.path.join(results_dir, pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in '{results_dir}'.")
    return max(files, key=os.path.getmtime)

def _read_splits(results_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_X = pd.read_csv(_find_latest(results_dir, "split_train_X_*.csv"))
    train_y = pd.read_csv(_find_latest(results_dir, "split_train_y_*.csv"))
    test_X  = pd.read_csv(_find_latest(results_dir, "split_test_X_*.csv"))
    test_y  = pd.read_csv(_find_latest(results_dir, "split_test_y_*.csv"))
    return train_X, train_y, test_X, test_y

def _read_leaderboard(results_dir: str) -> pd.DataFrame:
    lb_path = _find_latest(results_dir, "leaderboard_*.csv")
    return pd.read_csv(lb_path)

# ---------------------- Metrics ----------------------
def _specificity(y_true, y_pred):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    return tn / (tn + fp) if (tn + fp) > 0 else 0.0

# ---------------------- Model builders ----------------------
def _build_lr(params: Dict[str, Any]) -> Pipeline:
    penalty = params.get("penalty", "l2")
    solver = params.get("solver", "lbfgs")
    C = float(params.get("C", 1.0))
    l1_ratio = params.get("l1_ratio", None)
    return Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", LogisticRegression(
            max_iter=20000, class_weight="balanced",
            penalty=penalty, solver=solver, C=C, l1_ratio=l1_ratio
        ))
    ])

def _build_lsvc(params: Dict[str, Any]) -> Pipeline:
    C = float(params.get("C", 1.0))
    dual = bool(params.get("dual", True))
    max_iter = int(params.get("max_iter", 10000))
    return Pipeline([
        ("scaler", StandardScaler(with_mean=False)),
        ("clf", LinearSVC(
            C=C, class_weight="balanced",
            loss="squared_hinge", dual=dual, max_iter=max_iter, random_state=42
        ))
    ])

def _build_rf(params: Dict[str, Any]) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=int(params.get("n_estimators", 800)),
        max_depth=None if params.get("max_depth", -1) in [None, -1] else int(params.get("max_depth", 12)),
        min_samples_split=int(params.get("min_samples_split", 2)),
        min_samples_leaf=int(params.get("min_samples_leaf", 1)),
        max_features=params.get("max_features", "sqrt"),
        bootstrap=bool(params.get("bootstrap", True)),
        class_weight="balanced_subsample",
        n_jobs=-1, random_state=42
    )

def _build_et(params: Dict[str, Any]) -> ExtraTreesClassifier:
    kwargs = dict(
        n_estimators=int(params.get("n_estimators", 1000)),
        max_depth=None if params.get("max_depth", -1) in [None, -1] else int(params.get("max_depth", 12)),
        min_samples_split=int(params.get("min_samples_split", 2)),
        min_samples_leaf=int(params.get("min_samples_leaf", 1)),
        max_features=params.get("max_features", "sqrt"),
        bootstrap=bool(params.get("bootstrap", False)),
        class_weight="balanced",
        n_jobs=-1, random_state=42
    )
    if kwargs["bootstrap"] and "et_max_samples" in params:
        kwargs["max_samples"] = float(params["et_max_samples"])
    return ExtraTreesClassifier(**kwargs)

def _build_xgb(params: Dict[str, Any]):
    from xgboost import XGBClassifier
    return XGBClassifier(
        n_estimators=int(params.get("n_estimators", 800)),
        max_depth=int(params.get("max_depth", 6)),
        learning_rate=float(params.get("learning_rate", 0.05)),
        subsample=float(params.get("subsample", 0.8)),
        colsample_bytree=float(params.get("colsample_bytree", 0.8)),
        reg_lambda=float(params.get("reg_lambda", 1.0)),
        reg_alpha=float(params.get("reg_alpha", 0.0)),
        min_child_weight=float(params.get("min_child_weight", 1.0)),
        gamma=float(params.get("gamma", 0.0)),
        scale_pos_weight=float(params.get("scale_pos_weight", 1.0)),
        eval_metric="logloss", tree_method="hist",
        n_jobs=-1, random_state=42, verbosity=0
    )

def _build_lgbm(params: Dict[str, Any]):
    import lightgbm as lgb
    return lgb.LGBMClassifier(
        n_estimators=int(params.get("n_estimators", 800)),
        num_leaves=int(params.get("num_leaves", 63)),
        max_depth=int(params.get("max_depth", -1)),
        learning_rate=float(params.get("learning_rate", 0.05)),
        subsample=float(params.get("subsample", 0.8)),
        colsample_bytree=float(params.get("colsample_bytree", 0.8)),
        reg_lambda=float(params.get("reg_lambda", 1.0)),
        reg_alpha=float(params.get("reg_alpha", 0.0)),
        min_child_weight=float(params.get("min_child_weight", 1.0)),
        scale_pos_weight=float(params.get("scale_pos_weight", 1.0)),
        objective="binary", n_jobs=-1, random_state=42, verbosity=-1
    )

def _build_estimator(algo: str, params: Dict[str, Any]):
    algo = algo.upper()
    if algo == "LR":   return _build_lr(params)
    if algo == "LSVC": return _build_lsvc(params)
    if algo == "RF":   return _build_rf(params)
    if algo == "ET":   return _build_et(params)
    if algo == "XGB":  return _build_xgb(params)
    if algo == "LGBM": return _build_lgbm(params)
    raise ValueError(f"Unknown algorithm: {algo}")

# ---------------------- Threshold strategies ----------------------
def _thr_fixed(_: np.ndarray, __: np.ndarray, value: float = 0.5) -> float:
    return float(value)

def _thr_youden(y_true: np.ndarray, p: np.ndarray) -> float:
    fpr, tpr, th = roc_curve(y_true, p)
    j = tpr - fpr
    return float(th[np.argmax(j)])

def _thr_max_f1(y_true: np.ndarray, p: np.ndarray) -> float:
    prec, rec, th = precision_recall_curve(y_true, p)
    f1 = 2 * prec * rec / (prec + rec + 1e-12)
    return float(np.nan_to_num(th)[np.argmax(f1[:-1])]) if len(th) else 0.5

def _thr_max_mcc(y_true: np.ndarray, p: np.ndarray) -> float:
    grid = np.linspace(0.0, 1.0, 1001)
    mcc_vals = []
    for t in grid:
        y_pred = (p >= t).astype(int)
        mcc_vals.append(matthews_corrcoef(y_true, y_pred))
    return float(grid[int(np.argmax(mcc_vals))])

def _thr_target_sens(y_true: np.ndarray, p: np.ndarray, target: float = 0.80) -> float:
    fpr, tpr, th = roc_curve(y_true, p)
    idx = np.argmin(np.abs(tpr - target))
    return float(th[idx])

def _thr_target_spec(y_true: np.ndarray, p: np.ndarray, target: float = 0.80) -> float:
    fpr, tpr, th = roc_curve(y_true, p)
    spec = 1.0 - fpr
    idx = np.argmin(np.abs(spec - target))
    return float(th[idx])

def _thr_cost_ratio(_: np.ndarray, __: np.ndarray, c_fp: float = 1.0, c_fn: float = 1.0) -> float:
    # Bayes threshold assuming well-calibrated probabilities:
    return float(c_fn / (c_fp + c_fn))

# ---------------------- Plots ----------------------
def _plot_roc_pr(y_true, p, save_prefix: str):
    fpr, tpr, _ = roc_curve(y_true, p)
    prec, rec, _ = precision_recall_curve(y_true, p)

    plt.figure(figsize=(5,4))
    plt.plot(fpr, tpr, label=f"AUC = {roc_auc_score(y_true, p):.3f}")
    plt.plot([0,1],[0,1],'--',alpha=0.5)
    plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate")
    plt.title("ROC Curve"); plt.grid(alpha=0.3); plt.legend(loc="lower right")
    plt.tight_layout(); plt.savefig(f"{save_prefix}_roc.png", dpi=300); plt.close()

    plt.figure(figsize=(5,4))
    plt.plot(rec, prec, label=f"AP = {average_precision_score(y_true, p):.3f}")
    plt.xlabel("Recall"); plt.ylabel("Precision")
    plt.title("Precision-Recall Curve"); plt.grid(alpha=0.3); plt.legend(loc="lower left")
    plt.tight_layout(); plt.savefig(f"{save_prefix}_pr.png", dpi=300); plt.close()

def _plot_calibration(y_true, p, save_path: str):
    prob_true, prob_pred = calibration_curve(y_true, p, n_bins=10, strategy="quantile")
    plt.figure(figsize=(5,4))
    plt.plot(prob_pred, prob_true, marker="o")
    plt.plot([0,1],[0,1],'--',alpha=0.5)
    plt.xlabel("Predicted probability"); plt.ylabel("Observed positive rate")
    plt.title("Calibration Curve (Reliability)")
    plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(save_path, dpi=300); plt.close()

def _plot_confusion_and_save(y_true, y_pred, save_prefix: str):
    cm = confusion_matrix(y_true, y_pred, labels=[0,1])
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)

    # Save CSVs
    pd.DataFrame(cm, index=["True_0","True_1"], columns=["Pred_0","Pred_1"]) \
        .to_csv(f"{save_prefix}_cm_raw.csv")
    pd.DataFrame(cm_norm, index=["True_0","True_1"], columns=["Pred_0","Pred_1"]) \
        .to_csv(f"{save_prefix}_cm_normalized.csv")

    # Plot heatmap
    plt.figure(figsize=(4.8,4.2))
    sns.heatmap(cm, annot=True, fmt="d", cbar=False, cmap="Blues",
                xticklabels=["Pred 0","Pred 1"], yticklabels=["True 0","True 1"])
    plt.xlabel("Predicted"); plt.ylabel("True"); plt.title("Confusion Matrix")
    plt.tight_layout(); plt.savefig(f"{save_prefix}_cm.png", dpi=300); plt.close()

# ---------------------- Main class ----------------------
class ModelFinalization:
    """
    Config keys:
      - results_dir: "results"
      - algo: "auto" | "RF" | "ET" | "LR" | "LSVC" | "XGB" | "LGBM"
      - params: dict (optional; if absent, read from leaderboard)
      - calibration: "none" | "sigmoid" | "isotonic"  (default: "isotonic")
      - cv_folds: 5  (for CalibratedClassifierCV)
      - threshold_strategy:
          "fixed", "youden", "max_f1", "max_mcc",
          "target_sensitivity", "target_specificity", "cost_ratio"
      - threshold_kwargs: e.g., {"value":0.5}, {"target":0.9}, {"c_fp":1,"c_fn":5}
      - save_model: True
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = {"calibration": "isotonic", **config}  # default isotonic
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report = {}
        self.threshold_ = 0.5
        self.model_ = None
        self.algo_ = None
        self.params_ = None

    def _pick_algo_and_params(self, results_dir: str) -> Tuple[str, Dict[str, Any]]:
        algo = self.config.get("algo", "auto")
        params = self.config.get("params")
        if algo != "auto" and params is not None:
            return algo, params

        lb = _read_leaderboard(results_dir)
        best_row = lb.iloc[0]
        algo = str(best_row["Algorithm"])
        raw = best_row["Best Params"]
        if isinstance(raw, str):
            try:
                params = json.loads(raw.replace("'", '"'))
            except Exception:
                params = eval(raw)  # safe context assumed
        elif isinstance(raw, dict):
            params = raw
        else:
            params = {}
        return algo, params

    def _prob_fn(self, estimator):
        if hasattr(estimator, "predict_proba"):
            return lambda X: estimator.predict_proba(X)[:, 1]
        elif hasattr(estimator, "decision_function"):
            return lambda X: 1.0 / (1.0 + np.exp(-estimator.decision_function(X)))
        else:
            raise ValueError("Estimator has neither predict_proba nor decision_function.")

    def _choose_threshold(self, y_true: np.ndarray, p: np.ndarray) -> float:
        strat = self.config.get("threshold_strategy", "fixed").lower()
        kw = self.config.get("threshold_kwargs", {}) or {}

        if strat == "fixed":               return _thr_fixed(y_true, p, value=float(kw.get("value", 0.5)))
        if strat == "youden":              return _thr_youden(y_true, p)
        if strat == "max_f1":              return _thr_max_f1(y_true, p)
        if strat == "max_mcc":             return _thr_max_mcc(y_true, p)
        if strat == "target_sensitivity":  return _thr_target_sens(y_true, p, target=float(kw.get("target", 0.80)))
        if strat == "target_specificity":  return _thr_target_spec(y_true, p, target=float(kw.get("target", 0.80)))
        if strat == "cost_ratio":          return _thr_cost_ratio(y_true, p, c_fp=float(kw.get("c_fp", 1.0)),
                                                                  c_fn=float(kw.get("c_fn", 1.0)))
        raise ValueError(f"Unknown threshold strategy: {strat}")

    def run(self):
        results_dir = self.config.get("results_dir", "results")
        os.makedirs(results_dir, exist_ok=True)

        # 1) Load splits
        train_X_df, train_y_df, test_X_df, test_y_df = _read_splits(results_dir)
        X_train = train_X_df.drop(columns=["SMILES"], errors="ignore").values
        y_train = train_y_df["y"].values.astype(int)
        X_test  = test_X_df.drop(columns=["SMILES"], errors="ignore").values
        y_test  = test_y_df["y"].values.astype(int)

        # 2) Pick best algo + params
        algo, params = self._pick_algo_and_params(results_dir)
        base_estimator = _build_estimator(algo, params)
        self.algo_, self.params_ = algo, params

        # 3) Calibration (default isotonic)
        calib = self.config.get("calibration", "isotonic").lower()
        cv_folds = int(self.config.get("cv_folds", 5))

        if calib == "none":
            estimator = base_estimator.fit(X_train, y_train)
        else:
            method = "sigmoid" if calib == "sigmoid" else "isotonic"
            estimator = CalibratedClassifierCV(base_estimator, method=method, cv=cv_folds).fit(X_train, y_train)

        self.model_ = estimator
        proba = self._prob_fn(estimator)

        # 4) Threshold on TRAIN (calibrated)
        p_train = proba(X_train)
        thr = self._choose_threshold(y_train, p_train)
        self.threshold_ = float(np.clip(thr, 0.0, 1.0))

        # 5) Evaluate on TEST
        p_test = proba(X_test)
        y_pred = (p_test >= self.threshold_).astype(int)

        metrics = {
            "ROC_AUC": float(roc_auc_score(y_test, p_test)),
            "PR_AUC": float(average_precision_score(y_test, p_test)),
            "Brier": float(brier_score_loss(y_test, p_test)),
            "F1": float(f1_score(y_test, y_pred)),
            "MCC": float(matthews_corrcoef(y_test, y_pred)),
            "Precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "Recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "Specificity": float(_specificity(y_test, y_pred)),
            "Balanced_Accuracy": float(balanced_accuracy_score(y_test, y_pred)),
            "Threshold": float(self.threshold_),
            "Algorithm": self.algo_,
            "Calibration": calib,
        }

        classif_rep = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

        # 6) Save artifacts
        ts = self.timestamp
        model_path = os.path.join(results_dir, f"final_model_{self.algo_}_{ts}.pkl")
        info_path  = os.path.join(results_dir, f"finalization_report_{ts}.json")
        preds_csv  = os.path.join(results_dir, f"test_predictions_{ts}.csv")
        figs_prefix = os.path.join(results_dir, f"finalization_{ts}")

        joblib.dump({"model": estimator, "threshold": self.threshold_, "algo": self.algo_, "params": self.params_},
                    model_path)

        with open(info_path, "w") as f:
            json.dump({"metrics": metrics, "params": self.params_, "algo": self.algo_,
                       "classification_report": classif_rep}, f, indent=2)

        pd.DataFrame({
            "SMILES": test_X_df.get("SMILES", pd.Series([None]*len(y_test))),
            "y_true": y_test,
            "p_pred": p_test,
            "y_pred": y_pred
        }).to_csv(preds_csv, index=False)

        _plot_roc_pr(y_test, p_test, save_prefix=figs_prefix)
        _plot_calibration(y_test, p_test, save_path=f"{figs_prefix}_reliability.png")
        _plot_confusion_and_save(y_test, y_pred, save_prefix=figs_prefix)

        # 7) Console summary
        print("\n=== Model Finalization Summary ===")
        print(f"Algorithm: {self.algo_}")
        print(f"Calibration: {calib}")
        print(f"Chosen threshold: {self.threshold_:.3f}")
        print(f"ROC-AUC: {metrics['ROC_AUC']:.3f} | PR-AUC: {metrics['PR_AUC']:.3f} | Brier: {metrics['Brier']:.4f}")
        print(f"F1: {metrics['F1']:.3f} | MCC: {metrics['MCC']:.3f} | Precision: {metrics['Precision']:.3f} | Recall: {metrics['Recall']:.3f}")
        print(f"Specificity: {metrics['Specificity']:.3f} | Balanced Acc: {metrics['Balanced_Accuracy']:.3f}")
        print(f"Model saved to: {model_path}")
        print(f"Report saved to: {info_path}")
        print(f"Predictions saved to: {preds_csv}")
        print(f"Figures saved to: {figs_prefix}_*.png")
        print("==================================\n")

        self.report = metrics
        return self


