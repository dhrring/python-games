# -*- coding: utf-8 -*-
"""
位运算迷宫 · BitSmith
====================================================
你手里有一个 8 位的字节（byte），它就像一排 8 个开关，只能取 0 或 1。
每一关给你：
  · 一个起始字节（起点）
  · 一组允许使用的操作（每个操作都有编号）
  · 一个目标字节（终点）
你要给出一个操作序列，让起始字节一步步变成目标字节。

可用的操作类型（每关只开放其中几种，并带固定参数）：
  and 掩码   → 与运算，相当于「只保留掩码里为 1 的那几位」
  or  掩码   → 或运算，相当于「把掩码里为 1 的位都点亮」
  xor 掩码   → 异或运算，相当于「掩码里为 1 的位取反」
  shl k      → 整体左移 k 位（超出 8 位的部分丢掉，低位补 0）
  shr k      → 整体右移 k 位（高位补 0）
  not        → 全部 8 位取反

游戏内命令：
  ops     再看一次本关可用操作
  bits    用开关图示查看当前字节（进位之后的临时状态）
  reset   回到起点
  q       退出

计分：每关满分 100。正好用最短步数完成 = 100；
每多走一步扣 15 分（最少 20 分）。先走错一次再继续，本关最高 70 分。
运行：python3 2026-11-15_位运算迷宫.py
"""

from collections import deque
import random

MASK8 = 0xFF

TYPE_NAMES = {
    "and": "与（AND）",
    "or": "或（OR）",
    "xor": "异或（XOR）",
    "shl": "左移",
    "shr": "右移",
    "not": "取反",
}


def apply(op, x):
    kind, arg = op
    if kind == "and":
        return x & arg & MASK8
    if kind == "or":
        return (x | arg) & MASK8
    if kind == "xor":
        return (x ^ arg) & MASK8
    if kind == "shl":
        return (x << arg) & MASK8
    if kind == "shr":
        return x >> arg
    if kind == "not":
        return (~x) & MASK8
    raise ValueError(kind)


def op_text(op, idx=None):
    kind, arg = op
    prefix = f"[{idx}] " if idx is not None else ""
    if kind in ("and", "or", "xor"):
        return f"{prefix}{kind.upper()} {fmt_bin(arg)}（0x{arg:02X}）"
    if kind in ("shl", "shr"):
        return f"{prefix}{kind.upper()} {arg}"
    return f"{prefix}NOT"


def fmt_bin(x):
    return format(x, "08b")


def show_bits(x):
    """把字节画成一排开关。"""
    chars = "".join("█" if ch == "1" else "·" for ch in fmt_bin(x))
    return f"{fmt_bin(x)}  |{chars}|  = {x}"


def bfs(start, ops):
    """从起点出发，求出到每个字节的最短步数与路径。"""
    dist = {start: 0}
    path = {start: ()}
    q = deque([start])
    while q:
        cur = q.popleft()
        for i, op in enumerate(ops):
            nxt = apply(op, cur)
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                path[nxt] = path[cur] + (i,)
                q.append(nxt)
    return dist, path


# 每关：起点、可用操作、目标距离（目标由 BFS 在指定距离上确定，保证可解）
LEVELS = [
    (0b1010_0001, [("and", 0b1111_0000), ("or", 0b0000_0011), ("shr", 1)], 3),
    (0b1100_0011, [("xor", 0b1111_0000), ("shl", 1), ("or", 0b0000_0001)], 4),
    (0b0000_1111, [("not", 0), ("and", 0b1010_1010), ("shr", 2), ("or", 0b1000_0000)], 5),
    (0b0110_1001, [("xor", 0b0101_0101), ("shl", 2), ("shr", 1), ("and", 0b1110_0111)], 6),
    (0b0011_1100, [("shl", 3), ("xor", 0b1000_0001), ("not", 0), ("and", 0b0111_1111), ("shr", 2)], 6),
]


def pick_goal(start, ops, want_dist, exclude=()):
    """在恰好 want_dist 步可达的字节里，取数值最大的一个作为目标（确定性、可复现）。
    exclude 用于避免不同关卡出现相同的目标值。"""
    dist, _ = bfs(start, ops)
    cands = [v for v, d in dist.items() if d == want_dist and v not in exclude]
    if not cands:
        raise RuntimeError(f"没有距离为 {want_dist} 的目标，请调整关卡参数")
    return max(cands)


def run_level(idx, level, goal):
    start, ops, _want = level
    dist, path = bfs(start, ops)
    optimal = dist[goal]

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print(f"  起点：{show_bits(start)}")
    print(f"  目标：{show_bits(goal)}")
    print("  可用操作：")
    for i, op in enumerate(ops):
        print("    " + op_text(op, i))
    print("  请输入操作编号序列，用空格分隔（例：0 2 1），回车执行。")

    x = start
    steps = 0
    penalty = 0
    used_retry = False
    while True:
        try:
            raw = input("  > ").strip()
        except EOFError:
            print("\n输入中断，提前结算。")
            return 0
        low = raw.lower()
        if low in ("q", "quit"):
            return None
        if low == "ops":
            for i, op in enumerate(ops):
                print("    " + op_text(op, i))
            continue
        if low == "bits":
            print("    临时状态：" + show_bits(x))
            continue
        if low == "reset":
            x = start
            steps = 0
            print("    已回到起点。")
            continue
        if not raw:
            continue

        tokens = raw.replace(",", " ").split()
        ok = True
        tmp = x
        seq = []
        for tk in tokens:
            if not tk.isdigit() or int(tk) >= len(ops):
                ok = False
                break
            seq.append(int(tk))
            tmp = apply(ops[int(tk)], tmp)
        if not ok:
            print(f"  编号要写 0 到 {len(ops) - 1} 之间的数字。")
            continue

        if tmp == goal:
            steps += len(seq)
            x = tmp
            base = 100 - max(0, steps - optimal) * 15
            score = max(20, base)
            if used_retry:
                score = min(score, 70)
            print(f"  ✅ 到达目标！用了 {steps} 步，最短是 {optimal} 步。本关 {score} 分。")
            return score

        steps += len(seq)
        x = tmp
        print(f"  ❌ 还没到目标。当前状态：{show_bits(x)}（已走 {steps} 步）")
        if not used_retry:
            used_retry = True
            print("  可以继续在这个状态上追加操作；如果本关最终完成，最高 70 分。")
        else:
            print("  继续输入操作，或输入 reset 重来。")


def play():
    print("=" * 62)
    print("      🔧 位运算迷宫 · BitSmith")
    print("=" * 62)
    print("用位运算把一个 8 位字节从起点推到目标。输入操作编号序列即可。")
    # 预先确定每关目标，避免不同关卡目标重复
    used = set()
    goals = []
    for start, ops, want in LEVELS:
        g = pick_goal(start, ops, want, used)
        used.add(g)
        goals.append(g)

    total = 0
    got = []
    for i, lv in enumerate(LEVELS):
        res = run_level(i, lv, goals[i])
        if res is None:
            break
        total += res
        got.append(res)

    print("\n" + "=" * 62)
    print(f"  结算：{len(got)}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 450:
        print("  🏆 你对掩码和移位已经形成肌肉记忆了。")
    elif total >= 250:
        print("  👍 会用掩码清位/点灯，注意移位丢位会改变高位。")
    else:
        print("  🙂 解题思路：先用 AND 掩码把无关位清零，再用 OR 点灯、XOR 取反。")
    print("=" * 62)


if __name__ == "__main__":
    play()
