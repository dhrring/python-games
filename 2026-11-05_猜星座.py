# -*- coding: utf-8 -*-
"""
猜星座（Guess the Zodiac）
============================
随机给出一个日期，猜它属于哪个星座。每题 3 次机会，
答错会提示星座的元素（火/土/风/水）归属。共 5 题，统计正确率。
纯标准库实现。
运行：python3 2026-11-05_猜星座.py
"""

import random

# (星座名, 元素, 起始(月,日), 结束(月,日))
ZODIAC = [
    ("水瓶座", "风", (1, 20), (2, 18)),
    ("双鱼座", "水", (2, 19), (3, 20)),
    ("白羊座", "火", (3, 21), (4, 19)),
    ("金牛座", "土", (4, 20), (5, 20)),
    ("双子座", "风", (5, 21), (6, 21)),
    ("巨蟹座", "水", (6, 22), (7, 22)),
    ("狮子座", "火", (7, 23), (8, 22)),
    ("处女座", "土", (8, 23), (9, 22)),
    ("天秤座", "风", (9, 23), (10, 23)),
    ("天蝎座", "水", (10, 24), (11, 22)),
    ("射手座", "火", (11, 23), (12, 21)),
    ("摩羯座", "土", (12, 22), (1, 19)),
]


def which_zodiac(month, day):
    """根据月日返回星座名（用 月*100+日 整数比较，摩羯跨年单独处理）。"""
    md = month * 100 + day
    if md >= 1222 or md <= 119:  # 摩羯座 12.22 - 1.19（跨年）
        return "摩羯座", "土"
    for name, elem, (sm, sd), (em, ed) in ZODIAC:
        if sm * 100 + sd <= md <= em * 100 + ed:
            return name, elem
    return None, None


def main():
    print("=" * 46)
    print("        🌌 猜星座 Guess the Zodiac")
    print("=" * 46)
    print("给出一个日期，猜它属于哪个星座。每题 3 次机会，答错给元素提示。")
    print("输入 'q' 提前结束。")

    # 生成 12 个有代表性的日期（每个星座取一个中间日期）
    sample_dates = [
        (1, 25), (2, 25), (3, 25), (4, 25), (5, 25), (6, 25),
        (7, 25), (8, 25), (9, 25), (10, 25), (11, 25), (12, 25),
    ]
    random.shuffle(sample_dates)
    total = 5
    correct = 0
    for i in range(total):
        month, day = sample_dates[i]
        name, elem = which_zodiac(month, day)
        print(f"\n第 {i+1}/{total} 题：{month} 月 {day} 日出生，是什么星座？")
        for chance in range(1, 4):
            got = input(f"第{chance}次尝试：").strip()
            if got.lower() in ("q", "quit", "exit"):
                print("提前结束。")
                total = i
                print_summary(correct, total)
                return
            got = got.replace("座", "")
            if got == name:
                correct += 1
                print("✅ 答对了！")
                break
            if chance < 3:
                print(f"线索：这个星座属于【{elem}】元素系。")
            else:
                print(f"❌ 答案是：{name}（{month}月{day}日）")

    print_summary(correct, total)


def print_summary(correct, total):
    if total == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / total * 100
    print("\n" + "=" * 46)
    print(f"        结果：{correct}/{total}  正确率 {acc:.1f}%")
    print("=" * 46)
    if acc == 100:
        print("🏆 满分！星座达人！")
    elif acc >= 60:
        print("👍 不错，天文小能手！")
    else:
        print("🔭 查查星座表，下次更好！")


if __name__ == "__main__":
    main()
