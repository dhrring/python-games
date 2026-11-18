# -*- coding: utf-8 -*-
"""
幻方填充 · Magic Square
====================================================
幻方：把 1 到 n² 的数字填进 n×n 的方格，使**每一行、每一列、
以及两条对角线**的数字之和都相等。这个和叫「幻和」。

  3 阶幻和 = 15　　4 阶幻和 = 34　　5 阶幻和 = 65
  （规律：幻和 = n × (n² + 1) / 2）

本游戏每关给出一个被挖掉几个数的幻方，空格标成 ① ② ③ …
你要把「缺少的那几个数」按编号顺序填回去，让所有行、列、对角线都成立。

命令：
  ① ② ③ 的值用空格依次输入，例如：  8 1 6
  missing   看还缺哪些数
  hint      提示第一个空格（−30 分）
  q         退出

运行：python3 2026-11-18_幻方填充.py
"""


def lo_shu():
    """3 阶幻方（洛书）：最经典的一个。"""
    return [[8, 1, 6],
            [3, 5, 7],
            [4, 9, 2]]


def durer():
    """4 阶幻方（丢勒 1514 年刻在《忧郁 I》上的那个）。"""
    return [[16, 3, 2, 13],
            [5, 10, 11, 8],
            [9, 6, 7, 12],
            [4, 15, 14, 1]]


def siamese(n):
    """奇数阶幻方的 Siamese（连续摆数）构造法。"""
    g = [[0] * n for _ in range(n)]
    i, j = 0, n // 2
    for k in range(1, n * n + 1):
        g[i][j] = k
        ni, nj = (i - 1) % n, (j + 1) % n      # 右上方
        if g[ni][nj]:                          # 被占了就从当前格往下落一格
            ni, nj = (i + 1) % n, j
        i, j = ni, nj
    return g


LEVELS = [
    {"name": "3 阶洛书", "grid": lo_shu(), "blanks": [(0, 1), (1, 0), (2, 2)],
     "note": "最古老的幻方，幻和 15。三个空正好练手。"},
    {"name": "4 阶丢勒幻方", "grid": durer(), "blanks": [(0, 0), (1, 2), (2, 1), (3, 3)],
     "note": "丢勒版画里那个幻方，幻和 34。四阶的信息更多，耐心推。"},
    {"name": "5 阶幻方", "grid": siamese(5), "blanks": [(0, 2), (1, 4), (2, 0), (3, 3), (4, 1)],
     "note": "奇数阶幻方有构造公式，但这里请你像解题一样推出来，幻和 65。"},
]

MARKS = "①②③④⑤⑥⑦⑧⑨"


def magic_sum(grid):
    n = len(grid)
    return n * (n * n + 1) // 2


def check(grid):
    """返回 (是否合法, 问题列表)。"""
    n = len(grid)
    target = magic_sum(grid)
    problems = []
    for r in range(n):
        s = sum(grid[r])
        if s != target:
            problems.append(f"第 {r + 1} 行之和是 {s}，应为 {target}")
    for c in range(n):
        s = sum(grid[r][c] for r in range(n))
        if s != target:
            problems.append(f"第 {c + 1} 列之和是 {s}，应为 {target}")
    d1 = sum(grid[i][i] for i in range(n))
    d2 = sum(grid[i][n - 1 - i] for i in range(n))
    if d1 != target:
        problems.append(f"主对角线之和是 {d1}，应为 {target}")
    if d2 != target:
        problems.append(f"副对角线之和是 {d2}，应为 {target}")
    vals = [v for row in grid for v in row]
    if sorted(vals) != list(range(1, n * n + 1)):
        problems.append("数字必须刚好是 1 到 n² 各出现一次")
    return (not problems), problems


def render(grid, blanks):
    n = len(grid)
    width = len(str(n * n)) + 1
    idx = {}
    for i, pos in enumerate(blanks, 1):
        idx[pos] = i
    print("    行\\列  " + " ".join(f"{c + 1:>{width}}" for c in range(n)))
    for r in range(n):
        cells = []
        for c in range(n):
            if (r, c) in idx:
                cells.append(f"{MARKS[idx[(r, c)] - 1]:>{width}}")
            else:
                cells.append(f"{grid[r][c]:>{width}}")
        print(f"      {r + 1:>2}  " + " ".join(cells))
    print(f"\n    幻和 = {magic_sum(grid)}（每行 / 每列 / 两条对角线都要等于它）")


def run_level(idx, level):
    grid = [row[:] for row in level["grid"]]
    blanks = level["blanks"]
    missing = [grid[r][c] for r, c in blanks]
    for r, c in blanks:
        grid[r][c] = 0

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关 · {level['name']}")
    print("=" * 62)
    print("  " + level["note"])
    render(grid, blanks)
    print(f"  缺少的 {len(blanks)} 个数：{sorted(missing)}（顺序打乱过，需你自己判断）")

    score = 100
    while True:
        try:
            raw = input(f"\n  依次填入 {' '.join(MARKS[i] for i in range(len(blanks)))} 的值 > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "missing":
            print(f"  还缺这些数：{sorted(missing)}")
            continue
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：{MARKS[0]} 的值是 {missing[0]}。（本题上限 {score} 分）")
            continue

        parts = raw.replace(",", " ").split()
        if len(parts) != len(blanks) or any(not p.lstrip("-").isdigit() for p in parts):
            print(f"  要输入 {len(blanks)} 个整数，用空格分开。")
            continue
        vals = [int(p) for p in parts]

        for (r, c), v in zip(blanks, vals):
            grid[r][c] = v
        ok, problems = check(grid)
        if ok:
            print("  ✅ 全对！所有行、列、对角线都等于幻和。本关 100 分。")
            for i, (r, c) in enumerate(blanks):
                grid[r][c] = missing[i]
            render(grid, blanks)
            return 100, True

        print("  ❌ 还不对：")
        for p in problems[:4]:
            print("    · " + p)
        score = max(40, score - 20)
        print(f"  再想想（本题当前上限 {score} 分）。")
        for r, c in blanks:
            grid[r][c] = 0


def play():
    print("=" * 62)
    print("      🔢 幻方填充 · Magic Square")
    print("=" * 62)
    print("把缺的数填回去，让每行、每列、两条对角线的和都相等。")

    # 开局自检：原始幻方必须合法；幻和公式必须与实测一致
    for i, lv in enumerate(LEVELS, 1):
        g = lv["grid"]
        ok, problems = check(g)
        assert ok, f"第 {i} 关的原始幻方不合法：{problems}"
        n = len(g)
        assert magic_sum(g) == sum(g[0]), f"第 {i} 关幻和公式与实际不符"
        assert all(g[r][c] in range(1, n * n + 1) for r in range(n) for c in range(n))

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
        print("  🏆 你已经会用「幻和」反推出每个空格了。")
    elif total >= 100:
        print("  👍 诀窍：一行里只缺一个数，用幻和减去其余数就够了。")
    else:
        print("  🙂 先从「只缺一个空」的那一行/列下手，其余自然浮出来。")
    print("=" * 62)


if __name__ == "__main__":
    play()
