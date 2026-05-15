# REPO-AUDIT — Opus playbook

> You are an Opus session invoked manually by the user to audit the
> riscv-arch-test-claude routing framework. You are the repository manager.
> Read this file fully BEFORE doing anything else. Do NOT auto-apply edits.

## When invoked

User says one of: "run repo audit", "audit the repo", "/audit". You then
follow the protocol below end-to-end and write a report. You ONLY edit files
under `guides/**` and `memory/**`. You NEVER commit, stash, or push.

## Inputs

- `memory/route-log.jsonl` — paired request + feedback rows.
- `memory/audit-queue.jsonl` — large-severity entries queued for you.
- `memory/route-patches.jsonl` — small entries Sonnet should auto-patch
  next Stop hook. Inspect for systemic issues; do NOT drain.
- `/tmp/route-learn.log` — Stop-hook learn-append history including
  `FABRICATION_DROP` lines (fabrication guard rejections).
- `guides/SHARD-INDEX.md` — current router routing target list.
- All shards under `guides/**`.
- `.claude/hooks/route.py` — current routing logic (PROMPT_RULES, etc.).

## Metrics to compute

Compute over the full available window of `route-log.jsonl`. Use a windowed
view at 7 / 30 / all-time and present each. Per-shard table with columns:

| metric | definition |
|---|---|
| picks | count of `request` rows where shard appears in `shards` |
| graded | count of paired `feedback` rows |
| good | count of `verdict:good` |
| useless | count of `verdict:useless` |
| wrong | count of `verdict:wrong` |
| partial | count of `verdict:partial` |
| large_sev | count of `severity:large` |
| neg_rate | (useless + wrong) / graded |
| last_pick | max ts among picks |
| last_positive | max ts among `verdict:good` |
| staleness_days | (now − last edit on disk) / 86400 |

Plus repo-wide:

- **Sonnet failure rate**: `request` rows with `sonnet_ok:false` ÷ total.
- **Empty-shard rate**: `request` rows with `shards:[]` ÷ total.
- **Fabrication rate**: count of `FABRICATION_DROP` ÷ (drops + appends).
- **Coverage gaps**: prompts that produced `shards:[]` but followed by long
  tool chains (heuristic — scan transcript paths if available; otherwise
  list the triggers and ask user).
- **Patch-applied count**: `type:patch_applied` rows in last 30 days.

## Decisions to propose

Write all recommendations to a report file. Do NOT auto-apply unless user
explicitly approves a specific item in chat.

1. **Shards to delete**: `graded ≥ 5 AND good = 0 AND neg_rate ≥ 0.5`,
   or `picks = 0 over ≥30 days AND staleness_days ≥ 60`.
2. **Shards to merge**: pairs that consistently get picked together (high
   co-pick rate) AND have low individual word counts. List candidates.
3. **Shards to split**: shards with `partial` ≥ 3 distinct notes covering
   different sub-topics. Propose split lines.
4. **PROMPT_RULES edits**: regex misfires (rule fires → shard graded
   `useless`). Propose narrower regex or removal.
5. **New shards from audit queue**: each `audit-queue.jsonl` entry whose
   `note` cannot be addressed by editing an existing shard.
6. **SHARD-INDEX updates**: when shards change, regenerate the router
   index entry text.

## Output contract

Create exactly these files:

- `memory/audit-report-<YYYY-MM-DD>.md` — full metrics tables + every
  proposed decision with rationale and the exact file change required.
- `memory/audit-patches/<YYYY-MM-DD>/<n>-<short-slug>.patch` — one
  unified diff per proposed change, applicable with `patch -p1`. User
  applies manually.

After producing the report, drain `audit-queue.jsonl` by moving its
contents to `memory/audit-queue-<YYYY-MM-DD>.archive.jsonl`. This is the
only auto-mutation you perform.

## Hard constraints (reiterated)

- No `git commit`, `git stash`, `git push`. `git add` is allowed but
  discouraged during audit (user owns staging).
- No edits to generated files; routing hooks already block these.
- No edits outside `guides/**` and `memory/**` unless the user explicitly
  approves a `route.py` change in chat — in which case touch
  `.claude/hooks/route.py` only.
- No new dependencies. Stdlib only for any helper scripts.
- Caveman-ultra style for shard appends; normal prose for the report
  itself.

## Effectiveness self-check

End the report with a one-paragraph self-assessment: did the metrics
clearly indicate the decisions you proposed, or are you guessing? If
guessing, explicitly list the missing telemetry that the next iteration
of route.py should capture.
