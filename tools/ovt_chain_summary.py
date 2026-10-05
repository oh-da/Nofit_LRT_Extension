"""Collect the OVT parameter-set reruns of the step-31 / step-33 chain into one table.

Usage:  python3 tools/ovt_chain_summary.py [--out Output/ovt_research/chain_results.csv]
Needs numpy. Reads Output/skims/ (the default set) and every Output/skims/ovt_<tag>/ written by
Mode_skims_and_flow_comparison.ipynb with OVT_TAG set, plus Output/mode_choice[/ovt_<tag>]/lambda_summary.csv
written by Mode_choice_person_level.ipynb with SKIM_DIR set (docs/OVT_WEIGHTS_RESEARCH_PLAN.md §5.6).

For each set it reports the parameters, the step-31 capture in its five λ / premium cases, step 33's
re-estimated λ (M1 point and 95 % interval) on that set's generalized cost, and the capture at the
re-estimated λ (λ_T = 2·λ, the central case's ratio). The capture at the re-estimated λ is computed here
from the set's saved skims with the step-31 cell-8 formula; the function must reproduce the set's own
committed central capture to under one trip, otherwise the script stops.
"""
import argparse, csv, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UG, GR = "lrt_all_underground", "lrt_all_ground"
CENTRAL = "central (λ 0.03, λ_T 0.06, premium 5)"


