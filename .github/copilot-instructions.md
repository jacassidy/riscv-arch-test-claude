# Copilot Instructions

> Applies to GitHub Copilot. Claude Code uses CLAUDE.md + `.claude/hooks/route.py` and ignores this file.
> **Read `CLAUDE.md` first — all hard rules live there.** This file only covers what Copilot must do that Claude's hooks would otherwise automate.

Copilot runs fully agentically here. The `.claude/hooks/` machinery does not fire for Copilot, so Copilot must perform those duties itself.

## 1. Shard routing (replaces `route.py`)

Before answering any non-trivial question or touching any file:

1. Open `guides/SHARD-INDEX.md`.
2. Match task keywords + target path against entries.
3. Read every matching shard fully before editing.
4. Re-consult on task switch (new file, new subsystem, new question). Context drift = #1 mistake source.

If no shard matches, proceed and note that no shard guidance was found.

## 2. Shard grading (replaces `/route-feedback`)

When a shard you read was useless / wrong / partial / notably good, log it. Append one JSONL line to `memory/route-log.jsonl` with fields:

```
{"ts": <unix>, "shard": "guides/...", "verdict": "useless|wrong|partial|good", "severity": "none|small|large", "note": "<one line>", "source": "copilot"}
```

- `large` severity → also append to `memory/audit-queue.jsonl` (triggers opus audit).
- `small` severity → append to `memory/route-patches.jsonl` (queued shard patch).

One entry per real grievance. Don't batch speculative grades.

## 3. Shard updates (replaces Stop-hook auto-patch)

When you discover a shard is outdated / missing info, fix it in the same session:

- Edit the shard directly with the corrected info.
- Keep `.md` style: bullets > prose, one source of truth per fact, delete stale lines.
- If the fix changes routing, update `guides/SHARD-INDEX.md`.

## 4. Repo audit (replaces opus audit nudge)

When `memory/audit-queue.jsonl` has ≥3 unresolved entries, or shard rot is obvious across a session, run the playbook at `guides/REPO-AUDIT.md` end-to-end. Don't wait to be told.

## 5. Compressed output (optional, opt-in)

Claude has a `caveman` mode (terse, fragments, no articles) that cuts tokens ~75%. Copilot may adopt the same style when the user asks for brevity ("be terse", "caveman", "less tokens"). Code, commits, and security warnings stay in normal prose. Resume normal prose if user says "normal mode".

## 6. Slash-command equivalents

Claude exposes these as `/commands`. Copilot has no slash UI; invoke the underlying action directly when the user names it:

| Claude command | Copilot action |
|---|---|
| `/route-feedback` | Append entry per §2. |
| `/caveman`, `/caveman lite\|full\|ultra` | Switch reply style per §5. |
| repo-audit (manual) | Run `guides/REPO-AUDIT.md` per §4. |

## 7. Out of bounds

Hard rules from `CLAUDE.md` are non-negotiable (no commits/stash/push, no editing generated files, no `-k` to make, no hardcoded registers). Hooks no longer enforce them for Copilot — you must self-enforce.
