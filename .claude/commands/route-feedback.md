---
description: Grade an injected shard reminder. Use when route.py reminders were useless, wrong, partial, or notably good.
---

# /route-feedback

Grade one shard reminder injected this session by `route.py`. Used by the
repo-audit pipeline to find rotten shards and bad routing rules.

## What to do

1. Pick ONE shard you want to grade (most recent or most-impactful pick).
2. Run the helper with these fields. If you have arg text after the command,
   parse it; otherwise fill in your best assessment.

```
$CLAUDE_PROJECT_DIR/scripts/claude-scripts/route_feedback.py \
  --session-id "$CLAUDE_SESSION_ID" \
  --shard "<guides/...>" \
  --verdict <useless|wrong|partial|good> \
  --severity <none|small|large> \
  --note "<one short line>"
```

Field meanings:
- **shard**: exact path from the `READ guides/...` reminder.
- **verdict**:
  - `useless` — reminder was irrelevant to the task.
  - `wrong` — reminder pointed at a shard whose content contradicted reality.
  - `partial` — relevant but missing or outdated info.
  - `good` — shard saved time / prevented a mistake.
- **severity**:
  - `large` — wrong info caused real damage or a long wrong path; queues an opus audit item.
  - `small` — minor; queues a Sonnet patch for next-session auto-fix.
  - `none` — informational (use with `good`, or for trivial misses).
- **note**: one line, what was wrong and what the shard should say instead.

## Output

After running, briefly tell the user what you submitted. Do NOT batch many
calls; one per `/route-feedback` invocation.

Args from user (if any): $ARGUMENTS
