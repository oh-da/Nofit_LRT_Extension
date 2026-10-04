"""Screen how sensitive the step-31 LRT capture is to the out-of-vehicle (OVT) weights and times.

Usage:  python3 tools/ovt_sensitivity_screen.py [--csv path/to/results.csv]
Needs numpy. Reads committed outputs only (Output/skims/*, Output/corridor_v2/*), writes nothing unless --csv.

Method. Generalized cost is rebuilt from the saved components,
    GC = ivt + w_walk * walk + w_wait * wait + w_transfer * transfers
(the identity holds on every saved skim cell to 0.02 min), with the weights and times varied, and the
pivoted capture of Mode_skims_and_flow_comparison.ipynb (cell 8) is rerun on the 25 V2 areas, 06:00-09:00,
off-diagonal, lambda 0.03, lambda_T 0.06, LRT premium 5, 5-min headway, full bus competition.
The base case must reproduce Output/skims/lrt_capture_scenarios.csv to under 1 trip, otherwise the script stops.

Limits (screening grade). The feeder / gateway path choices of the LRT composites are held at their
base-case values, so a re-optimisation would soften the penalty effects somewhat. "Vertical access" is
added as walk-weighted minutes per LRT trip (both station ends) to the underground case only. The BRT-LRT
penalty is charged once per Metronit feeder leg found in skim_lrt_*_legs.csv. Background and use of the
results: docs/OVT_WEIGHTS_RESEARCH_PLAN.md.
"""
import argparse, csv, re, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SK = ROOT / "Output" / "skims"
MODES = ("car", "bus", "brt", "lrt_all_underground", "lrt_all_ground")
UG, GR = "lrt_all_underground", "lrt_all_ground"


def read_mat(path):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    cols = [int(c) for c in rows[0][1:]]
    idx = [int(r[0]) for r in rows[1:]]
    M = np.full((len(idx), len(cols)), np.nan)
    for i, r in enumerate(rows[1:]):
        for j, v in enumerate(r[1:]):
            if v.strip() not in ("", "nan", "NaN"):
                try:
                    M[i, j] = float(v)
                except ValueError:
                    pass
    return idx, M


def read_flow(path, areas):
    rows = list(csv.reader(open(path, encoding="utf-8")))
    cols = [int(c) for c in rows[0][1:]]
    d = {(int(r[0]), cols[j]): float(v) for r in rows[1:] for j, v in enumerate(r[1:]) if v != ""}
    return np.array([[d.get((o, dd), 0.0) for dd in areas] for o in areas])


