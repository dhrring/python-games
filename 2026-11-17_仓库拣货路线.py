# -*- coding: utf-8 -*-
"""
仓库拣货路线 · 旅行商问题
====================================================
你是仓库拣货员。从起点 S 出发，要把货架上每一件货都取一遍，
最后回到打包台（也就是回到 S）。在货架间只能横竖走（曼哈顿距离），
所以要解决的问题是：按什么顺序取，总路程最短？

为什么不「看着最近的先取」？
  每一步都选最近的货位（贪心），容易在最后被迫绕远路；
  最优顺序要整体算，这类问题就叫旅行商问题（TSP）。

地图：Y 行是纵坐标，X 列是横坐标。S 为起点/打包台，1、2、3… 是货位。
      两点之间的距离 = |x1-x2| + |y1-y2|

玩法：每关输入取货顺序（货位编号，空格分隔），程序算总路程，
      和最优方案比较。路程 = 最优 → 100 分；否则按比例折分。

命令：
  map    再看一次地图与坐标
  hint   本题提示（−30 分，给出最优的第一步）
  q      退出

运行：python3 2026-11-17_仓库拣货路线.py
"""

LEVELS = [
    {
        "size": (10, 6),
        "start": (0, 0),
        "spots": {1: (2, 1), 2: (5, 5), 3: (8, 2)},
        "note": "三件货，先跑一趟熟悉一下。",
        "hint": "只有三件，三个顺序都试一遍就是最优解了。",
    },
    {
        "size": (10, 6),
        "start": (0, 0),
        "spots": {1: (1, 5), 2: (4, 1), 3: (6, 4), 4: (9, 0), 5: (3, 3)},
        "note": "五件货：注意别把远处的和近处的混着跑，容易来回折返。",
        "hint": "最优解通常是一条「绕一圈、不交叉」的路线，而不是每次挑最近的。",
    },
    {
        "size": (12, 8),
        "start": (0, 0),
        "spots": {1: (1, 7), 2: (4, 2), 3: (7, 6), 4: (10, 1),
                  5: (3, 5), 6: (9, 7), 7: (11, 4)},
        "note": "七件货，分布很散：这一关贪心一定不够用。",
        "hint": "先想清楚「最后从哪件货回起点最近」，从终点倒推往往更容易。",
    },
]


def dist(p, q):
    return abs(p[0] - q[0]) + abs(p[1] - q[1])


