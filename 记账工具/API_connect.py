import os
import json
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = os.environ["DEEPSEEK_API_KEY"]
TODAY = datetime.date.today().isoformat()

CATEGORIES = [
    "工资", "奖金", "理财收益", "红包", "其他收入",
    "餐饮", "交通", "购物", "居住", "医疗",
    "娱乐", "学习", "人情", "通讯", "其他支出",
]

SYSTEM_PROMPT = f"""你是记账信息提取器。今天是 {TODAY}。
从用户的话中提取一条记账记录，只输出 JSON，不要任何解释：
{{"日期": "YYYY-MM-DD", "类别": "类别名", "金额": 数字, "备注": "简短说明"}}
类别只能是：{'/'.join(CATEGORIES)}
相对日期（昨天、前天）换算成具体日期；金额为正数；无法确定的字段留空字符串。"""


def ask_model(text):
    resp = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        json={
            "model": "deepseek-flash",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            "thinking": {"type": "disabled"},
            "response_format": {"type": "json_object"},
            "temperature": 0,
            "stream": False,
        },
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    return json.loads(content)


if __name__ == "__main__":
    print(ask_model("昨天中午吃饭花了35块"))
#正常输出：{'日期': '2026-11-13', '类别': '餐饮', '金额': 35, '备注': '中午吃饭'}

