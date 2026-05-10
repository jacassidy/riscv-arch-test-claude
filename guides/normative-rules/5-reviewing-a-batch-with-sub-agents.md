# 5. Reviewing a batch with sub-agents


Each sub-agent gets:
1. Batch JSON (`/tmp/batch_N.json`) with `rule_name`, `spec_quote`, `current_coverpoints`.
2. Full coverpoint glossary (`/tmp/full_cp_glossary.json`) — union of `std_cp_defs.json` (from `v.adoc` table), `cp_glossary.json` (from custom defs CSVs), and prior-used coverpoints from rule CSV.
3. Strict instruction: **only use coverpoint names already in glossary** OR `implicit` / `untestable` / `cp_asm_count`. Verify:
   ```python
   g = json.load(open('/tmp/full_cp_glossary.json'))
   allowed = set(g) | {'implicit', 'untestable', 'cp_asm_count'}
   bad = [(p['rule_name'], c) for p in patch for c in p['coverpoints'] if c not in allowed]
   assert not bad
   ```
4. Output: JSON patch consumable by `update_norm_csv.py`.
