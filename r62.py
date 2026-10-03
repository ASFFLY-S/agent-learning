#目标，筛选标头所对应的值
import pandas as pd
import openpyxl
from openpyxl.reader.excel import load_workbook
location=r"C:\Users\fangm\Desktop\h货代信息\报价记录.xlsx"
df=pd.read_excel(location)
row_ningbo=df[df["origin"]=="宁波"]
print(row_ningbo)
if len(row_ningbo)>0:
    price=row_ningbo.iloc[1]["price_usd"]
    print(price)