class Screen:
    def __init__(self):
        self.areas, _ = read_mat(SK / "skim_car_ivt.csv")
        A = self.A = len(self.areas)
        self.comp = {m: {c: read_mat(SK / f"skim_{m}_{c}.csv")[1] for c in ("ivt", "walk", "wait", "transfers")} for m in MODES}
        legs = {m: list(csv.reader(open(SK / f"skim_{m}_legs.csv", encoding="utf-8")))[1:] for m in (UG, GR)}
        self.legs = {m: [[c.lower() for c in r[1:]] for r in rows] for m, rows in legs.items()}
        self.off = ~np.eye(A, dtype=bool)
        self.T_car = read_flow(ROOT / "Output/corridor_v2/car_2022_area_v2.csv", self.areas) * self.off
        self.T_tr = read_flow(ROOT / "Output/corridor_v2/transit_2022_area_v2.csv", self.areas) * self.off
        self.n_pair = self.T_car + self.T_tr
        self.n_brt = {m: np.array([[len(re.findall("brt", self.legs[m][i][j])) for j in range(A)] for i in range(A)], float) for m in (UG, GR)}

    def gc(self, mode, ww=2.0, wt=2.0, tp=8.0, walk_scale=1.0, extra=0.0, brt_pen=0.0):
        c = self.comp[mode]
        g = c["ivt"] + ww * c["walk"] * walk_scale + wt * c["wait"] + tp * c["transfers"] + extra
        if brt_pen and mode in self.n_brt:
            g = g + brt_pen * self.n_brt[mode]
        return g

    def capture(self, sc, lam=0.03, lt=0.06, prem=5.0, K_EB=20.0, ww=2.0, ww_lrt=None, wt=2.0, tp=8.0, walk_scale=1.0, extra=0.0, brt_pen=0.0):
        """LRT trips 06-09 and the part drawn from car (the notebook's cell 8 logic)."""
        common = dict(wt=wt, tp=tp, walk_scale=walk_scale)
        bus, car = self.gc("bus", ww=ww, **common), self.gc("car", ww=ww, **common)
        lrt = self.gc(sc, ww=ww if ww_lrt is None else ww_lrt, extra=extra, brt_pen=brt_pen, **common)
        T_car, T_tr, n_pair = self.T_car, self.T_tr, self.n_pair
        ok = np.isfinite(bus - car) & (n_pair > 0)
        p0 = T_tr[ok].sum() / n_pair[ok].sum()
        S_raw = np.where(n_pair > 0, T_tr / np.where(n_pair > 0, n_pair, 1), np.nan)
        S_piv = np.where(n_pair > 0, (n_pair * np.nan_to_num(S_raw) + K_EB * p0) / (n_pair + K_EB), np.nan)
        dL = lrt - prem - bus
        avail = np.isfinite(dL) & self.off & (n_pair > 0)
        dLz = np.nan_to_num(dL)
        P_L = np.where(avail, 1 / (1 + np.exp(lt * dLz)), 0.0)
        delta = np.where(avail, -(1 / lt) * np.log1p(np.exp(-lt * dLz)), 0.0)
        S_new = np.where(avail, S_piv * np.exp(-lam * delta) / (S_piv * np.exp(-lam * delta) + 1 - S_piv), S_piv)
        growth = np.where(avail, np.nan_to_num(S_new) / np.where(np.nan_to_num(S_piv) > 0, S_piv, 1), 1.0)
        T_lrt = np.minimum(T_tr * growth, n_pair) * P_L
        return float(T_lrt.sum()), float((T_lrt - T_tr * P_L).sum())


def validate(s):
    ref = [r for r in csv.DictReader(open(SK / "lrt_capture_scenarios.csv", encoding="utf-8"))
           if r["scenario"] in ("LRT all underground", "LRT all ground")]
    worst = 0.0
    print("Validation against Output/skims/lrt_capture_scenarios.csv (LRT trips 06-09):")
    for r in ref:
        sc = UG if r["scenario"] == "LRT all underground" else GR
        mine = s.capture(sc, lam=float(r["λ"]), lt=float(r["λ_T"]), prem=float(r["LRT premium"]))[0]
        d = mine - float(r["LRT trips 06–09"])
        worst = max(worst, abs(d))
        print(f"  {r['scenario']:20s} lambda={r['λ']:<5} premium={r['LRT premium']:<5} committed {r['LRT trips 06–09']:>5}  replicated {mine:8.1f}  diff {d:+.1f}")
    if worst >= 1.0:
        sys.exit(f"Validation FAILED (worst difference {worst:.1f} trips): the skims or flows changed, do not use the screen.")
    print(f"  worst difference {worst:.1f} trips: OK\n")


