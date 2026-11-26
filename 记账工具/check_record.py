import datetime
from rules import CATEGORIES

# 从类别字典里取出全部中文名，作为唯一合法白名单
NAMES = {c["name"] for c in CATEGORIES.values()}


def check_record(rec):
    """校验 ask_model 产出的一条记账记录。
    返回 (True, "") 表示通过；(False, 原因) 表示不通过。
    """
    # 1. 类型兜底：ask_model 可能返回 None 或别的东西
    if not isinstance(rec, dict):
        return False, f"提取结果不是字典，拿到的是 {type(rec).__name__}"

    # 2. 字段是否齐全
    need = {"日期", "类别", "金额", "备注"}
    missing = need - set(rec)
    if missing:
        return False, "缺字段：" + "、".join(sorted(missing))

    # 3. 类别必须在白名单里
    if rec["类别"] not in NAMES:
        return False, f"类别不存在：{rec['类别']}"

    # 4. 日期必须是严格 YYYY-MM-DD
    date_text = rec["日期"]
    if not isinstance(date_text, str) or len(date_text) != 10:
        return False, f"日期格式错误：{date_text}，应为 YYYY-MM-DD"
    try:
        datetime.date.fromisoformat(date_text)
    except ValueError:
        return False, f"日期格式错误：{date_text}，应为 YYYY-MM-DD"

    # 5. 金额必须是正数（type() 写法可把 True/False 一起挡掉）
    if type(rec["金额"]) not in (int, float) or rec["金额"] <= 0:
        return False, f"金额必须为正数：{rec['金额']}"

    return True, ""
if __name__ == "__main__":
    a={'日期': '2026-11-13', '类别': '餐饮', '金额': 35, '备注': '中午吃饭'}
    print(check_record(a))
    b={'日期': '2026-11-13', '类别': '餐饮', '金额': "35", '备注': '中午吃饭'}
    print(check_record(b))