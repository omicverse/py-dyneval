"""End-to-end R parity test."""
import json, os, subprocess, sys
from pathlib import Path
import pytest

_PORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PORT))


@pytest.fixture(scope="module")
def metrics_pair():
    DATA = _PORT/"data"; DATA.mkdir(exist_ok=True)
    ref, cand = DATA/"reference_metrics.json", DATA/"candidate_metrics.json"
    if not ref.exists():
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = ("/share/software/user/open/netcdf/4.8.1/lib:"
                                   + env.get("LD_LIBRARY_PATH",""))
        subprocess.run(["conda","run","-p",
                        os.environ.get("R_TEST_ENV","/scratch/users/steorra/env/CMAP"),
                        "Rscript", str(_PORT/"tests"/"r_reference_driver.R"), str(DATA)],
                       check=True, env=env, capture_output=True)
    if not cand.exists():
        subprocess.run([sys.executable, str(_PORT/"tests"/"_run_candidate.py"), str(DATA)],
                       check=True, capture_output=True)
    return json.loads(ref.read_text()), json.loads(cand.read_text())


@pytest.mark.parametrize("metric,tol", [
    ("correlation",     0.01),
    ("him",             0.01),
    ("edge_flip",       0.01),
    ("isomorphic",      0.001),
    ("F1_branches",     0.01),
    ("F1_milestones",   0.01),
    ("featureimp_cor",  0.10),  # RF nondeterminism
    ("featureimp_wcor", 0.10),
])
def test_metric_parity(metrics_pair, metric, tol):
    r, p = metrics_pair
    rv = r.get(metric, float("nan"))
    pv = p.get(metric, float("nan"))
    delta = abs(rv - pv)
    print(f"  {metric:24s} R={rv:.4f}  Py={pv:.4f}  |Δ|={delta:.4f}  (tol {tol})")
    assert delta <= tol, f"{metric}: R={rv:.4f} Py={pv:.4f} |Δ|={delta:.4f} > {tol}"
