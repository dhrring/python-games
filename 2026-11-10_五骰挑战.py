# -*- coding: utf-8 -*-
"""
五骰挑战（Yahtzee 简化版 · 组合计分）
=======================================
5 颗骰子，每轮最多掷 3 次（第一次全掷，之后你可以只重掷其中几颗）。
一共 6 轮，每轮结算时必须占用一个还没用过的计分类别。
怎么分配类别，全看你的判断 —— 这就是这个游戏的核心策略。

6 个计分类别：
  总和     5 颗骰子的点数相加（稳定拿分）
  三条+    至少有 3 颗同点数 → 该点数×3 + 另外两颗之和；否则 0
  葫芦     3 颗同点 + 2 颗同点 → 40 分（否则 0）
  小顺     含 4 颗连续点数（如 1-2-3-4）→ 30 分
  大顺     5 颗正好连续（如 2-3-4-5-6）→ 40 分
  五同     5 颗全部同点 → 50 分（很难，压轴）

游玩方法：
  掷完骰子后，输入要「保留」的骰子编号（空格分隔，如 1 3 5），
  其余骰子会被重掷；直接回车表示全部重掷。
  掷满 3 次后，输入类别编号（0~5 见屏幕提示）结算。
  输入 q 可随时退出。
运行：python3 2026-11-10_五骰挑战.py
"""

import random

N_DICE = 5
MAX_ROLLS = 3

CATEGORIES = [
    ("总和", "5 颗骰子点数相加"),
    ("三条+", "至少 3 颗同点：该点数×3 + 另外两颗之和"),
    ("葫芦", "3 颗同点 + 2 颗同点 = 40 分"),
    ("小顺", "含 4 颗连续点数 = 30 分"),
    ("大顺", "5 颗连续点数 = 40 分"),
    ("五同", "5 颗全部同点 = 50 分"),
]


def roll(n):
    return [random.randint(1, 6) for _ in range(n)]


def counts(dice):
    c = {v: dice.count(v) for v in range(1, 7)}
    return c


def has_run(dice, length):
    vals = sorted(set(dice))
    best = 1
    cur = 1
    for i in range(1, len(vals)):
        if vals[i] == vals[i - 1] + 1:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best >= length


def score(dice, cat_index):
    """返回该类别下的分数（0 表示没凑成）。"""
    c = counts(dice)
    total = sum(dice)
    top = max(c.items(), key=lambda x: (x[1], x[0]))  # 最多的点数及其个数

    if cat_index == 0:  # 总和
        return total
    if cat_index == 1:  # 三条+
        if top[1] >= 3:
            return top[0] * 3 + (total - top[0] * top[1])
        return 0
    if cat_index == 2:  # 葫芦
        freqs = sorted(c.values(), reverse=True)
        if freqs[0] == 3 and freqs[1] == 2:
            return 40
        if freqs[0] == 5:
            return 40  # 五同也含 3+2 结构，给分
        return 0
    if cat_index == 3:  # 小顺
        return 30 if has_run(dice, 4) else 0
    if cat_index == 4:  # 大顺
        return 40 if has_run(dice, 5) else 0
    if cat_index == 5:  # 五同
        return 50 if top[1] == 5 else 0
    return 0


def show_dice(dice, kept=()):
    marks = []
    for i, v in enumerate(dice):
        s = f"[{'★' if i in kept else ' '}{i + 1}:{v}]"
        marks.append(s)
    print("  " + " ".join(marks) + "   （★ = 本轮保留）")


def ask_keep(dice, rolls_used):
    while True:
        raw = input(f"  （第 {rolls_used} 次掷完）保留哪些骰子编号？回车=全部重掷，q=退出：").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        if raw == "":
            return set()
        parts = raw.replace("，", " ").replace(",", " ").split()
        if not all(p.isdigit() and 1 <= int(p) <= N_DICE for p in parts):
            print("  请输入 1~5 之间的编号，例如 1 3 5。")
            continue
        keep = {int(p) - 1 for p in parts}
        # 不允许保留全部（那样等于不重掷，浪费一次机会）
        if len(keep) == N_DICE:
            print("  保留全部就没有重掷的意义了，请至少留一颗重掷；回车可放弃重掷直接选类别。")
            continue
        return keep


def play_round(round_no, used):
    print("\n" + "=" * 52)
    print(f"  第 {round_no} / 6 轮    已用类别：{[CATEGORIES[i][0] for i in used] or '无'}")
    print("=" * 52)

    dice = roll(N_DICE)
    rolls = 1
    show_dice(dice)

    while rolls < MAX_ROLLS:
        keep = ask_keep(dice, rolls)
        if keep is None:
            return None, 0
        if not keep:
            # 全部重掷 / 或者玩家想直接结算（这里用空回车表示全掷）
            dice = roll(N_DICE)
        else:
            dice = [v if i in keep else random.randint(1, 6) for i, v in enumerate(dice)]
        rolls += 1
        show_dice(dice, keep if keep else ())

    print("\n  本轮最终骰面：" + " ".join(str(v) for v in dice))
    print("  可选的计分类别：")
    for i, (name, rule) in enumerate(CATEGORIES):
        if i in used:
            continue
        print(f"    {i}. {name:<6} 本类别当前可得 {score(dice, i):>3} 分   （{rule}）")

    while True:
        raw = input("  选择类别编号结算：").strip()
        if raw.lower() in ("q", "quit", "exit"):
            return None, 0
        if not raw.isdigit() or int(raw) not in range(len(CATEGORIES)):
            print("  请输入 0~5 的编号。")
            continue
        idx = int(raw)
        if idx in used:
            print("  这个类别已经用过了，换一个。")
            continue
        pts = score(dice, idx)
        print(f"  ➜ 「{CATEGORIES[idx][0]}」得 {pts} 分")
        return idx, pts


def main():
    print("=" * 52)
    print("      🎲 五骰挑战 Yahtzee")
    print("=" * 52)
    print("5 颗骰子、3 次掷骰机会、6 轮结算 —— 把好骰面用在分值最高的类别上。")
    print("满分理论值 50+40+40+30+ (6×3+12=30) + 30 = 220 左右，能上 120 就算厉害了。")

    total = 0
    used = set()
    for r in range(1, 7):
        idx, pts = play_round(r, used)
        if idx is None:
            print("\n你已退出。")
            print(f"当前总分：{total}")
            return
        used.add(idx)
        total += pts
        print(f"  累计总分：{total}")

    print("\n" + "=" * 52)
    print(f"  最终总分：{total}")
    if total >= 130:
        print("  🏆 骰运与决策俱佳，接近理论最优。")
    elif total >= 90:
        print("  👍 打得不错，注意把「五同 / 葫芦」留给真正凑成的轮次。")
    else:
        print("  🙂 下一局可以更保守：总和类永远能拿 15~25 分，是保底盘。")
    print("=" * 52)


if __name__ == "__main__":
    main()
