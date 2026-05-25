"""F1_branches / F1_milestones — Jaccard mapping between two cell groupings."""

from __future__ import annotations
from typing import Callable
import numpy as np
import pandas as pd

import pydynwrap as dw


def _harmonic_mean(*xs):
    xs = [x for x in xs if x is not None and not np.isnan(x)]
    if not xs or any(x == 0 for x in xs):
        return 0.0
    return float(len(xs) / sum(1.0 / x for x in xs))


def _calculate_mapping(dataset, prediction, grouping: str) -> dict:
    if dataset is None or prediction is None:
        return {"recovery": 0.0, "relevance": 0.0, "F1": 0.0}

    if grouping == "branches":
        g_data = dw.group_onto_trajectory_edges(dataset)
        g_pred = dw.group_onto_trajectory_edges(prediction)
    elif grouping == "milestones":
        g_data = dw.group_onto_nearest_milestones(dataset)
        g_pred = dw.group_onto_nearest_milestones(prediction)
    else:
        raise ValueError(f"unknown grouping: {grouping}")

    df = pd.DataFrame({"cell_id": list(g_data.index), "group_data": g_data.values,
                       "group_pred": g_pred.reindex(g_data.index).values})
    df = df.dropna(subset=["group_data", "group_pred"])
    if df.empty:
        return {"recovery": 0.0, "relevance": 0.0, "F1": 0.0}

    # Jaccard per (group_data, group_pred) pair
    inter = df.groupby(["group_data", "group_pred"]).size().rename("intersection").reset_index()
    n_data = df.groupby("group_data").size().rename("n_data").reset_index()
    n_pred = df.groupby("group_pred").size().rename("n_pred").reset_index()
    j = (inter.merge(n_data, on="group_data")
              .merge(n_pred, on="group_pred"))
    j["jaccard"] = j["intersection"] / (j["n_data"] + j["n_pred"] - j["intersection"])

    # Per data-group: best matching predicted-group (recovery)
    recoveries = (j.sort_values("jaccard", ascending=False)
                   .groupby("group_data").head(1)["jaccard"])
    # Per predicted-group: best matching data-group (relevance)
    relevances = (j.sort_values("jaccard", ascending=False)
                   .groupby("group_pred").head(1)["jaccard"])
    rec = float(np.nan_to_num(recoveries.mean()))
    rel = float(np.nan_to_num(relevances.mean()))
    return {"recovery": rec, "relevance": rel, "F1": _harmonic_mean(rec, rel)}


def calculate_mapping_branches(dataset, prediction) -> dict:
    out = _calculate_mapping(dataset, prediction, "branches")
    return {f"{k}_branches": v for k, v in out.items()}


def calculate_mapping_milestones(dataset, prediction) -> dict:
    out = _calculate_mapping(dataset, prediction, "milestones")
    return {f"{k}_milestones": v for k, v in out.items()}
