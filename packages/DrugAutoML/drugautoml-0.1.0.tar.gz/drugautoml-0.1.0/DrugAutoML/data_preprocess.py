"""
Data Preprocessing Module for DrugAutoML
----------------------------------------

This module handles:
1. Reading input bioactivity datasets from multiple file formats.
2. Cleaning and standardizing SMILES strings.
3. Converting activity values into binary classification labels
   (based on pChEMBL cutoffs or explicit binary labels).
4. Generating processing reports and saving outputs.

Dependencies:
- pandas
- rdkit (optional, for SMILES standardization)
"""

from __future__ import annotations
from typing import Optional, Tuple, Dict, Any
import os, json, re
from datetime import datetime
import pandas as pd

# ===== RDKit imports =====
try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import rdMolStandardize, SaltRemover
    RDLogger.DisableLog("rdApp.error")
    RDKit_AVAILABLE = True
except ImportError:
    RDKit_AVAILABLE = False


# ---------- File Reader ----------
def _smart_read_table(path: str) -> pd.DataFrame:
    """Reads tabular data from various file formats and normalizes column names."""
    if path.lower().endswith((".parquet", ".pq")):
        df = pd.read_parquet(path)
    else:
        try:
            df = pd.read_csv(path, sep=None, engine="python", encoding="utf-8-sig")
        except Exception:
            for sep in [",", "\t", ";", "|"]:
                try:
                    df = pd.read_csv(path, sep=sep, encoding="utf-8-sig")
                    break
                except Exception:
                    continue
            else:
                df = pd.read_csv(path, sep=None, engine="python", on_bad_lines="skip", encoding="utf-8-sig")
    df.rename(columns=lambda c: c.replace("\ufeff", "").strip(), inplace=True)
    return df


# ---------- Molecule Standardization ----------
def _standardize_mol_rdms(smi: str):
    """Standardizes a molecule using RDKit's rdMolStandardize module."""
    mol = Chem.MolFromSmiles(str(smi))
    if mol is None:
        return None
    clean = rdMolStandardize.Cleanup(mol)
    parent = rdMolStandardize.FragmentParent(clean)
    uncharged = rdMolStandardize.Uncharger().uncharge(parent)
    can_taut = rdMolStandardize.TautomerEnumerator().Canonicalize(uncharged)
    return can_taut


def _standardize_mol_fallback(smi: str):
    """Fallback standardization if rdMolStandardize fails."""
    mol = Chem.MolFromSmiles(str(smi), sanitize=True)
    if mol is None:
        return None
    mol = SaltRemover.SaltRemover().StripMol(mol, dontRemoveEverything=True)
    Chem.SanitizeMol(mol)
    return mol


def _standardize_to_smiles(smi: str) -> Optional[str]:
    """Standardizes SMILES string and returns canonical SMILES."""
    mol_std = None
    if RDKit_AVAILABLE:
        try:
            mol_std = _standardize_mol_rdms(smi)
        except Exception:
            try:
                mol_std = _standardize_mol_fallback(smi)
            except Exception:
                mol_std = None
    return Chem.MolToSmiles(mol_std, canonical=True) if mol_std else None


# ---------- SMILES Cleaning ----------
def _clean_smiles(df: pd.DataFrame, smiles_col: str, standardize: bool) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """Removes missing/invalid SMILES and optionally standardizes them."""
    stats = {"missing_smiles": 0, "invalid_smiles": 0, "standardized": 0, "standardization_failed": 0}
    before = len(df)
    mask_nonempty = df[smiles_col].notna() & (df[smiles_col].astype(str).str.strip() != "")
    stats["missing_smiles"] = int(before - mask_nonempty.sum())
    df = df.loc[mask_nonempty].copy()

    if not RDKit_AVAILABLE:
        return df.reset_index(drop=True), stats

    keep_idx, new_smiles = [], []
    for i, smi in enumerate(df[smiles_col].astype(str)):
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            stats["invalid_smiles"] += 1
            continue

        smi2 = None
        if standardize:
            smi2 = _standardize_to_smiles(smi)
            if smi2:
                stats["standardized"] += 1
            else:
                stats["standardization_failed"] += 1

        if not smi2:
            try:
                smi2 = Chem.MolToSmiles(mol, canonical=True)
            except Exception:
                smi2 = smi

        new_smiles.append(smi2)
        keep_idx.append(i)

    out = df.iloc[keep_idx].copy().reset_index(drop=True)
    out[smiles_col] = new_smiles
    return out, stats


# ---------- Binary Mapping ----------
def _map_binary_keywords(series: pd.Series) -> pd.Series:
    """Maps text-based binary activity labels to integers."""
    positive_labels = ["1", "true", "yes", "pos", "positive", "active"]
    negative_labels = ["0", "false", "no", "neg", "negative", "inactive", "not active", "no activity"]
    s = series.astype(str).str.strip().str.lower()

    def f(x: str):
        if any(re.fullmatch(k, x) for k in positive_labels):
            return 1
        if any(re.fullmatch(k, x) for k in negative_labels):
            return 0
        return float("nan")

    return s.map(f)


# ---------- Save Outputs ----------
def _save_outputs(df: pd.DataFrame, report: Dict[str, Any], module_name: str, results_dir: str) -> Dict[str, str]:
    """Saves processed data and preprocessing report to disk."""
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_path = os.path.join(results_dir, f"{module_name}_output_{ts}.csv")
    log_path = os.path.join(results_dir, f"{module_name}_log_{ts}.json")
    df.to_csv(data_path, index=False)
    with open(log_path, "w") as f:
        json.dump(report, f, indent=2)
    return {"data_path": data_path, "log_path": log_path}


