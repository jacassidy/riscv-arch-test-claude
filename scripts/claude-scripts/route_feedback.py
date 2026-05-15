#!/usr/bin/env python3
"""Append a /route-feedback entry to memory logs.

Pairs feedback with the most recent matching `request` row in
memory/route-log.jsonl by (session_id, shard). Routes by severity:
  large  → memory/audit-queue.jsonl (opus picks up on manual audit)
  small  → memory/route-patches.jsonl (Sonnet auto-patches next Stop)
All feedback ALWAYS lands in memory/route-log.jsonl for offline review.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR",
                          Path(__file__).resolve().parents[2]))
# Canonical claude-files repo. This script lives in canonical repo's scripts/,
# so parents[2] is canonical even when REPO points at a worktree.
CANONICAL_REPO = Path(__file__).resolve().parents[2]


def _branch_slug() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(REPO), "branch", "--show-current"],
            stderr=subprocess.DEVNULL, timeout=2,
        ).decode().strip()
        if out:
            return re.sub(r"[^A-Za-z0-9._-]+", "_", out)
    except Exception:
        pass
    return "unknown"


MEMORY_DIR = CANONICAL_REPO / "memory" / _branch_slug()
ROUTE_LOG = MEMORY_DIR / "route-log.jsonl"
AUDIT_QUEUE = MEMORY_DIR / "audit-queue.jsonl"
PATCH_QUEUE = MEMORY_DIR / "route-patches.jsonl"

VALID_VERDICTS = {"useless", "wrong", "partial", "good"}
VALID_SEVERITY = {"none", "small", "large"}


def append_jsonl(path: Path, row: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_request_id(session_id: str, shard: str):
    """Most recent matching request row's id, or empty string."""
    if not ROUTE_LOG.exists():
        return ""
    last = ""
    try:
        with open(ROUTE_LOG) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("type") != "request":
                    continue
                if r.get("session_id") != session_id:
                    continue
                if shard not in (r.get("shards") or []):
                    continue
                last = r.get("request_id", "") or last
    except Exception:
        return ""
    return last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-id", required=True)
    ap.add_argument("--shard", required=True)
    ap.add_argument("--verdict", required=True, choices=sorted(VALID_VERDICTS))
    ap.add_argument("--severity", required=True, choices=sorted(VALID_SEVERITY))
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    shard = args.shard.strip()
    if ".." in shard or not (shard.startswith("guides/") or shard == ""):
        print(f"reject: shard must be under guides/ (got {shard!r})",
              file=sys.stderr)
        return 2

    rid = find_request_id(args.session_id, shard)
    feedback_id = uuid.uuid4().hex[:12]
    row = {
        "type": "feedback",
        "ts": time.time(),
        "session_id": args.session_id,
        "feedback_id": feedback_id,
        "request_id": rid,        # empty string if no pair found
        "shard": shard,
        "verdict": args.verdict,
        "severity": args.severity,
        "note": args.note[:500],
        "source": "manual",
    }
    append_jsonl(ROUTE_LOG, row)

    if args.severity == "large":
        append_jsonl(AUDIT_QUEUE, row)
    elif args.severity == "small" and args.verdict in ("wrong", "partial"):
        append_jsonl(PATCH_QUEUE, row)

    print(f"recorded feedback_id={feedback_id} paired_request_id={rid or '<none>'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
