"""Boolean: are the two milestone graphs isomorphic? Returns 0.0 / 1.0."""

from __future__ import annotations
import networkx as nx
import pandas as pd


def calculate_isomorphic(net1, net2) -> float:
    def _graph(net):
        G = nx.Graph()
        for _, e in pd.DataFrame(net).iterrows():
            G.add_edge(e["from"], e["to"])
        return G
    G1, G2 = _graph(net1), _graph(net2)
    return 1.0 if nx.is_isomorphic(G1, G2) else 0.0
