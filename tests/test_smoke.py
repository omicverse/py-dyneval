"""Smoke tests for pydyneval."""
import sys
from pathlib import Path
import numpy as np
import pandas as pd
_PORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PORT))
import pydyneval as de
import pydynwrap as dw


def _make_traj():
    t = dw.wrap_data([f"c{i}" for i in range(30)])
    t = dw.add_branch_trajectory(t,
        pseudotime=np.tile(np.linspace(0,1,10), 3),
        branch=np.repeat(["A","B","C"], 10))
    t.waypoint_cells = list(t.cell_ids)
    return t


def test_import():
    assert de.__version__ == "0.1.0"


def test_metrics_perfect():
    """Perfect prediction (gold == pred) → all metrics 1.0."""
    g = _make_traj(); p = _make_traj()
    res = de.calculate_metrics(g, p, metrics=["correlation","him","edge_flip","isomorphic",
                                                "F1_branches","F1_milestones"])
    for col in res.columns:
        assert res[col].iloc[0] >= 0.99, f"{col} = {res[col].iloc[0]}"


def test_metrics_null_model():
    """model=None → all metrics 0."""
    g = _make_traj()
    res = de.calculate_metrics(g, None, metrics=["correlation","him","edge_flip","isomorphic",
                                                  "F1_branches","F1_milestones"])
    for col in res.columns:
        assert res[col].iloc[0] == 0.0


def test_calculate_him_identical():
    mn = pd.DataFrame({"from":["A","A"],"to":["B","C"],"length":[1.0,1.0]})
    assert de.calculate_him(mn, mn) == 1.0


def test_calculate_edge_flip_perfect():
    mn = pd.DataFrame({"from":["A","A"],"to":["B","C"],"length":[1.0,1.0]})
    assert de.calculate_edge_flip(mn, mn) == 1.0
