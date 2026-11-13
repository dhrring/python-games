# -*- coding: utf-8 -*-
"""
排序算法擂台（3 位选手 · 3 局不同数据 · 押注式观赛）
====================================================
擂台上有三个选手，同一时刻从同一个数组出发，各自排序：
    1 号 冒泡排序      2 号 选择排序      3 号 插入排序
它们一步一步往前走，屏幕上实时显示谁比较了多少次、交换了多少次。

每局你要押注：这一局谁的「比较次数」最少？
（注意：判定指标每局不同，屏幕上会写清楚是比「比较次数」还是「交换次数」。）

三局的数据分布各不相同：
    第一局：完全随机的数组
    第二局：几乎已经排好序（只有几个元素错位）
    第三局：完全逆序（最坏情况）
押对 +100 分，押错 −20 分，满分 300。

这个游戏真正想告诉你的：没有「最好的排序算法」，只有「最适合当前数据的排序算法」。
运行：python3 2026-11-13_排序算法擂台.py
"""

import random


def bubble_steps(a0):
    a = list(a0)
    n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            yield "cmp"
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                yield "swap"
        if not swapped:
            break
    return a


def selection_steps(a0):
    a = list(a0)
    n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            yield "cmp"
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            yield "swap"
    return a


def insertion_steps(a0):
    a = list(a0)
    n = len(a)
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0:
            yield "cmp"
            if a[j] > key:
                a[j + 1] = a[j]
                j -= 1
                yield "swap"
            else:
                break
        a[j + 1] = key
    return a


ALGOS = [
    ("冒泡排序", bubble_steps),
    ("选择排序", selection_steps),
    ("插入排序", insertion_steps),
]

def make_random():
    return [random.randint(1, 99) for _ in range(10)]


def make_almost_sorted():
    a = sorted(random.sample(range(1, 99), 10))
    for _ in range(2):
        i = random.randint(0, len(a) - 2)
        a[i], a[i + 1] = a[i + 1], a[i]
    if a == sorted(a):
        a[-2], a[-1] = a[-1], a[-2]
    return a


def make_reversed():
    a = random.sample(range(1, 99), 10)
    a.sort(reverse=True)
    return a


ROUNDS = [
    {"name": "第一局 · 随机数组", "make": make_random, "metric": "cmp",
     "question": "押「谁的比较次数最少」",
     "note": "随机数据下插入排序最省比较（平均约 n²/4），冒泡最吃亏。"},
    {"name": "第二局 · 近乎有序", "make": make_almost_sorted, "metric": "cmp",
     "question": "押「谁的比较次数最少」",
     "note": "几乎有序时插入排序近乎线性（约 n−1 次比较），差距被拉到极致。"},
    {"name": "第三局 · 完全逆序", "make": make_reversed, "metric": "swap",
     "question": "押「谁的交换次数最少」",
     "note": "逆序时三者比较次数都是 n(n−1)/2，只能看交换次数——选择排序每轮只换一次，共 n−1 次。"},
]


def bar(cnt, total, width=14):
    filled = int(width * cnt / max(1, total))
    return "█" * filled + "·" * (width - filled)


def run_round(arr, bet, metric="cmp"):
    print("\n" + "=" * 62)
    print(f"  起跑数组：{arr}")
    print("=" * 62)
    steps = [g(arr) for _, g in ALGOS]
    cmp_cnt = [0, 0, 0]
    swap_cnt = [0, 0, 0]
    done = [False, False, False]
    final = [None, None, None]
    events = 0

    while not all(done):
        for k in range(3):
            if done[k]:
                continue
            try:
                ev = next(steps[k])
                if ev == "cmp":
                    cmp_cnt[k] += 1
                else:
                    swap_cnt[k] += 1
                events += 1
            except StopIteration as e:
                done[k] = True
                final[k] = e.value
        if events and events % 10 == 0:
            print(f"  进度（第 {events} 步）" + "  ".join(
                f"{ALGOS[k][0]} {bar(cmp_cnt[k], 50)} {cmp_cnt[k]}次"
                for k in range(3)))

    print("\n" + "-" * 62)
    print("  赛果")
    print(f"  {'选手':<8}{'比较次数':>8}{'交换次数':>10}")
    for k, (name, _) in enumerate(ALGOS):
        print(f"  {name:<8}{cmp_cnt[k]:>8}{swap_cnt[k]:>10}")

    assert all(f == sorted(arr) for f in final), f"排序结果错误: {final}"
    metric_name = "比较次数" if metric == "cmp" else "交换次数"
    counts = cmp_cnt if metric == "cmp" else swap_cnt
    best = min(counts)
    winners = [k for k in range(3) if counts[k] == best]
    print(f"\n  {metric_name}最少：{', '.join(ALGOS[k][0] for k in winners)}（{best} 次）")

    got = 0
    if bet is not None:
        if bet in winners:
            got = 100
        else:
            got = -20
    return got, winners, cmp_cnt


def main():
    print("=" * 62)
    print("      🏁 排序算法擂台")
    print("=" * 62)
    print("三个选手：1 号冒泡排序 / 2 号选择排序 / 3 号插入排序")
    print("每局押注一个指标的最少者，押对 +100，押错 −20。")

    total = 0
    for rd in ROUNDS:
        arr = rd["make"]()
        print("\n" + "=" * 62)
        print(f"  {rd['name']}")
        print("=" * 62)
        bet = None
        while True:
            try:
                raw = input(f"  {rd['question']} (1 冒泡 / 2 选择 / 3 插入 / s 不押)：").strip().lower()
            except EOFError:
                print("\n输入中断，提前结束。")
                print(f"  当前总分 {total}")
                return
            if raw in ("s", "skip"):
                print("  本局不押注，纯观赛。")
                break
            if raw in ("1", "2", "3"):
                bet = int(raw) - 1
                print(f"  你押了 {ALGOS[bet][0]}。")
                break
            print("  输入 1 / 2 / 3 / s。")

        got, winners, cmp_cnt = run_round(arr, bet, rd["metric"])
        if bet is not None:
            if got > 0:
                print(f"  🎯 押对！+{got} 分")
            else:
                print(f"  😑 押错，−{-got} 分（你押 {ALGOS[bet][0]}，赢家 {ALGOS[winners[0]][0]}）")
            total += got
        print(f"  小结：{rd['note']}")

    print("\n" + "=" * 62)
    print(f"  三局结束，总分 {total}/300")
    if total >= 200:
        print("  🏆 你已经是懂复杂度的观众了：数据分布决定赢家。")
    elif total >= 80:
        print("  👍 有感觉，但还容易被「随机数据」骗一次。")
    else:
        print("  🙂 复盘一句：比较次数看的是数据有序程度，交换次数看的是逆序对数量。")
    print("=" * 62)


if __name__ == "__main__":
    main()
