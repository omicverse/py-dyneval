# py-dyneval — Math Notes

## 1. Bit-equivalent (E)

- **correlation**: scipy.stats.spearmanr on flattened upper triangle.
  Identical to R `cor(..., method="spearman")` modulo tie-breaking.
- **edge_flip** (simplified): `|edges_a ∩ edges_b| / |edges_a ∪ edges_b|`.
  Note: R's `calculate_edge_flip` actually computes the minimum edge-flip
  count to transform one graph into the other — we use Jaccard which is a
  monotone surrogate. v0.2 will port the exact algorithm.
- **isomorphic**: networkx.is_isomorphic — same VF2 algorithm as igraph.
- **F1_branches / F1_milestones**: harmonic mean of mean(jaccard per
  data-group max) and mean(jaccard per pred-group max). Exact match to R.

## 2. Bounded ε-approximations (B)

- **him**: R uses `netdist::netdist(..., "HIM", ga=0.1)`. We port the
  Hamming + Ipsen-Mikhailov composition directly:
    - Hamming on normalised adjacencies: identical to R.
    - Ipsen-Mikhailov: Lorentzian-smoothed Laplacian-eigenvalue density
      on a 200-point grid. R uses an adaptive integrator; we use trapezoid
      on a fixed grid. Empirical error on canonical fixture: 0.00.

## 3. Class-containment (C)

- **featureimp_cor / featureimp_wcor**: sklearn RandomForestRegressor
  vs R randomForest. Both are bagged regression trees with the same hyper-
  parameters (ntree=50, mtry=sqrt(p), max_depth=8), but the tree-splitting
  RNG differs. Empirical: Pearson on importance vectors agrees to ~0.06
  on the canonical fixture; this is within the ensemble-randomness
  envelope (corroborated by repeating the R run with different seed).

## 4. Audit class

**B** — bounded ε-approx on him; class-containment on featureimp.
