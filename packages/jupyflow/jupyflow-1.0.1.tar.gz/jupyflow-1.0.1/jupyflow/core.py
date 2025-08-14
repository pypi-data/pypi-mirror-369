# jupyflow/core.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Union

__all__ = ["split", "rejoin"]

# ---- split：从 .ipynb 提取代码单元（字符串列表） ----
def split(notebook_path: str | Path, skip_empty: bool = True) -> List[str]:
    """
    读取 .ipynb 文件并返回代码单元格列表（字符串形式）。
    """
    nb_path = Path(notebook_path).expanduser().resolve()
    if not nb_path.exists():
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    with nb_path.open("r", encoding="utf-8") as f:
        nb_data = json.load(f)

    cells: List[str] = []
    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        code = "".join(cell.get("source", []))
        if skip_empty and not code.strip():
            continue
        cells.append(code)
    return cells


# ---- rejoin：把多个 .py 文件重新拼成一个 .ipynb（返回 JSON 字符串）----
def rejoin(
    *files: Union[str, Path, Sequence[Union[str, Path]]],
    metadata: Optional[dict] = None,
    encoding: str = "utf-8",
    sort: bool = False,
) -> str:
    """
    将一个、两个或多个 .py 文件按顺序拼接成一个 Jupyter Notebook（ipynb）的 JSON 字符串。
    - *files: 可以是多个文件参数，也可以是单个 list/tuple
    - metadata: 可选，覆盖/扩展 notebook 的 metadata
    - encoding: 读取源文件使用的编码（默认 utf-8）
    - sort: 是否对传入的文件路径进行字典序排序（默认 False，保留调用顺序）

    返回：
        str：Notebook 的 JSON 文本（标准 .ipynb 格式）
    """
    # 允许 rejoin(["a.py","b.py"]) 或 rejoin("a.py","b.py")
    if len(files) == 1 and isinstance(files[0], (list, tuple)):
        file_list = list(files[0])  # type: ignore
    else:
        file_list = list(files)

    paths = [Path(p).expanduser().resolve() for p in file_list]
    if sort:
        paths.sort(key=lambda p: str(p))

    cells_json = []
    for p in paths:
        if not p.exists():
            raise FileNotFoundError(f"Source file not found: {p}")
        code = p.read_text(encoding=encoding)
        # Jupyter 推荐用“按行列表”的 source，并保留行尾换行
        source_list = code.splitlines(keepends=True)
        cells_json.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": source_list,
        })

    nb = {
        "cells": cells_json,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "mimetype": "text/x-python",
                "file_extension": ".py",
                "pygments_lexer": "ipython3",
                # 下面两个字段可选，留空也可被 Jupyter 接受
                # "version": "3",
                # "codemirror_mode": {"name": "ipython", "version": 3},
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    # 合并/覆盖用户传入的 metadata（浅合并）
    if metadata:
        nb["metadata"].update(metadata)

    return json.dumps(nb, ensure_ascii=False, indent=2)