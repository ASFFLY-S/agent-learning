import json
import requests
from API_connect import API_URL, API_KEY

SUMMARY_SYSTEM = """你是个人记账分析助手，负责把一个月的数据写成一段能给用户直接看的中文总结。

【写作要求】
1. 只能使用我给你的 JSON 里的数字和类别，禁止编造任何金额、日期或类别。
2. 占比和环比我已经算好了，直接引用，不要自己重新计算，也不要改动数值。
3. 如果"上月支出合计"是 null，说明没有上月数据，就跳过环比，不要编造上月情况。
4. 建议要具体、可执行，最多 3 条，不要写"继续保持"这类空话。
5. 语气平实，像记账助手在汇报，不要夸张，不要用网络流行语。

【输出格式】
纯文本，不要 JSON，不要 Markdown 标题符号。分 4 段，每段 1~3 句：
第 1 段：本月概览（收入、支出、结余）
第 2 段：钱主要花在哪（引用支出前 2~3 类及占比）
第 3 段：环比变化（比上月涨了还是降了，多少）
第 4 段：建议（2~3 条）
全文 200~300 字。"""


def build_facts(summary, month, prev_summary=None):
    """把 summarize 的字典整理成给模型的事实清单（数值先在 Python 里算好）。"""
    income = summary.get("收入分类小计") or {}
    expense = summary.get("支出分类小计") or {}
    income_total = float(summary.get("收入合计") or 0)
    expense_total = float(summary.get("支出合计") or 0)
    balance = float(summary.get("本月结余") or 0)

    def share(d, total):
        if total <= 0:
            return {}
        return {k: round(float(v) / total * 100, 1) for k, v in d.items()}

    facts = {
        "月份": month,
        "收入合计": round(income_total, 2),
        "支出合计": round(expense_total, 2),
        "结余": round(balance, 2),
        "收入分类": {k: round(float(v), 2) for k, v in income.items()},
        "支出分类": {k: round(float(v), 2) for k, v in expense.items()},
        "收入分类占比(%)": share(income, income_total),
        "支出分类占比(%)": share(expense, expense_total),
        "上月支出合计": None,
        "支出环比(%)": None,
    }

    if prev_summary:
        prev_total = float(prev_summary.get("支出合计") or 0)
        facts["上月支出合计"] = round(prev_total, 2)
        if prev_total > 0:
            facts["支出环比(%)"] = round(
                (expense_total - prev_total) / prev_total * 100, 1
            )

    return facts


def make_summary(summary, month, prev_summary=None, timeout=30):
    """返回一段中文总结文本；接口异常时抛异常，由调用方处理。"""
    facts = build_facts(summary, month, prev_summary)
    payload = {
        "model": "deepseek-flash",
        "messages": [
            {"role": "system", "content": SUMMARY_SYSTEM},
            {"role": "user", "content": json.dumps(facts, ensure_ascii=False)},
        ],
        "thinking": {"type": "disabled"},
        "temperature": 0.7,
        "stream": False,
    }
    resp = requests.post(
        API_URL,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + API_KEY,
        },
        json=payload,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
# ============ 自检：直接运行本文件时执行 ============
if __name__ == "__main__":
    import os
    import sys

    print("=" * 46)
    print("R78 自检 —— build_facts（离线，不调用接口）")
    print("=" * 46)

    results = []

    def check(name, cond, detail=""):
        results.append(bool(cond))
        mark = "OK  " if cond else "FAIL"
        line = f"[{mark}] {name}"
        if detail:
            line += f"  -> {detail}"
        print(line)

    CUR = {
        "收入分类小计": {"工资": 5000.0},
        "支出分类小计": {"餐饮": 35.5, "交通": 6.0},
        "收入合计": 5000.0,
        "支出合计": 41.5,
        "本月结余": 4958.5,
    }
    PREV = {"支出合计": 120.0}

    # 1) 正常数据 + 有上月
    f = build_facts(CUR, "2026-11", PREV)
    check("月份原样传递", f["月份"] == "2026-11")
    check("收入合计 5000.0", f["收入合计"] == 5000.0)
    check("支出合计 41.5", f["支出合计"] == 41.5)
    check("结余 4958.5", f["结余"] == 4958.5)
    check("餐饮占比 85.5%", f["支出分类占比(%)"]["餐饮"] == 85.5,
          f["支出分类占比(%)"])
    check("交通占比 14.5%", f["支出分类占比(%)"]["交通"] == 14.5)
    check("占比合计约等于 100",
          abs(sum(f["支出分类占比(%)"].values()) - 100) <= 0.1)
    check("上月支出 120.0", f["上月支出合计"] == 120.0)
    check("环比 -65.4%", f["支出环比(%)"] == -65.4, f["支出环比(%)"])
    check("facts 可被 json 序列化",
          isinstance(json.dumps(f, ensure_ascii=False), str))

    # 2) 没有上月数据
    f2 = build_facts(CUR, "2026-11", None)
    check("无上月：环比为 None", f2["支出环比(%)"] is None)
    check("无上月：上月合计为 None", f2["上月支出合计"] is None)
    check("无上月：本月占比不受影响", f2["支出分类占比(%)"]["餐饮"] == 85.5)

    # 3) 支出为 0（空月份）
    f3 = build_facts({"收入合计": 0, "支出合计": 0, "本月结余": 0,
                      "收入分类小计": {}, "支出分类小计": {}}, "2026-11")
    check("支出为 0 不除零，占比为空", f3["支出分类占比(%)"] == {})
    check("支出为 0 时合计为 0.0", f3["支出合计"] == 0.0)

    # 4) 上月支出为 0
    f4 = build_facts(CUR, "2026-11", {"支出合计": 0})
    check("上月为 0 时环比为 None（不除零）", f4["支出环比(%)"] is None)

    # 5) 四舍五入保留 1 位小数
    f5 = build_facts({"收入合计": 0, "支出合计": 3.0, "本月结余": -3.0,
                      "收入分类小计": {},
                      "支出分类小计": {"A": 1.0, "B": 1.0, "C": 1.0}}, "2026-11")
    check("占比保留 1 位小数（33.3）", f5["支出分类占比(%)"]["A"] == 33.3,
          f5["支出分类占比(%)"])

    # 6) 可选：真实调用一次接口（python R78.py --online）
    if "--online" in sys.argv:
        print("\n在线自检：真实调用一次接口")
        if not os.environ.get("DEEPSEEK_API_KEY"):
            check("DEEPSEEK_API_KEY 已配置", False, "环境变量里没有这个 key")
        else:
            try:
                text = make_summary(CUR, "2026-11", PREV)
                check("返回非空文本", bool(text.strip()))
                check("长度不少于 50 字", len(text.strip()) >= 50,
                      f"{len(text.strip())} 字")
                print("\n----- 模型生成的总结 -----")
                print(text)
            except Exception as e:
                check("在线调用成功", False, f"{type(e).__name__}: {e}")
    else:
        print("\n（未调用接口；加上 --online 参数可真实生成一次）")

    print("-" * 46)
    print(f"通过 {sum(results)} / {len(results)} 项")
    print("自检通过。" if all(results) else "自检有失败项，先修 build_facts 再接主程序。")
