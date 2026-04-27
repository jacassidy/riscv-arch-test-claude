#!/usr/bin/env python3
"""Update the rule -> coverpoint mapping CSV from a JSON patch file.

The patch JSON is a list of objects:

  [
    {
      "rule_name": "vl_op",
      "coverpoints": ["cp_custom_vl_set", "cp_vcsrrswc"],   # full replacement list
      "descriptions": ["...", "..."],                        # optional, parallel to coverpoints
      "explanation": "vl is a CSR; the previous mapping wrongly tied it to indexed-load edges.",
      "gaps": ""
    },
    ...
  ]

For each entry, the row whose `rule_name` matches (case-insensitive,
hyphen/underscore-equivalent) has its `cp_name_*` and `coverage_desc_*` columns
fully reset to the supplied lists, and the `explanation` / `gaps` columns are
overwritten if provided. Other columns are untouched.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

DEFAULT_CSV = Path(
    "/home/jacassidy/cvw/addins/riscv-arch-test-claude/working-testplans/csvs/v-st-ext-normative-rules.csv"
)


def norm(s: str) -> str:
    return s.strip().lower().replace("-", "_")


def cp_columns(headers: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for h in headers:
        m = re.fullmatch(r"cp_name_(\d+)", h)
        if m:
            pairs.append((h, f"coverage_desc_{m.group(1)}"))
    pairs.sort(key=lambda x: int(x[0].split("_")[-1]))
    return pairs


def apply_patches(csv_path: Path, patches: list[dict], dry_run: bool = False) -> tuple[int, list[str]]:
    with csv_path.open(newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    headers = rows[0]
    cp_pairs = cp_columns(headers)
    name_idx = headers.index("rule_name")
    expl_idx = headers.index("explanation") if "explanation" in headers else None
    gaps_idx = headers.index("gaps") if "gaps" in headers else None

    by_name: dict[str, int] = {}
    for i, row in enumerate(rows[1:], start=1):
        if len(row) <= name_idx:
            continue
        by_name[norm(row[name_idx])] = i

    applied = 0
    missing: list[str] = []
    for p in patches:
        key = norm(p["rule_name"])
        if key not in by_name:
            missing.append(p["rule_name"])
            continue
        row_idx = by_name[key]
        row = rows[row_idx]
        # Pad row to header length.
        while len(row) < len(headers):
            row.append("")
        cps = p.get("coverpoints", []) or []
        descs = p.get("descriptions", []) or []
        for j, (name_col, desc_col) in enumerate(cp_pairs):
            cn_idx = headers.index(name_col)
            cd_idx = headers.index(desc_col)
            row[cn_idx] = cps[j] if j < len(cps) else ""
            row[cd_idx] = descs[j] if j < len(descs) else ""
        if expl_idx is not None and "explanation" in p:
            row[expl_idx] = p.get("explanation", "") or ""
        if gaps_idx is not None and "gaps" in p:
            row[gaps_idx] = p.get("gaps", "") or ""
        rows[row_idx] = row
        applied += 1

    if not dry_run:
        with csv_path.open("w", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerows(rows)
    return applied, missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("patch", type=Path, help="JSON file with the patch list")
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    patches = json.loads(args.patch.read_text())
    applied, missing = apply_patches(args.csv, patches, dry_run=args.dry_run)
    print(f"Applied {applied} patches to {args.csv}")
    if missing:
        print(f"Missing {len(missing)} rule(s):", file=sys.stderr)
        for n in missing:
            print(f"  {n}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
