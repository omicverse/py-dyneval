# Discovery — py-dyneval

## 1. Is the target already ported?

`gh repo view omicverse/py-dyneval` → not found at port start.

## 2. R dep audit + reuse

| R dep | Status |
|---|---|
| dynwrap | ✅ omicverse/py-dynwrap v0.1.0 — direct dep |
| dynfeature | ⏳ inline RF importance via sklearn (not a separate port; ~20 LOC) |
| dynutils | ⛔ inline distance helpers |
| netdist | ⛔ inline HIM via numpy eigvalsh + Lorentzian rho |
| testthat | n/a |

## 3. v0.1 scope

dyneval has 5 R exports + 14 metric IDs. v0.1 implements the 8 most-used:
- `correlation` (Spearman on geodesics)
- `him` (Hamming-Ipsen-Mikhailov)
- `edge_flip` (Jaccard on edge sets)
- `isomorphic` (binary)
- `F1_branches` / `recovery_branches` / `relevance_branches`
- `F1_milestones` / `recovery_milestones` / `relevance_milestones`
- `featureimp_cor` / `featureimp_wcor`

Deferred: `featureimp_ks` / `featureimp_wilcox` (enrichment tests),
`rf_mse / rf_rsq / lm_*` (position prediction). These are minor and
require less.

## 4. Decision

Proceed with full port; algorithm class: deterministic + RF-stochastic for
featureimp. Parity gates:
- correlation, him, edge_flip, isomorphic, F1_branches/milestones: |Δ| < 0.01
- featureimp_cor / wcor: |Δ| < 0.10 (RandomForest non-determinism)