def route_cost(order, level):
    pts = [level["start"]] + [level["spots"][i] for i in order] + [level["start"]]
    return sum(dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def best_route(level):
    """位掩码 DP 求最短闭环路线（起点与终点都是 S）。"""
    ids = sorted(level["spots"])
    n = len(ids)
    coord = {i: level["spots"][i] for i in ids}
    start = level["start"]
    INF = float("inf")
    # dp[mask][j] = 从 S 出发、已取完 mask 这些货、最后停在 ids[j] 的最短路程
    dp = [[INF] * n for _ in range(1 << n)]
    prev = [[-1] * n for _ in range(1 << n)]
    for j in range(n):
        dp[1 << j][j] = dist(start, coord[ids[j]])

    for mask in range(1 << n):
        for j in range(n):
            cur = dp[mask][j]
            if cur == INF:
                continue
            for k in range(n):
                if mask >> k & 1:
                    continue
                nxt = mask | (1 << k)
                val = cur + dist(coord[ids[j]], coord[ids[k]])
                if val < dp[nxt][k]:
                    dp[nxt][k] = val
                    prev[nxt][k] = j

    full = (1 << n) - 1
    best = INF
    best_last = -1
    for j in range(n):
        val = dp[full][j] + dist(coord[ids[j]], start)
        if val < best:
            best = val
            best_last = j

    order = []
    mask, j = full, best_last
    while j != -1:
        order.append(ids[j])
        pj = prev[mask][j]
        mask ^= 1 << j
        j = pj
    order.reverse()
    return best, order


def brute_force(level):
    import itertools
    ids = sorted(level["spots"])
    best = (float("inf"), [])
    for perm in itertools.permutations(ids):
        c = route_cost(list(perm), level)
        if c < best[0]:
            best = (c, list(perm))
    return best


def show_map(level):
    w, h = level["size"]
    grid = [["·" for _ in range(w)] for _ in range(h)]
    for i, (x, y) in level["spots"].items():
        grid[y][x] = str(i) if i < 10 else "*"
    sx, sy = level["start"]
    grid[sy][sx] = "S"
    print(f"\n  地图（宽 {w}、高 {h}，纵轴 y 从下往上算）：")
    for y in range(h - 1, -1, -1):
        print(f"    y={y:<2} " + " ".join(grid[y]))
    print("          " + " ".join(str(x) for x in range(w)))
    print(f"  起点 S = {level['start']}")
    for i, (x, y) in level["spots"].items():
        print(f"    货位 {i}: ({x}, {y})　距 S 直线步数 {dist((x, y), level['start'])}")


def greedy_route(level):
    ids = list(level["spots"])
    cur = level["start"]
    order = []
    left = ids[:]
    while left:
        nxt = min(left, key=lambda i: dist(cur, level["spots"][i]))
        order.append(nxt)
        left.remove(nxt)
        cur = level["spots"][nxt]
    return route_cost(order, level), order


def run_level(idx, level):
    best_cost, best_order = best_route(level)
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + level["note"])
    show_map(level)
    print(f"  （要从 S 出发走遍 {len(level['spots'])} 个货位，最后回到 S。）")

    score = 100
    while True:
        try:
            raw = input("\n  取货顺序（如 3 1 4 2）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "map":
            show_map(level)
            continue
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：{level['hint']}")
            print(f"  另外，最优的第一步是从 {best_order[0]} 号货位开始。（本题上限 {score} 分）")
            continue

        tokens = raw.replace(",", " ").replace("->", " ").split()
        if any(not t.isdigit() for t in tokens):
            print("  只输入货位编号，用空格分开。")
            continue
        order = [int(t) for t in tokens]
        ids = set(level["spots"])
        if set(order) != ids or len(order) != len(ids):
            print(f"  要把 {len(ids)} 个货位各取一次（不能漏、不能重复）：{sorted(ids)}")
            continue

        cost = route_cost(order, level)
        if cost == best_cost:
            print(f"  ✅ 最优路线！总路程 {cost} 步。")
            print(f"  参考解：{' → '.join(map(str, best_order))}（{best_cost} 步）")
            return score, True

        ratio = best_cost / cost
        got = max(20, int(score * ratio))
        print(f"  ⚠ 总路程 {cost} 步，最优是 {best_cost} 步（多走了 {cost - best_cost} 步）。")
        g_cost, g_order = greedy_route(level)
        if g_cost > best_cost:
            print(f"  （顺便一提：每次挑最近的货位，只能做到 {g_cost} 步，所以贪心在这关不够用。）")
        print(f"  本次 {got} 分。改个顺序再试（本题上限 {got} 分）。")
        score = min(score, got)


def play():
    print("=" * 62)
    print("      🛒 仓库拣货路线 · 旅行商问题")
    print("=" * 62)
    print("从 S 出发取完所有货再回到 S，路线越短越好。")

    # 开局自检：DP 最优必须与穷举一致（货位少时穷举可算）
    for i, lv in enumerate(LEVELS, 1):
        b_cost, b_order = best_route(lv)
        f_cost, _ = brute_force(lv)
        assert b_cost == f_cost, f"第 {i} 关 DP({b_cost}) 与穷举({f_cost}) 不一致"
        assert set(b_order) == set(lv["spots"]), f"第 {i} 关最优解没覆盖全部货位"

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
        print("  🏆 你已经在按「整条闭环」想问题，而不是一步一回头了。")
    elif total >= 100:
        print("  👍 有进步：先把远端货位连成一条线，最后顺路回起点。")
    else:
        print("  🙂 诀窍：画一条不交叉的回路，比每次挑最近的货位更省路。")
    print("=" * 62)


if __name__ == "__main__":
    play()
