## VL/LMUL Sweep


```python
for l_exp in range(4):
    for vl in ["vlmax", 1, "random"]:
        cur_lmul = 2 ** l_exp
        data = randomizeVectorInstructionData(test, sew, getLengthSuiteTestCount(), suite="length", lmul=cur_lmul)
        writeTest(f"lmul={cur_lmul} vl={vl}", test, data, sew=sew, lmul=cur_lmul, vl=vl)
        incrementLengthtestCount()
        vsAddressCount("length")
```
