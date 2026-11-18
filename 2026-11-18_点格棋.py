# -*- coding: utf-8 -*-
"""
点格棋 · Dots and Boxes
====================================================
棋盘上有一排排小圆点，两位玩家轮流把相邻的两点连起来（横线或竖线）。
谁画下某条线、把一个小方格的四条边「封口」了，这个小方格就归谁，
而且封口之后**还能再画一条线**（连续吃子，叫「链」）。

终局：所有线都画完，谁占的格子多谁赢。

思路提示：
  随便乱画，会把方格画成「三边已封、只差一边」的样子，
  下一个轮到的人一补就白拿一格。所以真正的高手会
  「先把安全的边填完，把危险的三边框留给对手」。

画线命令（行列都从 1 开始数，跟棋盘上的坐标一致）：
  h 行 列    画横线：第 行 行的点与它右边那一列的点相连
  v 行 列    画竖线：第 行 行的点与它下面一行的点相连
  show      重画棋盘
  q         退出

运行：python3 2026-11-18_点格棋.py
"""

import random

LEVELS = [
    {"n": 3, "name": "热身 3×3 点阵", "note": "只有 4 个格子，先熟悉画线的坐标。"},
    {"n": 4, "name": "标准 4×4 点阵", "note": "9 个格子，注意别把三边框白送。"},
    {"n": 5, "name": "进阶 5×5 点阵", "note": "16 个格子，链越长越容易翻盘。"},
]

PLAYER = "P"
AI = "A"


def all_edges(n):
    es = []
    for r in range(n):
        for c in range(n - 1):
            es.append(("H", r, c))
    for r in range(n - 1):
        for c in range(n):
            es.append(("V", r, c))
    return es


def box_edges(r, c):
    """格子 (r, c) 的四条边。"""
    return [("H", r, c), ("H", r + 1, c), ("V", r, c), ("V", r, c + 1)]


def adj_boxes(edge, n):
    """一条边最多属于两个格子。"""
    kind, r, c = edge
    out = []
    if kind == "H":
        for br in (r - 1, r):
            if 0 <= br <= n - 2 and 0 <= c <= n - 2:
                out.append((br, c))
    else:
        for bc in (c - 1, c):
            if 0 <= bc <= n - 2 and 0 <= r <= n - 2:
                out.append((r, bc))
    return out


def closed_boxes(edge, drawn, n):
    """放下这条边之后，有哪些格子刚好被封口。"""
    got = []
    for b in adj_boxes(edge, n):
        if all(e in drawn or e == edge for e in box_edges(*b)):
            got.append(b)
    return got


def render(n, drawn, owner):
    lines = []
    for r in range(n):
        row = ""
        for c in range(n):
            row += "•"
            if c < n - 1:
                row += " ── " if ("H", r, c) in drawn else "    "
        lines.append(row)
        if r < n - 1:
            mid = ""
            for c in range(n):
                mid += "│" if ("V", r, c) in drawn else " "
                if c < n - 1:
                    o = owner.get((r, c))
                    mid += f" {o} " if o else " . "
                else:
                    mid += "   "
            lines.append(mid)
    return "\n".join("    " + ln for ln in lines)


def coord_legend(n):
    print("    格子坐标（行, 列）：")
    for r in range(n - 1):
        print("    " + "  ".join(f"({r + 1},{c + 1})" for c in range(n - 1)))


def ai_choose(drawn, n):
    """贪心 + 避免送格：先吃能吃的，其次只画安全的边。"""
    cand = [e for e in all_edges(n) if e not in drawn]
    if not cand:
        return None

    # 1. 能立刻封口的边，先吃
    for e in cand:
        if closed_boxes(e, drawn, n):
            return e

    # 2. 安全边：画下去之后，不会让任何未完成格子变成「三边已封」
    safe = []
    for e in cand:
        danger = False
        for b in adj_boxes(e, n):
            cnt = sum(1 for be in box_edges(*b) if be in drawn or be == e)
            if cnt == 3:
                danger = True
                break
        if not danger:
            safe.append(e)
    if safe:
        return random.choice(safe)
    return random.choice(cand)