# ---------- Main Class ----------
class DataPreprocessor:
    """Main class for preprocessing bioactivity datasets."""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Dictionary containing preprocessing parameters.
        """
        self.config = config
        self.data = None
        self.report = {}
        self.metadata = {"module": "data_preprocess", "timestamp": datetime.now().isoformat()}

    def run(self):
        """Executes preprocessing workflow."""
        path = self.config["path"]
        smiles_col = self.config["smiles_col"]
        activity_col = self.config["activity_col"]
        activity_type = self.config["activity_type"]
        active_cutoff = self.config.get("active_cutoff")
        inactive_cutoff = self.config.get("inactive_cutoff")
        standardize_smiles = self.config.get("standardize_smiles", True)
        save_results = self.config.get("save_results", True)
        results_dir = self.config.get("results_dir", "results")

        df0 = _smart_read_table(path)
        if smiles_col not in df0.columns:
            raise ValueError(f"SMILES column '{smiles_col}' not found.")
        if activity_col not in df0.columns:
            raise ValueError(f"Activity column '{activity_col}' not found.")

        n_rows_in = int(len(df0))
        mask_missing_act = df0[activity_col].isna() | (df0[activity_col].astype(str).str.strip() == "")
        n_missing_activity = int(mask_missing_act.sum())

        df = df0[[smiles_col, activity_col]].copy()
        df.rename(columns={smiles_col: "SMILES", activity_col: "ACT"}, inplace=True)
        df, smi_stats = _clean_smiles(df, "SMILES", standardize=standardize_smiles)

        report: Dict[str, Any] = {
            "schema": activity_type.lower(),
            "active_cutoff": active_cutoff,
            "inactive_cutoff": inactive_cutoff,
            "n_rows_in": n_rows_in,
            **smi_stats,
            "missing_activity": n_missing_activity,
        }

        mask_act = df["ACT"].notna() & (df["ACT"].astype(str).str.strip() != "")
        df = df.loc[mask_act].copy()
        report["dropped_rows_missing_activity"] = int(~mask_act.sum())

        if activity_type.lower() == "binary":
            y_map = _map_binary_keywords(df["ACT"])
            keep = ~y_map.isna()
            report["dropped_rows_unmapped_binary"] = int(y_map.isna().sum())
            df = df.loc[keep].copy()
            y_map = y_map.loc[keep].astype(int)
            df["ACT_BIN"] = y_map
            n_before = len(df)
            df = df.groupby("SMILES", as_index=False).agg({"ACT_BIN": "max"})
            report["duplicates_removed"] = n_before - len(df)
            out = pd.DataFrame({"SMILES": df["SMILES"], "y": df["ACT_BIN"].astype(int)})

        elif activity_type.lower() == "px":
            if active_cutoff is None or inactive_cutoff is None:
                raise ValueError("For 'px' activity_type, both active_cutoff and inactive_cutoff must be provided.")
            s = pd.to_numeric(df["ACT"], errors="coerce")
            keep_num = s.notna()
            report["dropped_rows_non_numeric_px"] = int((~keep_num).sum())
            df = df.loc[keep_num].copy()
            df["ACT_NUM"] = s.loc[keep_num].copy()
            n_before = len(df)
            df = df.groupby("SMILES", as_index=False).agg({"ACT_NUM": "median"})
            report["duplicates_removed"] = n_before - len(df)
            n_gray_dropped = 0
            if inactive_cutoff < active_cutoff:
                keep = (df["ACT_NUM"] >= active_cutoff) | (df["ACT_NUM"] <= inactive_cutoff)
                n_gray_dropped = int((~keep).sum())
                df = df.loc[keep].copy()
            y = (df["ACT_NUM"] >= active_cutoff).astype(int)
            out = pd.DataFrame({"SMILES": df["SMILES"], "y": y})
            report["dropped_rows_gray_zone"] = n_gray_dropped
        else:
            raise ValueError("activity_type must be 'px' or 'binary'")

        report.update({
            "n_rows_out": len(out),
            "n_active": int(out["y"].sum()),
            "n_inactive": len(out) - int(out["y"].sum()),
        })

        if save_results:
            paths = _save_outputs(out, report, module_name=self.metadata["module"], results_dir=results_dir)
            report.update({"saved_data_path": paths["data_path"], "saved_log_path": paths["log_path"]})

        # --- PRINT SUMMARY ---
        print("\n=== Data Preprocessing Summary ===")
        print(f"Initial molecules: {report['n_rows_in']}")
        print(f"Missing SMILES removed: {report['missing_smiles']}")
        print(f"Invalid SMILES removed: {report['invalid_smiles']}")
        print(f"Standardization applied: {report['standardized']}")
        print(f"Standardization failed: {report['standardization_failed']}")
        print(f"Missing activity removed: {report['missing_activity']}")
        if activity_type.lower() == "binary":
            print(f"Unmapped binary labels removed: {report.get('dropped_rows_unmapped_binary', 0)}")
        elif activity_type.lower() == "px":
            print(f"Non-numeric activities removed: {report.get('dropped_rows_non_numeric_px', 0)}")
            print(f"Gray zone removed: {report.get('dropped_rows_gray_zone', 0)}")
        print(f"Duplicates removed: {report['duplicates_removed']}")
        print(f"Final dataset size: {report['n_rows_out']}")
        print(f"Active count: {report['n_active']}")
        print(f"Inactive count: {report['n_inactive']}")
        print("==================================\n")

        self.data = out
        self.report = report
        return self