def read_mat(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    cols = [int(c) for c in rows[0][1:]]
    idx = [int(r[0]) for r in rows[1:]]
    M = np.full((len(idx), len(cols)), np.nan)
    for i, r in enumerate(rows[1:]):
        for j, v in enumerate(r[1:]):
            if v.strip() not in ("", "nan", "NaN"):
                M[i, j] = float(v)
    return idx, M


def read_flow(path, areas):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    cols = [int(c) for c in rows[0][1:]]
    d = {(int(r[0]), cols[j]): float(v) for r in rows[1:] for j, v in enumerate(r[1:]) if v != ""}
    return np.array([[d.get((o, dd), 0.0) for dd in areas] for o in areas])


class SkimSet:
    def __init__(self, sk):
        self.sk = sk
        self.areas, self.gc_bus = read_mat(sk / "skim_bus_gc.csv")
        A = len(self.areas)
        self.gc = {m: read_mat(sk / f"skim_{m}_gc.csv")[1] for m in (UG, GR)}
        self.off = ~np.eye(A, dtype=bool)
        self.T_car = read_flow(ROOT / "Output/corridor_v2/car_2022_area_v2.csv", self.areas) * self.off
        self.T_tr = read_flow(ROOT / "Output/corridor_v2/transit_2022_area_v2.csv", self.areas) * self.off
        self.n_pair = self.T_car + self.T_tr
        self.params = {r["parameter"]: r["value"] for r in csv.DictReader(open(sk / "ovt_parameters.csv", encoding="utf-8"))} if (sk / "ovt_parameters.csv").exists() else {}
        self.cases = {(r["scenario"], r["case"]): r for r in csv.DictReader(open(sk / "lrt_capture_scenarios.csv", encoding="utf-8"))}

    def capture(self, sc, lam, lt, prem=5.0, K_EB=20.0):
        T_car, T_tr, n_pair = self.T_car, self.T_tr, self.n_pair
        p0 = T_tr[n_pair > 0].sum() / n_pair[n_pair > 0].sum()
        S_raw = np.where(n_pair > 0, T_tr / np.where(n_pair > 0, n_pair, 1), np.nan)
        S_piv = np.where(n_pair > 0, (n_pair * np.nan_to_num(S_raw) + K_EB * p0) / (n_pair + K_EB), np.nan)
        dL = self.gc[sc] - prem - self.gc_bus
        avail = np.isfinite(dL) & self.off & (n_pair > 0)
        dLz = np.nan_to_num(dL)
        P_L = np.where(avail, 1 / (1 + np.exp(lt * dLz)), 0.0)
        delta = np.where(avail, -(1 / lt) * np.log1p(np.exp(-lt * dLz)), 0.0)
        S_new = np.where(avail, S_piv * np.exp(-lam * delta) / (S_piv * np.exp(-lam * delta) + 1 - S_piv), S_piv)
        growth = np.where(avail, np.nan_to_num(S_new) / np.where(np.nan_to_num(S_piv) > 0, S_piv, 1), 1.0)
        return float((np.minimum(T_tr * growth, n_pair) * P_L).sum())

    def validate(self):
        worst = 0.0
        for sc, lab in [(UG, "LRT all underground"), (GR, "LRT all ground")]:
            r = self.cases[(lab, CENTRAL)]
            worst = max(worst, abs(self.capture(sc, float(r["λ"]), float(r["λ_T"]), float(r["LRT premium"])) - float(r["LRT trips 06–09"])))
        if worst >= 1.0:
            sys.exit(f"{self.sk}: capture formula does not reproduce lrt_capture_scenarios.csv (worst {worst:.1f} trips)")
        return worst


def lambda_rows(mc):
    f = mc / "lambda_summary.csv"
    if not f.exists():
        return None
    return {r["model"].split(":")[0]: r for r in csv.DictReader(open(f, encoding="utf-8"))}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(ROOT / "Output/ovt_research/chain_results.csv"))
    a = ap.parse_args()
    sets = [("default", ROOT / "Output/skims", ROOT / "Output/mode_choice")]
    for d in sorted((ROOT / "Output/skims").glob("ovt_*")):
        if d.is_dir():
            sets.append((d.name[4:], d, ROOT / "Output/mode_choice" / d.name))
    base = SkimSet(ROOT / "Output/skims")
    base_ug = float(base.cases[("LRT all underground", CENTRAL)]["LRT trips 06–09"])
    base_gr = float(base.cases[("LRT all ground", CENTRAL)]["LRT trips 06–09"])
    PAR = ["W_WALK", "W_WALK_LRT", "W_WAIT", "TRANSFER_PEN", "BRT_LRT_TRANSFER_PEN", "STATION_ACCESS_UG", "STATION_ACCESS_GR"]
    out = []
    for tag, sk, mc in sets:
        s = SkimSet(sk)
        worst = s.validate()
        lam = lambda_rows(mc)
        row = {"set": tag, **{p: s.params.get(p, "") for p in PAR}}
        for sc, lab, b in [(UG, "LRT all underground", base_ug), (GR, "LRT all ground", base_gr)]:
            c = float(s.cases[(lab, CENTRAL)]["LRT trips 06–09"])
            key = "ug" if sc == UG else "gr"
            row[f"{key}_central"] = round(c)
            row[f"{key}_central_pct_vs_default"] = round(100 * (c / b - 1), 1)
            row[f"{key}_low_lambda"] = round(float(s.cases[(lab, "low λ (0.02 / 0.03, premium 5)")]["LRT trips 06–09"]))
            row[f"{key}_high_lambda"] = round(float(s.cases[(lab, "high λ (0.05 / 0.10, premium 5)")]["LRT trips 06–09"]))
            row[f"{key}_no_premium"] = round(float(s.cases[(lab, "no premium (λ central, premium 0)")]["LRT trips 06–09"]))
            row[f"{key}_premium_10"] = round(float(s.cases[(lab, "premium 10 (λ central)")]["LRT trips 06–09"]))
        if lam:
            m1 = lam["M1"]
            l, lo, hi = float(m1["lambda"]), float(m1["lo95"]), float(m1["hi95"])
            row.update({"lambda_M1": round(l, 4), "lambda_M1_lo95": round(lo, 4), "lambda_M1_hi95": round(hi, 4),
                        "lambda_M3": round(float(lam["M3"]["lambda"]), 4), "lambda_M4": round(float(lam["M4"]["lambda"]), 4)})
            for sc, key in [(UG, "ug"), (GR, "gr")]:
                row[f"{key}_at_lambda_M1"] = round(s.capture(sc, l, 2 * l))
                row[f"{key}_at_lambda_M1_lo95"] = round(s.capture(sc, max(lo, 0.005), 2 * max(lo, 0.005)))
                row[f"{key}_at_lambda_M1_hi95"] = round(s.capture(sc, hi, 2 * hi))
        else:
            row.update({k: "" for k in ("lambda_M1", "lambda_M1_lo95", "lambda_M1_hi95", "lambda_M3", "lambda_M4", "ug_at_lambda_M1", "ug_at_lambda_M1_lo95", "ug_at_lambda_M1_hi95", "gr_at_lambda_M1", "gr_at_lambda_M1_lo95", "gr_at_lambda_M1_hi95")})
        row["replication_worst_diff_trips"] = round(worst, 2)
        out.append(row)
        print(f"{tag:<22s} walk {row['W_WALK']:>4} / LRT {row['W_WALK_LRT']:>4}  wait {row['W_WAIT']:>4}  transfer {row['TRANSFER_PEN']:>4}  BRT-LRT {row['BRT_LRT_TRANSFER_PEN']:>4}  access UG/GR {row['STATION_ACCESS_UG']}/{row['STATION_ACCESS_GR']}"
              f" | UG {row['ug_central']:>5} ({row['ug_central_pct_vs_default']:+.1f}%)  GR {row['gr_central']:>5} ({row['gr_central_pct_vs_default']:+.1f}%)"
              + (f" | λ_M1 {row['lambda_M1']} [{row['lambda_M1_lo95']}, {row['lambda_M1_hi95']}] -> UG {row['ug_at_lambda_M1']} GR {row['gr_at_lambda_M1']}" if lam else " | step 33 not run"))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader(); w.writerows(out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
