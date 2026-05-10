## Edge Value Test


```python
from vector_testgen_common import vedgesemul1
for v in vedgesemul1:
    data = randomizeVectorInstructionData(test, sew, getBaseSuiteTestCount(), lmul=1, vs2_val_pointer=v)
    writeTest(f"edge {v}", test, data, sew=sew, vl=1, lmul=1)
    incrementBasetestCount()
    vsAddressCount()
```
