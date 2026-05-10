# riscv-arch-test-claude

Claude working files (guides, scripts, tools, hooks) for `riscv-arch-test-cvw` and worktrees.

## Setup (main repo)

```bash
# Symlink CLAUDE.md into the working repo
ln -s $WALLY/addins/riscv-arch-test-claude/CLAUDE.md $WALLY/addins/riscv-arch-test-cvw/CLAUDE.md

# Symlink .claude/ — provides settings.json (permissions + read-before-act hooks)
ln -s $WALLY/addins/riscv-arch-test-claude/.claude $WALLY/addins/riscv-arch-test-cvw/.claude

# Share Claude Code project memory dir
rm -rf ~/.claude/projects/-home-jacassidy-cvw-addins-riscv-arch-test-cvw/memory
ln -s /home/jacassidy/cvw/addins/riscv-arch-test-claude/memory \
      ~/.claude/projects/-home-jacassidy-cvw-addins-riscv-arch-test-cvw/memory
```

## Setup (new worktree)

After `git worktree add ../my-worktree branch-name`:

```bash
ln -s ../riscv-arch-test-claude/CLAUDE.md <worktree>/CLAUDE.md
ln -s ../riscv-arch-test-claude/.claude   <worktree>/.claude

# Share memory with the worktree (replace <worktree-dir-name> below)
mkdir -p ~/.claude/projects/-home-jacassidy-cvw-addins-<worktree-dir-name>
ln -s /home/jacassidy/cvw/addins/riscv-arch-test-claude/memory \
      ~/.claude/projects/-home-jacassidy-cvw-addins-<worktree-dir-name>/memory
```

## What's in `.claude/`

- `settings.json` — `permissions` allow Read + Bash, deny `git commit`/`stash`/`push`. Wires routing hook.
- `hooks/route.py` — fires on `UserPromptSubmit` + `PreToolUse`. Inject `READ <guide>` reminders matched on task keywords / target paths. Hard-block writes to generated files + live `testplans/*.csv`.

## Layout

```
riscv-arch-test-claude/
├── CLAUDE.md                 # short routing-table; universal rules only
├── .claude/                  # settings + read-before-act hooks (symlink into worktrees)
├── guides/                   # read-before-task references (routing-table targets)
├── memory/                   # state files only (e.g. progress.json) — NOT prose
├── tools/                    # csv_edit.py, isolate_coverpoint.py, fill_vx_coverpoints.py, etc.
├── scripts/claude-scripts/   # coverage tools, orchestrator
├── working-testplans/        # canonical CSV source + backups
├── hooks/                    # `make` wrapper that blocks `-k` (PATH=hooks:$PATH)
└── simulator-issues.md       # confirmed/suspected Sail bugs, with reproduction
```

## Notes

- Python scripts auto-detect repo root from cwd via `git rev-parse --show-toplevel` — work in any worktree, no config.
- `memory/` holds **only** state files (e.g. `progress.json`-style). Prose / how-to-do-X go in `guides/` — see CLAUDE.md routing table.