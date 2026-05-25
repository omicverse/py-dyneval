"""pydyneval — pure-Python port of dynverse/dyneval.

The metric library used by the dynbenchmark trajectory inference comparison
(Saelens et al. Nat Biotechnol 2019).

v0.1 implements the 8 metrics directly invoked by `calculate_metrics`:
- correlation       (Spearman on geodesic distances)
- him               (Hamming-Ipsen-Mikhailov on milestone graphs)
- edge_flip         (Hamming on matched adjacencies)
- isomorphic        (binary graph isomorphism)
- F1_branches       (Jaccard F1 on cell→edge groups)
- F1_milestones     (Jaccard F1 on cell→milestone groups)
- featureimp_cor    (Pearson on per-gene RF importances)
- featureimp_wcor   (importance-weighted Pearson)

Also exports `calculate_metrics(dataset, model, metrics=...)` matching R.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .metric_correlation import calculate_correlation
from .metric_him import calculate_him
from .metric_flip import calculate_edge_flip
from .metric_isomorphic import calculate_isomorphic
from .metric_mapping import (
    calculate_mapping_branches,
    calculate_mapping_milestones,
)
from .metric_featureimp import calculate_featureimp_cor
from .calculate_metrics import calculate_metrics, METRICS

__all__ = [
    "calculate_metrics",
    "METRICS",
    "calculate_correlation",
    "calculate_him",
    "calculate_edge_flip",
    "calculate_isomorphic",
    "calculate_mapping_branches",
    "calculate_mapping_milestones",
    "calculate_featureimp_cor",
    "__version__",
]
