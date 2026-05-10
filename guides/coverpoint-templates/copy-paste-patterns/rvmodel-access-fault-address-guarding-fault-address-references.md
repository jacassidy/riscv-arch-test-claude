## RVMODEL_ACCESS_FAULT_ADDRESS — Guarding Fault-Address References


Not every DUT defines `RVMODEL_ACCESS_FAULT_ADDRESS` (only DUTs with addresses
that reliably generate access faults do). Any coverpoint that references the
macro must be wrapped in `` `ifdef RVMODEL_ACCESS_FAULT_ADDRESS `` / `` `endif ``
so covergroups compile on DUTs without one. Wrap only the helpers and crosses
that depend on it — keep unrelated coverpoints outside the guard so they still
cover on all DUTs (see `templates/vector/cp_custom_maskLS.sv`).

The **associated test `.py`** (the custom script that emits assembly for that
coverpoint) must also emit matching `#ifdef RVMODEL_ACCESS_FAULT_ADDRESS` /
`#endif` around each `writeTest(...)` call — otherwise the test runs on a DUT
where the covergroup is compiled out, wasting sim time on an unfillable bin.
Use `writeLine("#ifdef RVMODEL_ACCESS_FAULT_ADDRESS")` before and
`writeLine("#endif")` after (see `custom/cp_custom_maskLS.py`).
