"""
Prediction Module for DrugAutoML
================================

Purpose
-------
Score NEW (external) molecules with the finalized, *calibrated* model.
- Works with **unlabeled** input (SMILES only): outputs probabilities & class calls.
- Works with **labeled** input: also computes external-set metrics and a confusion matrix.

What it loads from `results/`
-----------------------------
- final_model_*.pkl           (dict with keys: "model", "threshold", "algo", ...)
- split_features_*.json       (ordered feature names kept after constant-drop)
- featurize_log_*.json        (ECFP params: radius, nbits, use_counts)

What it expects from the user
-----------------------------
An input table with at least a SMILES column (name configurable).
Optional ground-truth labels can come as:
  - a binary column (0/1 or {yes/true/active vs. no/false/inactive}), or
  - a numeric potency column together with cutoffs for active/inactive.

Outputs (saved under `results/`)
--------------------------------
- predict_output_<TS>.csv        (SMILES_in, SMILES, proba, y_pred, [y_true], flags)
- predict_metrics_<TS>.json      (if labels provided)
- predict_cm_<TS>.png            (confusion matrix, if labels provided)
- predict_log_<TS>.json          (I/O + QC summary)

Dependencies
------------
pandas, numpy, rdkit, scikit-learn, matplotlib, joblib
"""

from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
import os, json, glob, re, warnings
from datetime import datetime

import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix, roc_auc_score, average_precision_score, brier_score_loss,
    f1_score, matthews_corrcoef, precision_score, recall_score, balanced_accuracy_score
)
from scipy.special import expit

# RDKit
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.error")
warnings.filterwarnings("ignore")


