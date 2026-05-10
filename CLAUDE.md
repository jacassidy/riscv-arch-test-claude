# CLAUDE.md

> Claude working files repo (`riscv-arch-test-claude`). Generated guides/scripts live here. Main working repo = current cwd (worktree). All edits target the worktree.

`.claude/settings.json` (symlinked into every worktree) hard-blocks `git commit`/`stash`/`push` + writes to generated files / live CSVs. Hooks fire on prompt + Read/Edit/Write/MultiEdit; Sonnet routes target path against `guides/SHARD-INDEX.md` and injects `READ <shard>` reminders. **When you see one, open the shard with the Read tool BEFORE acting.**

## Hard rules

- **Never `git commit`/`stash`/`push`** — user owns commits. `git add` only.
- **Never edit generated files**: `coverpoints/{unpriv,priv}/*_coverage.svh`, `tests/rv{32,64}i/**/*.S`. Edit source (template/script/CSV) → `make vector-tests`.
- **Never pass `-k`/`--keep-going` to `make`.** `hooks/make` wrapper enforces.
- **Never hardcode register numbers** (`x{N}/v{N}/f{N}`). See `guides/register-allocation.md`.
- **Re-read shard reminders on task switch.** Context drift = #1 mistake source.
- **`.md` style**: bullets > prose; delete as you edit; one source of truth per fact.

## Pointers

- Shard router table: `guides/SHARD-INDEX.md` (Sonnet reads — you don't, unless hook fails).
- Definition CSVs: `working-testplans/csvs/Vector - V{ls,x,f}_custom_definitions.csv`.
- RISC-V V spec: `/home/jacassidy/cvw/addins/riscv-isa-manual/src/v-st-ext.adoc`.
- `memory/` — state files only (e.g. `progress.json`). Prose → `guides/`.
