# -*- coding: utf-8 -*-
"""
报刊亭进货决策 · 报童问题
====================================================
你盘下一个报刊亭。每天开门前要决定：某份报纸今天进多少份？

  · 进价 c 元/份，卖价 p 元/份，赚 p − c
  · 卖不掉的部分只能退报，每份退 v 元，亏 c − v
  · 但每天来看报的人数是随机的：进多了剩一堆，进少了白白流失客人

这就是经典的「报童问题」。直觉常常是错的：
  高利润报纸不一定该多进，关键是「卖不掉损失多少」。

理论结论（临界分位数，也叫临界比）：
      临界比 = (p − c) / (p − v)
  最优进货量 = 让「需求不超过 q」的概率刚好达到临界比的那个 q。
  也就是说：宁可偶尔缺货，也别囤一堆卖不掉——
  谁让「多进一份的期望损失」大于「多进一份的期望收益」呢。

玩法：每关给出进价、卖价、退价和需求分布，你决定进货量 q。
      程序会算出你的 q 的期望利润，并与最优 q 的期望利润比较，
      然后用 60 天模拟给你看看「现实长什么样」。

命令：
  calc 25   查任意 q 的期望利润（不扣分，用来验算）
  hint      提示临界比怎么算（−30 分）
  q         退出

运行：python3 2026-11-18_报刊亭进货.py
"""

import random

