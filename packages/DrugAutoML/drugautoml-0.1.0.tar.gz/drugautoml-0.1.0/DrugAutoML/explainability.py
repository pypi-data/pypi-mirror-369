"""
Explainability (TEST-only) — Bit Galleries + SHAP for DrugAutoML
================================================================

What this module does
---------------------
• Computes SHAP values on the TEST split using the *base* estimator
  (pre-calibration) to get meaningful feature contributions.
• Produces **bit galleries**: for the most important ECFP (Morgan) bits
  (by global |SHAP|), show how the SAME bit appears across multiple TEST
  molecules, with clear, filled highlights.
• Saves global SHAP plots (beeswarm + classic bar + signed bar).

Expected inputs under `results/` (produced by previous modules)
---------------------------------------------------------------
- final_model_*.pkl           # calibrated model bundle (from ModelFinalization)
- split_test_X_*.csv          # TEST features (must include 'SMILES' + feature columns)
- split_features_*.json       # ordered feature names used by the model (post constant-drop)
- featurize_log_*.json        # featurizer config: radius, nbits, use_counts

Outputs (created)
-----------------
- results/explain_<TS>_figs/
    - bit_<ID>_gallery.png         # grid: SAME bit highlighted across molecules
    - bit_gallery_index.csv        # which bits were rendered + file paths
    - shap_summary_beeswarm.png
    - shap_summary_bar.png
    - shap_signed_bar.png

Python API
----------
config = {
    "results_dir": "results",
    "sample_limit": 1000,            # None for full TEST
    "gallery_top_bits": 6,           # how many bits to visualize as galleries
    "gallery_examples_per_bit": 6,   # molecules per bit
    "gallery_cols": 3,
    "gallery_sub_img": [280, 240],   # per-cell size (w, h)
    "bw_base": True,                 # black&white skeleton (no heteroatom colors)
    "hide_atom_labels": True,        # hide element labels (“O”, “N”, “HN”…)
    "highlight_rgb": [0.0, 0.75, 1.0], # turquoise highlight color (0..1)
    "highlight_radius": 0.60,        # highlight bubble radius (filled)
    "bond_line_width": 1.0,          # thinner skeleton
    "also_beeswarm": True,           # save global SHAP plots
    "random_seed": 42
}
Explainability(config).run()
"""

from __future__ import annotations
import os, glob, json, re, warnings
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import numpy as np
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt
from scipy.special import expit
from sklearn.calibration import CalibratedClassifierCV

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit import RDLogger
RDLogger.DisableLog("rdApp.error")
warnings.filterwarnings("ignore")


# ----------------------------- IO helpers ----------------------------- #
def _find_latest(results_dir: str, pattern: str) -> str:
    files = glob.glob(os.path.join(results_dir, pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' in '{results_dir}'.")
    return max(files, key=os.path.getmtime)

def _load_model_bundle(results_dir: str):
    """Return (calibrated_model, algo_name)."""
    pkl_path = _find_latest(results_dir, "final_model_*.pkl")
    bundle = joblib.load(pkl_path)
    return bundle["model"], bundle.get("algo", "UNKNOWN")

def _load_schema(results_dir: str) -> List[str]:
    with open(_find_latest(results_dir, "split_features_*.json")) as f:
        return json.load(f)

def _load_testX(results_dir: str) -> pd.DataFrame:
    return pd.read_csv(_find_latest(results_dir, "split_test_X_*.csv"))

def _load_featurize_cfg(results_dir: str) -> Dict:
    with open(_find_latest(results_dir, "featurize_log_*.json")) as f:
        return json.load(f)


# ----------------------------- SHAP helpers ---------------------------- #
def _predict_proba(model, X: np.ndarray) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)[:, 1]
    if hasattr(model, "decision_function"):
        return expit(model.decision_function(X))
    raise ValueError("Model has neither predict_proba nor decision_function.")

def _base_for_shap(model):
    """Unwrap CalibratedClassifierCV to its base estimator for SHAP."""
    if isinstance(model, CalibratedClassifierCV):
        try:
            return model.calibrated_classifiers_[0].estimator
        except Exception:
            return model
    return model

def _pick_explainer(base_model, X_bg: np.ndarray):
    """Prefer TreeExplainer, then LinearExplainer, else KernelExplainer."""
    try:
        return shap.TreeExplainer(base_model, feature_perturbation="interventional"), "tree"
    except Exception:
        pass
    try:
        return shap.LinearExplainer(base_model, X_bg, feature_dependence="independent"), "linear"
    except Exception:
        pass
    bg = shap.sample(X_bg, 200) if X_bg.shape[0] > 200 else X_bg
    f = base_model.predict_proba if hasattr(base_model, "predict_proba") else base_model.decision_function
    return shap.KernelExplainer(f, bg), "kernel"

def _make_explanation(shap_vals, X, feature_names, explainer):
    """Return a shap.Explanation robustly (works with old/new SHAP versions)."""
    if isinstance(shap_vals, shap.Explanation):
        return shap_vals
    base = getattr(explainer, "expected_value", 0.0)
    try:
        base = np.asarray(base).ravel()
        base = float(base[1] if base.size > 1 else base[0])
    except Exception:
        base = float(base)
    base_values = np.full(X.shape[0], base, dtype=float)
    return shap.Explanation(values=shap_vals, base_values=base_values, data=X, feature_names=feature_names)

def _save_shap_summary_robust(explanation, X, feature_names, out_dir: str):
    """Save beeswarm + classic bar (works across SHAP versions)."""
    # beeswarm
    try:
        shap.plots.beeswarm(explanation, show=False)
    except Exception:
        shap.summary_plot(explanation.values, X, feature_names=feature_names, show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "shap_summary_beeswarm.png"), dpi=300)
    plt.close()

    # classic bar (mean|SHAP|)
    try:
        shap.plots.bar(explanation, show=False)
    except Exception:
        shap.summary_plot(explanation.values, X, feature_names=feature_names, plot_type="bar", show=False)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "shap_summary_bar.png"), dpi=300)
    plt.close()

