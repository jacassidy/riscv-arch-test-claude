#!/usr/bin/env python3
"""Build an audit worksheet for normative-rule -> coverpoint mappings.

For every rule listed in `riscv-isa-manual/normative_rule_defs/v-st-ext.yaml`, emit:

  rule_name | tag(s) | spec_quote | current_coverpoints | flag

Where `flag` is one of:
  EMPTY         - no coverpoints (or only `[""]`)
  PLACEHOLDER   - only `implicit` or `untestable` style entries
  GENERIC_ONLY  - only generic placeholder coverpoints like `cp_asm_count`
  SUSPECT       - rule subject (CSR/register name) appears unrelated to coverpoints
                  (heuristic: rule name mentions one CSR/register and coverpoints
                  reference a different one)
  OK            - has real coverpoints, no obvious mismatch

Outputs a CSV (default /tmp/vx_audit.csv) plus a JSON.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_YAML = Path("/home/jacassidy/cvw/addins/riscv-isa-manual/normative_rule_defs/v-st-ext.yaml")
VX_YAML = Path("/home/jacassidy/normative_rules/coverpoints/norm/Vx.yaml")
NORM_CSV = Path(
    "/home/jacassidy/cvw/addins/riscv-arch-test-claude/working-testplans/csvs/v-st-ext-normative-rules.csv"
)
QUOTES_JSON = Path("/tmp/norm_quotes.json")

PLACEHOLDER_VALUES = {"implicit", "untestable", ""}
GENERIC_CPS = {"cp_asm_count"}


def load_yaml_rules(path: Path) -> list[dict]:
    """Tiny YAML loader for the structure used in these defs (no PyYAML needed)."""
    rules: list[dict] = []
    text = path.read_text().splitlines()
    i = 0
    n = len(text)
    while i < n:
        line = text[i]
        s = line.strip()
        if s.startswith("- name:"):
            name = s.split(":", 1)[1].strip()
            tags: list[str] = []
            j = i + 1
            while j < n and text[j].strip() and not text[j].strip().startswith("- name") and not text[j].strip().startswith("- names"):
                t = text[j].strip()
                if t.startswith("tags:"):
                    rest = t.split(":", 1)[1].strip()
                    if rest.startswith("["):
                        tags = re.findall(r'"([^"]+)"', rest)
                j += 1
            rules.append({"names": [name], "tags": tags})
            i = j
        elif s.startswith("- names:"):
            rest = s.split(":", 1)[1].strip()
            if rest.startswith("["):
                names = re.findall(r"[A-Za-z0-9_\-]+", rest)
            else:
                names = []
                j2 = i + 1
                while j2 < n and "]" not in text[j2]:
                    j2 += 1
                if j2 < n:
                    block = "\n".join(text[i:j2 + 1])
                    inner = block[block.find("[") + 1 : block.rfind("]")]
                    names = [s.strip() for s in inner.split(",") if s.strip()]
            tags: list[str] = []
            j = i + 1
            while j < n and text[j].strip() and not text[j].strip().startswith("- name") and not text[j].strip().startswith("- names"):
                t = text[j].strip()
                if t.startswith("tags:"):
                    rest2 = t.split(":", 1)[1].strip()
                    if rest2.startswith("["):
                        tags = re.findall(r'"([^"]+)"', rest2)
                j += 1
            rules.append({"names": names, "tags": tags})
            i = j
        else:
            i += 1
    return rules


def load_csv_mapping(path: Path) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        cp_cols = sorted(
            (c for c in reader.fieldnames or [] if re.fullmatch(r"cp_name_\d+", c)),
            key=lambda c: int(c.split("_")[-1]),
        )
        for row in reader:
            name = (row.get("rule_name") or "").strip()
            if not name:
                continue
            cps: list[str] = []
            seen: set[str] = set()
            for col in cp_cols:
                v = (row.get(col) or "").strip()
                if v and v not in seen:
                    seen.add(v)
                    cps.append(v)
            mapping[name.lower().replace("-", "_")] = cps
    return mapping


CSR_TOKENS = {
    "vl", "vlenb", "vstart", "vtype", "vxrm", "vxsat", "vcsr",
    "mstatus", "vsstatus", "sstatus", "misa", "mcause", "mip", "mie",
    "scause", "sip", "sie", "vsie", "vsip", "vsstatus",
}


def _extract_subjects(name: str) -> set[str]:
    parts = re.split(r"[-_]", name.lower())
    return set(parts) & CSR_TOKENS


def classify(rule_name: str, cps: list[str], spec: str) -> tuple[str, str]:
    """Return (flag, note)."""
    if not cps:
        return "EMPTY", "no coverpoints"
    real = [c for c in cps if c not in PLACEHOLDER_VALUES and not c.startswith("Rule states")]
    real = [c for c in real if not c.startswith("Requires privileged")]
    if not real:
        return "PLACEHOLDER", f"only placeholders: {cps}"
    if all(c in GENERIC_CPS for c in real):
        return "GENERIC_ONLY", f"only generic: {real}"
    # Heuristic: if rule subject is a CSR but no coverpoint references it.
    subjects = _extract_subjects(rule_name)
    if subjects:
        cp_text = " ".join(real).lower()
        if not any(sub in cp_text for sub in subjects):
            # Also check spec text — sometimes a rule belongs to another CSR's section.
            spec_subjects = _extract_subjects(spec.lower()) if spec else set()
            if subjects - spec_subjects:
                return "SUSPECT", f"rule mentions {subjects} but none appear in coverpoints"
    return "OK", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rules", type=Path, default=RULES_YAML)
    ap.add_argument("--vx", type=Path, default=VX_YAML)
    ap.add_argument("--csv", type=Path, default=NORM_CSV)
    ap.add_argument("--quotes", type=Path, default=QUOTES_JSON)
    ap.add_argument("--out-csv", type=Path, default=Path("/tmp/vx_audit.csv"))
    ap.add_argument("--out-json", type=Path, default=Path("/tmp/vx_audit.json"))
    args = ap.parse_args()

    rules = load_yaml_rules(args.rules)
    csv_map = load_csv_mapping(args.csv)
    quotes = json.loads(args.quotes.read_text()) if args.quotes.exists() else {}

    rows: list[dict] = []
    counts: dict[str, int] = {}
    for r in rules:
        for name in r["names"]:
            key = name.lower().replace("-", "_")
            cps = csv_map.get(key, [])
            spec = ""
            for tag in r["tags"]:
                spec = quotes.get(tag) or quotes.get(tag.lower()) or spec
                if spec:
                    break
            flag, note = classify(name, cps, spec)
            rows.append({
                "rule_name": name,
                "tags": ";".join(r["tags"]),
                "spec_quote": spec,
                "current_coverpoints": "; ".join(cps),
                "flag": flag,
                "note": note,
            })
            counts[flag] = counts.get(flag, 0) + 1

    with args.out_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    args.out_json.write_text(json.dumps(rows, indent=2))

    print(f"Wrote {len(rows)} rows to {args.out_csv}", file=sys.stderr)
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
