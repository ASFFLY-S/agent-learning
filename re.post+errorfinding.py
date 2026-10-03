#导入库
import time
import requests
import os
from dotenv import load_dotenv
import json
#数据配置区
load_dotenv()
url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.environ.get("DEEPSEEK_API_KEY"),
}
history_prompt="你是DEEPSEEK,一只蓝色大肥鱼"
history=[
    {"role":"system","content":history_prompt},
]
print("我是DeepSeek!")
#定义一个函数，注入post三要素安全进行https请求
def chat_with_model(url, headers, data, retries=2):
    for attempt in range(retries + 1):          # 最多试 3 次
        try:
            resp = requests.post(url, headers=headers, json=data, timeout=30)
            resp.raise_for_status()              # 4xx/5xx 会抛异常，进 except
            return resp.json()
        except requests.exceptions.Timeout:
            print(f"连接超时（第 {attempt+1} 次尝试）")
        except requests.exceptions.ConnectionError:
            print("网络不通，请检查网络连接")
            return None                          # 断网重试也没用，直接返回
        except requests.exceptions.HTTPError:
            code = resp.status_code
            if code == 401:
                print("密钥错误：检查 .env 里的 DEEPSEEK_API_KEY")
                return None
            elif code == 429:
                print("请求太频繁，休息 3 秒重试")
                time.sleep(3)
            elif code >= 500:
                print("服务器开小差了，休息 2 秒重试")
                time.sleep(2)
            else:
                print(f"请求失败（状态码 {code}），检查参数")
                return None
    print("多次尝试仍失败，请稍后再来")
    return None
#重复执行对话主文件
while True:
    user_input = input("你：").strip()
    if user_input == "quit":
        break

    history.append({"role": "user", "content": user_input})

    data = {
        "model": "deepseek-flash",
        "messages": history,
        "stream": False,
        "thinking": {"type": "disabled"},
    }

    result = chat_with_model(url, headers, data)

    if result is None:                 # 请求失败
        history.pop()                  # 回滚：把刚才那条 user 消息弹掉
        continue                       # 跳过本轮，继续下一问

    answer = result["choices"][0]["message"]["content"]
    print("AI：", answer)
    history.append({"role": "assistant", "content": answer})
