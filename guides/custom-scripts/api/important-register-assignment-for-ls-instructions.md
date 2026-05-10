# Important: Register Assignment for LS Instructions


For load/store instructions, EMUL = EEW/SEW × LMUL, can differ from LMUL. **Never manually pick vd with `randint()`** — register assigner inside `randomizeVectorInstructionData` handles EMUL alignment automatically. Use `additional_no_overlap` to add constraints:

```python
# WRONG — vd may not be EMUL-aligned for LS instructions
vd = randint(1, 31)
data = randomizeVectorInstructionData(test, sew, count, lmul=1, vs2=0, vd=vd)

# RIGHT — let assigner pick vd, constrain with no_overlap
data = randomizeVectorInstructionData(test, sew, count, lmul=1, vs2=0,
    additional_no_overlap=[['vd', 'v0']])
```
