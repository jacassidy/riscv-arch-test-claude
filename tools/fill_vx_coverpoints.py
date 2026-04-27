#!/usr/bin/env python3
"""Fill coverpoint arrays in a normative-rule YAML from a CSV.

IMPORTANT: Run `make covergroupgen` BEFORE running this script. Each
coverpoint pulled from the CSV is resolved against the generated
`*_coverage.svh` files in `coverpoints/priv/` and `coverpoints/unpriv/`,
and rewritten as `<covergroup>/<coverpoint>` (e.g. `ExceptionsZicboU_cg/cp_cbcfe`).
Coverpoints that don't match any covergroup are dropped, except for the
textual placeholders in `TEXTUAL_PLACEHOLDERS` (e.g. `implicit`, `untestable`).

For each `- name: <rule>` entry in the YAML, find the matching row in the CSV
(case-insensitive match on the `rule_name` column) and replace its
`coverpoint: [...]` list with the non-empty `cp_name_*` values from that row,
qualified by their covergroup.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

DEFAULT_YAML = Path("/home/jacassidy/normative_rules/coverpoints/norm/Vx.yaml")
DEFAULT_CSV = Path(
    "/home/jacassidy/cvw/addins/riscv-arch-test-claude/"
    "working-testplans/csvs/v-st-ext-normative-rules.csv"
)
DEFAULT_COVERGROUPS = Path("/home/jacassidy/normative_rules/coverpoints")

# Textual markers in the CSV that aren't real coverpoint identifiers — keep
# them in the output even if they don't resolve to a covergroup.
TEXTUAL_PLACEHOLDERS = {"implicit", "untestable", "todo", "n/a", "na", "none"}

# `covergroup <Name> ...`
COVERGROUP_RE = re.compile(r"^\s*covergroup\s+([A-Za-z_]\w*)")
# `<name> : coverpoint ...`  or  `<name> : cross ...`
COVERPOINT_DEF_RE = re.compile(r"^\s+([A-Za-z_]\w*)\s*:\s*(?:coverpoint|cross)\b")


def build_covergroup_index(
    base: Path,
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Scan `<base>/priv/**/*_coverage.svh` and `<base>/unpriv/**/*_coverage.svh`.

    Returns (exact, ordered):
      exact   : coverpoint name -> covergroup name (first occurrence wins).
      ordered : list of (cp_name, cg_name) in scan order, used for prefix
                matching when an exact name isn't defined.
    """
    exact: dict[str, str] = {}
    ordered: list[tuple[str, str]] = []
    for sub in ("priv", "unpriv"):
        d = base / sub
        if not d.is_dir():
            continue
        for svh in sorted(d.rglob("*_coverage.svh")):
            current_cg: str | None = None
            try:
                lines = svh.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for line in lines:
                m = COVERGROUP_RE.match(line)
                if m:
                    current_cg = m.group(1)
                    continue
                if current_cg is None:
                    continue
                m = COVERPOINT_DEF_RE.match(line)
                if m:
                    cp_name = m.group(1)
                    ordered.append((cp_name, current_cg))
                    exact.setdefault(cp_name, current_cg)
    return exact, ordered


def qualify_coverpoint(
    name: str, exact: dict[str, str], ordered: list[tuple[str, str]]
) -> str | None:
    """Resolve a CSV coverpoint to `<covergroup>/<coverpoint>`.

    - Names containing `/` are assumed pre-qualified, returned unchanged.
    - Textual placeholders (`implicit`, `untestable`, ...) are returned unchanged.
    - Exact match in the index wins; otherwise the first defined coverpoint
      whose name starts with `<name>_` is used (handles CSV abbreviations
      like `cr_vl_lmul` -> svh `cr_vl_lmul_sew32`).
    - Returns None when nothing matches; caller should drop the entry.
    """
    if "/" in name:
        return name
    if name.lower() in TEXTUAL_PLACEHOLDERS:
        return name
    cg = exact.get(name)
    if cg is not None:
        return f"{cg}/{name}"
    prefix = name + "_"
    for cp_name, cg_name in ordered:
        if cp_name.startswith(prefix):
            return f"{cg_name}/{cp_name}"
    return None


def norm_key(s: str) -> str:
    return s.strip().lower().replace("-", "_")


# Wildcard expansion sets.
SEW_VALUES = ["8", "16", "32", "64"]
DEFAULT_STAR_VALUES = ["1", "2"]

PAREN_VARIANT_RE = re.compile(r"^(.+?)\s*\(([^)]+?)\s+variant\)\s*$")
BRACE_RE = re.compile(r"\{([^}]+)\}")
INLINE_SLASH_RE = re.compile(r"([A-Za-z0-9]+)/([A-Za-z0-9]+)")


def expand_parenthetical(s: str) -> str:
    """`base (ls_e* variant)` -> `base_ls_e*`."""
    m = PAREN_VARIANT_RE.match(s)
    if m:
        return f"{m.group(1).strip()}_{m.group(2).strip()}"
    return s


