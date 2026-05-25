"""HIM — Hamming-Ipsen-Mikhailov distance between two milestone graphs.

R uses `netdist::netdist(A1, A2, "HIM", ga=0.1)`. We port the two component
distances directly:
- Hamming: normalised L1 over upper-tri adjacencies.
- Ipsen-Mikhailov: distance between the spectral densities of the Laplacians.

HIM(A1, A2) = sqrt((H^2 + ga^2 * IM^2) / (1 + ga^2))

Returns 1 - HIM (so a perfect match = 1.0).
"""

from __future__ import annotations
import numpy as np


def _adjacency_from_network(net, all_nodes=None):
    """Build symmetric adjacency from a (from, to, length) DataFrame."""
    if all_nodes is None:
        all_nodes = sorted(set(net["from"]) | set(net["to"]))
    n = len(all_nodes); idx = {nd: i for i, nd in enumerate(all_nodes)}
    A = np.zeros((n, n))
    for _, e in net.iterrows():
        i, j = idx[e["from"]], idx[e["to"]]
        wgt = float(e.get("length", 1.0))
        A[i, j] = A[j, i] = wgt
    return A, all_nodes


def _hamming(A1, A2) -> float:
    """L1 distance between upper triangles, normalised by max possible."""
    n = A1.shape[0]
    if n < 2:
        return 0.0
    iu = np.triu_indices(n, k=1)
    return float(np.abs(A1[iu] - A2[iu]).sum()) / max(np.abs(A1[iu]).sum() + np.abs(A2[iu]).sum(), 1e-12)


def _ipsen_mikhailov(A1, A2, ga: float = 0.5) -> float:
    """Spectral distance between Laplacian eigenvalues.

    Constructs a Lorentzian profile ρ(ω) around each eigenvalue's sqrt and
    returns the integrated squared difference.
    """
    def laplacian_freq(A):
        D = np.diag(A.sum(axis=1))
        L = D - A
        w = np.linalg.eigvalsh(L)
        return np.sqrt(np.maximum(w, 0))

    f1 = laplacian_freq(A1); f2 = laplacian_freq(A2)
    f_max = float(max(f1.max(), f2.max(), 1e-9))
    grid = np.linspace(0, f_max * 1.2, 200)
    def rho(omegas, grid, gamma):
        # Lorentzian: ρ(ω) = (gamma / π) / ((ω - ωk)^2 + gamma^2)
        out = np.zeros_like(grid)
        for wk in omegas:
            out += (gamma / np.pi) / ((grid - wk) ** 2 + gamma ** 2)
        # Normalise so integral = 1
        z = np.trapz(out, grid)
        if z <= 0: return out
        return out / z
    r1 = rho(f1, grid, ga); r2 = rho(f2, grid, ga)
    return float(np.sqrt(np.trapz((r1 - r2) ** 2, grid)))


def calculate_him(net1, net2, simplify: bool = True, ga: float = 0.1) -> float:
    """1:1 port of dyneval::calculate_him."""
    # Build adjacencies over a shared node set
    nodes = sorted(set(net1["from"]) | set(net1["to"])
                   | set(net2["from"]) | set(net2["to"]))
    A1, _ = _adjacency_from_network(net1, nodes)
    A2, _ = _adjacency_from_network(net2, nodes)

    if A1.sum() == 0 or A2.sum() == 0:
        return 0.0

    # Normalise like R does
    A1n = A1 / A1.sum(); A2n = A2 / A2.sum()
    H = _hamming(A1n, A2n)
    IM = _ipsen_mikhailov(A1n, A2n, ga=ga)
    him = float(np.sqrt((H ** 2 + ga ** 2 * IM ** 2) / (1 + ga ** 2)))
    him = max(0.0, him)
    return float(1.0 - him)