# (group, [(setting label, kwargs, applies_to_ground)])
SCREENS = [
    ("Walk weight, all modes", [(f"{w}", dict(ww=w), True) for w in (1.5, 2.0, 2.5, 3.0)]),
    ("Walk weight, LRT side only (bus-side 2.0)", [(f"{w}", dict(ww_lrt=w), True) for w in (1.75, 1.5, 2.5)]),
    ("Walk weight, bus side only (LRT-side 2.0)", [("1.5", dict(ww=1.5, ww_lrt=2.0), True)]),
    ("Wait weight, all modes", [(f"{w}", dict(wt=w), True) for w in (1.5, 2.0, 2.5, 3.0)]),
    ("Transfer penalty, min (bus<->LRT, bus-bus)", [(f"{t}", dict(tp=t), True) for t in (5, 8, 10, 12)]),
    ("BRT-LRT transfer penalty, min per Metronit feeder leg (base 0)", [(f"{b}", dict(brt_pen=b), True) for b in (0, 3, 5, 8)]),
    ("Walk time scale (detour 1.3 and 80 m/min)", [(f"x{f}", dict(walk_scale=f), True) for f in (0.85, 1.0, 1.154, 1.2, 1.3)]),
    ("Underground vertical access, min per station end (walk-weighted, underground only)",
     [(f"+{x}", dict(extra=2 * x * 2.0), False) for x in (0, 1, 2, 3)]),
    ("Generalized minutes added to the LRT side", [(f"+{k}", dict(extra=float(k)), True) for k in (0.5, 1, 2, 4)]),
    ("Stacked bounds (screening, not estimates)", [
        ("LRT-favourable: walk 1.5, wait 1.5, transfer 5, walk time x0.85", dict(ww=1.5, wt=1.5, tp=5, walk_scale=0.85), True),
        ("LRT-unfavourable: walk 2.5, wait 2.5, transfer 10, walk time x1.15, BRT-LRT 5",
         dict(ww=2.5, wt=2.5, tp=10, walk_scale=1.154, brt_pen=5), True),
        ("... plus vertical access 2 min per end", dict(ww=2.5, wt=2.5, tp=10, walk_scale=1.154, brt_pen=5, extra=2 * 2 * 2.5), False),
    ]),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--csv", help="also write the results table to this csv")
    a = ap.parse_args()
    s = Screen()
    validate(s)
    base_ug, base_gr = s.capture(UG)[0], s.capture(GR)[0]
    print(f"BASE (lambda 0.03, lambda_T 0.06, premium 5; walk 2 / wait 2 / transfer 8): underground {base_ug:,.0f}   ground {base_gr:,.0f}\n")
    out = []
    for group, items in SCREENS:
        print(f"-- {group}")
        for label, kw, on_ground in items:
            ug = s.capture(UG, **kw)[0]
            gr = s.capture(GR, **kw)[0] if on_ground else None   # None = not applicable to the ground case
            gtxt = f"GR {gr:7,.0f} ({100 * (gr / base_gr - 1):+5.1f}%)" if gr is not None else "GR     n/a"
            print(f"  {label:<76s} UG {ug:7,.0f} ({100 * (ug / base_ug - 1):+5.1f}%)   {gtxt}")
            out.append([group, label, round(ug, 1), round(100 * (ug / base_ug - 1), 2),
                        "" if gr is None else round(gr, 1), "" if gr is None else round(100 * (gr / base_gr - 1), 2)])
        print()
    # context quoted in the research plan
    trunk = np.array([[s.legs[UG][i][j] == "directlrt" for j in range(s.A)] for i in range(s.A)]) & s.off
    w = s.T_tr * trunk

    def wm(M):
        m = np.isfinite(M) & (w > 0)
        return (M[m] * w[m]).sum() / w[m].sum()
    lrt, bus = s.comp[UG], s.comp["bus"]
    print(f"Trunk pairs, transit-trip-weighted minutes: LRT ivt {wm(lrt['ivt']):.1f} walk {wm(lrt['walk']):.1f} wait {wm(lrt['wait']):.1f} | "
          f"bus ivt {wm(bus['ivt']):.1f} walk {wm(bus['walk']):.1f} wait {wm(bus['wait']):.1f} transfers {wm(bus['transfers']):.2f}")
    dL = s.gc(UG) - 5.0 - s.gc("bus")
    avail = np.isfinite(dL) & s.off & (s.n_pair > 0)
    P = np.where(avail, 1 / (1 + np.exp(0.06 * np.nan_to_num(dL))), 0.0)
    brt_fed, all_ = (s.T_tr * P * (s.n_brt[UG] > 0)).sum(), (s.T_tr * P).sum()
    print(f"Pairs with a Metronit feeder leg carry {brt_fed:,.0f} of the {all_:,.0f} LRT trips drawn from existing transit ({100 * brt_fed / all_:.0f}%).")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["group", "setting", "underground_trips", "underground_pct_vs_base", "ground_trips", "ground_pct_vs_base"])
            wr.writerows(out)
        print("wrote", a.csv)


if __name__ == "__main__":
    main()
