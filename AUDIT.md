# AUDIT — py-dyneval

R exports per `dyneval::NAMESPACE`: 5 (calculate_metrics, calculate_him,
calculate_edge_flip, calculate_featureimp_cor, calculate_featureimp_enrichment).
Metric IDs: 14.

## Metric ID coverage

| Metric | Python | Status |
|---|---|---|
| `correlation` | calculate_correlation (in `calculate_metrics`) | ✅ |
| `him` | calculate_him | ✅ |
| `edge_flip` | calculate_edge_flip | ✅ (Jaccard surrogate) |
| `isomorphic` | calculate_isomorphic | ✅ |
| `F1_branches` | calculate_mapping_branches | ✅ |
| `recovery_branches` | same | ✅ |
| `relevance_branches` | same | ✅ |
| `F1_milestones` | calculate_mapping_milestones | ✅ |
| `recovery_milestones` | same | ✅ |
| `relevance_milestones` | same | ✅ |
| `featureimp_cor` | calculate_featureimp_cor | ✅ |
| `featureimp_wcor` | same | ✅ |
| `featureimp_ks` | — | ⏳ v0.2 |
| `featureimp_wilcox` | — | ⏳ v0.2 |
| `rf_mse / rf_rsq / rf_nmse / lm_*` | — | ⏳ v0.2 (position_predict) |

## NAMESPACE exports

| R | Python | Status |
|---|---|---|
| `calculate_metrics` | same | ✅ |
| `calculate_him` | same | ✅ |
| `calculate_edge_flip` | same | ✅ |
| `calculate_featureimp_cor` | same | ✅ |
| `calculate_featureimp_enrichment` | — | ⏳ v0.2 |
| `evaluate_ti_method` | — | ⛔ v0.3+ (depends on dynwrap method runners) |
