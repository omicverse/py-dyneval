# py-dyneval

A **Python port of [dynverse/dyneval](https://github.com/dynverse/dyneval)** (Saelens et al. *Nat Biotechnol* 2019) — the metric library used by the dynbenchmark trajectory inference benchmark.

- Pure NumPy / SciPy / NetworkX / scikit-learn — no R
- Depends on `pydynwrap` for trajectory wrappers + geodesic distances
- 8/14 dyneval metric IDs ported in v0.1

## Install

```bash
pip install pydyneval-bio   # pulls in pydynwrap-bio
```

## Quick-start

```python
import pydyneval as de
import pydynwrap as dw
import numpy as np

gold = dw.wrap_data([f"c{i}" for i in range(30)])
gold = dw.add_branch_trajectory(gold,
    pseudotime=np.tile(np.linspace(0,1,10), 3),
    branch=np.repeat(["A","B","C"], 10))

pred = dw.wrap_data([f"c{i}" for i in range(30)])
pred = dw.add_branch_trajectory(pred,
    pseudotime=np.tile(np.linspace(0,1,10), 3),
    branch=np.repeat(["A","B","C"], 10))

scores = de.calculate_metrics(gold, pred)
print(scores)
#    correlation  him  edge_flip  isomorphic  F1_branches  F1_milestones ...
# 0          1.0  1.0        1.0         1.0          1.0           1.0
```

## Function map

| Python | R `dyneval::` | Status |
|---|---|---|
| `calculate_metrics(dataset, model, metrics=...)` | same | ✅ |
| `calculate_him(net1, net2)` | same | ✅ (Lorentzian inline) |
| `calculate_edge_flip(net1, net2)` | same | ✅ (Jaccard surrogate) |
| `calculate_isomorphic(net1, net2)` | (implicit) | ✅ |
| `calculate_mapping_branches(dataset, prediction)` | same | ✅ |
| `calculate_mapping_milestones(dataset, prediction)` | same | ✅ |
| `calculate_featureimp_cor(dataset, model)` | same | ✅ |
| `calculate_featureimp_enrichment` (ks / wilcox) | — | ⏳ v0.2 |
| `calculate_position_predict` (rf_mse / rf_rsq / lm_*) | — | ⏳ v0.2 |
| `evaluate_ti_method` | — | ⛔ v0.3+ (depends on TI runners) |

## R parity on canonical fixture (3-branch, 30 cells × 50 genes)

| Metric | R | Py | |Δ| |
|---|---|---|---|
| correlation | 0.9812 | 0.9813 | 0.0001 |
| him | 1.0 | 1.0 | 0.0 |
| edge_flip | 1.0 | 1.0 | 0.0 |
| isomorphic | 1.0 | 1.0 | 0.0 |
| F1_branches | 1.0 | 1.0 | 0.0 |
| F1_milestones | 0.6667 | 0.6667 | 0.0 |
| featureimp_cor | 0.9622 | 0.9005 | 0.0617 |
| featureimp_wcor | 0.9664 | 0.9548 | 0.0115 |

`featureimp_*` differs slightly because of Random Forest non-determinism
between R `randomForest` and sklearn `RandomForestRegressor` — both
implement Breiman 2001 with the same hyperparameters; tree-splitting RNG
differs.

## Citation

> Saelens, W. et al. *A comparison of single-cell trajectory inference methods.* Nat Biotechnol 37, 547–554 (2019).

## License

MIT.
