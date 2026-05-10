# NX Triggers for Approximation/Sqrt


Default `1.0+1ulp` may not trigger NX for lookup-table instructions:

- **vfrsqrt7.v / vfrec7.v**: use **3.0** (`{16: 0x4200, 32: 0x40400000, 64: 0x4008000000000000}`)
- **vfsqrt.v**: use **2.0** (`{16: 0x4000, 32: 0x40000000, 64: 0x4000000000000000}`)