def _save_shap_signed_bar(shap_vals, feature_names, out_path, top_n: int = 12):
    """Signed mean(SHAP) per feature to show direction (green + / purple −)."""
    vals = np.asarray(shap_vals)            # [n_samples, n_features]
    mean_abs = np.mean(np.abs(vals), axis=0)
    mean_signed = np.mean(vals, axis=0)

    idx = np.argsort(mean_abs)[-top_n:][::-1]
    feats = [feature_names[i] for i in idx]
    signed = mean_signed[idx]
    colors = ['#1b9e77' if s >= 0 else '#8e44ad' for s in signed]  # green / purple

    plt.figure(figsize=(7.5, 5.0))
    y = np.arange(len(idx))
    plt.barh(y, signed, color=colors)
    plt.yticks(y, feats)
    plt.xlabel('mean(SHAP value) (signed)')
    plt.axvline(0, color='k', lw=0.6)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


# --------------------- RDKit drawing (compatibility) ------------------- #
def _draw_molecules_compat(
    d,
    mols,
    highlight_lists=None,
    legends=None,
    highlight_atom_colors=None,
    highlight_atom_radii=None,
):
    """
    RDKit DrawMolecules signature varies by version.
    This wrapper tries keyword, semi-positional and positional forms.

    - highlight_lists       : [[atom_idx, ...], ...]
    - highlight_atom_colors : [ {atom_idx: (r,g,b)}, ... ]
    - highlight_atom_radii  : [ {atom_idx: radius}, ... ]
    """
    n = len(mols)
    if highlight_lists is None:
        highlight_lists = [()] * n
    if legends is None:
        legends = [""] * n
    if highlight_atom_colors is None:
        highlight_atom_colors = [{}] * n
    if highlight_atom_radii is None:
        highlight_atom_radii = [{}] * n

    hl = [tuple(int(a) for a in lst) for lst in highlight_lists]

    # New-style keywords
    try:
        return d.DrawMolecules(
            mols,
            highlightAtomLists=hl,
            highlightAtomColors=highlight_atom_colors,
            highlightAtomRadii=highlight_atom_radii,
            legends=legends,
        )
    except Exception:
        pass
    # Semi-positional (legends second)
    try:
        return d.DrawMolecules(mols, legends, hl, None, None, None, None, highlight_atom_radii)
    except Exception:
        pass
    # Oldest positional
    return d.DrawMolecules(mols, hl, None, highlight_atom_colors, None, highlight_atom_radii, None, legends)


# ------------------------- Bit gallery utilities ----------------------- #
def _bit_id_from_name(name: str) -> Optional[int]:
    m = re.match(r"ECFP(\d+)$", str(name), re.IGNORECASE)
    return int(m.group(1)) - 1 if m else None

def _collect_atoms_for_bit_in_mol(mol, bit_id: int, radius: int, nbits: int) -> List[int]:
    """Return atom indices that constitute the given ECFP bit for a molecule."""
    bitInfo = {}
    _ = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits, bitInfo=bitInfo)
    if bit_id not in bitInfo:
        return []
    atoms = set()
    for atom_idx, rad in bitInfo[bit_id]:
        env = Chem.FindAtomEnvironmentOfRadiusN(mol, rad, atom_idx)
        atoms.add(atom_idx)
        for bnd_id in env:
            b = mol.GetBondWithIdx(bnd_id)
            atoms.add(b.GetBeginAtomIdx())
            atoms.add(b.GetEndAtomIdx())
    return sorted(atoms)

