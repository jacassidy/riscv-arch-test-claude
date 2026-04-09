# riscv-arch-test-claude

Claude working files (guides, scripts, tools, memory) for the `riscv-arch-test-cvw` repo and its worktrees.

## Setup (main repo)

```bash
ln -s $WALLY/addins/riscv-arch-test-claude/CLAUDE.md $WALLY/addins/riscv-arch-test-cvw/CLAUDE.md
```

Then symlink the Claude Code project memory:
```bash
rm -rf ~/.claude/projects/-home-jacassidy-cvw-addins-riscv-arch-test-cvw/memory
ln -s /home/jacassidy/cvw/addins/riscv-arch-test-claude/memory \
      ~/.claude/projects/-home-jacassidy-cvw-addins-riscv-arch-test-cvw/memory
```

## Setup (new worktree)

After creating a worktree (e.g. `git worktree add ../my-worktree branch-name`):

```bash
# 1. Symlink CLAUDE.md into the worktree
ln -s ../riscv-arch-test-claude/CLAUDE.md <worktree>/CLAUDE.md

# 2. Share memory with the worktree (replace <worktree-dir-name> with the directory name)
mkdir -p ~/.claude/projects/-home-jacassidy-cvw-addins-<worktree-dir-name>
ln -s /home/jacassidy/cvw/addins/riscv-arch-test-claude/memory \
      ~/.claude/projects/-home-jacassidy-cvw-addins-<worktree-dir-name>/memory
```

## Notes

- All Python scripts auto-detect the repo root from cwd via `git rev-parse --show-toplevel`, so they work in any worktree without configuration.
- Memory is stored in this repo under `memory/` and symlinked into each Claude Code project directory — single source of truth, no duplicates.
