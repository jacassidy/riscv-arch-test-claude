# `randomizeVectorInstructionData` — nf × EMUL ≤ 8 guard

Per RISC-V V spec, `nf × EMUL` must not exceed 8. Violating ops **illegal**, never generate. When `lmul > 1` and instruction has `EEW ≠ SEW` or `nf > 1`, effective EMUL can grow beyond script author intent. Example: `vlseg3e64ff.v` with SEW=16, LMUL=2 → EMUL = 64/16 × 2 = 8, nf=3 → nf × EMUL = 24 (illegal).

**Any script using `lmul > 1` with LS instructions must guard.** Function handles register assignment for legal cases but cannot reject illegal SEW/LMUL/EEW/nf combos — script responsibility.

```python
import re

def _get_eew(instruction):
    """Get EEW from instruction name (e.g., vlseg3e64ff.v → 64). Returns None if SEW-based."""
    m = re.search(r'e(\d+)', instruction.split('seg')[-1] if 'seg' in instruction else instruction)
    return int(m.group(1)) if m else None

def _get_nf(instruction):
    """Get nfields from segmented instruction name. Returns 1 if not segmented."""
    m = re.search(r'seg(\d+)', instruction)
    return int(m.group(1)) if m else 1

# In make():
eew = _get_eew(test)
if eew is not None:
    emul = eew * lmul // sew
else:
    emul = lmul
nf = _get_nf(test)
if emul * nf > 8:
    return  # Illegal: nf × EMUL exceeds 8
```