def parse_edge(raw, n):
    parts = raw.replace(",", " ").split()
    if len(parts) != 3:
        raise ValueError("格式是：h 行 列 或 v 行 列")
    kind = parts[0].lower()
    if kind in ("h", "横向", "-"):
        kind = "H"
    elif kind in ("v", "竖向", "|"):
        kind = "V"
    else:
        raise ValueError("第一条只能是 h（横线）或 v（竖线）")
    if not (parts[1].isdigit() and parts[2].isdigit()):
        raise ValueError("行和列要写数字")
    r, c = int(parts[1]) - 1, int(parts[2]) - 1
    if not (0 <= r < n and 0 <= c < n):
        raise ValueError(f"行、列的取值范围是 1 到 {n}")
    if kind == "H" and c > n - 2:
        raise ValueError(f"横线的列最多到 {n - 1}（右边没有点了）")
    if kind == "V" and r > n - 2:
        raise ValueError(f"竖线的行最多到 {n - 1}（下边没有点了）")
    return (kind, r, c)


def play_level(idx, level):
    n = level["n"]
    total_boxes = (n - 1) ** 2
    drawn = set()
    owner = {}
    score = {PLAYER: 0, AI: 0}
    turn = PLAYER

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关 · {level['name']}")
    print("=" * 62)
    print("  " + level["note"])
    print(f"  格子总数 {total_boxes}，你是 P，电脑是 A。")

    while len(drawn) < len(all_edges(n)):
        if turn == AI:
            e = ai_choose(drawn, n)
            drawn.add(e)
            got = closed_boxes(e, drawn, n)
            for b in got:
                owner[b] = AI
                score[AI] += 1
            print(f"\n  电脑画了 {e[0]} {e[1] + 1} {e[2] + 1}"
                  + (f"，吃了 {len(got)} 格" if got else ""))
            if not got:
                turn = PLAYER
            continue

        print(render(n, drawn, owner))
        print(f"  比分　你 {score[PLAYER]} : {score[AI]} 电脑　（还剩 "
              f"{len(all_edges(n)) - len(drawn)} 条线没画）")
        try:
            raw = input("\n  你画哪条线？（h 行 列 / v 行 列）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return score[PLAYER], None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score[PLAYER], None
        if low in ("show", "map"):
            coord_legend(n)
            continue
        try:
            e = parse_edge(raw, n)
        except ValueError as msg:
            print(f"  {msg}")
            continue
        if e in drawn:
            print("  这条线已经画过了，换一条。")
            continue

        drawn.add(e)
        got = closed_boxes(e, drawn, n)
        for b in got:
            owner[b] = PLAYER
            score[PLAYER] += 1
        if got:
            print(f"  ✅ 封口 {len(got)} 格！还能继续画一条线。")
        else:
            turn = AI
            if not closed_boxes(e, drawn, n):
                pass

    print(render(n, drawn, owner))
    p, a = score[PLAYER], score[AI]
    print(f"\n  终局：你 {p} : {a} 电脑（共 {p + a} 格）")
    if p > a:
        print("  🏆 你赢了这一关！")
    elif p == a:
        print("  🤝 平局。")
    else:
        print("  🙂 电脑赢了：下次先把安全边填完，别把三边框送给它。")
    return p, True


def play():
    print("=" * 62)
    print("      🔲 点格棋 · Dots and Boxes")
    print("=" * 62)
    print("轮流画线，谁把方格四条边封口，方格就归谁，并且能继续画。")

    # 开局自检：AI 自对弈必须能正常走完，格子总数对得上
    for i, lv in enumerate(LEVELS, 1):
        n = lv["n"]
        drawn, owner = set(), {}
        cnt = {PLAYER: 0, AI: 0}
        turn = PLAYER
        guard = 0
        while len(drawn) < len(all_edges(n)):
            e = ai_choose(drawn, n)
            assert e not in drawn, f"第 {i} 关自检：AI 选了已画的线"
            drawn.add(e)
            got = closed_boxes(e, drawn, n)
            for b in got:
                assert b not in owner, f"第 {i} 关自检：同一格被重复占领"
                owner[b] = turn
                cnt[turn] += 1
            if not got:
                turn = AI if turn == PLAYER else PLAYER
            guard += 1
            assert guard <= 500
        assert len(drawn) == len(all_edges(n))
        assert cnt[PLAYER] + cnt[AI] == (n - 1) ** 2, "格子数不等于 (n-1)^2"
        assert len(owner) == (n - 1) ** 2

    total = done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = play_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  本次共占 {total} 格（完成 {done}/{len(LEVELS)} 关）")
    print("=" * 62)


if __name__ == "__main__":
    play()
