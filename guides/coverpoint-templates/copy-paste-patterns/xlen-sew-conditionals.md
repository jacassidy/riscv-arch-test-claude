## XLEN / SEW Conditionals


```systemverilog
    `ifdef XLEN32
        bins val32 = {32'hFFFFFFFF};
    `endif
    `ifdef XLEN64
        bins val64 = {64'hFFFFFFFFFFFFFFFF};
    `endif
    `ifdef SEW64_SUPPORTED
        // SEW=64 specific bins
    `endif

    // D extension guard
    `ifndef D_COVERAGE
        // bins for SEW=64 being unsupported for FP
    `endif
```
