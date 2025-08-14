"""
Data Splitting Module for DrugAutoML
------------------------------------

This module splits featurized molecular datasets into training and testing sets
for bioactivity prediction.

Supported splitting methods:
- Scaffold split (structure-aware, uses RDKit Murcko scaffolds)
- Stratified random split (class-proportion preserving random split)

Features:
1. Loads the latest featurized dataset (or accepts a DataFrame directly).
2. Ensures no duplicate SMILES between train and test sets.
3. Preserves class distribution in both splits.
4. Saves full train/test sets, X and y matrices, and metadata logs.

Dependencies:
- pandas
- numpy
- rdkit (required for scaffold split)
"""

from __future__ import annotations
from typing import Dict, Any, Optional
import os, json, glob
from datetime import datetime
import pandas as pd
import numpy as np


# ---------- RDKit Check ----------
def has_rdkit() -> bool:
    """Checks if RDKit is installed."""
    try:
        import rdkit  # noqa: F401
        return True
    except Exception:
        return False


# ---------- Save Outputs ----------
def _save_splits(train_df, test_df, feature_cols, y_col, report, results_dir="results") -> Dict[str, str]:
    """Saves train/test datasets, feature lists, and split reports."""
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    paths = {
        "train_full": os.path.join(results_dir, f"split_train_{ts}.csv"),
        "test_full": os.path.join(results_dir, f"split_test_{ts}.csv"),
        "train_X": os.path.join(results_dir, f"split_train_X_{ts}.csv"),
        "train_y": os.path.join(results_dir, f"split_train_y_{ts}.csv"),
        "test_X": os.path.join(results_dir, f"split_test_X_{ts}.csv"),
        "test_y": os.path.join(results_dir, f"split_test_y_{ts}.csv"),
        "features": os.path.join(results_dir, f"split_features_{ts}.json"),
        "log": os.path.join(results_dir, f"split_log_{ts}.json")
    }

    # Full train/test CSV (SMILES + y + features)
    train_df.to_csv(paths["train_full"], index=False)
    test_df.to_csv(paths["test_full"], index=False)

    # Feature matrices (SMILES + features)
    train_df[["SMILES"] + feature_cols].to_csv(paths["train_X"], index=False)
    test_df[["SMILES"] + feature_cols].to_csv(paths["test_X"], index=False)

    # Target vectors (SMILES + y)
    train_df[["SMILES", y_col]].rename(columns={y_col: "y"}).to_csv(paths["train_y"], index=False)
    test_df[["SMILES", y_col]].rename(columns={y_col: "y"}).to_csv(paths["test_y"], index=False)

    # Feature list JSON
    with open(paths["features"], "w") as f:
        json.dump(feature_cols, f, indent=2)

    # Report JSON
    with open(paths["log"], "w") as f:
        json.dump(report, f, indent=2)

    return paths


# ---------- Find latest featurize output ----------
def _find_latest_featurize_output(results_dir="results") -> str:
    """Finds the most recent featurize output CSV file."""
    files = glob.glob(os.path.join(results_dir, "featurize_output_*.csv"))
    if not files:
        raise FileNotFoundError(f"No featurized data found in '{results_dir}'. Run featurization first.")
    return max(files, key=os.path.getmtime)


# ---------- Scaffold split helpers ----------
def _generate_scaffolds(smiles_list):
    """Generates Murcko scaffolds from a list of SMILES strings."""
    from rdkit import Chem
    from rdkit.Chem.Scaffolds import MurckoScaffold
    scaffolds = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol:
            scaffold = MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False)
        else:
            scaffold = None
        scaffolds.append(scaffold)
    return scaffolds


def stratified_scaffold_split(df: pd.DataFrame, smiles_col: str, y_col: str,
                              frac_train=0.8, random_state=None):
    """Performs a stratified scaffold split preserving class balance."""
    scaffolds = _generate_scaffolds(df[smiles_col].tolist())
    df = df.copy()
    df["scaffold"] = scaffolds

    scaffold_groups = []
    for scaf, sub_df in df.groupby("scaffold"):
        counts = sub_df[y_col].value_counts(normalize=True).to_dict()
        scaffold_groups.append((scaf, counts, sub_df))

    rng = np.random.default_rng(random_state)
    rng.shuffle(scaffold_groups)
    scaffold_groups.sort(key=lambda x: min(x[1].get(0, 0), x[1].get(1, 0)), reverse=True)

    train_df, test_df = [], []
    train_size = frac_train * len(df)
    current_train = 0

    for _, _, sub_df in scaffold_groups:
        if current_train < train_size:
            train_df.append(sub_df)
            current_train += len(sub_df)
        else:
            test_df.append(sub_df)

    train_df = pd.concat(train_df).drop(columns=["scaffold"])
    test_df = pd.concat(test_df).drop(columns=["scaffold"])
    return train_df, test_df