def expand_braces(items: list[str]) -> list[str]:
    """`sew{8/16}` -> [`sew8`, `sew16`]."""
    out = []
    for s in items:
        pending = [s]
        while pending:
            cur = pending.pop(0)
            m = BRACE_RE.search(cur)
            if not m:
                out.append(cur)
                continue
            for alt in m.group(1).split("/"):
                pending.append(cur[: m.start()] + alt.strip() + cur[m.end() :])
    return out


def expand_inline_slash(items: list[str]) -> list[str]:
    """`vs1/vs2` -> [`vs1`, `vs2`] in place within a token."""
    out = []
    for s in items:
        pending = [s]
        while pending:
            cur = pending.pop(0)
            m = INLINE_SLASH_RE.search(cur)
            if not m:
                out.append(cur)
                continue
            pending.append(cur[: m.start()] + m.group(1) + cur[m.end() :])
            pending.append(cur[: m.start()] + m.group(2) + cur[m.end() :])
    return out


def _star_values(prefix: str) -> list[str]:
    # Contextual: `ls_e*` -> SEW widths; everything else -> [1, 2].
    if prefix.endswith("ls_e") or prefix.endswith("_e") or prefix.endswith("sew"):
        return SEW_VALUES
    return DEFAULT_STAR_VALUES


def expand_wildcards(items: list[str]) -> list[str]:
    """`vs*` -> [`vs1`, `vs2`]; `ls_e*` -> SEW widths; cartesian over multiple `*`."""
    out = []
    for s in items:
        pending = [s]
        while pending:
            cur = pending.pop(0)
            idx = cur.find("*")
            if idx < 0:
                out.append(cur)
                continue
            # Inspect up to 5 chars of preceding context for routing.
            prefix = cur[max(0, idx - 5) : idx]
            for v in _star_values(prefix):
                pending.append(cur[:idx] + v + cur[idx + 1 :])
    return out


def expand_shorthand(raw: str) -> list[str]:
    """Expand one CSV cell into one or more concrete coverpoint names."""
    # 1. Split on ` / ` (space-slash-space) into independent entries.
    top = [p.strip() for p in re.split(r"\s+/\s+", raw) if p.strip()]
    # 2. Strip `(X variant)` parenthetical.
    top = [expand_parenthetical(p) for p in top]
    # 3. Brace expansion `{A/B}`.
    top = expand_braces(top)
    # 4. Inline slash alternation `foo/bar`.
    top = expand_inline_slash(top)
    # 5. Wildcard `*` expansion.
    top = expand_wildcards(top)
    return top


def load_rule_to_cps(csv_path: Path) -> dict[str, list[str]]:
    mapping: dict[str, list[str]] = {}
    with csv_path.open(newline="") as f:
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
                val = (row.get(col) or "").strip()
                if not val:
                    continue
                for expanded in expand_shorthand(val):
                    if expanded and expanded not in seen:
                        seen.add(expanded)
                        cps.append(expanded)
            mapping[norm_key(name)] = cps
    return mapping


def format_array(cps: list[str], indent: str = "    ") -> str:
    if not cps:
        return '[""]'
    inline = "[" + ", ".join(f'"{c}"' for c in cps) + "]"
    if len(inline) <= 100:
        return inline
    body = ",\n".join(f'{indent}    "{c}"' for c in cps)
    return f"\n{indent}  [\n{body},\n{indent}  ]"


NAME_RE = re.compile(r"^(\s*)- name:\s*(\S+)\s*$")
NAMES_INLINE_RE = re.compile(r"^(\s*)- names:\s*\[([^\]]*)\]\s*$")
NAMES_OPEN_RE = re.compile(r"^(\s*)- names:\s*$")
CP_RE = re.compile(r"^(\s*)coverpoint:\s*(\[.*\]|\[)\s*$")
CP_OPEN_RE = re.compile(r"^(\s*)coverpoint:\s*$")


def parse_names_list(text: str) -> list[str]:
    """Parse a YAML inline list body like 'a, b, c' (without surrounding [])."""
    return [s.strip().strip('"').strip("'") for s in text.split(",") if s.strip()]


