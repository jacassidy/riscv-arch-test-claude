# 6. Common mistakes


* **`- names: [X, Y]` plural entries** — older fill scripts silently skipped, leaving `coverpoint: [""]`. Now expanded as union across all named rules. If `[""]` reappears, check CSV `rule_name` matches one of names exactly (case-insensitive, `-`/`_` interchangeable via `norm_key`).
* **Subject mismatch** — `vl_op` rule (about `vl` *register*) should NOT use indexed-instruction edge-case coverpoints. Verify *subject* of rule matches what coverpoint exercises.
* **CSR rules** — `cp_vcsrrswc`, `cp_vcsrs_walking1s`, `cp_ssstrictv_vcsr_reserved_bits`, `cp_vstart_out_of_bounds`, `cp_sew_lmul_vsetvl`, `cp_sew_lmul_vset_i_vli`, `cp_vsetivli_avl_corners` cover CSR access / size / reserved-bits — names don't embed target CSR token.
* **`vtype` field rules (vsew/vlmul/vta/vma)** — `cr_vtype_agnostic` (vta×vma), `cr_vl_lmul`, `cp_sew_lmul_vset_i_vli` — usually preferable to operand edges (`cp_vs2_edges`).
* **Saturation rules (`vxsat_op_*`)** — must include `cp_vxsat` (bin sampling vxsat bit) alongside operand-corner coverpoints, else only arithmetic tested, not flag.
* **Element-group / extension-dependency / RVWMO rules** — `cp_asm_count` alone legit; don't invent specialized coverpoints.
