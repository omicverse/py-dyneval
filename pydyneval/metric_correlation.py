"""Spearman correlation between gold and pred geodesic-distance matrices."""

from __future__ import annotations
import numpy as np
from scipy.stats import spearmanr


def calculate_correlation(gold_gd, pred_gd) -> float:
    """Spearman on flattened upper triangle of two cell-cell distance matrices.

    Args:
        gold_gd: DataFrame or ndarray (n_waypoints × n_cells) for gold trajectory.
        pred_gd: same shape for prediction.

    Returns:
        max(0, Spearman r) ∈ [0, 1]; 0 if either input is constant.
    """
    A = np.asarray(gold_gd, dtype=np.float64)
    B = np.asarray(pred_gd, dtype=np.float64)
    # Replace Inf with .Machine$double.xmax-equivalent (≈ 1e308)
    A = np.where(np.isinf(A), 1e308, A)
    B = np.where(np.isinf(B), 1e308, B)
    if A.shape != B.shape:
        return 0.0
    a = A.ravel(); b = B.ravel()
    if len(np.unique(a)) == 1 or len(np.unique(b)) == 1:
        return 0.0
    r, _ = spearmanr(a, b)
    if not np.isfinite(r):
        return 0.0
    return float(max(0.0, r))
