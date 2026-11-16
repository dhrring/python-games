# -*- coding: utf-8 -*-
"""
背包淘金 · 0/1 背包挑战
====================================================
你是一个背包客，容量有限，面前一堆金块，每块有重量和价值。
目标很朴素：在总重量不超过容量的前提下，让背走的总价值最大。

玩法：
  每关列出物品（编号、重量、价值），你输入要带的编号，用空格分隔。
  例：带 1、3、5 号 → 输入  1 3 5
  每关满分 100 = 只要拿到最优解。没到最优就按比例给分；
  超重直接 0 分（但会告诉你超了多少）。

命令：
  list   再看一次物品清单
  hint   本题提示（−30 分）
  q      退出

和普通「贪心」的区别：
  按「单位重量价值最高」先拿，在有些关卡里会卡住走不下去，
  必须整体权衡——这正是 0/1 背包要用动态规划的原因。

运行：python3 2026-11-16_背包淘金.py
"""

import itertools

LEVELS = [
    {
        "cap": 10,
        "items": [("金块", 5, 10), ("银锭", 4, 7), ("铜钱袋", 3, 6), ("宝石", 2, 5)],
        "note": "小试身手：四件东西，容量 10。",
        "hint": "先算每件东西的「价值/重量」，从高的开始往里塞，再看有没有空位补小件。",
    },
    {
        "cap": 10,
        "items": [
            ("大金砖", 6, 30), ("银锭甲", 5, 21), ("银锭乙", 5, 21), ("铜佛", 6, 25), ("碎银", 2, 3),
        ],
        "note": "别贪心：这一关按「单位重量价值最高」先拿，反而会亏。",
        "hint": "大金砖单位价值最高（5.0），但它占 6 格；试着拿两件各占 5 格的银锭，看看总价值。",
    },
    {
        "cap": 20,
        "items": [
            ("夜明珠", 11, 24), ("翡翠镯", 8, 17), ("鎏金佛", 7, 15), ("紫檀匣", 6, 13),
            ("古钱币", 5, 11), ("铜炉", 4, 9), ("绢画", 3, 6), ("瓷碗", 2, 4),
        ],
        "note": "物品多了：值钱的往往也重，需要动态规划那种「逐件权衡」的思路。",
        "hint": "先固定 1 到 4 件的组合，再看剩下的容量还能塞哪些小件；重点比较总价值而不是单件。",
    },
]


def solve(cap, items):
    """标准 0/1 背包 DP，返回 (最优价值, 对应的物品下标列表)。"""
    n = len(items)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        w, v = items[i - 1][1], items[i - 1][2]
        for c in range(cap + 1):
            dp[i][c] = dp[i - 1][c]
            if c >= w and dp[i - 1][c - w] + v > dp[i][c]:
                dp[i][c] = dp[i - 1][c - w] + v
    # 回溯一组最优解
    picked = []
    c = cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            picked.append(i - 1)
            c -= items[i - 1][1]
    return dp[n][cap], sorted(picked)


def greedy_by_ratio(cap, items):
    """贪心对照组：按 价值/重量 从高到低塞，返回 (价值, 下标)。"""
    order = sorted(range(len(items)), key=lambda i: -(items[i][2] / items[i][1]))
    total_w = total_v = 0
    picked = []
    for i in order:
        w, v = items[i][1], items[i][2]
        if total_w + w <= cap:
            total_w += w
            total_v += v
            picked.append(i)
    return total_v, sorted(picked)


def brute_force(cap, items):
    """穷举所有子集，用于交叉校验 DP 的结果。"""
    best = (0, [])
    n = len(items)
    for mask in range(1 << n):
        w = v = 0
        idx = []
        for i in range(n):
            if mask >> i & 1:
                w += items[i][1]
                v += items[i][2]
                idx.append(i)
        if w <= cap and v > best[0]:
            best = (v, idx)
    return best


def show_items(cap, items):
    print(f"\n  背包容量：{cap}")
    print("  编号  物品      重量  价值")
    print("  " + "-" * 30)
    for i, (name, w, v) in enumerate(items, 1):
        print(f"   {i:>2}   {name:<6}  {w:>3}   {v:>3}")
    print(f"  （物品共 {len(items)} 件）")


def run_level(idx, level):
    cap = level["cap"]
    items = level["items"]
    best_v, best_idx = solve(cap, items)
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + level["note"])
    show_items(cap, items)

    score = 100
    while True:
        try:
            raw = input("\n  要带哪些（编号，空格分隔）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "list":
            show_items(cap, items)
            continue
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：{level['hint']}（本题剩 {score} 分）")
            continue

        tokens = raw.replace(",", " ").split()
        bad = [t for t in tokens if not t.isdigit()]
        if bad:
            print("  只要数字编号。")
            continue
        picks = sorted(set(int(t) - 1 for t in tokens))
        if any(p < 0 or p >= len(items) for p in picks):
            print(f"  编号要在 1 到 {len(items)} 之间。")
            continue

        # 去重后重新累加（同一件东西不能拿两次）
        weight = sum(items[p][1] for p in picks)
        value = sum(items[p][2] for p in picks)
        if weight > cap:
            print(f"  ❌ 超重了：{weight} > 容量 {cap}。超重不计分。")
            print(f"  最优解是 {best_v} 价值，重 {sum(items[i][1] for i in best_idx)}。")
            return 0, True

        if value == best_v:
            names = "、".join(items[p][0] for p in picks) if picks else "什么都不带"
            print(f"  ✅ 最优！总重 {weight}/{cap}，总价值 {value}。带了：{names}")
            if score < 100:
                print(f"  （用了提示，本关 {score} 分）")
            return score, True

        ratio = value / best_v
        got = max(0, int(score * ratio))
        print(f"  ⚠ 不是最优：总重 {weight}/{cap}，总价值 {value}，最优是 {best_v}。")
        g_v, _g_idx = greedy_by_ratio(cap, items)
        if g_v < best_v:
            print(f"  （顺便一提：无脑按「单位价值」贪心最多只能拿到 {g_v}，所以这关必须整体权衡。）")
        print(f"  本次得 {got} 分。要不要再试一次？直接重新输入编号即可（本题上限 {score} 分）。")
        score = got if got < score else score
        continue


def play():
    print("=" * 62)
    print("      🎒 背包淘金 · 0/1 背包挑战")
    print("=" * 62)
    print("在容量限制内挑物品，让总价值最大。输入编号提交，hint 看提示。")

    # 开局先自检：DP 结果必须与穷举一致，否则关卡数据有问题
    for lv in LEVELS:
        dp_best = solve(lv["cap"], lv["items"])
        bf_best = brute_force(lv["cap"], lv["items"])
        assert dp_best[0] == bf_best[0], (dp_best, bf_best)

    total = 0
    done = 0
    for i, lv in enumerate(LEVELS):
        sc, ok = run_level(i, lv)
        total += sc
        if ok is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 250:
        print("  🏆 你已经不看单价，而是看「整体最优」了。")
    elif total >= 100:
        print("  👍 有感觉了：容量紧的时候，先试大件再补小件往往更快。")
    else:
        print("  🙂 技巧：先算两三种「大件 + 小件」组合的总价值，再挑最高的那组。")
    print("=" * 62)


if __name__ == "__main__":
    play()
