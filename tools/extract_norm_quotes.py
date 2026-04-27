#!/usr/bin/env python3
"""Extract the spec text associated with each `norm:` anchor in a riscv-isa-manual adoc.

Two anchor styles are supported:

  Inline:  `[#norm:foo]#The body sentence ending here.#`
  Block:   `[[norm:foo]]\nFollowing paragraph(s)`

For block anchors we capture the next paragraph (until the next blank line, header,
or another anchor). For inline anchors we capture the bracketed body.

Output:
  - JSON to stdout (or --out FILE) mapping {tag: quote}.
  - Optional --csv writes a 2-column CSV (tag, quote) for diffing/inspection.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

DEFAULT_ADOC = Path("/home/jacassidy/cvw/addins/riscv-isa-manual/src/v-st-ext.adoc")

INLINE_RE = re.compile(r"\[#(norm:[A-Za-z0-9_\-]+)\]#")
BLOCK_RE = re.compile(r"^\[\[(norm:[A-Za-z0-9_\-]+)\]\]\s*$")


def _scan_inline_value(text: str, start: int) -> tuple[str, int]:
    """From the position of the opening `#` after `]`, return body up to the
    matching closing `#` (single-character delimiter). Allow nested brackets.
    Returns (body, end_index_after_closing_hash).
    """
    # text[start] should be '#'
    assert text[start] == "#"
    i = start + 1
    depth = 0  # bracket depth of `[ ]` so we don't get confused by nested anchors
    while i < len(text):
        c = text[i]
        if c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
        elif c == "#" and depth <= 0:
            return text[start + 1 : i], i + 1
        i += 1
    return text[start + 1 :], len(text)


def _next_paragraph(lines: list[str], start: int) -> str:
    """Return the next non-blank paragraph after `start` (block anchor line),
    skipping blanks. Stops at a blank line, header, table marker, or another anchor.
    """
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    buf: list[str] = []
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s:
            break
        if s.startswith("=") or s.startswith("|===") or s.startswith("[["):
            break
        # Skip note/admonition openers but include their body.
        if s in ("====", "----"):
            i += 1
            continue
        buf.append(s)
        i += 1
    return " ".join(buf)


def extract(adoc_path: Path) -> dict[str, str]:
    text = adoc_path.read_text()
    lines = text.splitlines()
    out: dict[str, str] = {}

    # Inline anchors anywhere in the file (even in the middle of a paragraph).
    pos = 0
    while True:
        m = INLINE_RE.search(text, pos)
        if not m:
            break
        tag = m.group(1)
        # The opening `#` of the body is right after `]`.
        body_start = m.end() - 1  # position of `#`
        body, end = _scan_inline_value(text, body_start)
        body = re.sub(r"\s+", " ", body).strip()
        # Strip surrounding backticks/asterisks for cleanliness.
        if tag not in out or len(body) > len(out[tag]):
            out[tag] = body
        pos = end

    # Block anchors line-by-line.
    for idx, line in enumerate(lines):
        m = BLOCK_RE.match(line.rstrip("\n"))
        if not m:
            continue
        tag = m.group(1)
        para = _next_paragraph(lines, idx + 1)
        para = re.sub(r"\s+", " ", para).strip()
        # Prefer the longer of inline vs block if duplicates.
        if tag not in out or (para and len(para) > len(out.get(tag, ""))):
            out[tag] = para

    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--adoc", type=Path, default=DEFAULT_ADOC)
    ap.add_argument("--out", type=Path, help="Write JSON to FILE")
    ap.add_argument("--csv", type=Path, help="Also write a 2-col CSV to FILE")
    args = ap.parse_args()

    quotes = extract(args.adoc)
    payload = json.dumps(quotes, indent=2, sort_keys=True)
    if args.out:
        args.out.write_text(payload)
        print(f"Wrote {len(quotes)} quotes to {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(payload)
    if args.csv:
        with args.csv.open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["tag", "quote"])
            for k in sorted(quotes):
                w.writerow([k, quotes[k]])
    return 0


if __name__ == "__main__":
    sys.exit(main())
