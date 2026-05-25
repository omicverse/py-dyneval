"""featureimp_cor / featureimp_wcor — Pearson on per-gene RF importances.

R uses `dynfeature::calculate_overall_feature_importance(traj, expression)`.
That function fits a Random Forest regressing the trajectory pseudotime
onto each gene, returning gene_id, importance. We do the same with sklearn.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def _feature_importance(traj, expression: np.ndarray) -> pd.Series:
    """Per-gene Random Forest importance regressing pseudotime onto each gene."""
    if traj.pseudotime is None:
        # Use mean of milestone percentages as a proxy
        from pydynwrap import group_onto_nearest_milestones
        groups = group_onto_nearest_milestones(traj).astype(str)
        # Map groups to integers
        codes = groups.astype("category").cat.codes.values.astype(float)
        y = codes
    else:
        y = np.asarray(traj.pseudotime.fillna(0.0).values, dtype=np.float64)
    X = np.asarray(expression, dtype=np.float64)
    if X.shape[0] != len(y):
        # Try transposing — expression might be (genes, cells)
        if X.shape[1] == len(y):
            X = X.T
    rf = RandomForestRegressor(n_estimators=50, n_jobs=-1, random_state=42,
                                max_depth=8)
    rf.fit(X, y)
    feature_ids = traj.feature_ids or [f"gene_{i}" for i in range(X.shape[1])]
    return pd.Series(rf.feature_importances_, index=feature_ids[:X.shape[1]],
                     name="importance")


def calculate_featureimp_cor(dataset, prediction, expression_source=None) -> dict:
    """1:1 port of dyneval::calculate_featureimp_cor.

    Returns dict with `featureimp_cor` (Pearson r) and `featureimp_wcor`
    (importance-weighted Pearson) ∈ [0, 1] (negative clamped to 0).
    """
    if prediction is None:
        return {"featureimp_cor": 0.0, "featureimp_wcor": 0.0}

    if expression_source is None:
        expr = dataset.expression if dataset.expression is not None else dataset.counts
    elif isinstance(expression_source, str):
        expr = getattr(dataset, expression_source, None)
    elif callable(expression_source):
        expr = expression_source()
    else:
        expr = expression_source
    if expr is None:
        return {"featureimp_cor": 0.0, "featureimp_wcor": 0.0}

    imp_d = _feature_importance(dataset, expr)
    imp_p = _feature_importance(prediction, expr)
    common = sorted(set(imp_d.index) & set(imp_p.index))
    if len(common) < 2:
        return {"featureimp_cor": 0.0, "featureimp_wcor": 0.0}
    a = imp_d.reindex(common).values; b = imp_p.reindex(common).values

    # Standard Pearson
    if np.std(a) < 1e-12 or np.std(b) < 1e-12:
        cor = 0.0
    else:
        cor = float(max(0.0, np.corrcoef(a, b)[0, 1]))

    # Weighted Pearson — weights = gold importances (clipped non-negative)
    w = np.maximum(a, 0); w_sum = w.sum()
    if w_sum < 1e-12:
        wcor = 0.0
    else:
        mu_a = np.sum(w * a) / w_sum
        mu_b = np.sum(w * b) / w_sum
        cov = np.sum(w * (a - mu_a) * (b - mu_b)) / w_sum
        var_a = np.sum(w * (a - mu_a) ** 2) / w_sum
        var_b = np.sum(w * (b - mu_b) ** 2) / w_sum
        denom = np.sqrt(var_a * var_b)
        wcor = 0.0 if denom < 1e-12 else float(max(0.0, cov / denom))

    return {"featureimp_cor": float(cor), "featureimp_wcor": float(wcor)}
