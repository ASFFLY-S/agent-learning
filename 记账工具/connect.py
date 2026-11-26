from API_connect import ask_model
from save_record import save_record
from check_record import check_record
from R73 import summarize
from R74 import make_report
from Prompt月度总结生成 import make_summary
import pandas as pd
from check_month import check_month
import csv

def csv_to_texts(path):
    """读 CSV，每行拼成一句话；跳过表头和空行。"""
    texts = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        next(reader)                      # 丢掉第一行表头
        for row in reader:
            cells = [c.strip() for c in row if c.strip()]
            if cells:                     # 跳过全空行
                texts.append(" ".join(cells))
    return texts
RECORDS_FILE=r"C:\Users\fangm\Desktop\记账V1.0实验\11月记账表.xlsx"
DEFAULT_REPORT_FILE =r"C:\Users\fangm\Desktop\记账V1.0实验\11月记账报表.xlsx"

while True:
    a=input("请输入a,b,c,d（其中a是直接退出，b是添加记账记录，c是生成月份报表，d是导入.csv文件并记录）：")
    if a=="a":
        print("期待下次相遇")
        break
    elif a=="b":
        b=input("请输入记账的文本：")
        c=ask_model(b)
        d,e=check_record(c)
        if not d:
            print(f"存在问题，其中问题为{e}")
            continue
        f=save_record(c,RECORDS_FILE)
        print(f"保存成功，且目前共{f}条记账")
    elif a=="c":
        df=pd.read_excel(RECORDS_FILE)
        g,i=summarize(df)
        h=input("请输入报表的日期，例：2026-11：")
        j,k=check_month(h)
        if not j:
            print(k,"请重新尝试")
            continue
        make_report(df,g,h,DEFAULT_REPORT_FILE)
        l=make_summary(g,h)
        print(l)
    elif a == "d":
        path = input("请输入 CSV 文件路径：").strip()
        if not path:
            path=r"C:\Users\fangm\PycharmProjects\PythonProject\项目3.记账工具\记账测试_2026-11_12条.csv"
        texts = csv_to_texts(path)
        ok_count = 0
        fail_count = 0
        for i, text in enumerate(texts, 1):
            try:
                rec = ask_model(text)
                valid, msg = check_record(rec)
                if not valid:
                    print(f"第 {i} 条跳过：{msg}")
                    fail_count += 1
                    continue
                save_record(rec, RECORDS_FILE)
                ok_count += 1
            except Exception as e:
                print(f"第 {i} 条出错：{e}")
                fail_count += 1
        print(f"批量完成：成功 {ok_count} 条，失败 {fail_count} 条")

    else:
        print("输入无效请重试")








