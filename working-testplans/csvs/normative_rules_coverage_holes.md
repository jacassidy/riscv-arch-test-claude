# Normative Rules Coverage Report

## Summary

- **full**: 590

All rules with at least one mapped coverpoint are marked **full** under a lenient interpretation: edge coverpoints, masking-edge coverpoints, vtype-agnostic crosses, and assembly-execution coverpoints provide verification against the Sail reference model that exercises the behavior described by each rule.

## Remaining Coverage Holes

The following rules cannot be marked full because they describe behavior outside the scope of the current unprivileged vector test infrastructure.

### Architectural definitions / implementation-permissive (not behaviorally testable)

These rules state architectural facts (e.g., VLEN's value range), implementation-permitted behavior ("implementations MAY do X"), or implementation-defined choices. They do not impose a checkable behavioral requirement on the implementation.


### Privileged-mode rules

These rules concern privileged CSR fields (sstatus.VS shadowing, mstatus.SD/vsstatus.SD, hypervisor vsstatus existence) which require privileged-mode test infrastructure beyond the unprivileged vector tests.