def merge_cps_for_names(names: list[str], mapping: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """Union of coverpoints across all names. Returns (cps, missing_names)."""
    seen: set[str] = set()
    out: list[str] = []
    missing: list[str] = []
    for nm in names:
        key = norm_key(nm)
        if key not in mapping:
            missing.append(nm)
            continue
        for cp in mapping[key]:
            if cp not in seen:
                seen.add(cp)
                out.append(cp)
    return out, missing


def consume_block_value(lines: list[str], i: int) -> tuple[str, int]:
    """Given the start index of a YAML value that may span multiple lines (because it
    starts with '[' but the matching ']' is on a later line), return the joined
    text of the bracketed list and the index just past the closing line.
    """
    buf = [lines[i].rstrip("\n")]
    i += 1
    while "]" not in buf[-1]:
        if i >= len(lines):
            break
        buf.append(lines[i].rstrip("\n"))
        i += 1
    return " ".join(buf), i


def qualify_cps(
    cps: list[str], exact: dict[str, str], ordered: list[tuple[str, str]]
) -> tuple[list[str], list[str]]:
    """Apply qualify_coverpoint to a list. Returns (kept, dropped)."""
    kept: list[str] = []
    dropped: list[str] = []
    for cp in cps:
        q = qualify_coverpoint(cp, exact, ordered)
        if q is None:
            dropped.append(cp)
        else:
            kept.append(q)
    return kept, dropped


def fill_yaml(
    yaml_path: Path,
    mapping: dict[str, list[str]],
    exact: dict[str, str],
    ordered: list[tuple[str, str]],
) -> tuple[int, list[str], list[str]]:
    lines = yaml_path.read_text().splitlines(keepends=True)
    out: list[str] = []
    filled = 0
    missing: list[str] = []
    dropped: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.rstrip("\n")

        # Match either `- name: X` or `- names: [X, Y, ...]` (single or multi-line).
        names: list[str] | None = None
        m_single = NAME_RE.match(stripped)
        m_inline = NAMES_INLINE_RE.match(stripped)
        m_open = NAMES_OPEN_RE.match(stripped)
        if m_single:
            names = [m_single.group(2)]
            out.append(line)
            i += 1
        elif m_inline:
            names = parse_names_list(m_inline.group(2))
            out.append(line)
            i += 1
        elif m_open:
            # Multi-line: gather lines until ']' present.
            out.append(line)
            i += 1
            buf: list[str] = []
            while i < n:
                out.append(lines[i])
                buf.append(lines[i].rstrip("\n"))
                bracketed = "".join(buf).strip()
                if "]" in bracketed:
                    # Strip surrounding [] then split.
                    inner = bracketed[bracketed.find("[") + 1 : bracketed.rfind("]")]
                    names = parse_names_list(inner)
                    i += 1
                    break
                i += 1

        if names is None:
            out.append(line)
            i += 1
            continue

        # Now find the coverpoint: line for this entry, before the next entry.
        while i < n:
            sub = lines[i].rstrip("\n")
            if NAME_RE.match(sub) or NAMES_INLINE_RE.match(sub) or NAMES_OPEN_RE.match(sub):
                # No coverpoint found before next entry.
                break
            cp_match = CP_RE.match(sub)
            cp_open_match = CP_OPEN_RE.match(sub)
            if cp_match or cp_open_match:
                indent_match = cp_match if cp_match else cp_open_match
                assert indent_match is not None
                indent = indent_match.group(1)
                raw_cps, miss = merge_cps_for_names(names, mapping)
                missing.extend(miss)
                cps, drop = qualify_cps(raw_cps, exact, ordered)
                dropped.extend(drop)
                if cp_match:
                    # Possibly a multi-line existing array starting with `[`.
                    val = cp_match.group(2)
                    if val == "[":
                        # consume until matching ']'
                        _, i = consume_block_value(lines, i)
                    else:
                        i += 1
                else:
                    # `coverpoint:` with array on subsequent lines (e.g., `      [\n  ...]`)
                    i += 1
                    # consume until ']' line
                    while i < n and "]" not in lines[i]:
                        i += 1
                    if i < n:
                        i += 1
                if cps or all(norm_key(nm) in mapping for nm in names):
                    out.append(f"{indent}coverpoint: {format_array(cps)}\n")
                    filled += 1
                else:
                    out.append(f"{indent}coverpoint: [\"\"]\n")
                break
            out.append(lines[i])
            i += 1
    yaml_path.write_text("".join(out))
    return filled, missing, dropped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--yaml", type=Path, default=DEFAULT_YAML)
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument(
        "--covergroups",
        type=Path,
        default=DEFAULT_COVERGROUPS,
        help="Base dir; scans <dir>/priv and <dir>/unpriv for *_coverage.svh. "
        "Run `make covergroupgen` first.",
    )
    args = ap.parse_args()

    exact, ordered = build_covergroup_index(args.covergroups)
    if not exact:
        print(
            f"Warning: no covergroups found under {args.covergroups}/(priv|unpriv). "
            "Did you run `make covergroupgen`? All coverpoints will be dropped.",
            file=sys.stderr,
        )

    mapping = load_rule_to_cps(args.csv)
    filled, missing, dropped = fill_yaml(args.yaml, mapping, exact, ordered)
    print(f"Filled {filled} rule(s) in {args.yaml}")
    if dropped:
        unique_dropped = sorted(set(dropped))
        print(
            f"Dropped {len(dropped)} unmatched coverpoint reference(s) "
            f"({len(unique_dropped)} unique):",
            file=sys.stderr,
        )
        for cp in unique_dropped:
            print(f"  {cp}", file=sys.stderr)
    if missing:
        print(f"No CSV match for {len(missing)} rule(s):", file=sys.stderr)
        for name in missing:
            print(f"  {name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
