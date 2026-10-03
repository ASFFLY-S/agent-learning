import os
import requests
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
URL="https://api.deepseek.com/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
history_prompt="你是DEEPSEEK大模型，是一只鲸鱼娘"
history=[
    {"role":"system","content":history_prompt},
]

while True:
    user_input=input("你：").strip()
    if user_input=="quit":
        break
    s_user_input={"role":"user","content":user_input}
    data={"model":"deepseek-flash",
          "messages":history,
          }
    history.append(s_user_input)
    resp = requests.post(url=URL, json=data, headers=headers)
    AI=resp.json()
    answer=AI["choices"][0]["message"]["content"]
    history.append({"role":"assistant","content":answer})
    print("AI:",answer)


