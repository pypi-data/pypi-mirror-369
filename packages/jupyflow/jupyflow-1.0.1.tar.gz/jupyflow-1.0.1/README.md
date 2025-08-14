# jupyflow
_Split & rejoin Jupyter notebooks, simply._

---

## Overview
**jupyflow** is a tiny, zero‑dependency library that helps you move code **in and out** of Jupyter notebooks with confidence:

- `split(notebook_path) -> list[str]`: extract all **code cells** from a `.ipynb` into a Python list of strings.
- `rejoin(*files, ...) -> str`: take one or more **`.py` files** (each file = one cell) and rebuild a **valid `.ipynb`** JSON string.

It’s ideal for lightweight refactors, quick round‑trips, or preparing notebooks for CI/CD and code reviews—without imposing a custom file layout or heavy dependencies.

> Python ≥ 3.8. No third‑party dependencies.

---

## Installation
```bash
pip install jupyflow
```

---

## Quick Start

### 1) Split a notebook into code strings
```python
from pathlib import Path
import jupyflow as jf

cells = jf.split("Your_filename.ipynb", skip_empty=True)  # List[str]
print(f"Found {len(cells)} cells")
print(cells[0][:120])  # peek the first 120 chars
```

### 2) Rejoin multiple `.py` files into one notebook
```python
from pathlib import Path
import jupyflow as jf

ipynb_text = jf.rejoin("cells/001_intro.py", "cells/002_calc.py")
Path("combined.ipynb").write_text(ipynb_text, encoding="utf-8")
```

### 3) Rejoin all `.py` files in a folder (natural sort)
```python
from pathlib import Path
import re
import jupyflow as jf

def natural_key(name: str):
    # Ensure 2 < 10 when sorting: ['1','2','10'] not ['1','10','2']
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r"(\d+)", name)]

src = Path("./Your_filename_py")
py_files = sorted(src.glob("*.py"), key=lambda p: natural_key(p.name))
ipynb_text = jf.rejoin(py_files)          # respects passed order by default
Path("Your_filename_combined.ipynb").write_text(ipynb_text, encoding="utf-8")
```

### 4) Round‑trip idea (optional)
```python
# Split → write each cell to a file → rejoin later
import jupyflow as jf
from pathlib import Path

cells = jf.split("demo.ipynb")
out = Path("cells"); out.mkdir(exist_ok=True)
for i, code in enumerate(cells, start=1):
    (out / f"{i:03d}.py").write_text(code, encoding="utf-8")

# ...edit files... then rejoin:
from sortedcontainers import SortedList  # or use your own sorting if desired
# (Note: this line is only illustrative; jupyflow itself has no deps.)
```

---

## API Reference

### `split(notebook_path: str | Path, skip_empty: bool = True) -> list[str]`
Extract the **code cells** (in order) from a notebook.
- **Parameters**
  - `notebook_path`: path to `.ipynb`
  - `skip_empty` (default `True`): skip cells that are empty or whitespace‑only
- **Returns**: `list[str]` — each element is a code cell’s source
- **Raises**: `FileNotFoundError` if the notebook path does not exist

### `rejoin(*files, metadata: dict | None = None, encoding: str = "utf-8", sort: bool = False) -> str`
Build a valid `.ipynb` JSON **string** from one or more `.py` files (each file becomes **one code cell**).
- **Parameters**
  - `*files`: pass multiple paths or a single sequence (`list/tuple`) of paths
  - `metadata`: optional dict to merge into the notebook’s metadata (e.g. custom kernelspec)
  - `encoding`: file encoding for reading `.py` (default `utf-8`)
  - `sort`: `True` to lexicographically sort inputs; by default the **call order** is preserved
- **Returns**: `str` — the full notebook JSON (ready to write to disk)
- **Raises**: `FileNotFoundError` if any source file is missing
- **Defaults**
  - `nbformat=4`, `nbformat_minor=5`
  - Basic `kernelspec` & `language_info` (Python 3) included
  - Each code cell keeps original line endings via `splitlines(keepends=True)`

**Customize metadata example**
```python
ipynb_text = jupyflow.rejoin(
    "a.py", "b.py",
    metadata={"kernelspec": {"display_name": "Python 3.11", "language": "python", "name": "python3"}}
)
```
---

