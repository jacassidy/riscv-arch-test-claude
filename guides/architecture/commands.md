# Commands


```bash
make --jobs                          # Generate and compile all tests
make vector-tests                    # Generate vector tests only
FAST=True timeout 60s make coverage   # Isolated coverpoint (60s max)
FAST=True timeout 300s make coverage # Full suite iteration (5 min max)
make clean                           # Remove generated tests AND covergroups (only after fixing a hang)
make clean-tests                     # Remove generated tests only
make CONFIG_FILES=config/duts/cvw/cvw-rv64gc/test_config.yaml EXTENSIONS=I,M,A
make lint / make lint-fix / make format
```

**Never pass `--keep-going` / `-k` to any `make` invocations.** Hides failures that need addressing — let build stop on first error.

### Incremental Rebuild (no clean needed)

After fixing testgen script, regenerate and re-run coverage without `make clean`:

```bash
make vector-tests                    # Regenerates .S files (~30s)
rm work/sail-rv64-max/build/rv64i/<Ext>/*.sig   # Delete sigs for affected tests
FAST=True make coverage              # Recompiles elfs (~2 min), re-sims only missing sigs
```

If test content unchanged (same seed), coverage finishes ~2s. See `guides/custom-scripts/CLAUDE-coverage-workflow.md` for details.
