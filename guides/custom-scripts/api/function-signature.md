# Function Signature


```python
from coverpoint_registry import register
from vector_testgen_common import (
    writeTest, randomizeVectorInstructionData,
    incrementBasetestCount, getBaseSuiteTestCount, vsAddressCount,
    incrementLengthtestCount, getLengthSuiteTestCount,
    randomizeMask, randomizeOngroupVectorRegister, vreg_count,
)

@register("cp_custom_YOUR_NAME_HERE")
def make(test, sew):
    # test = instruction mnemonic (e.g. "vfrsqrt7.v")
    # sew = selected element width (8, 16, 32, 64)
```

`@register` decorator **required**. Must match **CSV column name** in `testplans/`.
