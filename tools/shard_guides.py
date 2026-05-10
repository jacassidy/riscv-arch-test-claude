#!/usr/bin/env python3
"""Split markdown guides into ≤50-line topic shards on ## (and ### if needed).

Usage:
  python3 tools/shard_guides.py <guide.md> [--out-dir guides/<topic>/]
  python3 tools/shard_guides.py --all          # process whole queue

For each guide:
  - Read whole file.
  - Detect H1 (preserved as shard title prefix) + leading prose (intro shard).
  - Walk H2 sections; if a section >50 lines, split on H3 sub-sections.
  - If still >50 lines, leave as-is and warn (manual split needed).
  - Slugify section title for filename.
  - Code blocks copied EXACT.
"""
import re
import sys
from pathlib import Path

MAX_LINES = 50
REPO = Path(__file__).resolve().parent.parent

# (guide_path_relative_to_repo, topic_dir_name)
QUEUE = [
    ("guides/coverpoint-templates.md", "coverpoint-templates"),
    ("guides/vector-reference.md", "vector-reference"),
    ("guides/custom-scripts/CLAUDE-coverage-workflow.md", "custom-scripts/coverage-workflow"),
    ("guides/custom-scripts/GUIDE.md", "custom-scripts/api"),
    ("guides/custom-scripts/GUIDE-api-reference.md", "custom-scripts/api-reference"),
    ("guides/pitfalls.md", "pitfalls"),
    ("guides/architecture.md", "architecture"),
    ("guides/debugging-hangs.md", "debugging-hangs"),
    ("guides/normative-rules.md", "normative-rules"),
    ("simulator-issues.md", "simulator-issues"),
]


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "section"


def split_on_heading(lines, level):
    """Return list of (heading_text_or_None, body_lines)."""
    pat = re.compile(rf"^{'#' * level} (.+)$")
    sections = []
    cur_head = None
    cur = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
        if not in_code:
            m = pat.match(line)
            if m:
                if cur_head is not None or cur:
                    sections.append((cur_head, cur))
                cur_head = m.group(1).strip()
                cur = [line]
                continue
        cur.append(line)
    if cur_head is not None or cur:
        sections.append((cur_head, cur))
    return sections


def shard_file(src: Path, out_dir: Path):
    text = src.read_text()
    lines = text.splitlines(keepends=False)

    # Detect H1
    h1 = None
    body_start = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            h1 = ln[2:].strip()
            body_start = i + 1
            break
    body = lines[body_start:]

    # Split on H2
    sections = split_on_heading(body, 2)
    intro = []
    h2_sections = []
    for head, blines in sections:
        if head is None:
            intro = blines
        else:
            h2_sections.append((head, blines))

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []

    if intro and any(ln.strip() for ln in intro):
        intro_lines = [f"# {h1}" if h1 else "# Intro", ""] + intro
        intro_path = out_dir / "intro.md"
        intro_path.write_text("\n".join(intro_lines).rstrip() + "\n")
        written.append((intro_path, len(intro_lines)))

    for head, blines in h2_sections:
        slug = slugify(head)
        if len(blines) <= MAX_LINES:
            shard = [f"# {head}", ""] + blines[1:]  # blines[0] is the H2 line itself
            path = out_dir / f"{slug}.md"
            path.write_text("\n".join(shard).rstrip() + "\n")
            written.append((path, len(shard)))
        else:
            # Try H3 split
            sub_sections = split_on_heading(blines[1:], 3)
            sub_intro = []
            h3_sections = []
            for sh, slines in sub_sections:
                if sh is None:
                    sub_intro = slines
                else:
                    h3_sections.append((sh, slines))
            sub_dir = out_dir / slug
            sub_dir.mkdir(exist_ok=True)
            if sub_intro and any(ln.strip() for ln in sub_intro):
                p = sub_dir / "intro.md"
                content = [f"# {head}", ""] + sub_intro
                p.write_text("\n".join(content).rstrip() + "\n")
                written.append((p, len(content)))
            for sh, slines in h3_sections:
                sub_slug = slugify(sh)
                p = sub_dir / f"{sub_slug}.md"
                content = [f"## {sh}", ""] + slines[1:]
                p.write_text("\n".join(content).rstrip() + "\n")
                written.append((p, len(content)))

    return written


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        queue = QUEUE
    elif len(sys.argv) == 3:
        queue = [(sys.argv[1], sys.argv[2])]
    else:
        print(__doc__)
        sys.exit(1)

    total_oversized = []
    for src_rel, topic in queue:
        src = REPO / src_rel
        if not src.exists():
            print(f"SKIP missing: {src_rel}")
            continue
        out_dir = REPO / "guides" / topic
        print(f"\n=== {src_rel} -> guides/{topic}/ ===")
        written = shard_file(src, out_dir)
        for path, n in sorted(written):
            marker = " ⚠OVER" if n > MAX_LINES else ""
            print(f"  {n:>4}  {path.relative_to(REPO)}{marker}")
            if n > MAX_LINES:
                total_oversized.append(path)

    if total_oversized:
        print(f"\n{len(total_oversized)} shards exceed {MAX_LINES} lines — need manual split:")
        for p in total_oversized:
            print(f"  {p.relative_to(REPO)}")


if __name__ == "__main__":
    main()
