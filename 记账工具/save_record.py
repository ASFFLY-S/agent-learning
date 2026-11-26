import os
from pathlib import Path

import pandas as pd

COLUMNS = ["日期", "类别", "金额", "备注"]


def save_record(rec, path):
    """
    (rec,path)
    把一条记账记录追加进 Excel。

    rec  : 已通过 check_record 的单条字典 {"日期","类别","金额","备注"}
    path : xlsx 文件的【绝对路径】；文件不存在会新建，父目录不存在会一并创建
    返回 : 写入后表里的总行数
    """
    if not isinstance(rec, dict):
        raise TypeError(f"rec 必须是字典，收到的是 {type(rec).__name__}")

    path = Path(path)
    if not path.is_absolute():
        raise ValueError(f"path 必须是绝对路径，收到的是：{path}")
    if path.suffix.lower() != ".xlsx":
        raise ValueError(f"只支持 .xlsx 文件，收到的是：{path.suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)      # 目录不在就先建

    row = pd.DataFrame([{c: rec.get(c, "") for c in COLUMNS}])

    if path.exists() and path.stat().st_size > 0:       # 文件存在 → 读出来接在后面
        old = pd.read_excel(path).reindex(columns=COLUMNS)
        df = pd.concat([old, row], ignore_index=True)
    else:                                               # 不存在 → 这一行就是第一行
        df = row

    # 先写临时文件，写完再整体替换，避免写到一半崩溃把整张表毁掉
    tmp = path.with_name(path.stem + ".tmp.xlsx")
    df.to_excel(tmp, index=False)
    os.replace(tmp, path)

    return len(df)
