# 3. End-to-end fix workflow


```bash
cd /home/jacassidy/cvw/addins/riscv-arch-test-claude

# 1. Re-extract spec quotes if the spec changed
uv run python tools/extract_norm_quotes.py --out /tmp/norm_quotes.json

# 2. Generate / refresh audit
uv run python tools/audit_norm_yaml.py    # writes /tmp/vx_audit.csv + .json

# 3. Inspect SUSPECT / PLACEHOLDER / GENERIC_ONLY rows; produce a JSON patch
#    (manual or via sub-agent — see § 5 below)

# 4. Apply patch and regenerate Vx.yaml
uv run python tools/update_norm_csv.py /tmp/my_patch.json
(cd /home/jacassidy/normative_rules && make covergroupgen)   # required before fill
uv run python tools/fill_vx_coverpoints.py

# 5. Re-audit to confirm
uv run python tools/audit_norm_yaml.py
```
