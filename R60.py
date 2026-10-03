import pandas as pd
from openpyxl import Workbook
df=pd.read_excel(r"C:\Users\fangm\Desktop\h货代信息\运价表.xlsx")
print("表头",(df.columns))
print("行列数：",df.shape)
print(df.dtypes)
print(df.head())
wb=Workbook()
ws=wb.active
ws.append(["origin", "destination", "carrier", "container_type",
           "price_usd", "fee_note", "free_time_days", "sailing_date"])
ws.append(["宁波", "伊斯坦布尔", "MSK", "20DC",2900
           , "含OWS",14, "9.28-10.4"])
wb.save(r"C:\Users\fangm\Desktop\h货代信息\报价记录.xlsx")
print("已生成：报价记录.xlsx")