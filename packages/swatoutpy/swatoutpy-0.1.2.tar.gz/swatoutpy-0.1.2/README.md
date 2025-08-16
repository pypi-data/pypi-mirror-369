# swatoutpy

A lightweight Python package to read SWAT model (Rev 681) output files: `.rch`, `.sub`, and `.hru`.

## How to install

```bash
pip install swatoutpy
```

## How to use

For `*.rch` files

```bash
from swatoutpy.reader import read_rch

df = read_rch("output.rch", timestep="monthly")
print(df.head())
```

For `*.sub` files

```bash
from swatoutpy.reader import read_sub

df = read_sub("output.sub", timestep="annual")
print(df.head())
```

For multiple files

```bash
from swatoutpy.reader import read_multiple_rch

scenarios = [
    ("./sce1/output.rch", "Sce-1"),
    ("./sce1/output.rch", "Sce-2")
]

df = read_multiple_rch(scenarios, timestep="monthly")
print(df.head())
```
