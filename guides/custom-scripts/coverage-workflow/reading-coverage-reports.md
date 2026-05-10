# Reading Coverage Reports


Use `coverage_summary.py` — not grep/file reads:

- `--uncovered` — compact table of instructions not at 100%
- `--bins <instruction>` — specific missing bins grouped by coverpoint

Report files: `work/sail-rv64-max/reports/` and `work/sail-rv32-max/reports/`

- `_overall_summary.txt` — safe read for high-level %
- `*_uncovered.txt` — large, use coverage_summary.py instead

If `<Category><SEW>_uncovered.txt` absent, that SEW = 100%.