LEVELS = [
    {
        "name": "街角小报亭",
        "c": 1.0, "p": 2.0, "v": 0.5,
        "demand": [(d, 1) for d in range(20, 41)],
        "note": "需求 20~40 份，等概率。进价 1 元、卖 2 元、退 0.5 元。",
    },
    {
        "name": "写字楼门口的财经报",
        "c": 1.2, "p": 3.0, "v": 0.2,
        "demand": [(d, d - 14) for d in range(15, 36)],
        "note": "看报的人集中在下午，需求偏向 30 份以上（分布向右堆）。",
    },
    {
        "name": "景区的高价纪念报",
        "c": 0.8, "p": 5.0, "v": 0.0,
        "demand": [(d, 1 + (d - 30) ** 2 // 40) for d in range(30, 51)],
        "note": "卖价高、但退不掉（v=0）；需求波动大，30~50 份，两头少中间多。",
    },
]


def dist_norm(demand):
    total = sum(w for _, w in demand)
    return [(d, w / total) for d, w in demand]


PROBS = {lv["name"]: dist_norm(lv["demand"]) for lv in LEVELS}


def eprofit(q, probs, c, p, v):
    """求进货 q 份时的期望利润。"""
    val = 0.0
    for d, pr in probs:
        sold = min(q, d)
        left = max(0, q - d)
        val += pr * (p * sold + v * left - c * q)
    return val


def best_q(probs, c, p, v):
    """枚举所有可能的 q，找期望利润最大者（并列时取较小 q）。"""
    maxd = max(d for d, _ in probs)
    best = (-1e18, 0)
    for q in range(0, maxd + 1):
        val = eprofit(q, probs, c, p, v)
        if val > best[0] + 1e-9:
            best = (val, q)
    return best[1], best[0]


def critical_q(probs, c, p, v):
    """临界分位数法：最小的 q，使 P(需求 <= q) >= (p-c)/(p-v)。"""
    ratio = (p - c) / (p - v)
    acc = 0.0
    for d, pr in probs:
        acc += pr
        if acc >= ratio - 1e-12:
            return d, ratio
    return max(d for d, _ in probs), ratio


def cdf_table(probs):
    acc = 0.0
    rows = []
    for d, pr in probs:
        acc += pr
        rows.append((d, pr, acc))
    return rows


def show_dist(level, probs):
    print("\n  需求分布（每份概率）：")
    scale = max(pr for _, pr in probs)
    for d, pr in probs:
        bar = "█" * int(round(pr / scale * 30))
        print(f"    {d:>3} 份  {pr * 100:5.1f}%  {bar}")
    print(f"    进价 c={level['c']} 元　卖价 p={level['p']} 元　退报 v={level['v']} 元")
    print(f"    单份毛利 p−c={level['p'] - level['c']:.2f}　单份滞销损失 c−v={level['c'] - level['v']:.2f}")


def simulate(q, probs, c, p, v, days=60, seed=20261118):
    rng = random.Random(seed)
    demands = [d for d, _ in probs]
    weights = [pr for _, pr in probs]
    profit = 0.0
    sold_total = 0
    waste_total = 0
    miss_total = 0
    for _ in range(days):
        d = rng.choices(demands, weights=weights, k=1)[0]
        sold = min(q, d)
        waste = max(0, q - d)
        miss_total += max(0, d - q)
        sold_total += sold
        waste_total += waste
        profit += p * sold + v * waste - c * q
    return profit / days, sold_total / days, waste_total / days, miss_total / days


def run_level(idx, level):
    probs = PROBS[level["name"]]
    c, p, v = level["c"], level["p"], level["v"]
    q_star, best_val = best_q(probs, c, p, v)
    q_crit, ratio = critical_q(probs, c, p, v)

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关 · {level['name']}")
    print("=" * 62)
    print("  " + level["note"])
    show_dist(level, probs)

    score = 100
    while True:
        try:
            raw = input("\n  今天进多少份？> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：临界比 = (p−c)/(p−v) = ({p}−{c})/({p}−{v}) = {ratio:.3f}；"
                  f"去找「需求不超过多少份」的累积概率刚好达到 {ratio:.3f} 的那个点。"
                  f"（本题上限 {score} 分）")
            continue
        if low.startswith("calc"):
            parts = raw.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("  用法：calc 25（查进 25 份的期望利润）")
                continue
            q = int(parts[1])
            print(f"  进 {q} 份的期望利润 ≈ {eprofit(q, probs, c, p, v):.2f} 元/天")
            continue

        if not raw.lstrip("-").isdigit():
            print("  请输入一个整数（份数）。")
            continue
        q = int(raw)
        maxd = max(d for d, _ in probs)
        if q < 0 or q > maxd:
            print(f"  份数请取 0 到 {maxd} 之间。")
            continue

        val = eprofit(q, probs, c, p, v)
        print(f"\n  进 {q} 份 → 期望利润 {val:.2f} 元/天")
        avg, sold, waste, miss = simulate(q, probs, c, p, v)
        print(f"  60 天模拟（固定随机种子）：日均利润 {avg:.2f} 元，"
              f"日均卖出 {sold:.1f} 份，剩报 {waste:.1f} 份，缺货 {miss:.1f} 份")

        if abs(val - best_val) < 1e-9:          # 期望利润持平即最优（允许并列解）
            tie = "" if q == q_star else f"（与 {q_star} 份同为最优解）"
            print(f"  ✅ 达到最优期望利润 {best_val:.2f} 元/天{tie}，本关 100 分。")
            print(f"  核对：临界比法算出的最优 q 是 {q_crit}（临界比 {ratio:.2f}）。")
            return 100, True

        got = max(20, int(score * val / best_val)) if best_val > 0 else 20
        diff = val - best_val
        print(f"  ⚠ 与最优（{q_star} 份，{best_val:.2f} 元/天）相差 {diff:+.2f} 元/天，本次 {got} 分。")
        if q > q_star:
            print("  提示：进多了。多进一份的期望损失 = (c−v)×P(卖不掉)，"
                  "已经超过毛利 (p−c)×P(卖得掉)。")
        else:
            print("  提示：进少了。少进一份就少赚一次 (p−c)，"
                  "而多进一份最多只亏 (c−v)。")
        score = min(score, got)


def play():
    print("=" * 62)
    print("      📰 报刊亭进货决策 · 报童问题")
    print("=" * 62)
    print("每天开门前决定进货量：进多了剩一堆，进少了流失生意。")

    # 开局自检：期望利润的枚举最优 必须与临界分位数法一致
    for i, lv in enumerate(LEVELS, 1):
        probs = PROBS[lv["name"]]
        c, p, v = lv["c"], lv["p"], lv["v"]
        assert abs(sum(pr for _, pr in probs) - 1.0) < 1e-9, f"第 {i} 关概率和不为 1"
        q_star, best_val = best_q(probs, c, p, v)
        q_crit, ratio = critical_q(probs, c, p, v)
        assert q_star == q_crit, f"第 {i} 关枚举最优 {q_star} ≠ 临界比法 {q_crit}"
        assert 0 <= ratio <= 1, f"第 {i} 关临界比越界"
        # 最优点的期望利润必须不低于任何其他点
        for q in range(0, max(d for d, _ in probs) + 1):
            assert eprofit(q, probs, c, p, v) <= best_val + 1e-9

    total = done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 250:
        print("  🏆 你已经掌握了临界比：按「卖得掉 / 卖不掉」的损失比例定进货量。")
    elif total >= 100:
        print("  👍 记住：临界比 = (p−c)/(p−v)，去找累积概率刚达到它的那个需求点。")
    else:
        print("  🙂 诀窍：先算临界比，再查需求的累积概率，越过临界比的那一步就是最优 q。")
    print("=" * 62)


if __name__ == "__main__":
    play()
