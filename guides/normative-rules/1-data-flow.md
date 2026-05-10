# 1. Data flow


```
v-st-ext.adoc                                  # spec source — [[norm:tag]] anchors
  └─> normative_rule_defs/v-st-ext.yaml        # groups norm:* tags into named "rules"
        └─> working-testplans/csvs/v-st-ext-normative-rules.csv
              # cols: rule_name, spec_text, cp_name_1..36, coverage_desc_1..36,
              #       coverage_status, explanation, gaps
              └─[ tools/fill_vx_coverpoints.py ]─>
                  normative_rules/coverpoints/norm/Vx.yaml
                    # normative_rule_definitions:
                    #   - name: <rule>
                    #     coverpoint: ["cg/cp_a", "cg/cp_b", ...]
```

Coverpoint definitions:
- **Standard** (`cp_vd`, `cp_vs2_edges`, `cr_vl_lmul`, …): `normative_rules/docs/ctp/src/v.adoc` (table ~L122) + variant suffixes (`nv0`, `emul2`, `wv`, `wred`, …) below.
- **Custom** (`cp_custom_*`, `cp_ssstrictv_*`): `working-testplans/csvs/Vector - V{x,ls,f}_custom_definitions.csv`. Goal / Feature Description / Expectation cols = human definition.
