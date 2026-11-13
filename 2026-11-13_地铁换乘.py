# -*- coding: utf-8 -*-
"""
地铁换乘挑战（3 条线路 · 14 座车站 · 5 道行程题）
====================================================
这座城市只有三条地铁线，但车站之间靠「换乘站」串起来。
你每次拿到一张「从 A 站到 B 站」的行程单，要写出完整的乘车路线：

    输入格式：站名之间用 -> 分隔，例如
        大学城 -> 中央广场 -> 商业街 -> 科技园

判定规则：
  · 相邻两站必须真的有线路相连，跳站不算
  · 不能重复经过同一站
  · 站数越少越好；站数一样时，换乘次数越少越好

游戏内命令：
  map    显示完整线路图
  hint   看最优站数提示（本题 −30 分）
  q      退出

计分：每题基准 100 分；每比最优多走 1 站 −15 分；每多换乘 1 次 −25 分。
运行：python3 2026-11-13_地铁换乘.py
"""

LINES = {
    "红线": ["文化宫", "图书馆", "中央广场", "体育中心", "大学城"],
    "蓝线": ["火车站", "中央广场", "商业街", "科技园"],
    "绿线": ["老城区", "图书馆", "商业街", "河畔", "机场"],
}

# 站点 -> 所属线路
STATION_LINES = {}
for line, stations in LINES.items():
    for st in stations:
        STATION_LINES.setdefault(st, []).append(line)

# 无向邻接：线路内前后站相连
ADJ = {}
for line, stations in LINES.items():
    for i in range(len(stations) - 1):
        a, b = stations[i], stations[i + 1]
        ADJ.setdefault(a, set()).add(b)
        ADJ.setdefault(b, set()).add(a)


def lines_between(a, b):
    """两站共用的线路（即这段可以坐哪条线）。"""
    out = []
    for line, stations in LINES.items():
        for i in range(len(stations) - 1):
            if {stations[i], stations[i + 1]} == {a, b}:
                out.append(line)
    return out


def dijkstra(src, dst):
    """返回 (最少站数, 对应最少换乘次数)。状态 = (车站, 当前所在线路)。"""
    import heapq
    best = {}
    pq = []
    for line in STATION_LINES[src]:
        state = (src, line)
        best[state] = (0, 0)
        heapq.heappush(pq, (0, 0, src, line))

    while pq:
        stops, trans, st, line = heapq.heappop(pq)
        if best.get((st, line), (10 ** 9, 10 ** 9)) < (stops, trans):
            continue
        if st == dst:
            return stops, trans
        # 同一条线继续往前坐
        idx = LINES[line].index(st)
        for nxt in (LINES[line][idx - 1] if idx > 0 else None,
                    LINES[line][idx + 1] if idx + 1 < len(LINES[line]) else None):
            if nxt is None:
                continue
            cand = (stops + 1, trans)
            if best.get((nxt, line), (10 ** 9, 10 ** 9)) > cand:
                best[(nxt, line)] = cand
                heapq.heappush(pq, (cand[0], cand[1], nxt, line))
        # 在同站换乘到别的线
        for other in STATION_LINES[st]:
            if other == line:
                continue
            cand = (stops, trans + 1)
            if best.get((st, other), (10 ** 9, 10 ** 9)) > cand:
                best[(st, other)] = cand
                heapq.heappush(pq, (cand[0], cand[1], st, other))
    return None, None


def path_transfers(path):
    """在给定站序下，最少的换乘次数（DP：每段可选一条线路）。"""
    if len(path) < 2:
        return 0
    options = [lines_between(path[i], path[i + 1]) for i in range(len(path) - 1)]
    if any(not o for o in options):
        return None
    cur = {line: 0 for line in options[0]}
    for i in range(1, len(options)):
        nxt = {}
        for line in options[i]:
            nxt[line] = min(c + (0 if prev == line else 1) for prev, c in cur.items())
        cur = nxt
    return min(cur.values())


