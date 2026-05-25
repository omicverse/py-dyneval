"""Entry point — calculate_metrics(dataset, model, metrics=...)."""

from __future__ import annotations
from typing import Iterable, Optional, Union, Callable

import numpy as np
import pandas as pd

import pydynwrap as dw

from .metric_correlation import calculate_correlation
from .metric_him import calculate_him
from .metric_flip import calculate_edge_flip
from .metric_isomorphic import calculate_isomorphic
from .metric_mapping import calculate_mapping_branches, calculate_mapping_milestones
from .metric_featureimp import calculate_featureimp_cor


METRICS = [
    "correlation", "him", "edge_flip", "isomorphic",
    "F1_branches", "recovery_branches", "relevance_branches",
    "F1_milestones", "recovery_milestones", "relevance_milestones",
    "featureimp_cor", "featureimp_wcor",
]


def _ensure_waypoints(traj):
    if traj is None: return traj
    if not dw.is_wrapper_with_waypoint_cells(traj):
        dw.add_cell_waypoints(traj, n_waypoints=min(100, len(traj.cell_ids)))
    return traj


def calculate_metrics(
    dataset,
    model,
    metrics: Optional[Iterable[Union[str, Callable]]] = None,
    expression_source=None,
) -> pd.DataFrame:
    """1:1 port of dyneval::calculate_metrics.

    Args:
        dataset: gold trajectory (pydynwrap.Trajectory).
        model: predicted trajectory; None → all metrics = 0.
        metrics: list of metric_ids to compute (default: all METRICS).
        expression_source: expression matrix or dataset attribute name.

    Returns:
        single-row DataFrame with one column per metric.
    """
    metrics = list(metrics) if metrics is not None else list(METRICS)
    out = {}

    # Ensure waypoints if correlation requested
    if "correlation" in metrics:
        _ensure_waypoints(dataset)
        if model is not None:
            _ensure_waypoints(model)
            # Align cell ids
            if set(model.cell_ids) != set(dataset.cell_ids):
                model.cell_ids = list(dataset.cell_ids)
            waypoints = list(dict.fromkeys(
                (dataset.waypoint_cells or []) + (model.waypoint_cells or [])))
            gold_gd = dw.calculate_geodesic_distances(dataset, waypoints)
            pred_gd = dw.calculate_geodesic_distances(model, waypoints)
            out["correlation"] = calculate_correlation(gold_gd, pred_gd)
        else:
            out["correlation"] = 0.0

    if "him" in metrics:
        out["him"] = (calculate_him(model.milestone_network, dataset.milestone_network)
                      if model is not None else 0.0)

    if "edge_flip" in metrics:
        out["edge_flip"] = (calculate_edge_flip(model.milestone_network,
                                                  dataset.milestone_network)
                            if model is not None else 0.0)

    if "isomorphic" in metrics:
        out["isomorphic"] = (calculate_isomorphic(model.milestone_network,
                                                    dataset.milestone_network)
                              if model is not None else 0.0)

    if any(m in metrics for m in ("F1_branches", "recovery_branches", "relevance_branches")):
        if model is None:
            out["recovery_branches"] = out["relevance_branches"] = out["F1_branches"] = 0.0
        else:
            out.update(calculate_mapping_branches(dataset, model))

    if any(m in metrics for m in ("F1_milestones", "recovery_milestones", "relevance_milestones")):
        if model is None:
            out["recovery_milestones"] = out["relevance_milestones"] = out["F1_milestones"] = 0.0
        else:
            out.update(calculate_mapping_milestones(dataset, model))

    if any(m in metrics for m in ("featureimp_cor", "featureimp_wcor")):
        out.update(calculate_featureimp_cor(dataset, model,
                                             expression_source=expression_source))

    # Custom callable metrics
    for m in metrics:
        if callable(m):
            name = m.__name__
            out[name] = float(m(dataset, model)) if model is not None else 0.0

    return pd.DataFrame([out])
