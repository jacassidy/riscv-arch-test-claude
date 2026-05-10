# vill Testing Pattern


Testing vill (illegal vtype) — do NOT assume a particular SEW/LMUL config will set vill. Explicitly load a register with vtype vill bit set, use `vsetvl` to load that as vtype. Reference: `cp_custom_vwholeRegLS_vill.py`.