def show_map():
    print("\n  线路图（相邻站之间有连线，跨线路的交点就是换乘站）")
    print("  " + "-" * 58)
    for line, stations in LINES.items():
        print(f"  {line}： " + " —— ".join(stations))
    print("  换乘站： " + "、".join(st for st, ls in STATION_LINES.items() if len(ls) > 1))
    print("  " + "-" * 58)


TASKS = [
    ("大学城", "科技园"),
    ("老城区", "体育中心"),
    ("机场", "火车站"),
    ("河畔", "大学城"),
    ("文化宫", "机场"),
]


def parse_path(raw):
    for sep in ("->", "→", "—", "-"):
        if sep in raw:
            return [p.strip() for p in raw.split(sep) if p.strip()]
    return [p.strip() for p in raw.replace("，", " ").replace(",", " ").split() if p.strip()]


def main():
    print("=" * 62)
    print("      🚇 地铁换乘挑战")
    print("=" * 62)
    print("三条线、14 座车站，5 张行程单。输入 map 看线路图，hint 看提示。")
    total = 0

    for idx, (src, dst) in enumerate(TASKS, 1):
        best_stops, best_trans = dijkstra(src, dst)
        score = 100
        print("\n" + "-" * 62)
        print(f"  第 {idx} 题：{src} → {dst}")
        print("  写出完整路线（站名之间用 -> 分隔）：")

        attempts = 0
        while True:
            try:
                raw = input("  > ").strip()
            except EOFError:
                print("\n输入中断，提前结束。")
                return summary(total)
            low = raw.lower()
            if low in ("q", "quit", "exit"):
                print("\n你出站了。")
                return summary(total)
            if low == "map":
                show_map()
                continue
            if low == "hint":
                if score >= 30:
                    score -= 30
                print(f"  提示：最优只要 {best_stops} 站；最少换乘 {best_trans} 次。（本题剩 {score} 分）")
                continue

            path = parse_path(raw)
            if not path:
                print("  没读懂，试着这样写：图书馆 -> 中央广场 -> 商业街")
                continue
            if path[0] != src or path[-1] != dst:
                print(f"  路线必须从 {src} 出发，到 {dst} 结束。")
                continue
            if len(set(path)) != len(path):
                print("  路线里不能重复经过同一个车站。")
                continue
            ok = True
            for i in range(len(path) - 1):
                if path[i + 1] not in ADJ.get(path[i], set()):
                    print(f"  ❌ {path[i]} 和 {path[i + 1]} 之间没有直达线路。")
                    ok = False
                    break
            if not ok:
                attempts += 1
                if attempts >= 3:
                    print(f"  三次都没走通，这题 0 分。最优方案：{best_stops} 站、换乘 {best_trans} 次。")
                    break
                continue

            stops = len(path) - 1
            trans = path_transfers(path)
            print(f"\n  路线有效：{stops} 站、换乘 {trans} 次（最优：{best_stops} 站、换乘 {best_trans} 次）")
            extra_s = stops - best_stops
            extra_t = trans - best_trans
            if extra_s > 0:
                score -= 15 * extra_s
                print(f"  · 多走了 {extra_s} 站（−{15 * extra_s} 分）")
            if extra_t > 0:
                score -= 25 * extra_t
                print(f"  · 多换乘 {extra_t} 次（−{25 * extra_t} 分）")
            score = max(0, score)
            if score >= 100:
                print("  🌟 完美路线！")
            elif score >= 60:
                print("  👍 能到，但还有更省事的走法。")
            else:
                print("  🙂 到是到了，绕了不少路。")
            print(f"  本题得 {score} 分")
            total += score
            break

    return summary(total)


def summary(total):
    print("\n" + "=" * 62)
    print(f"  五张行程单跑完，总分 {total}/500")
    if total >= 430:
        print("  🏆 活地图：你对换乘站的位置了如指掌。")
    elif total >= 300:
        print("  👍 熟客水平，偶尔绕一站。")
    elif total >= 150:
        print("  🙂 能找到路，但不算最优。")
    else:
        print("  😅 建议先记住三个换乘站：中央广场、图书馆、商业街。")
    print("  思路提示：找最短路线就是图上的广度优先搜索（BFS），换乘次数是第二优先级。")
    print("=" * 62)
    return total


if __name__ == "__main__":
    main()