def _save_bit_gallery(
    bit_id: int,
    label: str,
    mols: List,
    highlight_lists: List[List[int]],
    outfile: str,
    cols: int = 3,
    sub_img: Tuple[int, int] = (280, 240),
    bw: bool = True,
    hide_atom_labels: bool = True,
    highlight_rgb: Tuple[float, float, float] = (0.0, 0.75, 1.0),  # turquoise
    highlight_radius: float = 0.60,                                 # filled circles
    bond_line_width: float = 1.0,                                   # thinner skeleton
):
    """
    Grid image: same ECFP bit across multiple molecules (bonds-only + clear highlights).
    """
    if not mols:
        return

    # draw without explicit H so “HN” labels disappear
    mols_draw = [Chem.RemoveHs(m) for m in mols]

    rows = (len(mols_draw) + cols - 1) // cols
    w, h = cols * sub_img[0], rows * sub_img[1]
    d = rdMolDraw2D.MolDraw2DCairo(w, h, sub_img[0], sub_img[1])
    opts = d.drawOptions()

    # BW palette + thin bonds
    if bw:
        try:
            opts.useBWAtomPalette = True
        except Exception:
            for Z in range(1, 119):
                opts.atomColourPalette[Z] = (0, 0, 0)
    try:
        opts.bondLineWidth = float(bond_line_width)
    except Exception:
        pass

    # hide element labels entirely (bonds-only look)
    if hide_atom_labels:
        try:
            for idx in range(1000):  # more than enough for typical molecules
                opts.atomLabels[idx] = ""
        except Exception:
            pass

    # filled, circular highlights (so they really pop)
    for attr in ("fillHighlights", "atomHighlightsAreCircles"):
        try:
            setattr(opts, attr, True)
        except Exception:
            pass

    # per-cell color & radius dicts
    color = tuple(highlight_rgb)
    col_dicts = [{a: color for a in atoms} for atoms in highlight_lists]
    rad_dicts = [{a: float(highlight_radius) for a in atoms} for atoms in highlight_lists]

    legends = [""] * len(mols_draw)  # clean grid (no subtitles per cell)
    _draw_molecules_compat(
        d,
        mols_draw,
        highlight_lists=highlight_lists,
        legends=legends,
        highlight_atom_colors=col_dicts,
        highlight_atom_radii=rad_dicts,
    )
    d.FinishDrawing()
    with open(outfile, "wb") as f:
        f.write(d.GetDrawingText())

def _select_top_bits_by_global_abs_shap(feature_names, shap_values, top_bits: int):
    """Return a list of (feat_idx, bit_id, importance) sorted by importance desc."""
    glob_importance = np.mean(np.abs(shap_values), axis=0)  # [n_features]
    cand = []
    for i, name in enumerate(feature_names):
        bit_id = _bit_id_from_name(name)
        if bit_id is not None:
            cand.append((i, bit_id, float(glob_importance[i])))
    cand.sort(key=lambda x: x[2], reverse=True)
    return cand[:top_bits]


