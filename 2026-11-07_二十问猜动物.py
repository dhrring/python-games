# -*- coding: utf-8 -*-
"""
二十问猜动物（20 Questions: Animal）
=====================================
你心里想一种动物（从游戏给出的候选清单里挑），电脑用一组「是/否」问题
逐步缩小范围，最后猜出你心中所想的那种动物。
每题回答：y = 是，n = 否，u = 不确定（不筛除任何候选）。
纯标准库实现。
运行：python3 2026-11-07_二十问猜动物.py
"""

# 特征顺序（与下面向量一一对应）
KEYS = [
    ("mammal", "是哺乳动物吗？"),
    ("fly", "会飞吗？"),
    ("aquatic", "主要生活在水里吗？"),
    ("egg", "会下蛋吗？"),
    ("carnivore", "是肉食性的（吃其他动物）吗？"),
    ("hair", "身上有毛或羽毛吗？"),
    ("legs", "有腿吗？"),
    ("insect", "是昆虫吗？"),
    ("small", "体型明显比人小（不到 1 米）吗？"),
    ("stripe", "身上有明显条纹吗？"),
    ("climb", "善于爬树或攀爬吗？"),
    ("large", "体型比人还大吗？"),
]

# 每个动物的特征向量（1=是，0=否），顺序同 KEYS
ANIMALS = {
    "老虎": [1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1],
    "狮子": [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    "大象": [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    "熊猫": [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
    "兔子": [1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
    "猫":   [1, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0],
    "狗":   [1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    "猴子": [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0],
    "马":   [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    "鲸鱼": [1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    "鲨鱼": [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    "青蛙": [0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0],
    "蛇":   [0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0],
    "乌龟": [0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],
    "麻雀": [0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    "老鹰": [0, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    "鸭子": [0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0],
    "企鹅": [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
    "蜜蜂": [0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
    "蜘蛛": [0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0],
}


def best_question(candidates, asked):
    """选一个能最均衡拆分候选集、且尚未问过的特征。"""
    best_idx, best_balance = -1, 0
    for i in range(len(KEYS)):
        if i in asked:
            continue
        yes = sum(1 for a in candidates if ANIMALS[a][i] == 1)
        no = len(candidates) - yes
        if yes == 0 or no == 0:
            continue
        balance = min(yes, no)
        if balance > best_balance:
            best_idx, best_balance = i, balance
    return best_idx


def main():
    print("=" * 48)
    print("        🐾 二十问猜动物 20 Questions")
    print("=" * 48)
    print("候选动物（共 %d 种）：" % len(ANIMALS))
    print("、".join(ANIMALS.keys()))
    print("\n请在心里选定其中一种，然后只回答 y（是）/ n（否）/ u（不确定）。")
    print("输入 q 退出。")

    candidates = list(ANIMALS.keys())
    asked = []
    qcount = 0

    while True:
        if len(candidates) == 1:
            print("\n" + "=" * 48)
            print(f"🎯 我猜你想的是：{candidates[0]} ！")
            fb = input("猜对了吗？(y/n)：").strip().lower()
            if fb == "y":
                print("🎉 太棒了，我猜对了！")
            else:
                print("🤔 猜错了，看来你的特征组合比较特别。")
            return

        if not candidates:
            print("\n😵 你的回答让所有候选动物都被排除了，信息可能有点矛盾。")
            print("要不要重来一局？")
            return

        idx = best_question(candidates, asked)
        if idx == -1:
            print("\n🤷 问题问完了，但仍无法唯一确定。剩下的候选是：")
            print("、".join(candidates))
            return

        asked.append(idx)
        qcount += 1
        name, text = KEYS[idx]
        print(f"\n第 {qcount} 问：{text}  （剩余候选 {len(candidates)} 种）")
        while True:
            ans = input("你的回答 y/n/u：").strip().lower()
            if ans in ("y", "n", "u", "q"):
                break
            print("请输入 y、n 或 u。")
        if ans == "q":
            print("你已退出游戏。")
            return
        if ans == "y":
            candidates = [a for a in candidates if ANIMALS[a][idx] == 1]
        elif ans == "n":
            candidates = [a for a in candidates if ANIMALS[a][idx] == 0]
        # u：不筛除


if __name__ == "__main__":
    main()
