# -*- coding: utf-8 -*-
"""
万年历侦探 · 日期推理 6 题
====================================================
日历不是背出来的，是推出来的。这个游戏只考三件事：
  · 星期的循环（7 天一轮）
  · 闰年的规则（四年一闰、百年不闰、四百年再闰）
  · 天数的加减（每月天数、跨年）

6 道题，题型各不同：
  1）某一天是星期几
  2）某月的第 N 个星期几是几号
  3）某一年是不是闰年
  4）两个日期之间隔了多少天
  5）某天是当年的第几天
  6）某天往前推 N 天是哪一天

命令：
  hint   本题提示（−30 分）
  q      退出

计分：每题 100 分。
运行：python3 2026-11-15_万年历侦探.py
"""

from datetime import date, timedelta

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
WEEK_CN = "一二三四五六日"


def is_leap(y):
    return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)


def days_in_month(y, m):
    if m == 2 and is_leap(y):
        return 29
    return MONTH_DAYS[m - 1]


def nth_weekday(year, month, weekday, n):
    """某年某月的第 n 个星期几（weekday: 0=周一 … 6=周日），返回日号。"""
    d = date(year, month, 1)
    first = (weekday - d.weekday()) % 7 + 1
    return first + (n - 1) * 7


def yday(d):
    return (d - date(d.year, 1, 1)).days + 1


def cn_weekday(d):
    return "星期" + WEEK_CN[d.weekday()]


# 每题：题型、题干、正确答案、提示
QUESTIONS = []


def build_questions():
    QUESTIONS.clear()

    base = date(2026, 11, 15)
    d1 = date(2027, 1, 1)
    span = (d1 - base).days
    QUESTIONS.append({
        "kind": "weekday",
        "q": "已知 2026 年 11 月 15 日是星期日，那么 2027 年元旦（1 月 1 日）是星期几？",
        "answer": d1.weekday() + 1,          # 1=周一 … 7=周日
        "hint": f"先算两个日期相差 {span} 天，再用天数对 7 取余，从星期日往后推。",
        "explain": f"2026-11-15 到 2027-01-01 相差 {span} 天，{span} % 7 = {span % 7}，"
                   f"星期日往后推 {span % 7} 天就是{cn_weekday(d1)}。",
        "input_hint": "输入 1-7（1=周一，7=周日），也可以写「一」到「日」",
    })

    q2_day = nth_weekday(2026, 12, 3, 3)     # 3 = 周四
    QUESTIONS.append({
        "kind": "date",
        "q": "2026 年 12 月的第 3 个星期四是 12 月几号？",
        "answer": f"12-{q2_day}",
        "hint": "先算出 12 月 1 日是星期几，再往后数两个整周。",
        "explain": f"2026-12-01 是{cn_weekday(date(2026,12,1))}，"
                   f"第一个星期四是 12 月 {nth_weekday(2026,12,3,1)} 号，"
                   f"每 7 天一个，第 3 个就是 12 月 {q2_day} 号。",
        "input_hint": "输入「月-日」，例如 12-5",
    })

    QUESTIONS.append({
        "kind": "yesno",
        "q": "2100 年是闰年吗？（y=是 / n=不是）",
        "answer": "n",
        "hint": "整百年要额外检查能不能被 400 整除。",
        "explain": "2100 能被 4 整除，但它也是整百年且不能被 400 整除，所以是平年（365 天）。"
                   "这正是「四年一闰、百年不闰、四百年再闰」里最容易被忽略的一条。",
        "input_hint": "输入 y 或 n",
    })

    d_a, d_b = date(2026, 10, 24), date(2027, 2, 14)
    gap = (d_b - d_a).days
    QUESTIONS.append({
        "kind": "number",
        "q": "从 2026 年 10 月 24 日到 2027 年 2 月 14 日，一共经过多少天？（只算相差的天数）",
        "answer": gap,
        "hint": "先算 2026 年剩下的天数，再加上 2027 年的 1 月和 2 月上半月。",
        "explain": f"10-24 到 12-31 有 {(date(2026,12,31)-d_a).days} 天，"
                   f"再加 2027 年的 31 + 14 = 45 天，合计 {gap} 天。",
        "input_hint": "输入一个整数",
    })

    d5 = date(2026, 11, 15)
    QUESTIONS.append({
        "kind": "number",
        "q": "2026 年 11 月 15 日，是 2026 年的第几天？",
        "answer": yday(d5),
        "hint": "前 10 个月的天数加起来，再加 15。2026 不是闰年，2 月只有 28 天。",
        "explain": f"1 到 10 月共 {sum(MONTH_DAYS[:10])} 天，再加 15 天 = {yday(d5)} 天。",
        "input_hint": "输入一个整数",
    })

    d6 = date(2027, 1, 1) - timedelta(days=100)
    QUESTIONS.append({
        "kind": "date",
        "q": "2027 年 1 月 1 日往前数 100 天，是哪一天？（写成 年-月-日）",
        "answer": d6.isoformat(),
        "hint": "先退到 2026 年 12 月 1 日是往前 31 天，还剩 69 天要退。",
        "explain": f"2027-01-01 往前 31 天是 2026-12-01；还差 69 天："
                   f"12-01 退 30 天到 11-01，剩 39 天；11-01 再退 31 天到 10-01，剩 8 天，"
                   f"所以落在 {d6.isoformat()}。",
        "input_hint": "输入「年-月-日」，例如 2026-9-23",
    })


