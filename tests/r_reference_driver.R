#!/usr/bin/env Rscript
# R reference: compute calculate_metrics on a (gold, perturbed-pred) pair
suppressPackageStartupMessages({
  library(dyneval); library(dynwrap); library(dplyr); library(tibble)
  library(jsonlite)
})
args <- commandArgs(trailingOnly = TRUE)
out_dir <- args[1]
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

set.seed(42)

# Gold: 3-branch tent trajectory, 30 cells
make_traj <- function(branch_order, perturb_amount = 0) {
  cell_ids <- paste0("c", 1:30)
  milestone_network <- tribble(
    ~from, ~to, ~length, ~directed,
    "M0",  "MA", 1.0, TRUE,
    "M0",  "MB", 1.0, TRUE,
    "M0",  "MC", 1.0, TRUE,
  )
  pcts <- seq(0.05, 0.95, length.out = 10)
  if (perturb_amount > 0) pcts <- pcts + rnorm(10, 0, perturb_amount)
  pcts <- pmin(pmax(pcts, 0), 1)
  progressions <- bind_rows(
    tibble(cell_id = paste0("c", 1:10),  from = "M0", to = branch_order[1], percentage = pcts),
    tibble(cell_id = paste0("c", 11:20), from = "M0", to = branch_order[2], percentage = pcts),
    tibble(cell_id = paste0("c", 21:30), from = "M0", to = branch_order[3], percentage = pcts),
  )
  ds <- wrap_data(id = "fixture", cell_ids = cell_ids)
  ds <- add_trajectory(ds,
                        milestone_ids = c("M0","MA","MB","MC"),
                        milestone_network = milestone_network,
                        progressions = progressions)
  ds <- dynwrap::add_cell_waypoints(ds, num_cells_selected = length(cell_ids))
  # Generate fake expression with branch-correlated signal
  set.seed(42)
  expr <- matrix(rpois(30 * 50, 2), nrow = 30, ncol = 50)
  rownames(expr) <- cell_ids; colnames(expr) <- paste0("g", 1:50)
  pt_vec <- progressions$percentage
  names(pt_vec) <- progressions$cell_id
  for (i in 1:10) expr[, i] <- expr[, i] + rpois(30, lambda = 5 * pt_vec[cell_ids])
  ds <- add_expression(ds, counts = expr, expression = log2(expr + 1))
  ds$pseudotime <- setNames(pt_vec[cell_ids], cell_ids)
  ds
}

gold <- make_traj(c("MA","MB","MC"), 0)
pred <- make_traj(c("MA","MB","MC"), 0.05)   # slight perturbation

res <- calculate_metrics(gold, pred, metrics = c(
  "correlation","him","edge_flip","isomorphic",
  "F1_branches","F1_milestones",
  "featureimp_cor","featureimp_wcor"
))
write_json(as.list(res), file.path(out_dir, "reference_metrics.json"),
           auto_unbox = TRUE, digits = 10)

# Also dump the gold + pred so Py side uses the same fixture
dump_traj <- function(t) list(
  cell_ids = t$cell_ids,
  milestone_ids = t$milestone_ids,
  milestone_network = t$milestone_network,
  progressions = t$progressions,
  milestone_percentages = t$milestone_percentages,
  pseudotime = if (!is.null(t$pseudotime)) as.list(t$pseudotime) else NULL,
  expression = if (!is.null(t$expression)) as.matrix(t$expression) else NULL,
  feature_ids = colnames(t$expression)
)
write_json(list(gold = dump_traj(gold), pred = dump_traj(pred)),
           file.path(out_dir, "reference_traj.json"),
           auto_unbox = TRUE, digits = 10)
cat("R reference metrics:\n"); print(res)
