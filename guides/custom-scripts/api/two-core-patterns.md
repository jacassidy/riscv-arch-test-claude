# Two Core Patterns


### Base suite — register/value sweep

```python
for v in range(vreg_count):
    data = randomizeVectorInstructionData(test, sew, getBaseSuiteTestCount(), lmul=1, vd=v)
    writeTest(f"test vd=v{v}", test, data, sew=sew, lmul=1)
    incrementBasetestCount()
    vsAddressCount()
```

### Length suite — masked test

```python
maskval = randomizeMask(test, always_masked=True)
no_overlap = [['vs1', 'v0'], ['vs2', 'v0'], ['vd', 'v0']]
data = randomizeVectorInstructionData(test, sew, getLengthSuiteTestCount(), suite="length", lmul=1, additional_no_overlap=no_overlap)
writeTest("masked test", test, data, sew=sew, lmul=1, vl="vlmax", maskval=maskval)
incrementLengthtestCount()
vsAddressCount("length")
```
