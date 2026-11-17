# -*- coding: utf-8 -*-
"""
一笔画谜题 · 欧拉路径
====================================================
要求：笔不离纸，一次走完全部连线，每条线只走一次。
（这就是数学里的「欧拉迹」问题，起源于柯尼斯堡七桥问题。）

判断能不能一笔画的三个条件：
  1. 图必须是「连通」的（所有线连成一片）
  2. 奇数度（连着奇数条线）的顶点数只能是 0 个或 2 个
       · 0 个 → 一定可以，而且能回到起点（欧拉回路）
       · 2 个 → 一定可以，但必须从其中一个奇点出发，停在另一个奇点
       · 4 个及以上 → 一笔画不出来
  3. 线不能被重复使用

玩法：每关给你一张图（顶点字母 + 连线 + 每个点的度数），
      你输入经过的顶点序列，用空格或箭头分隔，例如：
          A B C D A
      程序会检查这条路径是否真的走完了所有线且没走重。

命令：
  deg    再看一次每个顶点的度数（判断奇点的关键）
  hint   本题提示（−30 分）
  q      退出

运行：python3 2026-11-17_一笔画谜题.py
"""

LEVELS = [
    {
        "name": "五边形",
        "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")],
        "note": "最简单的闭环：每个点都连着 2 条线。",
        "hint": "全是偶点（0 个奇点），所以随便从哪个点出发都能绕回原处。",
    },
    {
        "name": "小房子",
        "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"),
                  ("A", "E"), ("B", "E")],
        "note": "正方形加一个屋顶。屋顶的两个尖角是关键。",
        "hint": "C 和 D 各连 2 条，A 和 B 各连 3 条（奇点），E 连 2 条。要从 A 或 B 出发。",
    },
    {
        "name": "蝴蝶结",
        "edges": [("A", "B"), ("B", "C"), ("C", "A"),
                  ("A", "D"), ("D", "B")],
        "note": "两个三角形共用一条边 AB，像蝴蝶结。",
        "hint": "共享边 AB 让 A、B 各有 3 条线（奇点），C、D 各有 2 条。从 A 出发，最后落到 B。",
    },
    {
        "name": "方框加一条对角线",
        "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A", "C")],
        "note": "正方形里加了一条从 A 到 C 的斜线。",
        "hint": "B、D 是偶点（2 条），A、C 是奇点（3 条）。从 A 或 C 起步，另一端结束。",
    },
    {
        "name": "方环带尾巴",
        "edges": [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("C", "E")],
        "note": "一个方环，再从 C 伸出一条线到 E（终点挂了个小尾巴）。",
        "hint": "E 只连 1 条线，是最明显的奇点；另一个奇点是 C（连 3 条）。必须从 E 或 C 出发。",
    },
]


def build(level):
    """整理出邻接表与度数。"""
    adj = {}
    for a, b in level["edges"]:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    deg = {n: len(v) for n, v in adj.items()}
    return adj, deg


def is_connected(adj):
    if not adj:
        return True
    start = next(iter(adj))
    seen = {start}
    stack = [start]
    while stack:
        cur = stack.pop()
        for nb in adj[cur]:
            if nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(adj)


def odd_nodes(deg):
    return [n for n, d in deg.items() if d % 2 == 1]


def euler_trail(nodes, edges):
    """Hierholzer 算法求一条欧拉迹；不存在则返回 None。"""
    adj = {}
    for i, (a, b) in enumerate(edges):
        adj.setdefault(a, []).append((b, i))
        adj.setdefault(b, []).append((a, i))
    deg = {n: len(v) for n, v in adj.items()}
    odd = [n for n, d in deg.items() if d % 2]
    if len(odd) not in (0, 2):
        return None
    plain = {}
    for a, b in edges:                 # 连通性只看顶点关系，不看边编号
        plain.setdefault(a, []).append(b)
        plain.setdefault(b, []).append(a)
    if not is_connected(plain):
        return None

    start = odd[0] if odd else nodes[0]
    used_edge = [False] * len(edges)
    stack = [(start, iter(adj[start]))]
    trail = []
    while stack:
        node, it = stack[-1]
        advanced = False
        for nb, eid in it:
            if not used_edge[eid]:
                used_edge[eid] = True
                stack.append((nb, iter(adj[nb])))
                advanced = True
                break
        if not advanced:
            trail.append(stack.pop()[0])
    trail.reverse()
    return trail if trail[0] == start else [start] + trail


