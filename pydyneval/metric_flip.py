"""Edge flip — minimum number of edge flips to transform one graph into the other.

dyneval::calculate_edge_flip is a sophisticated algorithm. v0.1 uses a
simplified version: fraction of edges in the symmetric difference of the
two matched adjacencies. Returns 1 - that fraction.
"""

from __future__ import annotations
import numpy as np
import pandas as pd


def calculate_edge_flip(net1, net2) -> float:
    """Fraction of edges shared, after node-set alignment.

    1.0 means the two graphs share every edge; 0.0 means no overlap.
    """
    if isinstance(net1, pd.DataFrame): n1 = net1
    else: n1 = pd.DataFrame(net1, columns=["from","to","length"])
    if isinstance(net2, pd.DataFrame): n2 = net2
    else: n2 = pd.DataFrame(net2, columns=["from","to","length"])

    edges1 = set(zip(n1["from"], n1["to"])) | set(zip(n1["to"], n1["from"]))
    edges2 = set(zip(n2["from"], n2["to"])) | set(zip(n2["to"], n2["from"]))

    if not edges1 and not edges2:
        return 1.0
    if not edges1 or not edges2:
        return 0.0

    intersection = edges1 & edges2
    union = edges1 | edges2
    return float(len(intersection) / len(union))
