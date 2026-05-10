## Overlap Test (widening — vd overlaps vs2 top)


```python
import math
emul = 2 * lmul
vd = randint(0, math.floor((vreg_count - 1) / emul)) * emul
vs2 = vd + lmul
vs1 = randomizeOngroupVectorRegister(test, vs2, vd, lmul=lmul)
data = randomizeVectorInstructionData(test, sew, getBaseSuiteTestCount(), vd=vd, vs2=vs2, vs1=vs1, lmul=lmul)
writeTest(f"overlap lmul={lmul}", test, data, sew=sew, lmul=lmul)
incrementBasetestCount()
vsAddressCount()
```