def parse_path(raw, nodes):
    """把 A B C 或 A->B->C 或 a,b,c 都解析成顶点序列。"""
    s = raw.replace("->", " ").replace("→", " ").replace(",", " ")
    tokens = [t.strip().upper() for t in s.split() if t.strip()]
    bad = [t for t in tokens if t not in nodes]
    if bad:
        raise ValueError("这些顶点不存在：%s（本图顶点有：%s）" % ("、".join(bad), "、".join(nodes)))
    return tokens


def check_path(path, edges):
    """返回 (是否合法, 说明)。"""
    if len(path) < 2:
        return False, "至少要走一条线。"
    pairs = [(path[i].upper(), path[i + 1].upper()) for i in range(len(path) - 1)]
    remaining = sorted(tuple(sorted(e)) for e in edges)
    for p in pairs:
        key = tuple(sorted(p))
        if key in remaining:
            remaining.remove(key)
        else:
            return False, f"{p[0]}—{p[1]} 这条线不存在，或者已经走过一次了。"
    if remaining:
        return False, "还有 %d 条线没走到：%s" % (
            len(remaining), "、".join(f"{a}-{b}" for a, b in remaining))
    return True, "全部连线都恰好走过一次。"


def show(level):
    adj, deg = build(level)
    odd = odd_nodes(deg)
    print(f"\n  图名：{level['name']}")
    print("  " + level["note"])
    print("\n  连线：")
    for a, b in level["edges"]:
        print(f"    {a} — {b}")
    print("\n  邻接与度数：")
    for n in sorted(adj):
        mark = "  ← 奇点" if n in odd else ""
        print(f"    {n} 连 {deg[n]} 条：{'、'.join(sorted(adj[n]))}{mark}")
    print(f"  共 {len(level['edges'])} 条线，{len(adj)} 个顶点，奇点 {len(odd)} 个"
          + ("（有解）" if len(odd) in (0, 2) and is_connected(adj) else "（无解）"))


def run_level(idx, level):
    adj, deg = build(level)
    nodes = sorted(adj)
    sol = euler_trail(nodes, level["edges"])
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    show(level)

    score = 100
    while True:
        try:
            raw = input("\n  一笔画的顶点序列 > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "deg":
            show(level)
            continue
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：{level['hint']}（本题上限 {score} 分）")
            continue

        try:
            path = parse_path(raw, nodes)
        except ValueError as e:
            print(f"  {e}")
            continue
        ok, msg = check_path(path, level["edges"])
        if ok:
            print(f"  ✅ {msg}")
            if path[0] == path[-1]:
                print("  （起点即终点：这是一条欧拉回路）")
            print(f"  本关 {score} 分。参考解之一：{' → '.join(sol)}")
            return score, True

        print(f"  ❌ {msg}")
        score = max(40, score - 20)
        print(f"  再试一次（本题当前上限 {score} 分）。忘了就输入 deg 看度数。")


def play():
    print("=" * 62)
    print("      ✏️ 一笔画谜题 · 欧拉路径")
    print("=" * 62)
    print("笔不离纸走完全部连线，每条线只走一次。输入顶点序列提交。")

    # 开局自检：每关必须存在欧拉迹，且度数条件成立
    for i, lv in enumerate(LEVELS, 1):
        adj, deg = build(lv)
        odd = odd_nodes(deg)
        assert is_connected(adj), f"第 {i} 关不连通"
        assert len(odd) in (0, 2), f"第 {i} 关奇点 {len(odd)} 个，不可一笔画"
        trail = euler_trail(sorted(adj), lv["edges"])
        assert trail is not None, f"第 {i} 关求解失败"
        ok, msg = check_path(trail, lv["edges"])
        assert ok, f"第 {i} 关求解结果不合法：{msg}"

    total = done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 450:
        print("  🏆 你已经能靠度数直接判断一笔画了。")
    elif total >= 200:
        print("  👍 记住口诀：奇点 0 个或 2 个才能一笔画，2 个时必从奇点起笔。")
    else:
        print("  🙂 诀窍：先数每个点连几条线，奇点数超过 2 就直接无解；有解就从奇点出发。")
    print("=" * 62)


if __name__ == "__main__":
    play()
