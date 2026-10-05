"""Consolidate the OVT research extracts (Output/ovt_research/extracts/*.md) into one evidence table.

Usage:  python3 tools/ovt_build_evidence_table.py
Reads every markdown table in the extract reports, maps their differing column headings onto the plan's
schema (docs/OVT_WEIGHTS_RESEARCH_PLAN.md §5.2) and writes Output/ovt_research/evidence_table.csv, one row per
estimate, keeping each extract's own row id (prefixed by the extract) and verification status. The
'normalised_value' column is a multiplier on in-vehicle time for weights and in-vehicle-equivalent minutes
for penalties and times, parsed from the estimate when the unit is already in those terms (rule N1); rows whose
estimate is a range, a relative statement or in other units keep an empty normalised value and the note says why.
"""
import csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACTS = ROOT / "Output/ovt_research/extracts"
OUT = ROOT / "Output/ovt_research/evidence_table.csv"
SCHEMA = ["id", "parameter", "stream", "citation", "year", "country_city", "modes", "method", "sample", "definition_as_reported",
          "estimate", "interval_or_range", "unit", "context", "normalised_value", "normalisation_note", "quality_1_3",
          "applicability_haifa_1_3", "link", "verification_status", "extract"]
ALIASES = {
    "id": ["id"], "parameter": ["parameter"], "stream": ["stream"], "citation": ["citation", "model", "model (region, software)"],
    "year": ["year", "branch/commit date if visible", "branch/commit"], "country_city": ["country/city", "place", "country", "region"],
    "modes": ["mode(s)", "mode pair", "mode", "mode served", "modes"], "method": ["method"], "sample": ["sample"],
    "definition_as_reported": ["definition as reported", "definition"], "estimate": ["estimate", "value"],
    "interval_or_range": ["interval / range", "interval or range", "range", "range / detail", "interval/range"], "unit": ["unit"],
    "context": ["context", "notes", "notes (e.g. thresholds)", "interchange type", "pure/total", "whether pure (net of walk & wait) or total"],
    "quality_1_3": ["quality 1–3", "quality", "q"], "applicability_haifa_1_3": ["applicability to haifa 1–3", "applicability", "a", "h"],
    "link": ["url", "source file url", "link"], "verification_status": ["verification status", "verification"],
}


def parse_tables(text):
    lines = text.splitlines(); i = 0; tables = []
    while i < len(lines):
        if lines[i].lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            hdr = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows = []; i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", lines[i].strip().strip("|"))]
                rows.append([c.replace("\\|", "|") for c in cells]); i += 1
            tables.append((hdr, rows))
        else:
            i += 1
    return tables


def map_row(hdr, cells):
    low = [h.lower() for h in hdr]
    def get(key):
        for alias in ALIASES.get(key, []):
            if alias in low:
                j = low.index(alias)
                return cells[j] if j < len(cells) else ""
        return ""
    row = {k: get(k) for k in SCHEMA if k not in ("normalised_value", "normalisation_note", "extract")}
    # context: join the context-like columns that are present
    extra = []
    for name in ("interchange type", "pure/total", "whether pure (net of walk & wait) or total", "notes", "notes (e.g. thresholds)"):
        if name in low:
            j = low.index(name)
            if j < len(cells) and cells[j] and cells[j] not in ("—", "-", "n.r."):
                extra.append(f"{name}: {cells[j]}")
    if "context" in low:
        j = low.index("context"); base = cells[j] if j < len(cells) else ""
    else:
        base = ""
    row["context"] = "; ".join([x for x in [base] + extra if x])
    return row


NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")


def normalise(row):
    est, unit = row["estimate"], row["unit"].lower()
    nums = NUM.findall(est.replace(",", ""))
    if not nums:
        return "", "no numeric estimate"
    multi = len(nums) > 1
    if "× ivt" in unit or "x ivt" in unit or unit.strip() in ("ratio", "×"):
        return ("" if multi else nums[0]), ("weight already relative to in-vehicle time (N1)" if not multi else "several values in one cell: see estimate")
    if "min" in unit and ("ivt" in unit or "equiv" in unit or "generalised" in unit or "generalized" in unit or unit.strip() in ("min", "minutes", "min of ivt per transfer")):
        return ("" if multi else nums[0]), ("in-vehicle-equivalent minutes as reported (N2/N5)" if not multi else "several values in one cell: see estimate")
    return "", f"unit '{row['unit']}' not converted (N1 needs the study's own in-vehicle value)"


def main():
    rows = []
    for f in sorted(EXTRACTS.glob("*.md")):
        tag = f.stem
        for hdr, trs in parse_tables(f.read_text(encoding="utf-8")):
            low = [h.lower() for h in hdr]
            if "id" not in low or not any(a in low for a in ("estimate", "value")):
                continue
            for cells in trs:
                r = map_row(hdr, cells)
                if not r["id"]:
                    continue
                r["normalised_value"], r["normalisation_note"] = normalise(r)
                r["extract"] = tag
                r["id"] = f"{tag.split('_')[0]}-{r['id']}"
                rows.append({k: r.get(k, "") for k in SCHEMA})
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=SCHEMA); w.writeheader(); w.writerows(rows)
    n_ver = sum("read" in r["verification_status"].lower() and "unverified" not in r["verification_status"].lower() for r in rows)
    print(f"{len(rows)} rows from {len(list(EXTRACTS.glob('*.md')))} extracts -> {OUT.relative_to(ROOT)}; read in full: {n_ver}, search-summary only: {len(rows) - n_ver}")
    by = {}
    for r in rows: by[r["extract"]] = by.get(r["extract"], 0) + 1
    print(by)


if __name__ == "__main__":
    main()