def normalize_date(text):
    text = text.replace("/", "-").replace("月", "-").replace("日", "").strip()
    parts = [p for p in text.split("-") if p]
    if len(parts) == 2:
        return f"{int(parts[0])}-{int(parts[1])}"
    if len(parts) == 3:
        return f"{int(parts[0])}-{int(parts[1])}-{int(parts[2])}"
    return None


def check(item, raw):
    """返回 (是否正确, 标准化的用户答案)。"""
    low = raw.strip().lower()
    kind = item["kind"]
    if kind == "number":
        if not low.isdigit():
            return None, None
        return int(low) == item["answer"], low
    if kind == "yesno":
        if low in ("y", "yes", "是"):
            return item["answer"] == "y", "y"
        if low in ("n", "no", "不是", "否"):
            return item["answer"] == "n", "n"
        return None, None
    if kind == "weekday":
        table = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "日": 7, "天": 7}
        if low.isdigit() and 1 <= int(low) <= 7:
            return int(low) == item["answer"], low
        for ch, num in table.items():
            if ch in low:
                return num == item["answer"], str(num)
        return None, None
    if kind == "date":
        norm = normalize_date(raw)
        if norm is None:
            return None, None
        # 标准答案同样做一次规范化，避免「2026-9-23」与「2026-09-23」被判不等
        return norm == normalize_date(item["answer"]), norm
    return None, None


def play():
    build_questions()
    print("=" * 62)
    print("      📅 万年历侦探")
    print("=" * 62)
    print("6 道日期推理题，随时输入 hint 看提示（本题 −30 分），q 退出。")

    total = 0
    right = 0
    for idx, item in enumerate(QUESTIONS, 1):
        score = 100
        print("\n" + "-" * 62)
        print(f"  第 {idx} 题：{item['q']}")
        print(f"  （{item['input_hint']}）")
        while True:
            try:
                raw = input("  > ").strip()
            except EOFError:
                print("\n输入中断，提前结算。")
                return report(total, right, idx - 1)
            if not raw:
                continue
            low = raw.lower()
            if low in ("q", "quit"):
                return report(total, right, idx - 1)
            if low == "hint":
                if score > 30:
                    score -= 30
                print(f"  提示：{item['hint']}（本题剩 {score} 分）")
                continue
            ok, norm = check(item, raw)
            if ok is None:
                print(f"  格式不对。{item['input_hint']}")
                continue
            if ok:
                print("  ✅ 正确！" + item["explain"])
                total += score
                right += 1
            else:
                print(f"  ❌ 不对。正确答案：{item['answer']}。" + item["explain"])
            break

    return report(total, right, len(QUESTIONS))


def report(total, right, done):
    print("\n" + "=" * 62)
    print(f"  结算：{right}/{done} 题正确，总分 {total}/600")
    if total >= 500:
        print("  🏆 日历交给你，一天都不会错。")
    elif total >= 250:
        print("  👍 星期和闰年都清楚了，跨年天数再稳一点。")
    else:
        print("  🙂 记住三条：7 天循环、闰年规则、每月天数。")
    print("=" * 62)


if __name__ == "__main__":
    play()
