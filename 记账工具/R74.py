from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent          # R74.py 所在的绝对目录
DEFAULT_REPORT_FILE = BASE_DIR / "记账报表.xlsx"     # 默认报表路径（绝对）


def make_report(records, summary, month="2026-10", filename=DEFAULT_REPORT_FILE):
    filename = Path(filename)
    if not filename.is_absolute():
        filename = BASE_DIR / filename    # 传相对名字也锚定到代码目录，不跟 cwd 跑

    wb = Workbook()
    ws = wb.active
    ws.title = "记账报表"

    # 准备样式
    title_font = Font(name="黑体", size=14, bold=True)
    head_font  = Font(name="宋体", size=11, bold=True)
    body_font  = Font(name="宋体", size=11)
    head_fill  = PatternFill("solid", fgColor="D9D9D9")
    center = Alignment(horizontal="center", vertical="center")
    right  = Alignment(horizontal="right",  vertical="center")
    left   = Alignment(horizontal="left",   vertical="center")
    thin = Side(style="thin", color="999999")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    # ① 标题（第1行，合并 A1:E1）
    ws.merge_cells("A1:E1")
    ws["A1"] = f"{month}记账报表"
    ws["A1"].font = title_font
    ws["A1"].alignment = center

    # ② 明细表头（第3行）
    for col, h in enumerate(["序号", "日期", "类别", "金额", "备注"], start=1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font, cell.fill, cell.alignment, cell.border = head_font, head_fill, center, border

    # ③ 明细（第4行起）
    row = 4
    for i, (_, r) in enumerate(records.iterrows(), start=1):
        note = r["备注"] if pd.notna(r["备注"]) else ""   # ⚠ NaN 必须转空串，否则表格出乱码
        values = [i, r["日期"], r["类别"], r["金额"], note]
        for col, v in enumerate(values, start=1):
            cell = ws.cell(row=row, column=col, value=v)
            cell.font, cell.border = body_font, border
            if col == 4:   cell.alignment = right    # 金额右对齐
            elif col == 5: cell.alignment = left
            else:          cell.alignment = center
        row += 1

    # ④ 汇总区（空一行）
    row += 1
    for label, val in [("收入合计", summary["收入合计"]),
                       ("支出合计", summary["支出合计"]),
                       ("本月结余", summary["本月结余"])]:
        ws.cell(row=row, column=3, value=label).font = head_font
        ws.cell(row=row, column=3).alignment = center
        ws.cell(row=row, column=4, value=val).alignment = right
        row += 1

    # ⑤ 支出分类小计（空一行）
    row += 1
    ws.cell(row=row, column=2, value="支出分类小计").font = head_font
    row += 1
    for cat, val in summary["支出分类小计"].items():
        ws.cell(row=row, column=3, value=cat).alignment = center
        ws.cell(row=row, column=4, value=val).alignment = right
        row += 1

    # 列宽 + 保存
    for i, w in enumerate([6, 14, 12, 12, 20], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    wb.save(filename)
    print(f"报表已生成：{filename}")







