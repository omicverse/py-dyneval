"""Run pydyneval on the same trajectory pair the R reference saved."""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
_PORT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PORT))
import pydyneval as de
import pydynwrap as dw


def _load_traj(d):
    t = dw.wrap_data(d["cell_ids"], id="fixture")
    mn = pd.DataFrame(d["milestone_network"])
    mn["length"] = mn["length"].astype(float)
    mn["directed"] = mn["directed"].astype(bool)
    prog = pd.DataFrame(d["progressions"])
    prog["percentage"] = prog["percentage"].astype(float)
    t = dw.add_trajectory(t, milestone_ids=d["milestone_ids"],
                            milestone_network=mn, progressions=prog)
    t.waypoint_cells = list(t.cell_ids)
    if d.get("pseudotime"):
        pt = pd.Series(d["pseudotime"]).reindex(t.cell_ids).astype(float)
        dw.add_pseudotime(t, pt)
    if d.get("expression"):
        expr = np.asarray(d["expression"], dtype=np.float64)
        dw.add_expression(t, counts=expr, expression=expr, feature_ids=d.get("feature_ids"))
    return t


def main():
    out_dir = Path(sys.argv[1])
    out_dir.mkdir(exist_ok=True, parents=True)
    traj_dump = json.loads((out_dir/"reference_traj.json").read_text())
    gold = _load_traj(traj_dump["gold"])
    pred = _load_traj(traj_dump["pred"])
    res = de.calculate_metrics(gold, pred, metrics=de.METRICS)
    out_dict = {k: float(res[k].iloc[0]) for k in res.columns}
    (out_dir/"candidate_metrics.json").write_text(json.dumps(out_dict))
    print("Py candidate:", out_dict)


if __name__ == "__main__":
    main()
