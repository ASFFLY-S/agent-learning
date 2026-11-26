# rules.py —— 分类与统计规则（R72）
CATEGORIES = {
    "salary":       {"name": "工资",     "type": "收入"},
    "bonus":        {"name": "奖金",     "type": "收入"},
    "invest":       {"name": "理财收益", "type": "收入"},
    "redpacket":    {"name": "红包",     "type": "收入"},
    "other_income": {"name": "其他收入", "type": "收入"},
    "food":         {"name": "餐饮",     "type": "支出"},
    "transport":    {"name": "交通",     "type": "支出"},
    "shopping":     {"name": "购物",     "type": "支出"},
    "housing":      {"name": "居住",     "type": "支出"},
    "medical":      {"name": "医疗",     "type": "支出"},
    "entertainment":{"name": "娱乐",     "type": "支出"},
    "study":        {"name": "学习",     "type": "支出"},
    "social":       {"name": "人情",     "type": "支出"},
    "comm":         {"name": "通讯",     "type": "支出"},
    "other_expense":{"name": "其他支出", "type": "支出"},
}
#规定记账类别，其中每一个类都有两个属性（通过字典中每个单元的键对应的值为字典/列表实现）
def get_type(category_code: str) -> str:
    """类别代码 -> 收支方向；不在字典返回 '未知'"""
    return CATEGORIES.get(category_code, {}).get("type", "未知")
#双重get取值，目标：注入字典CATEGORIES中的一个大索引，提取出其对应type的值。
#get的一个重要特点，作用对象必须是字典/列表，无对应键不会报错
def is_valid_amount(amount) -> bool:
    """金额必须 > 0 的数字"""
    return isinstance(amount, (int, float)) and amount > 0
#注入amount变量，对其值进行布尔判断，如果大于零则返回True
def get_type_by_name(name: str) -> str:
    for c in CATEGORIES.values():
        if c["name"] == name:
            return c["type"]
    return "未知"
#为解决get_type是输入字典CATEGORIES中的大索引，返回其type对应的值，而实际是注入name返回其type，接口不对应
#输入name,返回type