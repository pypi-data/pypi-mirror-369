"""
Featurization Module for DrugAutoML
-----------------------------------

This module transforms molecular SMILES strings into numerical representations
(fingerprints) suitable for machine learning models in bioactivity prediction.

Currently supported:
- ECFP (Extended-Connectivity Fingerprint) with customizable radius, bit length,
  and optional count-based features.

Features:
1. Reads preprocessed data from the output of `data_preprocess`.
2. Generates molecular fingerprints (default: ECFP4, 2048 bits).
3. Optionally removes constant (non-informative) features.
4. Saves processed feature matrices and a summary report.

Dependencies:
- pandas
- numpy
- rdkit (required for fingerprint generation)
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import os, json, glob
from datetime import datetime
import numpy as np
import pandas as pd


# ---------- RDKit check ----------
def has_rdkit() -> bool:
    """Checks if RDKit is installed and available."""
    try:
        import rdkit  # noqa: F401
        return True
    except Exception:
        return False


# ---------- Save outputs ----------
def _save_outputs(df: pd.DataFrame, report: Dict[str, Any], results_dir="results") -> Dict[str, str]:
    """Saves the featurized dataset and process report."""
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_path = os.path.join(results_dir, f"featurize_output_{ts}.csv")
    log_path = os.path.join(results_dir, f"featurize_log_{ts}.json")
    df.to_csv(data_path, index=False)
    with open(log_path, "w") as f:
        json.dump(report, f, indent=2)
    return {"data_path": data_path, "log_path": log_path}


# ---------- Drop constant features ----------
def _drop_constant(df: pd.DataFrame):
    """
    Removes constant (zero-variance) features from the dataset.

    Returns:
        filtered_df: DataFrame without constant features
        dropped_count: Number of dropped features
    """
    n_before = df.shape[1]
    nunique = df.nunique(dropna=False)
    keep_cols = nunique[nunique > 1].index.tolist()
    return df[keep_cols].copy(), (n_before - len(keep_cols))


# ---------- ECFP generator ----------
def _ecfp_fp(mol, radius: int, nbits: int, use_counts: bool):
    """Generates ECFP fingerprints for a given RDKit molecule."""
    from rdkit import DataStructs
    from rdkit.Chem import AllChem
    try:
        fpgen = AllChem.GetMorganGenerator(radius=radius, fpSize=nbits)
        if use_counts:
            fp = fpgen.GetSparseCountFingerprint(mol)
            arr = np.zeros((nbits,), dtype=np.float32)
            for k, v in fp.GetNonzeroElements().items():
                if 0 <= k < nbits:
                    arr[int(k)] = float(v)
            return arr
        else:
            fp = fpgen.GetFingerprint(mol)
            arr = np.zeros((nbits,), dtype=np.int8)
            DataStructs.ConvertToNumpyArray(fp, arr)
            return arr.astype(np.float32)
    except Exception:
        # Fallback to hashed fingerprints
        if use_counts:
            fp = AllChem.GetHashedMorganFingerprint(mol, radius, nBits=nbits)
            arr = np.zeros((nbits,), dtype=np.float32)
            for k, v in fp.GetNonzeroElements().items():
                arr[k % nbits] = float(v)
            return arr
        else:
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
            arr = np.zeros((nbits,), dtype=np.int8)
            DataStructs.ConvertToNumpyArray(fp, arr)
            return arr.astype(np.float32)


# ---------- Get latest preprocess output ----------
def _find_latest_preprocess_output(results_dir="results") -> str:
    """Finds the most recent output file from `data_preprocess`."""
    files = glob.glob(os.path.join(results_dir, "data_preprocess_output_*.csv"))
    if not files:
        raise FileNotFoundError(f"No preprocessed data found in '{results_dir}'. Run data_preprocess first.")
    return max(files, key=os.path.getmtime)


# ---------- Main Class ----------
class Featurizer:
    """Main class for transforming SMILES into numerical fingerprints."""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Dictionary of parameters including:
                - fp_type: Fingerprint type (default: 'ECFP')
                - radius: Radius for circular fingerprints (default: 2)
                - nbits: Bit length of the fingerprint (default: 2048)
                - use_counts: Whether to use count-based features (default: False)
                - drop_constant: Remove constant features (default: True)
                - save_results: Save outputs to disk (default: True)
                - results_dir: Directory to save results (default: 'results')
        """
        self.config = config
        self.data = None
        self.report = {}
        self.metadata = {"module": "featurization", "timestamp": datetime.now().isoformat()}

    def run(self, preprocessed_df: Optional[pd.DataFrame] = None):
        """Executes the featurization process."""
        if not has_rdkit():
            raise RuntimeError("RDKit is required for featurization.")

        fp_type = self.config.get("fp_type", "ECFP")
        radius = self.config.get("radius", 2)
        nbits = self.config.get("nbits", 2048)
        use_counts = self.config.get("use_counts", False)
        drop_constant = self.config.get("drop_constant", True)
        save_results = self.config.get("save_results", True)
        results_dir = self.config.get("results_dir", "results")

        if preprocessed_df is None:
            preprocess_csv_path = self.config.get("preprocess_csv_path") or _find_latest_preprocess_output(results_dir)
            df = pd.read_csv(preprocess_csv_path)
        else:
            df = preprocessed_df.copy()

        if "SMILES" not in df.columns or "y" not in df.columns:
            raise ValueError(f"Preprocessed data must have 'SMILES' and 'y' columns. Found: {list(df.columns)}")

        from rdkit import Chem
        try:
            from rdkit import RDLogger
            RDLogger.DisableLog("rdApp.error")
        except Exception:
            pass

        X = []
        n_invalid = 0
        if fp_type.upper() == "ECFP":
            for smi in df["SMILES"].astype(str):
                mol = Chem.MolFromSmiles(smi)
                if mol is None:
                    n_invalid += 1
                    X.append(np.zeros((nbits,), dtype=np.float32))
                else:
                    X.append(_ecfp_fp(mol, radius, nbits, use_counts))
        else:
            raise NotImplementedError(f"Fingerprint type '{fp_type}' not implemented yet.")

        X = np.vstack(X)
        feat_cols = [f"{fp_type.upper()}{i+1}" for i in range(nbits)]
        feat_df = pd.DataFrame(X, columns=feat_cols)

        dropped_count = 0
        if drop_constant:
            feat_df, dropped_count = _drop_constant(feat_df)

        featurize_output = pd.concat([df[["SMILES", "y"]].reset_index(drop=True),
                                      feat_df.reset_index(drop=True)], axis=1)

        report = {
            "n_samples_in": int(len(df)),
            "n_invalid_smiles": int(n_invalid),
            "method": fp_type.upper(),
            "radius": radius if fp_type.upper() == "ECFP" else None,
            "nbits": nbits,
            "use_counts": use_counts,
            "drop_constant": drop_constant,
            "n_features_before": nbits,
            "n_features_after": int(feat_df.shape[1]),
            "dropped_constant_features": dropped_count
        }

        if save_results:
            paths = _save_outputs(featurize_output, report, results_dir=results_dir)
            report["saved_data_path"] = paths["data_path"]
            report["saved_log_path"] = paths["log_path"]

        # Summary print
        print("\n=== Featurization Summary ===")
        print(f"Samples processed: {report['n_samples_in']}")
        print(f"Invalid SMILES (zero vector assigned): {report['n_invalid_smiles']}")
        print(f"Method: {report['method']} (radius={radius}, nbits={nbits}, use_counts={use_counts})")
        print(f"Features before constant-drop: {report['n_features_before']}")
        print(f"Features after constant-drop: {report['n_features_after']}")
        print(f"Dropped constant features: {report['dropped_constant_features']}")
        print("==================================\n")

        self.data = featurize_output
        self.report = report
        return self
