#!/usr/bin/env python3
"""Routing hook for riscv-arch-test-claude.

Modes:
  prompt  — UserPromptSubmit. Regex match prompt → READ-shard reminders.
  tool    — PreToolUse for Read/Edit/Write/MultiEdit.
            * Edit/Write/MultiEdit: hard-block writes to generated files (exit 2).
            * For surviving calls: ask Sonnet which shards from
              guides/SHARD-INDEX.md the main agent should READ before acting.
              Cache by (file_path, sha(SHARD-INDEX)).

Failure-tolerant: any error → fall back to legacy regex PATH_RULES, log to stderr,
exit 0 so user flow never breaks.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path

REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parent.parent.parent))
# Canonical claude-files repo (where memory MUST land, never in worktrees).
# route.py is symlinked into every worktree; .resolve() follows symlink to real path.
CANONICAL_REPO = Path(__file__).resolve().parent.parent.parent
INDEX_PATH = REPO / "guides" / "SHARD-INDEX.md"
CACHE_PATH = Path("/tmp/route-cache.json")
SESSION_DIR = Path("/tmp/route-sessions")
SESSION_TTL = 24 * 3600  # 1 day
CACHE_TTL = 3600  # 1 hour
SONNET_TIMEOUT = 25  # seconds (Claude Code kills long hooks)
REMINDER_PREFIX = "[route.py] READ"


def _branch_slug() -> str:
    """Branch name of REPO (worktree), sanitized for filesystem. Falls back to 'unknown'."""
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


# Persistent paired log + queues — always under CANONICAL_REPO/memory/<branch>/,
# never in the worktree. Each worktree gets its own subdir keyed by branch.
MEMORY_DIR = CANONICAL_REPO / "memory" / _branch_slug()
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
ROUTE_LOG = MEMORY_DIR / "route-log.jsonl"
AUDIT_QUEUE = MEMORY_DIR / "audit-queue.jsonl"
PATCH_QUEUE = MEMORY_DIR / "route-patches.jsonl"
ROUTE_LOG_MAX = 10 * 1024 * 1024  # 10 MB rotation
AUDIT_WINDOW = 24 * 3600
AUDIT_LARGE_THRESHOLD = 3      # ≥3 large-severity feedbacks in window → nudge
AUDIT_NEG_RATIO = 0.3          # ≥30% useless+wrong over ≥10 graded → nudge
AUDIT_NEG_MIN = 10

# Prompt-keyword → shard-dir reminders (small set, hook-cheap).
PROMPT_RULES = [
    (r"\b(csv|testplan)\b", "guides/csv-editing/", "CSV/testplan work"),
    (r"cp_custom|custom script|cp_\w+\.py", "guides/custom-scripts/api/", "custom script"),
    (r"coverpoint template|covergroup|\.svh\b|template\.sv", "guides/coverpoint-templates/", "coverpoint template"),
    (r"coverage (hole|fail|debug|miss|fix|0%)|fix coverage|missing bin", "guides/custom-scripts/coverage-workflow/", "coverage workflow"),
    (r"\bhang(ing|s)?\b|infinite loop|stuck test|trap loop", "guides/debugging-hangs/", "hang debugging"),
    (r"normative|Vx\.yaml|norm[-_/]rule|fill_vx", "guides/normative-rules/", "normative rules"),
    (r"register (allocation|alloc|pick|number)|hardcoded register|pick.*register", "guides/register-allocation.md", "register allocation"),
    (r"priv test|tests/priv|@add_priv_test_generator|priv-?mode", "guides/architecture/privileged-test-generators-two-paths-pick-right-one/", "priv tests"),
    (r"vector reference|encoding|funct3|funct6|FP hex", "guides/vector-reference/", "vector reference"),
    (r"simulator|sail bug|spike disagreement|unsupported_test", "guides/simulator-issues/", "simulator issues"),
    (r"build|architecture|directory layout|make target", "guides/architecture/", "architecture/build"),
    (r"pitfall|known bug|past issue|fsflagsi|RVVI", "guides/pitfalls/", "known pitfalls"),
]

# Legacy path-regex fallback if Sonnet fails.
FALLBACK_PATH_RULES = [
    (r"tools/fill_vx_coverpoints\.py$|coverpoints/norm/.*\.ya?ml$", "guides/normative-rules/", "norm YAML tooling"),
    (r"generators/coverage/src/covergroupgen/templates/", "guides/coverpoint-templates/", "coverpoint template"),
    (r"generators/testgen/scripts/custom/cp_custom_.*\.py$", "guides/custom-scripts/api/", "custom script"),
    (r"generators/testgen/.*\.py$", "guides/register-allocation.md", "register allocation rule"),
    (r"working-testplans/.*\.csv$", "guides/csv-editing/", "CSV editing"),
    (r"\.S$", "guides/debugging-hangs/", "asm test (likely hang debug)"),
]

BLOCK_PATHS = [
    (r"coverpoints/unpriv/.*_coverage(_init)?\.svh$",
     "Generated file. Edit template under generators/coverage/src/covergroupgen/templates/ + run `make vector-tests`."),
    (r"coverpoints/priv/.*_coverage(_init)?\.svh$",
     "Generated file. Edit source CSV/template + re-run covergroupgen."),
    (r"tests/rv(32|64)i/.*\.S$",
     "Generated test. Edit source script/template/CSV + run `make vector-tests`."),
    (r"(?<!working-)testplans/.*\.csv$",
     "Live CSV. Use tools/csv_edit.py — never edit live CSVs by hand."),
]


def reminder(target, reason):
    return f"{REMINDER_PREFIX} {target} BEFORE proceeding ({reason}). If not yet read this session, open with the Read tool now."


# ---------- prompt mode ----------

def handle_prompt():
    data = json.load(sys.stdin)
    prompt = data.get("prompt", "") or ""
    sid = data.get("session_id", "") or ""
    injected = load_session(sid)
    hits, seen, new_targets = [], set(), []
    for pat, target, reason in PROMPT_RULES:
        if re.search(pat, prompt, re.IGNORECASE) and target not in seen:
            seen.add(target)
            if target in injected:
                continue
            new_targets.append(target)
            hits.append(reminder(target, reason))
    if hits:
        injected.update(new_targets)
        save_session(sid, injected)
        _log_request(sid, "prompt", prompt, new_targets, sonnet_ok=True)
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(hits),
            }
        }))


# ---------- tool mode ----------

def load_cache():
    if not CACHE_PATH.exists():
        return {}
    try:
        return json.loads(CACHE_PATH.read_text())
    except Exception:
        return {}


def save_cache(cache):
    try:
        CACHE_PATH.write_text(json.dumps(cache))
    except Exception as e:
        print(f"[route.py] cache write failed: {e}", file=sys.stderr)


def session_file(sid):
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_DIR / f"{re.sub(r'[^A-Za-z0-9_-]', '_', sid)}.json"


def load_session(sid):
    if not sid:
        return set()
    f = session_file(sid)
    if not f.exists():
        return set()
    try:
        d = json.loads(f.read_text())
        if time.time() - d.get("t", 0) > SESSION_TTL:
            return set()
        return set(d.get("shards", []))
    except Exception:
        return set()


def save_session(sid, shards):
    if not sid:
        return
    try:
        session_file(sid).write_text(json.dumps({"t": time.time(), "shards": sorted(shards)}))
    except Exception as e:
        print(f"[route.py] session write failed: {e}", file=sys.stderr)


def prune_sessions():
    if not SESSION_DIR.exists():
        return
    now = time.time()
    for f in SESSION_DIR.glob("*.json"):
        try:
            if now - f.stat().st_mtime > SESSION_TTL:
                f.unlink()
        except Exception:
            pass


def _append_jsonl(path: Path, row: dict):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[route.py] jsonl append err {path}: {e}", file=sys.stderr)


def _rotate_log(path: Path):
    try:
        if path.exists() and path.stat().st_size > ROUTE_LOG_MAX:
            backup = path.with_suffix(path.suffix + ".1")
            if backup.exists():
                backup.unlink()
            path.rename(backup)
    except Exception:
        pass


def _log_request(sid: str, mode: str, trigger: str, shards: list, sonnet_ok: bool) -> str:
    rid = uuid.uuid4().hex[:12]
    _rotate_log(ROUTE_LOG)
    _append_jsonl(ROUTE_LOG, {
        "type": "request",
        "ts": time.time(),
        "session_id": sid,
        "request_id": rid,
        "mode": mode,
        "trigger": trigger[:300],
        "shards": shards,
        "sonnet_ok": bool(sonnet_ok),
    })
    return rid


def _iter_jsonl(path: Path):
    if not path.exists():
        return
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def index_sha():
    if not INDEX_PATH.exists():
        return ""
    return hashlib.sha256(INDEX_PATH.read_bytes()).hexdigest()[:16]


def call_sonnet(file_path, tool_name):
    """Ask Sonnet which shards apply. Return list of shard paths or None on failure."""
    if not INDEX_PATH.exists():
        return None
    index_text = INDEX_PATH.read_text()
    prompt = f"""Tool: {tool_name}
