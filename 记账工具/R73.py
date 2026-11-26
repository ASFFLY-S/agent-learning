import pandas as pd
from  rules import CATEGORIES,get_type_by_name
def summarize(records):
    if records is None or records.empty:
        return None,"记账表是空，没有数据可统计"
    need={"日期","类别","金额"}
    if not need <= set(records.columns):
        return None,f"缺列：{need-set(records.columns)}"
    records=records.copy()
    records["收支"]=records["类别"].map(get_type_by_name)
# 根据类别名称生成对应收支情况并映射到dataframe中
    income=records[records["收支"]=="收入"]
    expense=records[records["收支"]=="支出"]
    #目标：将收支为支出的选项收集并自成一组dataframe
    income_by_cat=income.groupby("类别")["金额"].sum().sort_values(ascending=False)
    expense_by_cat=expense.groupby("类别")["金额"].sum().sort_values(ascending=False)
    #.groupby()方法根据括号中的索引
    #求的各类的明细返回格式是series的形式
    income_total=income["金额"].sum()
    expense_total=expense["金额"].sum()
    balance=income_total-expense_total
    return {
        "收入分类小计":income_by_cat.to_dict(),
        "支出分类小计":expense_by_cat.to_dict(),
        "收入合计":income_total,
        "支出合计":expense_total,
        "本月结余":balance,
    },""
#正式代码
if __name__ == "__main__":
    df = pd.read_excel("记账表.xlsx")
    result, err = summarize(df)
    print(result or err)



