#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""管网最大流量（终端交互小游戏）

【背景】
一张供水管网：S 是水厂（源点），T 是小区（汇点），中间是加压站。
每根管道都标了「容量」——每秒最多能过多少单位的水。
水可以走任意路径，但中间每个加压站进多少、出多少必须相等（不能凭空造水）。
问：从 S 送到 T，每秒最多能送多少水？

【玩法】
共 5 关，每关 20 分，满分 100。看图后输入一个整数（最大流量）。
答错会告诉你「猜大了 / 猜小了」；答对后展示一条最小割（瓶颈）作为解释。
每关最多猜 3 次，答错一次扣 8 分（保底 0）。

【命令】
  hint / h / 提示 / ?  ：思路提示（每次用扣 10 分）
  q / quit / exit / 退出 ：退出
  直接回车            ：重画一遍管网
  Ctrl+C / Ctrl+D     ：安全退出

【运行】
  python3 2026-11-26_管网最大流量.py
  python3 2026-11-26_管网最大流量.py --check   # 自检（不进入游戏）
"""

import sys
from collections import deque

LEVELS = [
    {"nodes": ["S", "A", "B", "T"],
     "edges": [("S", "A", 3), ("S", "B", 2), ("A", "B", 2), ("A", "T", 2), ("B", "T", 2)]},
    {"nodes": ["S", "A", "B", "C", "T"],
     "edges": [("S", "A", 4), ("S", "B", 4), ("A", "B", 2), ("A", "C", 3),
               ("B", "C", 3), ("C", "T", 5), ("A", "T", 1)]},
    {"nodes": ["S", "A", "B", "C", "D", "T"],
     "edges": [("S", "A", 5), ("S", "B", 3), ("A", "C", 4), ("A", "D", 2),
               ("B", "C", 2), ("B", "D", 3), ("C", "T", 3), ("D", "T", 4)]},
    {"nodes": ["S", "A", "B", "C", "D", "T"],
     "edges": [("S", "A", 6), ("S", "C", 4), ("A", "B", 3), ("A", "D", 4),
               ("B", "C", 2), ("B", "T", 3), ("C", "D", 2), ("D", "T", 6)]},
    {"nodes": ["S", "A", "B", "C", "D", "T"],
     "edges": [("S", "A", 7), ("S", "B", 5), ("A", "B", 2), ("A", "C", 5),
               ("B", "D", 4), ("C", "D", 3), ("C", "T", 4), ("D", "T", 6)]},
]

MAX_TRY = 3
WRONG_PENALTY = 8
HINT_PENALTY = 10
POINTS = 20

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}


# ---------------- 图算法 ----------------

def caps_dict(edges):
    cap = {}
    for u, v, c in edges:
        cap[(u, v)] = cap.get((u, v), 0) + c
    return cap


def maxflow_ek(nodes, edges, s, t):
    """Edmonds–Karp：BFS 找最短增广路。返回 (最大流, 原始边上的流量字典)。"""
    cap = caps_dict(edges)
    adj = {v: set() for v in nodes}
    for u, v, _ in edges:
        adj[u].add(v)
        adj[v].add(u)
    flow = {(u, v): 0 for u, v, _ in edges}
    total = 0
    while True:
        parent = {s: None}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if v not in parent and cap.get((u, v), 0) > 0:
                    parent[v] = u
                    q.append(v)
        if t not in parent:
            break
        aug = None
        v = t
        while parent[v] is not None:
            u = parent[v]
            r = cap.get((u, v), 0)
            aug = r if aug is None else min(aug, r)
            v = u
        v = t
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= aug
            cap[(v, u)] = cap.get((v, u), 0) + aug
            if (u, v) in flow:
                flow[(u, v)] += aug
            elif (v, u) in flow:
                flow[(v, u)] -= aug
            v = u
        total += aug
    return total, flow


def maxflow_dfs(nodes, edges, s, t):
    """Ford–Fulkerson（DFS 找任意增广路）——独立实现，用于交叉验证。"""
    cap = caps_dict(edges)
    adj = {v: [] for v in nodes}
    for u, v, _ in edges:
        adj[u].append(v)
        adj[v].append(u)
    total = 0
    while True:
        parent = {s: None}
        stack = [s]
        while stack:
            u = stack.pop()
            if u == t:
                break
            for v in adj[u]:
                if v not in parent and cap.get((u, v), 0) > 0:
                    parent[v] = u
                    stack.append(v)
        if t not in parent:
            break
        aug = None
        v = t
        while parent[v] is not None:
            u = parent[v]
            r = cap.get((u, v), 0)
            aug = r if aug is None else min(aug, r)
            v = u
        v = t
        while parent[v] is not None:
            u = parent[v]
            cap[(u, v)] -= aug
            cap[(v, u)] = cap.get((v, u), 0) + aug
            v = u
        total += aug
    return total


def min_cut(nodes, edges, s):
    """在最大流残量网络上从 S 出发能到达的点集，割边容量之和 = 最大流。"""
    cap = caps_dict(edges)
    adj = {v: set() for v in nodes}
    for u, v, _ in edges:
        adj[u].add(v)
        adj[v].add(u)
    fl, flow_map = maxflow_ek(nodes, edges, s, "T")
    residual = dict(cap)
    for (u, v), f in flow_map.items():
        residual[(u, v)] = cap[(u, v)] - f          # 正向剩多少还能走
        residual[(v, u)] = residual.get((v, u), 0) + f  # 反向退流也算冗余容量
    reach = {s}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in adj[u]:
            if v not in reach and residual.get((u, v), 0) > 0:
                reach.add(v)
                q.append(v)
    cut = [(u, v, c) for u, v, c in edges if u in reach and v not in reach]
    return fl, reach, cut, sum(c for _, _, c in cut)


def layered_view(level):
    """按从 S 出发的最短有向距离分层，让图看起来更接近真实的水流走向。"""
    nodes, edges = level["nodes"], level["edges"]
    dist = {n: None for n in nodes}
    dist["S"] = 0
    q = deque(["S"])
    out = {n: [] for n in nodes}
    for u, v, _c in edges:
        out[u].append(v)
    while q:
        u = q.popleft()
        for v in out[u]:
            if dist[v] is None:
                dist[v] = dist[u] + 1
                q.append(v)
    unreachable = max([d for d in dist.values() if d is not None] + [0]) + 1
    for n in nodes:
        if dist[n] is None:
            dist[n] = unreachable
    layers = {}
    for n, k in dist.items():
        layers.setdefault(k, []).append(n)
    return [layers[k] for k in sorted(layers)]


# ---------------- 交互 ----------------

def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def show(level):
    print("  节点分层：")
    for i, ns in enumerate(layered_view(level)):
        print("    第{}层: {}".format(i, "  ".join(ns)))
    print("  管道（起点 → 终点  容量）：")
    srcs = {}
    for u, v, c in level["edges"]:
        srcs.setdefault(u, []).append("{}→{} {}".format(u, v, c))
    for u in sorted(srcs, key=lambda x: (x != "S", x)):
        print("    " + "   ".join(srcs[u]))


def ask_int(prompt, attempts, hint_text):
    tries = attempts
    while tries > 0:
        raw = ask("{}（余 {} 次）> ".format(prompt, tries))
        if raw is None:
            return "EOF", 0
        if raw in QUIT_WORDS:
            return "QUIT", 0
        if raw == "":
            print("  （重画管网）")
            return "EMPTY", tries
        if raw in HINT_WORDS:
            print(hint_text)
            return "HINT", tries
        try:
            return int(raw), tries - 1
        except ValueError:
            print("  ✗ 请输入一个整数。")
            tries -= 1
    return None, 0


def play():
    print("=" * 52)
    print("        管网最大流量 · 5 关满分 100")
    print("=" * 52)
    print("求从 S（水厂）到 T（小区）每秒最多能输送多少单位的水。")
    print("中间节点进出必须相等；每条管道不能超过标出的容量。")
    print("命令：hint 提示 ｜ q 退出 ｜ 回车 重画管网")
    print()

    total = 0
    for idx, lv in enumerate(LEVELS, 1):
        ans = maxflow_ek(lv["nodes"], lv["edges"], "S", "T")[0]
        attempts = MAX_TRY
        used_hint = False
        wrong = 0
        while True:
            print("—— 第 {} 关 ——".format(idx))
            show(lv)
            v, attempts = ask_int(
                "最大流量 = ?", attempts,
                "  提示：先随便找一条从 S 到 T 的路径，把这条路径上最小容量全部用上，\n"
                "        更新剩余容量后重复，直到再也找不到可有流量的路径；最后得到的总流量就是答案。\n"
                "        另一个看法：找一组「割」——把所有从 S 到 T 的路径都切断的管道，容量之和越小越接近答案。",
            )
            if v == "QUIT":
                print("\n已退出。")
                return
            if v == "EOF":
                print("输入已结束，游戏退出。")
                return
            if v == "HINT":
                if not used_hint:
                    used_hint = True
                    print("  （提示已用，本关 -10 分）")
                continue
            if v == "EMPTY":
                continue
            if v is None:
                print("  ✗ 次数用完，本关记 0 分。正确答案是 {}。".format(ans))
                break
            if v == ans:
                pts = max(0, POINTS - wrong * WRONG_PENALTY - (HINT_PENALTY if used_hint else 0))
                total += pts
                print("  ✓ 正确！最大流量 = {}（本关 +{} 分）".format(ans, pts))
                fl, reach, cut, cutcap = min_cut(lv["nodes"], lv["edges"], "S")
                print("  瓶颈（最小割）在：" + "、".join("{}→{} 容量{}".format(u, v, c) for u, v, c in cut))
                print("  这些管道割开后 S 再也到不了 T，容量和 {} = 最大流量，这就是「最小割=最大流」。".format(cutcap))
                break
            wrong += 1
            if v > ans:
                print("  ✗ 偏大了，管网里一定有某个瓶颈卡住了水量。")
            else:
                print("  ✗ 偏小了，还能再挤一点出来，试着多找几条并行的路径。")
            if attempts <= 0:
                print("  ✗ 次数用完，本关记 0 分。正确答案是 {}。".format(ans))
                break
        print("  当前总分：{}\n".format(total))

    print("=" * 52)
    print("最终得分：{} / 100".format(total))
    if total >= 90:
        print("评级：S —— 一眼看出瓶颈，最小割的直觉已经长出来了。")
    elif total >= 70:
        print("评级：A —— 会算，个别关卡差在「没注意到绕路的那根管子」。")
    elif total >= 50:
        print("评级：B —— 思路对了，但别用「S 出边容量之和」当答案。")
    else:
        print("评级：C —— 记住：答案 ≤ 任何一组割的容量和，找到最小的那组就赢了。")
    print("=" * 52)


def check():
    ok = True
    answers = []
    for idx, lv in enumerate(LEVELS, 1):
        nodes, edges = lv["nodes"], lv["edges"]
        ek = maxflow_ek(nodes, edges, "S", "T")[0]
        ff = maxflow_dfs(nodes, edges, "S", "T")
        fl, reach, cut, cutcap = min_cut(nodes, edges, "S")
        answers.append(ek)

        # 1) 两种最大流算法一致
        if ek != ff:
            ok = False
            print("✗ 第 {} 关 EK={} 与 DFS={} 不一致".format(idx, ek, ff))
        # 2) 最小割容量 = 最大流
        if cutcap != ek:
            ok = False
            print("✗ 第 {} 关 最小割 {} ≠ 最大流 {}".format(idx, cutcap, ek))
        # 3) 割边集合必须真的是割（断开后 S 到不了 T）
        cutset = {(u, v) for u, v, _c in cut}
        rest = [e for e in edges if (e[0], e[1]) not in cutset]
        if maxflow_dfs(nodes, rest, "S", "T") != 0:
            ok = False
            print("✗ 第 {} 关 割边去掉后仍能送水".format(idx))
        # 4) 流量可行性：容量不超、中间节点守恒、总量相符
        _val, flow_map = maxflow_ek(nodes, edges, "S", "T")
        bal = {n: 0 for n in nodes}
        for (u, v), f in flow_map.items():
            if f < 0 or f > caps_dict(edges)[(u, v)]:
                ok = False
                print("✗ 第 {} 关 {}→{} 流量 {} 越界".format(idx, u, v, f))
            bal[u] -= f
            bal[v] += f
        for n in nodes:
            if n not in ("S", "T") and bal[n] != 0:
                ok = False
                print("✗ 第 {} 关 节点 {} 不守恒：{}".format(idx, n, bal[n]))
        if bal["S"] != -ek or bal["T"] != ek:
            ok = False
            print("✗ 第 {} 关 源汇流量与最大值不符".format(idx))
        # 5) 非平凡：答案应小于 S 出边容量之和（除了最简单的第 1 关）
        sout = sum(c for u, _v, c in edges if u == "S")
        trivial = ek == sout
        if idx > 1 and trivial:
            ok = False
            print("✗ 第 {} 关 答案等于 S 出边容量和，题目太送分".format(idx))
        print("  第{}关：最大流 {}，最小割 {}，S出边总容量 {}，割边 {}".format(
            idx, ek, cutcap, sout, [u + "→" + v for u, v, _ in cut]))

    # 6) 关卡答案互不相同且递增（避免同质化）
    if len(set(answers)) != len(answers):
        ok = False
        print("✗ 关卡答案有重复：{}".format(answers))
    if answers != sorted(answers):
        ok = False
        print("✗ 关卡答案未按难度递增：{}".format(answers))

    # 7) 分层视图每关都覆盖全部节点
    for idx, lv in enumerate(LEVELS, 1):
        got = [n for layer in layered_view(lv) for n in layer]
        if set(got) != set(lv["nodes"]) or len(set(got)) != len(got):
            ok = False
            print("✗ 第 {} 关分层视图节点缺失/重复：{}".format(idx, got))

    # 8) 满分
    if 5 * POINTS != 100:
        ok = False
        print("✗ 满分不是 100")

    print("自检通过 ✅" if ok else "自检失败 ❌")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--check", "-c", "check"):
        return check()
    try:
        play()
    except (BrokenPipeError, KeyboardInterrupt):
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