Tool target: {file_path}

Below is the SHARD-INDEX. Pick which shards the main agent must read before acting on this tool target. Output STRICT JSON: an array of shard paths (strings). Nothing else, no prose, no markdown. Empty array `[]` if none apply. Hard cap 8 shards.

---
{index_text}
"""
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", "sonnet",
             "--output-format", "text", "--no-session-persistence",
             "--disable-slash-commands", prompt],
            capture_output=True, text=True, timeout=SONNET_TIMEOUT,
        )
        out = result.stdout.strip()
        # Strip code fences if Sonnet adds them.
        out = re.sub(r"^```(?:json)?\s*|\s*```$", "", out).strip()
        # Find JSON array if there's surrounding noise.
        m = re.search(r"\[.*\]", out, re.DOTALL)
        if not m:
            return None
        arr = json.loads(m.group(0))
        if not isinstance(arr, list):
            return None
        return [str(s) for s in arr][:10]
    except subprocess.TimeoutExpired:
        print("[route.py] sonnet timeout", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[route.py] sonnet error: {e}", file=sys.stderr)
        return None


def fallback_shards(path):
    seen, out = set(), []
    for pat, target, reason in FALLBACK_PATH_RULES:
        if re.search(pat, path) and target not in seen:
            seen.add(target)
            out.append(target)
    return out


def handle_tool():
    data = json.load(sys.stdin)
    tool = data.get("tool_name")
    sid = data.get("session_id", "") or ""
    if tool not in ("Read", "Edit", "Write", "MultiEdit"):
        return
    path = (data.get("tool_input") or {}).get("file_path", "") or ""
    if not path:
        return

    # Hard block (writes only)
    if tool in ("Edit", "Write", "MultiEdit"):
        for pat, msg in BLOCK_PATHS:
            if re.search(pat, path):
                print(f"BLOCKED write to {path}\n{msg}", file=sys.stderr)
                sys.exit(2)

    # Skip routing for our own shards/index — avoid recursive Sonnet on Read of guide files.
    if (path.startswith("guides/") or "/guides/" in path
            or path.endswith("CLAUDE.md") or path.endswith("SHARD-INDEX.md")
            or path.endswith(".original.md")):
        return

    # Cache lookup
    sha = index_sha()
    cache_key = f"{tool}|{path}|{sha}"
    cache = load_cache()
    entry = cache.get(cache_key)
    now = time.time()
    sonnet_ok = True
    if entry and now - entry.get("t", 0) < CACHE_TTL:
        shards = entry.get("shards", [])
    else:
        shards = call_sonnet(path, tool)
        if shards is None:
            sonnet_ok = False
            shards = fallback_shards(path)
        cache[cache_key] = {"t": now, "shards": shards}
        # Prune old entries
        cache = {k: v for k, v in cache.items() if now - v.get("t", 0) < CACHE_TTL * 24}
        save_cache(cache)

    if not shards:
        _log_request(sid, "tool", f"{tool}:{path}", [], sonnet_ok)
        return

    injected = load_session(sid)
    new_shards = [s for s in shards if s not in injected]
    if not new_shards:
        return
    injected.update(new_shards)
    save_session(sid, injected)
    prune_sessions()
    _log_request(sid, "tool", f"{tool}:{path}", new_shards, sonnet_ok)

    hits = [reminder(s, "shard router pick") for s in new_shards]
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": "\n".join(hits),
        }
    }))


# ---------- stop mode (knowledge capture) ----------

LEARN_LOG = Path("/tmp/route-learn.log")


def _read_transcript_tail(path, max_assistants=2):
    """Return last N assistant text turns concatenated."""
    if not path or not Path(path).exists():
        return ""
    msgs = []
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") != "assistant":
                    continue
                msg = rec.get("message", {})
                content = msg.get("content", [])
                if isinstance(content, list):
                    text_parts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                    text = "\n".join(t for t in text_parts if t)
                elif isinstance(content, str):
                    text = content
                else:
                    text = ""
                if text.strip():
                    msgs.append(text)
    except Exception as e:
        print(f"[route.py] transcript read err: {e}", file=sys.stderr)
        return ""
    return "\n\n---\n\n".join(msgs[-max_assistants:])


def _call_sonnet_raw(prompt, timeout=SONNET_TIMEOUT):
    try:
        r = subprocess.run(
            ["claude", "-p", "--model", "sonnet",
             "--output-format", "text", "--no-session-persistence",
             "--disable-slash-commands", prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip()
    except subprocess.TimeoutExpired:
        print("[route.py] stop sonnet timeout", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"[route.py] stop sonnet err: {e}", file=sys.stderr)
        return ""


def _log_patch_outcome(status, shard_rel, note, **extra):
    """Always log every patch_pass outcome to ROUTE_LOG for visibility."""
    row = {
        "type": "patch_outcome",
        "ts": time.time(),
        "status": status,
        "shard": shard_rel,
        "note": (note or "")[:200],
    }
    row.update(extra)
    _append_jsonl(ROUTE_LOG, row)


def _resolve_shard_target(shard_rel):
    """Map shard path to a concrete file. Dir → ask Sonnet to pick best .md.

    Returns (Path|None, status_str). status_str only used when None.
    """
    target = REPO / shard_rel
    if not target.exists():
        return None, "missing_target"
    if target.is_file():
        return target, ""
    if not target.is_dir():
        return None, "not_file_or_dir"
    md_files = sorted([p for p in target.rglob("*.md") if p.is_file()])
    if not md_files:
        return None, "dir_no_md"
    if len(md_files) == 1:
        return md_files[0], ""
    return md_files, "dir_multi"  # caller picks


def _patch_pass():
    """Drain up to N entries from PATCH_QUEUE; ask Sonnet for a focused shard edit each.

    Path-allowlisted to guides/**. Successful patches consumed from queue;
    failures kept for retry next session. Hard time-budgeted.
    """
    if not PATCH_QUEUE.exists():
        return
    try:
        lines = [l for l in PATCH_QUEUE.read_text().splitlines() if l.strip()]
    except Exception:
        return
    if not lines:
        return
    entries = [json.loads(l) for l in lines if l.startswith("{")]
    take, rest = entries[:3], entries[3:]
    kept = list(rest)
    budget_end = time.time() + 8.0
    for e in take:
        if time.time() > budget_end:
            kept.append(e)
            _log_patch_outcome("budget_exhausted", e.get("shard", ""), e.get("note", ""))
            continue
        shard_rel = (e.get("shard") or "").strip()
        note = (e.get("note") or "").strip()
        verdict = (e.get("verdict") or "").strip()
        if (not shard_rel or ".." in shard_rel
                or not shard_rel.startswith("guides/")):
            _log_patch_outcome("bad_path", shard_rel, note)
            continue  # drop bad entry
        resolved, status = _resolve_shard_target(shard_rel)
        if resolved is None:
            _log_patch_outcome(status, shard_rel, note)
            continue  # drop bad entry
        # Dir with multiple .md → ask Sonnet to pick file.
        if isinstance(resolved, list):
            md_files = resolved
            rel_names = [str(p.relative_to(REPO)) for p in md_files]
            pick_prompt = (
                "Shard feedback targets a directory. Pick ONE file from the list "
                "where this feedback should be addressed. Output STRICT JSON: "
                "{\"file\": \"<one path exactly from list>\"}. If none fit, {}.\n\n"
                f"FEEDBACK verdict={verdict}; note={note}\n\n"
                "FILES:\n" + "\n".join(rel_names) + "\n"
            )
            pick_out = _call_sonnet_raw(pick_prompt, timeout=10)
            chosen = None
            if pick_out:
                pick_out = re.sub(r"^```(?:json)?\s*|\s*```$", "", pick_out).strip()
                m = re.search(r"\{.*\}", pick_out, re.DOTALL)
                if m:
                    try:
                        pj = json.loads(m.group(0))
                        f = (pj.get("file") or "").strip()
                        if f in rel_names:
                            chosen = REPO / f
                    except Exception:
                        pass
            if chosen is None:
                kept.append(e)
                _log_patch_outcome("dir_pick_fail", shard_rel, note)
                continue
            target = chosen
            shard_rel = str(chosen.relative_to(REPO))
        else:
            target = resolved
        try:
            cur = target.read_text()
        except Exception as ex:
            kept.append(e)
            _log_patch_outcome("read_err", shard_rel, note, err=str(ex))
            continue
        prompt = (
            "You receive feedback that a shard gave wrong or partial guidance. "
            "Propose a MINIMAL edit. Output STRICT JSON only: "
            "{\"replace\": \"<exact existing substring>\", "
            "\"with\": \"<replacement>\"} OR "
            "{\"append\": \"<lines to append>\"}. "
            "Caveman-ultra style. No headings. If unsure, output {}.\n\n"
            f"SHARD PATH: {shard_rel}\n"
            f"FEEDBACK verdict={verdict}; note={note}\n\n"
            "--- SHARD CONTENT ---\n"
            f"{cur}\n"
        )
        out = _call_sonnet_raw(prompt, timeout=10)
        if not out:
            kept.append(e)
            _log_patch_outcome("sonnet_empty", shard_rel, note)
            continue
        out = re.sub(r"^```(?:json)?\s*|\s*```$", "", out).strip()
        m = re.search(r"\{.*\}", out, re.DOTALL)
        if not m:
            kept.append(e)
            _log_patch_outcome("no_json", shard_rel, note, raw=out[:200])
            continue
        try:
            pick = json.loads(m.group(0))
        except Exception as ex:
            kept.append(e)
            _log_patch_outcome("parse_fail", shard_rel, note, err=str(ex))
            continue
        if not pick:
            _log_patch_outcome("sonnet_unsure", shard_rel, note)
            continue  # drop — sonnet said {}
        applied = False
        reason = "unknown"
        try:
            if "replace" in pick and "with" in pick:
                if pick["replace"] in cur:
                    new = cur.replace(pick["replace"], pick["with"], 1)
                    target.write_text(new)
                    applied = True
                else:
                    reason = "replace_not_found"
            elif pick.get("append"):
                sep = "" if cur.endswith("\n\n") else ("\n" if cur.endswith("\n") else "\n\n")
                target.write_text(cur + sep + pick["append"].rstrip() + "\n")
                applied = True
            else:
                reason = "no_action_keys"
        except Exception as ex:
            print(f"[route.py] patch apply err: {ex}", file=sys.stderr)
            kept.append(e)
            _log_patch_outcome("apply_err", shard_rel, note, err=str(ex))
            continue
        if applied:
            _append_jsonl(ROUTE_LOG, {
                "type": "patch_applied",
                "ts": time.time(),
                "shard": shard_rel,
                "note": note[:200],
            })
        else:
            kept.append(e)
            _log_patch_outcome("not_applied", shard_rel, note, reason=reason)
    # Rewrite queue with survivors.
    try:
        PATCH_QUEUE.write_text("".join(json.dumps(e) + "\n" for e in kept))
    except Exception:
        pass


def _audit_nudge():
    """Emit stderr nudge if recent feedback skews negative."""
    cutoff = time.time() - AUDIT_WINDOW
    large = 0
    graded = 0
    negative = 0
    for row in _iter_jsonl(ROUTE_LOG):
        if row.get("type") != "feedback":
            continue
        if row.get("ts", 0) < cutoff:
            continue
        graded += 1
        sev = row.get("severity", "none")
        verdict = row.get("verdict", "")
        if sev == "large":
            large += 1
        if verdict in ("useless", "wrong"):
            negative += 1
    ratio = (negative / graded) if graded else 0.0
    nudge = None
    if large >= AUDIT_LARGE_THRESHOLD:
        nudge = f"[route.py] AUDIT RECOMMENDED — {large} large-severity feedbacks in 24h. Run opus per guides/REPO-AUDIT.md."
    elif graded >= AUDIT_NEG_MIN and ratio >= AUDIT_NEG_RATIO:
        nudge = (
            f"[route.py] AUDIT RECOMMENDED — {negative}/{graded} "
            f"({ratio:.0%}) negative feedbacks in 24h. Run opus per guides/REPO-AUDIT.md."
        )
    if nudge:
        print(nudge, file=sys.stderr)
    # Surface stuck patch queue depth.
    try:
        if PATCH_QUEUE.exists():
            depth = sum(1 for l in PATCH_QUEUE.read_text().splitlines() if l.strip())
            if depth >= 3:
                print(f"[route.py] patch queue depth={depth} — check memory/<branch>/route-log.jsonl for patch_outcome rows.", file=sys.stderr)
    except Exception:
        pass


def handle_stop():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return  # never recurse
    # Always-run maintenance passes (independent of learning).
    _patch_pass()
    _audit_nudge()
    transcript = data.get("transcript_path", "")
    tail = _read_transcript_tail(transcript)
    if not tail or len(tail) < 200:
        return  # too short to have learned anything
    sid = data.get("session_id", "") or ""
    injected_shards = sorted(load_session(sid)) if sid else []

    # Stage 1: did we learn anything worth saving? Also (lightweight, same
    # Sonnet call) grade which injected shards were actually needed this
    # session. GOAL of the shard-utility grade: make future shard injection
    # more efficient. The router only improves if it learns which shards
    # earned their slot. 'useless' (info NOT needed) is a first-class helpful
    # signal — it tells the router/auditor to inject less aggressively for
    # similar triggers. 'good' is NOT a polite default.
    # Default learned = false. No fabrication. Require evidence quote that substring-matches transcript.
    shard_list_block = (
        "\n".join(f"- {s}" for s in injected_shards) if injected_shards else "(none)"
    )
    p1 = (
        "You grade a coding-agent transcript from the riscv-arch-test-claude repo. "
        "DEFAULT verdict is learned:false. Set learned:true ONLY if one of these holds:\n"
        " (a) Agent hit a NON-OBVIOUS gotcha, hidden constraint, undocumented project "
        "convention, tool quirk, or bug+fix that — had it been documented in a shard up "
        "front — would have measurably saved time or tool calls THIS session.\n"
        " (b) Agent IMPLEMENTED something new this session (new script, new hook, new "
        "generator, new make target, new CSV column, new helper, new shard, new "
        "workflow/convention) that future sessions will need to know about — i.e. its "
        "existence/usage/contract is not yet documented in any shard. The 'learning' is "
        "the new artifact + how to use it.\n\n"
        "Do NOT manufacture content to fill the slot. The following are ALWAYS "
        "learned:false:\n"
        " - Routine task completion against an existing well-documented workflow.\n"
        " - Edits to existing code that don't change its contract or introduce new usage.\n"
        " - Restating facts already in CLAUDE.md / SHARD-INDEX / any guide.\n"
        " - Generic 'best practices' or inferred advice not grounded in a concrete "
        "   surprise or new artifact from this session.\n"
        " - Speculation about future sessions.\n\n"
        "If learned:true, you MUST quote an exact substring from the transcript as "
        "evidence — for (a) the surprise (error message, wrong assumption corrected, "
        "discovered constraint); for (b) the creation/use of the new artifact (file "
        "path being written, new function defined, new command run).\n\n"
        "ALSO grade the injected shards listed below. GOAL: tune future shard "
        "injection. For each shard, pick exactly one verdict:\n"
        "  useless — topic never came up / info not needed this session "
        "(HELPFUL signal — do not avoid it to be polite)\n"
        "  good    — transcript shows agent used or relied on the shard's content\n"
        "  partial — relevant but missing/outdated detail caused friction\n"
        "  wrong   — shard content contradicted reality and misled the agent\n"
        "If no shards were injected, return an empty shard_utility list.\n\n"
        "Output STRICT JSON only: "
        "{\"learned\": true|false, \"summary\": \"<1-3 caveman-ultra lines>\", "
        "\"evidence\": \"<exact substring from transcript, or empty>\", "
        "\"shard_utility\": [{\"shard\":\"guides/...\",\"verdict\":\"useless|good|partial|wrong\","
        "\"note\":\"<one short line>\"}, ...]}.\n"
        "If learned:false, summary and evidence MUST both be empty strings. "
        "shard_utility is independent of learned and should be filled whenever "
        "shards were injected.\n\n"
        f"INJECTED SHARDS THIS SESSION:\n{shard_list_block}\n\n"
        f"---\n{tail}\n"
    )
    out1 = _call_sonnet_raw(p1)
    if not out1:
        return
    out1 = re.sub(r"^```(?:json)?\s*|\s*```$", "", out1).strip()
    m = re.search(r"\{.*\}", out1, re.DOTALL)
    if not m:
        return
    try:
        verdict = json.loads(m.group(0))
    except Exception:
        return
    # Record shard-utility feedback rows regardless of learned outcome.
    util = verdict.get("shard_utility") or []
    if isinstance(util, list) and injected_shards:
        valid_v = {"useless", "good", "partial", "wrong"}
        injected_set = set(injected_shards)
        for g in util:
            if not isinstance(g, dict):
                continue
            shard_rel = (g.get("shard") or "").strip()
            v = (g.get("verdict") or "").strip().lower()
            note = (g.get("note") or "").strip()[:200]
            if shard_rel not in injected_set or v not in valid_v:
                continue
            severity = "small" if v in ("partial", "wrong") else "none"
            _append_jsonl(ROUTE_LOG, {
                "type": "feedback",
                "ts": time.time(),
                "session_id": sid,
                "shard": shard_rel,
                "verdict": v,
                "severity": severity,
                "note": note,
                "source": "auto-grade",
            })
            if v in ("partial", "wrong"):
                try:
                    with open(PATCH_QUEUE, "a") as f:
                        f.write(json.dumps({
                            "shard": shard_rel,
                            "verdict": v,
                            "severity": severity,
                            "note": note,
                        }) + "\n")
                except Exception as ex:
                    print(f"[route.py] patch enqueue err: {ex}", file=sys.stderr)
    if not verdict.get("learned") or not verdict.get("summary"):
        return
    summary = verdict["summary"].strip()
    evidence = (verdict.get("evidence") or "").strip()
    # Fabrication guard: evidence must be a substring of the transcript tail.
    if not evidence or evidence not in tail:
        try:
            with open(LEARN_LOG, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} FABRICATION_DROP: {summary[:120]}\n")
        except Exception:
            pass
        return

    # Stage 2: append to existing shard OR create new shard.
    if not INDEX_PATH.exists():
        return
    index_text = INDEX_PATH.read_text()
    p2 = (
        "Decide where to record this new knowledge from a coding-agent session. Two options:\n"
        " A. APPEND to an existing shard from SHARD-INDEX (PREFERRED when a topically "
        "    matching shard exists AND it is still short — shards aim for <50 lines).\n"
        " B. CREATE a new shard (ONLY when no existing shard fits topically, OR the "
        "    best-fit shard is already long and adding here would bloat it past ~50 lines, "
        "    OR the knowledge is a brand-new artifact deserving its own entry point).\n\n"
        "Output STRICT JSON only. Schema:\n"
        " - Append:  {\"action\":\"append\", \"shard\":\"guides/...md\", \"append\":\"<caveman-ultra body>\"}\n"
        " - Create:  {\"action\":\"create\", \"shard\":\"guides/<dir>/<slug>.md\", "
        "\"content\":\"<full new-shard body, caveman-ultra, no top-level # heading>\", "
        "\"index_section\":\"## <exact section header from SHARD-INDEX>\", "
        "\"index_row\":\"| guides/<dir>/<slug>.md | <When-column trigger phrase> |\"}\n"
        " - Skip:    {\"action\":\"skip\"}\n\n"
        "Caveman-ultra = arrows for causality, drop articles/conjunctions, "
        "abbreviate (DB/auth/cfg/req/res/fn/impl), one word when possible. "
        "Code symbols, file paths, and error strings stay exact. Append body max 6 lines. "
        "New-shard content max 40 lines. index_section MUST match a header that appears "
        "verbatim in SHARD-INDEX below.\n\n"
        f"NEW KNOWLEDGE:\n{summary}\n\n"
        f"---\n{index_text}\n"
    )
    out2 = _call_sonnet_raw(p2, timeout=SONNET_TIMEOUT + 10)
    if not out2:
        return
    out2 = re.sub(r"^```(?:json)?\s*|\s*```$", "", out2).strip()
    m2 = re.search(r"\{.*\}", out2, re.DOTALL)
    if not m2:
        return
    try:
        pick = json.loads(m2.group(0))
    except Exception:
        return
    action = (pick.get("action") or "").strip().lower()
    shard_rel = (pick.get("shard") or "").strip()
    if action == "append":
        append = (pick.get("append") or "").strip()
        if not shard_rel or not append:
            return
        if ".." in shard_rel or not shard_rel.startswith("guides/"):
            return
        target = REPO / shard_rel
        if not target.exists() or not target.is_file():
            return
        try:
            cur = target.read_text()
            sep = "" if cur.endswith("\n\n") else ("\n" if cur.endswith("\n") else "\n\n")
            target.write_text(cur + sep + append.rstrip() + "\n")
            with open(LEARN_LOG, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {shard_rel}: {summary[:120]}\n")
        except Exception as e:
            print(f"[route.py] shard append err: {e}", file=sys.stderr)
    elif action == "create":
        content = (pick.get("content") or "").strip()
        index_section = (pick.get("index_section") or "").strip()
        index_row = (pick.get("index_row") or "").strip()
        if not (shard_rel and content and index_section and index_row):
            return
        if ".." in shard_rel or not shard_rel.startswith("guides/") or not shard_rel.endswith(".md"):
            return
        target = REPO / shard_rel
        if target.exists():
            return  # refuse to clobber
        # index_section must appear verbatim as a line in index_text.
        idx_lines = index_text.splitlines()
        try:
            sec_idx = idx_lines.index(index_section)
        except ValueError:
            return
        # index_row sanity: markdown table row referencing the new shard.
        if not (index_row.startswith("|") and shard_rel in index_row and index_row.endswith("|")):
            return
        # Find end of this section's table (next "## " header or EOF).
        insert_at = len(idx_lines)
        for i in range(sec_idx + 1, len(idx_lines)):
            if idx_lines[i].startswith("## "):
                insert_at = i
                break
        # Walk back past trailing blank lines in this section so row sits with the table.
        while insert_at > sec_idx + 1 and idx_lines[insert_at - 1].strip() == "":
            insert_at -= 1
        idx_lines.insert(insert_at, index_row)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content.rstrip() + "\n")
            INDEX_PATH.write_text("\n".join(idx_lines) + ("\n" if index_text.endswith("\n") else ""))
            with open(LEARN_LOG, "a") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} CREATE {shard_rel}: {summary[:120]}\n")
        except Exception as e:
            print(f"[route.py] shard create err: {e}", file=sys.stderr)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    try:
        if mode == "prompt":
            handle_prompt()
        elif mode == "stop":
            handle_stop()
        else:
            handle_tool()
    except Exception as e:
        print(f"[route.py] error: {e}", file=sys.stderr)
        sys.exit(0)