## Minimal Tests (pytest example)
```python
# tests/test_basic.py
import json
from pathlib import Path
import jupyflow as jf

def make_nb(tmp: Path):
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Title"]},
            {"cell_type": "code", "source": ["print('A')\n"]},
            {"cell_type": "code", "source": ["x = 42\n"]},
            {"cell_type": "code", "source": ["   \n"]},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    p = tmp / "mini.ipynb"
    p.write_text(json.dumps(nb), encoding="utf-8")
    return p

def test_split(tmp_path: Path):
    nbp = make_nb(tmp_path)
    cells = jf.split(nbp, skip_empty=True)
    assert len(cells) == 2
    assert "print('A')" in cells[0]
    assert "x = 42" in cells[1]
```

---

## License
MIT. See `LICENSE`.

---

### 简介
**jupyflow** 是一个**零依赖**的小工具，用来在 Jupyter 笔记本与纯代码之间**轻盈往返**：

- `split(notebook_path) -> list[str]`：把 `.ipynb` 里的**代码单元**抽取为 Python 字符串列表。
- `rejoin(*files, ...) -> str`：把一个或多个 **`.py` 文件**（每个文件 = 一个单元）拼回**合法的 `.ipynb`** JSON 字符串。

适合做轻量重构、把 Notebook 纳入 CI/CD、或作为代码评审的过渡形态，简单直接。

> 需要 Python ≥ 3.8。无第三方依赖。

### 安装
```bash
pip install jupyflow
```

### 快速上手

**1）把 `.ipynb` 拆成代码字符串**
```python
import jupyflow as jf
cells = jf.split("Your_filename.ipynb", skip_empty=True)
print(len(cells), cells[0][:120])
```

**2）把多个 `.py` 合成一个 Notebook**
```python
from pathlib import Path
import jupyflow as jf

ipynb_text = jf.rejoin("cells/001_intro.py", "cells/002_calc.py")
Path("combined.ipynb").write_text(ipynb_text, encoding="utf-8")
```

**3）把文件夹中的所有 `.py` 合成（自然排序）**
```python
from pathlib import Path
import re
import jupyflow as jf

def natural_key(name: str):
    return [int(s) if s.isdigit() else s.lower() for s in re.split(r"(\d+)", name)]

src = Path("./Your_filename_py")
py_files = sorted(src.glob("*.py"), key=lambda p: natural_key(p.name))
ipynb_text = jf.rejoin(py_files)
Path("Your_filename_combined.ipynb").write_text(ipynb_text, encoding="utf-8")
```

### API 参考

**`split(notebook_path: str | Path, skip_empty: bool = True) -> list[str]`**
- **参数**
  - `notebook_path`：`.ipynb` 路径
  - `skip_empty`：是否跳过空白单元，默认 `True`
- **返回**：`list[str]`（每个元素是一段代码）
- **异常**：路径不存在则抛 `FileNotFoundError`

**`rejoin(*files, metadata: dict | None = None, encoding: str = "utf-8", sort: bool = False) -> str`**
- **参数**
  - `*files`：可传多个路径，或传入一个列表/元组
  - `metadata`：可选，合并到生成的 notebook 元数据里（如自定义 kernelspec）
  - `encoding`：读取 `.py` 的编码，默认 `utf-8`
  - `sort`：若为 `True`，对输入路径按字典序排序；默认按**传入顺序**生成
- **返回**：`.ipynb` 的 **JSON 字符串**
- **异常**：任何源文件缺失会抛 `FileNotFoundError`
- **默认设置**
  - `nbformat=4`，`nbformat_minor=5`
  - 默认包含 Python 3 的 `kernelspec` 与 `language_info`
  - 代码以逐行列表形式保存，保留换行

**自定义元数据示例**
```python
ipynb_text = jupyflow.rejoin(
    "a.py", "b.py",
    metadata={"kernelspec": {"display_name": "Python 3.11", "language": "python", "name": "python3"}}
)
```

### 简单测试（pytest 示例）
```python
# tests/test_basic.py
import json
from pathlib import Path
import jupyflow as jf

def make_nb(tmp: Path):
    nb = {
        "cells": [
            {"cell_type": "markdown", "source": ["# Title"]},
            {"cell_type": "code", "source": ["print('A')\n"]},
            {"cell_type": "code", "source": ["x = 42\n"]},
            {"cell_type": "code", "source": ["   \n"]},
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    p = tmp / "mini.ipynb"
    p.write_text(json.dumps(nb), encoding="utf-8")
    return p

def test_split(tmp_path: Path):
    nbp = make_nb(tmp_path)
    cells = jf.split(nbp, skip_empty=True)
    assert len(cells) == 2
    assert "print('A')" in cells[0]
    assert "x = 42" in cells[1]
```

### 许可
MIT（可在 `LICENSE` 中查看）。

---

_Your notebooks, now fluid._