# ------------------------------ Public API ----------------------------- #
class Explainability:
    """
    TEST-only explainability focused on **BIT GALLERIES** (plus global SHAP plots).

    Config keys:
      - results_dir: str = "results"
      - sample_limit: Optional[int] = None        # cap #samples for SHAP
      - gallery_top_bits: int = 6
      - gallery_examples_per_bit: int = 6
      - gallery_cols: int = 3
      - gallery_sub_img: List[int] = [280, 240]
      - bw_base: bool = True
      - hide_atom_labels: bool = True
      - highlight_rgb: List[float] = [0.0, 0.75, 1.0]
      - highlight_radius: float = 0.60
      - bond_line_width: float = 1.0
      - also_beeswarm: bool = True
      - random_seed: int = 42
    """
    def __init__(self, config: Dict):
        self.cfg = {
            "results_dir": "results",
            "sample_limit": None,
            "gallery_top_bits": 6,
            "gallery_examples_per_bit": 6,
            "gallery_cols": 3,
            "gallery_sub_img": [280, 240],
            "bw_base": True,
            "hide_atom_labels": True,
            "highlight_rgb": [0.0, 0.75, 1.0],
            "highlight_radius": 0.60,
            "bond_line_width": 1.0,
            "also_beeswarm": True,
            "random_seed": 42,
            **(config or {}),
        }
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fig_dir = os.path.join(self.cfg["results_dir"], f"explain_{ts}_figs")
        os.makedirs(self.fig_dir, exist_ok=True)

    def run(self):
        results_dir = self.cfg["results_dir"]

        # 1) Load artifacts
        model, algo = _load_model_bundle(results_dir)
        feature_names = _load_schema(results_dir)
        testX = _load_testX(results_dir)
        feat_cfg = _load_featurize_cfg(results_dir)
        radius = int(feat_cfg.get("radius", 2))
        nbits = int(feat_cfg.get("nbits", 2048))

        # 2) Build TEST matrix (labels not needed)
        if "SMILES" not in testX.columns:
            raise KeyError("split_test_X_*.csv must include a 'SMILES' column.")
        X_df = testX[["SMILES"] + feature_names].copy()
        X = X_df[feature_names].values.astype(float)

        # Optional cap for SHAP compute
        limit = self.cfg.get("sample_limit")
        if limit and len(X_df) > limit:
            X_df = X_df.iloc[:limit].copy()
            X = X[:limit]

        # 3) SHAP on the base estimator
        base_model = _base_for_shap(model)
        explainer, expl_kind = _pick_explainer(base_model, X)
        shap_vals_raw = explainer.shap_values(X)
        if isinstance(shap_vals_raw, list):
            shap_vals_raw = shap_vals_raw[1] if len(shap_vals_raw) > 1 else shap_vals_raw[0]
        exp = _make_explanation(shap_vals_raw, X, feature_names, explainer)

        # 4) Global SHAP plots
        if self.cfg.get("also_beeswarm", True):
            _save_shap_summary_robust(exp, X, feature_names, self.fig_dir)
            _save_shap_signed_bar(
                exp.values, feature_names,
                os.path.join(self.fig_dir, "shap_signed_bar.png"),
                top_n=12
            )

        # 5) Select top bits by global |SHAP|
        top_bits = _select_top_bits_by_global_abs_shap(
            feature_names, exp.values, int(self.cfg["gallery_top_bits"])
        )

        # 6) For each bit, sample molecules containing that bit and render a gallery
        rng = np.random.default_rng(int(self.cfg.get("random_seed", 42)))
        smiles_list = X_df["SMILES"].tolist()
        examples_per_bit = int(self.cfg["gallery_examples_per_bit"])
        cols = int(self.cfg["gallery_cols"])
        sub_w, sub_h = map(int, self.cfg["gallery_sub_img"])
        bw = bool(self.cfg["bw_base"])
        hide_labels = bool(self.cfg["hide_atom_labels"])
        hl_rgb = tuple(float(x) for x in self.cfg.get("highlight_rgb", [0.0, 0.75, 1.0]))
        hl_rad = float(self.cfg.get("highlight_radius", 0.60))
        bond_w = float(self.cfg.get("bond_line_width", 1.0))

        index_rows = []
        for rank, (feat_idx, bit_id, importance) in enumerate(top_bits, start=1):
            mols, hilists = [], []
            order = np.arange(len(smiles_list))
            rng.shuffle(order)

            for idx in order:
                smi = smiles_list[idx]
                mol = Chem.MolFromSmiles(smi)
                if not mol:
                    continue
                atoms = _collect_atoms_for_bit_in_mol(mol, bit_id, radius, nbits)
                if atoms:
                    mols.append(mol)
                    hilists.append(atoms)
                    if len(mols) >= examples_per_bit:
                        break

            if not mols:
                print(f"[bit {bit_id}] no examples found in TEST molecules")
                continue

            label = f"Morgan{bit_id} (|SHAP| rank {rank})"
            outfile = os.path.join(self.fig_dir, f"bit_{bit_id}_gallery.png")
            _save_bit_gallery(
                bit_id, label, mols, hilists, outfile,
                cols=cols, sub_img=(sub_w, sub_h), bw=bw,
                hide_atom_labels=hide_labels,
                highlight_rgb=hl_rgb, highlight_radius=hl_rad, bond_line_width=bond_w
            )

            index_rows.append({
                "rank": rank,
                "feature_index": feat_idx,
                "bit_id": bit_id,
                "importance_mean_abs_shap": float(importance),
                "gallery_path": outfile,
            })

        # Save an index CSV for convenience
        if index_rows:
            pd.DataFrame(index_rows).to_csv(
                os.path.join(self.fig_dir, "bit_gallery_index.csv"), index=False
            )

        print("\n=== Explainability — BIT GALLERIES (TEST only) ===")
        print(f"Algorithm: {algo} | SHAP explainer: {expl_kind}")
        print(f"Top bits rendered: {len(index_rows)}  "
              f"(requested {self.cfg['gallery_top_bits']}, per bit {examples_per_bit} molecules)")
        print(f"Figures dir: {self.fig_dir}")
        print("Index CSV:  bit_gallery_index.csv")
        print("===============================================\n")

        return self