# ------------------------ Utilities & IO helpers ------------------------ #
def _find_latest(results_dir: str, pattern: str) -> str:
    files = glob.glob(os.path.join(results_dir, pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in '{results_dir}'.")
    return max(files, key=os.path.getmtime)

def _smart_read_table(path: str) -> pd.DataFrame:
    """Robust CSV/TSV reader with separator sniffing; supports parquet."""
    p = path.lower()
    if p.endswith((".parquet", ".pq")):
        return pd.read_parquet(path)
    try:
        return pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
    except Exception:
        for sep in [",", "\t", ";", "|"]:
            try:
                return pd.read_csv(path, sep=sep, encoding="utf-8-sig")
            except Exception:
                pass
    # last resort
    return pd.read_csv(path, sep=None, engine="python", on_bad_lines="skip", encoding="utf-8-sig")

def _load_model_bundle(results_dir: str):
    pkl = _find_latest(results_dir, "final_model_*.pkl")
    bundle = joblib.load(pkl)
    model = bundle["model"]
    thr = float(bundle.get("threshold", 0.5))
    algo = bundle.get("algo", "UNKNOWN")
    return model, thr, algo, pkl

def _load_schema(results_dir: str) -> List[str]:
    with open(_find_latest(results_dir, "split_features_*.json")) as f:
        return json.load(f)

def _load_featurize_cfg(results_dir: str) -> Dict[str, Any]:
    with open(_find_latest(results_dir, "featurize_log_*.json")) as f:
        return json.load(f)


# ------------------------ SMILES & ECFP featurization ------------------- #
def _standardize_smiles(smi: str) -> Optional[str]:
    """Minimal, robust standardization → canonical SMILES (None if invalid)."""
    try:
        mol = Chem.MolFromSmiles(str(smi))
        if mol is None:
            return None
        return Chem.MolToSmiles(mol, canonical=True)
    except Exception:
        return None

def _ecfp_array(mol, radius: int, nbits: int, use_counts: bool) -> np.ndarray:
    """Return 1D numpy array (nbits,) of ECFP features."""
    from rdkit import DataStructs
    if use_counts:
        fp = AllChem.GetMorganFingerprint(mol, radius)  # SparseIntVect with counts
        arr = np.zeros((nbits,), dtype=np.float32)
        for k, v in fp.GetNonzeroElements().items():
            arr[int(k) % nbits] += float(v)
        return arr
    else:
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
        arr = np.zeros((nbits,), dtype=np.int8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        return arr.astype(np.float32)

def _featurize_smiles(smiles: List[str], radius: int, nbits: int, use_counts: bool) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Returns (df with ECFP1..ECFPnbits, stats). Invalid SMILES → zero vector."""
    cols = [f"ECFP{i+1}" for i in range(nbits)]
    X = np.zeros((len(smiles), nbits), dtype=np.float32)
    stats = {"n_invalid": 0}
    for i, smi in enumerate(smiles):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            stats["n_invalid"] += 1
            continue
        X[i] = _ecfp_array(mol, radius, nbits, use_counts)
    return pd.DataFrame(X, columns=cols), stats


# ------------------------ Label parsing (optional) ---------------------- #
_BIN_POS = {"1", "true", "yes", "pos", "positive", "active"}
_BIN_NEG = {"0", "false", "no", "neg", "negative", "inactive", "not active", "no activity"}

def _parse_binary(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    def f(x: str):
        if x in _BIN_POS: return 1
        if x in _BIN_NEG: return 0
        return np.nan
    return s.map(f)

def _derive_labels(df: pd.DataFrame,
                   label_col: Optional[str],
                   activity_type: Optional[str],
                   active_cutoff: Optional[float],
                   inactive_cutoff: Optional[float]) -> Optional[pd.Series]:
    """
    Returns y_true (0/1) or None.
    - If label_col is None → None.
    - If activity_type == 'binary' → parse keywords or numbers 0/1.
    - If activity_type == 'px' → numeric + cutoffs (gray zone dropped from metrics).
    """
    if not label_col or label_col not in df.columns:
        return None
    if activity_type is None or activity_type.lower() == "binary":
        s = pd.to_numeric(df[label_col], errors="coerce")
        y = s.where(s.isin([0, 1]), np.nan)
        if y.isna().all():
            y = _parse_binary(df[label_col])
        return y.astype("float")
    elif activity_type.lower() == "px":
        if active_cutoff is None or inactive_cutoff is None:
            raise ValueError("For 'px' labels you must provide active_cutoff and inactive_cutoff.")
        x = pd.to_numeric(df[label_col], errors="coerce")
        y = np.where(x >= float(active_cutoff), 1.0,
            np.where(x <= float(inactive_cutoff), 0.0, np.nan))
        return pd.Series(y, index=df.index)
    else:
        raise ValueError("activity_type must be 'binary' or 'px'.")


# ------------------------ Prediction + metrics -------------------------- #
def _predict_proba(model, X: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        return expit(model.decision_function(X))
    raise ValueError("Calibrated model has neither predict_proba nor decision_function.")

def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, proba: np.ndarray) -> Dict[str, float]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0,1]).ravel()
    out = {
        "ROC_AUC": float(roc_auc_score(y_true, proba)) if len(np.unique(y_true)) > 1 else float("nan"),
        "PR_AUC": float(average_precision_score(y_true, proba)) if len(np.unique(y_true)) > 1 else float("nan"),
        "Brier": float(brier_score_loss(y_true, proba)),
        "F1": float(f1_score(y_true, y_pred)),
        "MCC": float(matthews_corrcoef(y_true, y_pred)),
        "Precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "Recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "Specificity": float(tn / max(1, tn + fp)),
        "Balanced_Accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn)
    }
    return out

def _save_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, path: str):
    cm = confusion_matrix(y_true, y_pred, labels=[0,1])
    fig, ax = plt.subplots(figsize=(3.2, 3.2))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks([0,1]); ax.set_yticks([0,1])
    ax.set_xticklabels(["Inactive", "Active"]); ax.set_yticklabels(["Inactive", "Active"])
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    for (i, j), v in np.ndenumerate(cm):
        ax.text(j, i, int(v), ha="center", va="center", color="black")
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


# ------------------------------- Main class ---------------------------- #
class Predictor:
    """
    Predict with the finalized, calibrated model.

    Config
    ------
    results_dir: str = "results"
    input_path: Optional[str] = None            # if None, pass a DataFrame to run(df=...)
    smiles_col: str = "SMILES"
    label_col: Optional[str] = None             # optional external labels column
    activity_type: Optional[str] = "binary"     # "binary" or "px"
    active_cutoff: Optional[float] = None       # for px → y mapping
    inactive_cutoff: Optional[float] = None     # for px → y mapping
    threshold_override: Optional[float] = None  # if provided, override stored threshold
    standardize_smiles: bool = True
    save_results: bool = True

    Attributes after run()
    ----------------------
    predictions : pd.DataFrame
    metrics     : Optional[Dict[str, float]]
    report      : Dict[str, Any]
    """
    def __init__(self, config: Dict[str, Any]):
        self.cfg = {
            "results_dir": "results",
            "input_path": None,
            "smiles_col": "SMILES",
            "label_col": None,
            "activity_type": "binary",
            "active_cutoff": None,
            "inactive_cutoff": None,
            "threshold_override": None,
            "standardize_smiles": True,
            "save_results": True,
            **(config or {}),
        }
        self.predictions: Optional[pd.DataFrame] = None
        self.metrics: Optional[Dict[str, float]] = None
        self.report: Dict[str, Any] = {}

        self._timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ------------- public API ------------- #
    def run(self, df: Optional[pd.DataFrame] = None):
        results_dir = self.cfg["results_dir"]
        os.makedirs(results_dir, exist_ok=True)

        # Load model + schema + featurizer config
        model, thr_model, algo, model_path = _load_model_bundle(results_dir)
        feature_names = _load_schema(results_dir)
        feat_cfg = _load_featurize_cfg(results_dir)
        radius = int(feat_cfg.get("radius", 2))
        nbits = int(feat_cfg.get("nbits", 2048))
        use_counts = bool(feat_cfg.get("use_counts", False))

        threshold = float(self.cfg["threshold_override"]) if self.cfg["threshold_override"] is not None else float(thr_model)

        # Load input
        if df is None:
            inp_path = self.cfg.get("input_path")
            if not inp_path:
                raise ValueError("Provide either 'input_path' in config or a DataFrame to run(df=...).")
            df0 = _smart_read_table(inp_path)
        else:
            df0 = df.copy()

        if self.cfg["smiles_col"] not in df0.columns:
            raise KeyError(f"SMILES column '{self.cfg['smiles_col']}' not found in input.")

        # Prepare SMILES
        smi_in = df0[self.cfg["smiles_col"]].astype(str).tolist()
        smi_std = []
        n_missing, n_invalid = 0, 0
        for s in smi_in:
            if s is None or str(s).strip() == "":
                smi_std.append(None); n_missing += 1; continue
            c = _standardize_smiles(s) if self.cfg["standardize_smiles"] else str(s)
            if c is None:
                n_invalid += 1
            smi_std.append(c)

        # Featurize (invalid → zero vector)
        smiles_clean = [s if isinstance(s, str) else "" for s in smi_std]
        X_all, feat_stats = _featurize_smiles(smiles_clean, radius, nbits, use_counts=use_counts)

        # Align feature columns (after constant-drop)
        for c in [f"ECFP{i+1}" for i in range(nbits)]:
            if c not in X_all.columns:
                X_all[c] = 0.0
        X_df = X_all[feature_names].copy()
        X = X_df.values.astype(np.float32)

        # Predict
        proba = _predict_proba(model, X)
        y_pred = (proba >= threshold).astype(int)

        # Optional ground-truth parsing
        y_true = _derive_labels(
            df0,
            label_col=self.cfg.get("label_col"),
            activity_type=self.cfg.get("activity_type"),
            active_cutoff=self.cfg.get("active_cutoff"),
            inactive_cutoff=self.cfg.get("inactive_cutoff"),
        )

        # Build output table
        out = pd.DataFrame({
            "SMILES_in": df0[self.cfg["smiles_col"]],
            "SMILES": smi_std,
            "proba": proba,
            "y_pred": y_pred
        })
        if y_true is not None:
            out["y_true"] = y_true.values

        # Flags
        out["is_missing_smiles"] = [int(x is None or str(x).strip() == "") for x in smi_in]
        out["is_invalid_smiles"] = [int(x is None) for x in smi_std]

        # Metrics (only for rows with valid y_true)
        metrics = None
        if y_true is not None:
            mask_eval = y_true.notna() & (out["SMILES"].notna())
            if mask_eval.any():
                metrics = _compute_metrics(
                    y_true.loc[mask_eval].astype(int).values,
                    y_pred[mask_eval.values],
                    proba[mask_eval.values]
                )
                metrics["Threshold"] = float(threshold)
                metrics["Algorithm"] = str(algo)

                # Confusion matrix figure
                cm_path = os.path.join(results_dir, f"predict_cm_{self._timestamp}.png")
                _save_confusion_matrix(
                    y_true.loc[mask_eval].astype(int).values,
                    y_pred[mask_eval.values],
                    cm_path
                )

        # Report
        report = {
            "model_path": model_path,
            "algo": algo,
            "threshold_used": float(threshold),
            "n_rows_in": int(len(df0)),
            "n_missing_smiles": int(n_missing),
            "n_invalid_smiles": int(feat_stats.get("n_invalid", 0)),
            "radius": radius,
            "nbits": nbits,
            "use_counts": use_counts,
            "n_features_used": int(len(feature_names)),
        }

        # Save
        if self.cfg.get("save_results", True):
            pred_path = os.path.join(results_dir, f"predict_output_{self._timestamp}.csv")
            out.to_csv(pred_path, index=False)

            log_path = os.path.join(results_dir, f"predict_log_{self._timestamp}.json")
            with open(log_path, "w") as f:
                json.dump(report, f, indent=2)

            if metrics is not None:
                met_path = os.path.join(results_dir, f"predict_metrics_{self._timestamp}.json")
                with open(met_path, "w") as f:
                    json.dump(metrics, f, indent=2)

        # Console summary
        print("\n=== Prediction Summary ===")
        print(f"Rows scored: {len(out)} | Invalid SMILES (zero vector): {report['n_invalid_smiles']}")
        print(f"Model: {algo} | Threshold: {report['threshold_used']}")
        if metrics is not None:
            print(f"External set MCC: {metrics['MCC']:.3f} | F1: {metrics['F1']:.3f} | "
                  f"BalAcc: {metrics['Balanced_Accuracy']:.3f}")
        print("==========================\n")

        self.predictions = out
        self.metrics = metrics
        self.report = report
        return self
