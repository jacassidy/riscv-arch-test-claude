# hooks/

Wrappers that intercept commands whose use signals deferred work.

## `make`

Refuses `make -k` / `make --keep-going` (and combined forms like `-knj4`).

Per CLAUDE.md (no-keep-going rule): the *instinct* to add `-k` is itself a
signal that you are facing a failure requiring IMMEDIATE root-cause
investigation. Suppressing failures hides bugs that must be fixed.

### Activate

```sh
export PATH="$HOME/cvw/addins/riscv-arch-test-claude/hooks:$PATH"
```

(Or symlink `hooks/make` into a directory already on `PATH` ahead of
`/usr/bin`, e.g. `~/.local/bin/make`.)

### Verify

```sh
make -k        # → exits 2 with the no-keep-going message
make -nj4 help # → passes through to /usr/bin/make
```
