# Coverage Generator (`generate.py`)


`generators/coverage/src/covergroupgen/generate.py` produces per-extension `_coverage.svh` / `_coverage_init.svh` files:

- `write_covergroups` writes to `coverpoints/unpriv/` from testplans at root of `testplans/` (SEW-expanded for vector extensions).
- `write_priv_covergroups` writes to `coverpoints/priv/` from testplans under `testplans/priv/` (no SEW expansion).
- Both share `_parse_testplan_csv` (CSV parsing) and `_write_extension_files` (per-extension file writer); prefer extending those helpers over duplicating logic.

Regenerate via `uv run covergroupgen testplans` (or `make covergroupgen`). No hand-edit generated files under `coverpoints/unpriv/` or `coverpoints/priv/` for extensions with CSV — edits clobbered next run.
