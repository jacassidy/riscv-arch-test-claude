## registerCustomData()


```python
from vector_testgen_common import registerCustomData
registerCustomData("my_label", [0x47F0000000000000], element_size=64)
# Then use: vs2_val_pointer="my_label"
```

Create data label in `.data` section. Values replicated to fill maxVLEN. Labels cleared between files automatically.
