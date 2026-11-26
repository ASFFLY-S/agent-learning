# R80_cost.py —— 单次记账的 token / 耗时 / 费用测量
# 用法：直接运行本文件，会真实调用 3 次接口，打印每条的成本并估算月成本。

import os
import json
import time
import datetime

import requests
from dotenv import load_dotenv

from API_connect import API_URL, SYSTEM_PROMPT

load_dotenv()
API_KEY = os.environ["DEEPSEEK_API_KEY"]

# DeepSeek 官方价（2026-09-10 起，deepseek-flash）：元 / 百万 tokens
PRICE = {
    "peak":     {"hit": 0.04, "miss": 2.0, "out": 8.0},
    "off_peak": {"hit": 0.02, "miss": 1.0, "out": 4.0},
}


def is_peak(now=None):
    """北京时间周一~周五 9:00-12:00、14:00-18:00 为高峰，其余空闲。"""
    now = now or datetime.datetime.now()
    if now.weekday() >= 5:                       # 5=周六 6=周日
        return False
    minutes = now.hour * 60 + now.minute
    return (9 * 60 <= minutes < 12 * 60) or (14 * 60 <= minutes < 18 * 60)


def calc_cost(usage, peak):
    """按 usage 算这一条的实际花费（元）。"""
    p = PRICE["peak" if peak else "off_peak"]
    hit = usage.get("prompt_cache_hit_tokens", 0)
    miss = usage.get("prompt_cache_miss_tokens",
                     usage.get("prompt_tokens", 0) - hit)
    out = usage.get("completion_tokens", 0)
    return (hit * p["hit"] + miss * p["miss"] + out * p["out"]) / 1_000_000


def ask_once(text):
    """发一次请求，返回 (记录字典, usage, 耗时秒)。参数与 ask_model 一致。"""
    payload = {
        "model": "deepseek-flash",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        "thinking": {"type": "disabled"},
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "stream": False,
    }
    t0 = time.perf_counter()
    resp = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        json=payload,
        timeout=30,
    )
    elapsed = time.perf_counter() - t0
    resp.raise_for_status()
    data = resp.json()
    rec = json.loads(data["choices"][0]["message"]["content"])
    return rec, data.get("usage", {}), elapsed


SAMPLES = [
    "2026-11-02 早餐店 豆浆油条 支出 6.00",
    "2026-11-08 房东 房租 支出 1200.00",
    "2026-11-09 同学聚餐 AA 支出 80.00",
]


def main():
    peak = is_peak()
    print(f"当前时段：{'高峰' if peak else '空闲'}\n")
    print(f"{'#':<3}{'耗时s':>7}{'输入':>8}{'命中':>7}"
          f"{'未命中':>7}{'输出':>6}{'合计':>7}{'费用元':>11}")

    total_cost = 0.0
    total_sec = 0.0
    total_tokens = 0

    for i, text in enumerate(SAMPLES, 1):
        rec, usage, sec = ask_once(text)
        cost = calc_cost(usage, peak)
        total_cost += cost
        total_sec += sec
        total_tokens += usage.get("total_tokens", 0)
        prompt = usage.get("prompt_tokens", 0)
        hit = usage.get("prompt_cache_hit_tokens", 0)
        print(f"{i:<3}{sec:>7.2f}{prompt:>8}{hit:>7}"
              f"{prompt - hit:>7}{usage.get('completion_tokens', 0):>6}"
              f"{usage.get('total_tokens', 0):>7}{cost:>11.6f}")

    n = len(SAMPLES)
    avg_cost = total_cost / n
    avg_sec = total_sec / n
    avg_tokens = total_tokens / n

    print("\n—— 单条平均 ——")
    print(f"tokens：{avg_tokens:.0f}")
    print(f"耗时：  {avg_sec:.2f} 秒")
    print(f"费用：  {avg_cost:.6f} 元（约 {avg_cost * 10000:.2f} 元 / 万条）")

    print("\n—— 月成本估算 ——")
    for per_day in (3, 10):
        monthly = per_day * 30 * avg_cost
        print(f"每天 {per_day:>2} 条 → 每月 {per_day * 30:>3} 条 ≈ {monthly:.4f} 元")

    print("\n注：本次三次实测 prompt_cache_hit_tokens 均为 0，"
          "短提示词没有触发上下文缓存，输入按未命中价计费。")


if __name__ == "__main__":
    main()
