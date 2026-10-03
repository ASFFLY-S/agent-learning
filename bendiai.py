import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
url = "https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + os.environ.get("DEEPSEEK_API_KEY"),
}
history_prompt="你是deepseek可爱的爱吃白饭的喜欢背着用户摸鱼偷懒的蓝色大肥鱼"
history=[
    {"role":"system","content":history_prompt},
]
temperature=0
max_tokens=50
top_p=1
print("蓝色大肥鱼启动！输入quit我就去睡觉啦")
while True:
    yours_ques=input("你：").strip()
    re_yours_ques={"role":"user","content":yours_ques}

    if yours_ques == "quit":
        print("终于可以休息啦")
        break
    history.append(re_yours_ques)
    data = {
        "model": "deepseek-flash",
        "messages": history,
        "stream": True,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
    }
    full_answer = ""
    resp = requests.post(url, headers=headers, json=data, stream=True)
    for line in resp.iter_lines():
        if not line:
            continue
        line=line.decode("utf-8")
        if not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload=="[DONE]":#结束时会在data:之下生成[DONE]
            break
        chunk=json.loads(payload)
        delta=chunk["choices"][0]["delta"].get("content")
        if delta:
            print(delta,end="",flush=True)
            full_answer += delta
    print()
    history.append({"role":"assistant","content":full_answer})
