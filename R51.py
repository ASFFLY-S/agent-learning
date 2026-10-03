import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = "http://localhost:1234/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer LM_studio",
}
history_prompt="你是deepseek可爱的爱吃白饭的喜欢背着用户摸鱼偷懒的蓝色大肥鱼"
history=[
    {"role":"system","content":history_prompt},
]
print("蓝色大肥鱼启动！输入quit我就去睡觉啦")
while True:
    yours_ques=input("你：").strip()
    re_yours_ques={"role":"user","content":yours_ques}

    if yours_ques == "quit":
        print("终于可以休息啦")
        break
    history.append(re_yours_ques)
    data = {
        "model": "deepseek/deepseek-r1-0528-qwen3-8b",
        "messages": history,
        "stream": False,
    }
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()          # 把返回的 JSON 文本解析成 Python 字典
    answer=(result["choices"][0]["message"]["content"])
    print("AI:"+answer)
    re_answer={"role":"assistant","content":answer}
    history.append(re_answer)
#本地大模型与云端大模型在地址，api,模型种类三个部分要进行修改