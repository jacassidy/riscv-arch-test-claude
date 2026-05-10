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
from pathlib import Path

REPO = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path(__file__).resolve().parent.parent.parent))
INDEX_PATH = REPO / "guides" / "SHARD-INDEX.md"
CACHE_PATH = Path("/tmp/route-cache.json")
SESSION_DIR = Path("/tmp/route-sessions")
SESSION_TTL = 24 * 3600  # 1 day
CACHE_TTL = 3600  # 1 hour
SONNET_TIMEOUT = 25  # seconds (Claude Code kills long hooks)
REMINDER_PREFIX = "[route.py] READ"

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
    if entry and now - entry.get("t", 0) < CACHE_TTL:
        shards = entry.get("shards", [])
    else:
        shards = call_sonnet(path, tool)
        if shards is None:
            shards = fallback_shards(path)
        cache[cache_key] = {"t": now, "shards": shards}
        # Prune old entries
        cache = {k: v for k, v in cache.items() if now - v.get("t", 0) < CACHE_TTL * 24}
        save_cache(cache)

    if not shards:
        return

    injected = load_session(sid)
    new_shards = [s for s in shards if s not in injected]
    if not new_shards:
        return
    injected.update(new_shards)
    save_session(sid, injected)
    prune_sessions()

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


def handle_stop():
    data = json.load(sys.stdin)
    if data.get("stop_hook_active"):
        return  # never recurse
    transcript = data.get("transcript_path", "")
    tail = _read_transcript_tail(transcript)
    if not tail or len(tail) < 200:
        return  # too short to have learned anything

    # Stage 1: did we learn anything worth saving?
    p1 = (
        "Below is the last assistant response(s) from a coding agent working on "
        "the riscv-arch-test-claude repo. Did the agent discover any NEW durable "
        "knowledge (a non-obvious gotcha, hidden constraint, project convention, "
        "tool quirk, bug+fix) that future sessions should know? Routine task "
        "completion, code edits, and obvious facts do NOT count.\n\n"
        "Output STRICT JSON only: {\"learned\": true|false, \"summary\": \"<1-3 caveman-ultra lines>\"}.\n"
        "If false, summary = \"\".\n\n"
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
    if not verdict.get("learned") or not verdict.get("summary"):
        return
    summary = verdict["summary"].strip()

    # Stage 2: pick target shard + write caveman-ultra append.
    if not INDEX_PATH.exists():
        return
    index_text = INDEX_PATH.read_text()
    p2 = (
        "Pick the BEST existing shard from SHARD-INDEX below to append this new "
        "knowledge to. Output STRICT JSON only: {\"shard\": \"guides/...md\", "
        "\"append\": \"<caveman-ultra lines, no headings, append-ready>\"}. "
        "Caveman-ultra = arrows for causality, drop articles/conjunctions, "
        "abbreviate (DB/auth/cfg/req/res/fn/impl), one word when possible. "
        "Code symbols and error strings stay exact. Max 6 lines. "
        "If no shard fits well, output {\"shard\": \"\", \"append\": \"\"}.\n\n"
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
    shard_rel = (pick.get("shard") or "").strip()
    append = (pick.get("append") or "").strip()
    if not shard_rel or not append:
        return
    # Path safety: must be under guides/, must exist.
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