# ---------- Stratified random split ----------
def stratified_random_split(df: pd.DataFrame, y_col: str,
                            frac_train=0.8, random_state=None):
    """Performs a stratified random split preserving class balance."""
    from sklearn.model_selection import train_test_split
    train_df, test_df = train_test_split(df, train_size=frac_train,
                                         stratify=df[y_col], random_state=random_state)
    return train_df, test_df


# ---------- Main Class ----------
class DataSplitter:
    """Main class for splitting featurized datasets into train/test sets."""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Dictionary containing split parameters:
                - method: "scaffold" or "random"
                - frac_train: Train set fraction (default: 0.8)
                - random_state: Random seed (default: 42)
                - save_results: Save split outputs to disk (default: True)
                - results_dir: Output directory (default: 'results')
        """
        self.config = config
        self.data_train = None
        self.data_test = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.feature_cols = None
        self.report = {}
        self.metadata = {"module": "data_split", "timestamp": datetime.now().isoformat()}

    def run(self, featurized_df: Optional[pd.DataFrame] = None):
        """Executes the train/test splitting process."""
        smiles_col = self.config.get("smiles_col", "SMILES")
        y_col = self.config.get("y_col", "y")
        method = self.config.get("method", "scaffold")
        frac_train = self.config.get("frac_train", 0.8)
        random_state = self.config.get("random_state", 42)
        save_results = self.config.get("save_results", True)
        results_dir = self.config.get("results_dir", "results")

        # Load featurized data if not provided
        if featurized_df is None:
            csv_path = _find_latest_featurize_output(results_dir)
            df = pd.read_csv(csv_path)
            source_file = csv_path
        else:
            df = featurized_df.copy()
            source_file = "provided DataFrame"

        # Ensure no SMILES overlap between train/test
        df = df.drop_duplicates(subset=[smiles_col])

        if method not in ("scaffold", "random"):
            raise ValueError("method must be 'scaffold' or 'random'")
        if smiles_col not in df.columns or y_col not in df.columns:
            raise ValueError(f"df must contain '{smiles_col}' and '{y_col}'")

        # Select split method
        if method == "scaffold":
            if not has_rdkit():
                raise RuntimeError("Scaffold split requires RDKit.")
            train_df, test_df = stratified_scaffold_split(df, smiles_col, y_col, frac_train, random_state)
        else:
            train_df, test_df = stratified_random_split(df, y_col, frac_train, random_state)

        # Feature columns
        feature_cols = [c for c in train_df.columns if c not in [smiles_col, y_col]]
        self.feature_cols = feature_cols

        # Assign X and y
        self.X_train = train_df[feature_cols].values
        self.y_train = train_df[y_col].values
        self.X_test = test_df[feature_cols].values
        self.y_test = test_df[y_col].values

        # Build report
        report = {
            "method": method,
            "frac_train": frac_train,
            "frac_test": 1 - frac_train,
            "n_train": len(train_df),
            "n_test": len(test_df),
            "class_balance": {
                "train": train_df[y_col].value_counts(normalize=True).to_dict(),
                "test": test_df[y_col].value_counts(normalize=True).to_dict(),
            },
            "source_file": source_file,
            "n_features": len(feature_cols)
        }

        if save_results:
            paths = _save_splits(train_df, test_df, feature_cols, y_col, report, results_dir=results_dir)
            report["saved_paths"] = paths

        self.data_train = train_df
        self.data_test = test_df
        self.report = report

        # Summary
        print("\n=== Data Split Summary ===")
        print(f"Source file: {report['source_file']}")
        print(f"Method: {report['method']}")
        print(f"Train size: {report['n_train']} ({report['frac_train']*100:.1f}%)")
        print(f"Test size: {report['n_test']} ({report['frac_test']*100:.1f}%)")
        print(f"Train class balance: {report['class_balance']['train']}")
        print(f"Test class balance: {report['class_balance']['test']}")
        print(f"Number of features: {report['n_features']}")
        print("==================================\n")

        return self
