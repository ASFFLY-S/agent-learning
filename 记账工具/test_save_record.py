# -*- coding: utf-8 -*-
"""save_record 的单元测试。直接运行本文件即可（PyCharm 里右键 Run）。

特点：
- 全部用临时目录，不碰你真实的记账表
- 不依赖 pytest，只用 Python 标准库 unittest
"""
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from save_record import save_record

REC1 = {"日期": "2026-11-13", "类别": "餐饮", "金额": 35.5, "备注": "午饭"}
REC2 = {"日期": "2026-11-14", "类别": "交通", "金额": 6.0, "备注": "公交"}


class SaveRecordTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.path = self.dir / "数据" / "记账表.xlsx"    # 父目录故意不创建

    def tearDown(self):
        self._tmp.cleanup()

    def test_001_文件不存在时新建(self):
        self.assertFalse(self.path.exists())
        rows = save_record(REC1, self.path)
        self.assertEqual(rows, 1)
        self.assertTrue(self.path.exists())
        self.assertEqual(list(pd.read_excel(self.path).columns),
                         ["日期", "类别", "金额", "备注"])

    def test_002_已存在时追加(self):
        save_record(REC1, self.path)
        rows = save_record(REC2, self.path)
        self.assertEqual(rows, 2)
        df = pd.read_excel(self.path)
        self.assertEqual(list(df["类别"]), ["餐饮", "交通"])
        self.assertEqual(df.loc[1, "金额"], 6.0)

    def test_003_父目录自动创建(self):
        save_record(REC1, self.path)
        self.assertTrue(self.path.parent.is_dir())

    def test_004_相对路径被拒绝(self):
        with self.assertRaises(ValueError):
            save_record(REC1, "记账表.xlsx")

    def test_005_后缀不对被拒绝(self):
        with self.assertRaises(ValueError):
            save_record(REC1, str(self.dir / "记账表.csv"))

    def test_006_非字典被拒绝(self):
        with self.assertRaises(TypeError):
            save_record("不是字典", self.path)

    def test_007_字段顺序乱也能对齐(self):
        rec = {"备注": "买菜", "金额": 12, "类别": "购物", "日期": "2026-11-14"}
        save_record(rec, self.path)
        df = pd.read_excel(self.path)
        self.assertEqual(df.loc[0, "类别"], "购物")
        self.assertEqual(df.loc[0, "备注"], "买菜")
        self.assertEqual(df.loc[0, "金额"], 12)

    def test_008_不残留临时文件(self):
        save_record(REC1, self.path)
        save_record(REC2, self.path)
        names = sorted(p.name for p in self.path.parent.iterdir())
        self.assertEqual(names, ["记账表.xlsx"])

    def test_009_零字节文件当新文件处理(self):
        self.path.parent.mkdir(parents=True)
        self.path.touch()                # 造一个 0 字节的空文件
        rows = save_record(REC1, self.path)
        self.assertEqual(rows, 1)
        self.assertEqual(len(pd.read_excel(self.path)), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
