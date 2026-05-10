# Element Index Regions


```
Index:    0        vstart       vl        VLMAX
          |           |         |           |
          |--prestart-|--body---|---tail----|

Prestart: i < vstart       -> skip, no exceptions
Body:     vstart <= i < vl -> execute if mask[i]=1
Tail:     vl <= i < VLMAX  -> skip (agnostic if vta=1)

Body Active:   body AND mask[i]=1  -> execute, update dest
Body Inactive: body AND mask[i]=0  -> skip (agnostic if vma=1)
```
