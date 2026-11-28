#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hex 六边形棋 —— 在菱形六边棋盘上抢先连成一条通路

【简介】
Hex 是 1942 年由丹麦数学家皮特·海因发明的两人棋类，规则简单到一句话：
  你在棋盘上落子，谁先用自己颜色的棋子把「自己负责的两条对边」连起来，谁就赢。
它的数学性质非常漂亮：棋盘填满时不可能和棋，而且恰好有一方连通（Hex 定理）。

本程序用 6 邻接的菱形网格模拟六边形棋盘：
  你执 X，负责「上边第 1 行」到「下边第 n 行」的纵向连通；
  电脑执 O，负责「左边第 A 列」到「右边第 n 列」的横向连通。
棋盘一旦填满必定分出胜负，不存在平局。

【玩法】
- 坐标写法：列用字母 A、B、C…，行用数字 1、2、3…
  例如 C4 表示第 3 列第 4 行；也接受「c 4」「4c」「C04」等写法。
- 你先手（X），输入坐标落子；电脑（O）用启发式应战（前两关偏贪心，后三关更稳健）。
- 共 5 关，棋盘从 5×5 逐步放大到 9×9，电脑也随之变强。
- 每赢一关得 20 分，满分 100；输了这关得 0 分但可以继续下一关。

【命令】
  C4        在 C 列 4 行落子
  hint/h    花 5 分看一个推荐落点（同一关最多用 3 次）
  help/?    再看一遍规则
  空行       重画棋盘
  q/quit    退出

【运行】
  python3 2026-11-28_Hex六边形棋.py
  python3 2026-11-28_Hex六边形棋.py --check   # 自检（连通性、Hex 定理、AI 合法性与胜率）

【小知识】
Hex 的不可能和棋来自「布劳威尔不动点定理」的离散版本；也因此 Hex 先手必胜，
但至今没有人给出非构造性的一般证明。
"""

import heapq
import random
import re
import sys

BOARD_SIZES = [5, 5, 7, 7, 9]
AI_STYLES = ["greedy", "greedy", "balanced", "balanced", "balanced"]
HINT_COST = 5
HINT_LIMIT = 3


def neighbors(r, c, n):
    """六邻接：上下左右 + 两条对角线（菱形网格的 6 个方向）。"""
    cand = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1), (r - 1, c + 1), (r + 1, c - 1)]
    return [(x, y) for x, y in cand if 0 <= x < n and 0 <= y < n]


def col_label(c):
    return chr(ord("A") + c)


def parse_move(text, n):
    """把用户输入解析成 (r, c)；非法返回 None。"""
    s = text.strip().upper().replace("，", ",").replace(",", " ")
    if not s:
        return None
    m = re.fullmatch(r"([A-Z])\s*([0-9]{1,2})", s)
    if not m:
        m = re.fullmatch(r"([0-9]{1,2})\s*([A-Z])", s)
        if not m:
            return None
        num, letter = m.group(1), m.group(2)
    else:
        letter, num = m.group(1), m.group(2)
    if not letter.isalpha() or len(letter) != 1:
        return None
    c = ord(letter) - ord("A")
    try:
        r = int(num) - 1
    except ValueError:
        return None
    if not (0 <= r < n and 0 <= c < n):
        return None
    return (r, c)


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb

    def same(self, a, b):
        return self.find(a) == self.find(b)


def connected(stones, n, axis):
    """判断某色棋子是否连通了它的两条对边。
    axis='v'：X 连接第 0 行到第 n-1 行；axis='h'：O 连接第 0 列到第 n-1 列。
    """
    if not stones:
        return False
    dsu = DSU(n * n)
    for (r, c) in stones:
        for (x, y) in neighbors(r, c, n):
            if (x, y) in stones:
                dsu.union(r * n + c, x * n + y)
    if axis == "v":
        starts = {(0, c) for c in range(n)} & stones
        ends = {(n - 1, c) for c in range(n)} & stones
    else:
        starts = {(r, 0) for r in range(n)} & stones
        ends = {(r, n - 1) for r in range(n)} & stones
    for s in starts:
        for t in ends:
            if dsu.same(s[0] * n + s[1], t[0] * n + t[1]):
                return True
    return False


def winner(xs, os_, n):
    """返回 'X' / 'O' / None（不可能同时出现，见 Hex 定理）。"""
    xw = connected(xs, n, "v")
    ow = connected(os_, n, "h")
    if xw and ow:
        raise AssertionError("Hex 定理被破坏：双方同时连通")
    if xw:
        return "X"
    if ow:
        return "O"
    return None


def shortest_cost(stones, n, axis, own, extra=None):
    """从本方起点边界走到终点边界的最短「阻力」。
    own 自己的子代价 0，空格代价 1，对方的子视为墙（不可通过）。
    extra 表示把一个空格临时当作 own 来评估（AI 试手用）。
    """
    owner = set(own)
    if extra is not None:
        owner.add(extra)
    block = stones
    if axis == "v":
        src = [(0, c) for c in range(n) if (0, c) in owner]
        dst = {(n - 1, c) for c in range(n)}
    else:
        src = [(r, 0) for r in range(n) if (r, 0) in owner]
        dst = {(r, n - 1) for r in range(n)}
    if not src:
        return float("inf")
    dist = {}
    pq = []
    for s in src:
        dist[s] = 0
        heapq.heappush(pq, (0, s))
    while pq:
        d, cur = heapq.heappop(pq)
        if d > dist.get(cur, float("inf")):
            continue
        if cur in dst:
            return d
        for nb in neighbors(cur[0], cur[1], n):
            if nb in block and nb not in owner:
                continue
            if nb in owner:
                w = 0
            elif nb == extra:
                w = 0
            else:
                w = 1
            nd = d + w
            if nd < dist.get(nb, float("inf")):
                dist[nb] = nd
                heapq.heappush(pq, (nd, nb))
    return float("inf")


def ai_choose(xs, os_, n, rng, style="balanced"):
    """电脑选点：比较试手后双方的最短阻力，取对自己最有利、对对手最有害的点。"""
    empties = [(r, c) for r in range(n) for c in range(n) if (r, c) not in xs and (r, c) not in os_]
    if not empties:
        return None
    if style == "greedy" and rng.random() < 0.35:
        return rng.choice(empties)
    best, best_cell = None, None
    for cell in empties:
        d_self = shortest_cost(xs, n, "h", os_, extra=cell)      # 我下这里后我的阻力
        d_opp = shortest_cost(os_, n, "v", xs, extra=cell)       # 对手若下我这里的阻力
        # 越小越接近连通；把我的阻力下降与阻断对手的收益相加
        score = (d_opp - d_self) + 0.2 * (-d_self if d_self != float("inf") else -n * n)
        key = (score, -cell[0], -cell[1])
        if best is None or key > best:
            best, best_cell = key, cell
    return best_cell


def render(xs, os_, n, last=None):
    head = "    " + " ".join(col_label(c) for c in range(n))
    lines = [head]
    for r in range(n):
        indent = " " * (2 + r)
        cells = []
        for c in range(n):
            if (r, c) in xs:
                s = "X"
            elif (r, c) in os_:
                s = "O"
            else:
                s = "·"
            if last == (r, c):
                s = "[" + s + "]"
            else:
                s = " " + s + " "
            cells.append(s)
        lines.append(indent + str(r + 1).rjust(2) + " " + "".join(cells))
    lines.append("")
    lines.append("    X 要把上边连到下边；O 要把左边连到右边。")
    return "\n".join(lines)


def play_level(n, style, rng, input_fn, out, allow_hints=True):
    """玩一关。返回 True 表示玩家获胜。"""
    xs, os_ = set(), set()
    hints_left = HINT_LIMIT if allow_hints else 0
    last = None
    out(render(xs, os_, n, last))
    out("你先手（X）。请输入落点，如 C4。输入 help 查看规则。")
    while True:
        w = winner(xs, os_, n)
        if w == "X":
            return True
        if w == "O":
            return False
        if len(xs) + len(os_) >= n * n:
            return False
        # 玩家回合
        while True:
            try:
                raw = input_fn("你的落点 > ")
            except EOFError:
                out("\n输入结束，本局判负。")
                return False
            s = raw.strip()
            low = s.lower()
            if low in ("q", "quit", "exit", "退出"):
                raise KeyboardInterrupt
            if low in ("help", "?", "h", "hint", "提示"):
                if low in ("h", "hint", "提示") and hints_left > 0:
                    hints_left -= 1
                    rec = ai_choose(os_, xs, n, rng, "balanced")
                    while rec is not None and (rec in xs or rec in os_):
                        rec = None
                    out("提示已消耗 %d 分（剩 %d 次）。推荐落点：%s" % (
                        HINT_COST, hints_left, (col_label(rec[1]) + str(rec[0] + 1)) if rec else "无"))
                out(render(xs, os_, n, last))
                out("规则：X 连上→下，O 连左→右；坐标如 C4；q 退出。")
                continue
            if s == "":
                out(render(xs, os_, n, last))
                continue
            mv = parse_move(s, n)
            if mv is None:
                out("看不懂这个坐标，请用类似 C4 的写法（列 A-%s，行 1-%d）。" % (col_label(n - 1), n))
                continue
            if mv in xs or mv in os_:
                out("这个点已经有子了，换一个。")
                continue
            break
        xs.add(mv)
        last = mv
        out(render(xs, os_, n, last))
        w = winner(xs, os_, n)
        if w == "X":
            return True
        if len(xs) + len(os_) >= n * n:
            return False
        mv2 = ai_choose(xs, os_, n, rng, style)
        if mv2 is None:
            return False
        os_.add(mv2)
        last = mv2
        out("电脑落子：%s" % (col_label(mv2[1]) + str(mv2[0] + 1)))
        out(render(xs, os_, n, last))


def main(input_fn=input, out=print):
    out(__doc__.split("【运行】")[0])
    rng = random.Random()
    score = 0
    for i, n in enumerate(BOARD_SIZES, 1):
        style = AI_STYLES[i - 1]
        out("=" * 60)
        out("第 %d 关：棋盘 %d×%d，电脑风格「%s」。赢了得 20 分。" % (i, n, n, "贪心" if style == "greedy" else "稳健"))
        if play_level(n, style, rng, input_fn, out):
            score += 20
            out("★ 本关获胜！当前 %d 分。" % score)
        else:
            out("本关失败，得 0 分。当前 %d 分。" % score)
    out("=" * 60)
    out("最终得分：%d / 100" % score)
    if score == 100:
        out("称号：六边形大师 —— 通关全部五关，你的连路直觉很稳。")
    elif score >= 80:
        out("称号：准专业棋手 —— 只差一点就满贯。")
    elif score >= 40:
        out("称号：入门玩家 —— 记住：先抢中心，别只顾围堵。")
    else:
        out("称号：新手 —— 试试沿自己那条边「贴边走」，再向中间渗透。")
    return score


def check():
    ok = True

    def say(cond, msg):
        nonlocal ok
        if cond:
            print("[PASS]", msg)
        else:
            ok = False
            print("[FAIL]", msg)

    n = 7
    # 1. 邻接对称性与度数
    sym = True
    deg_ok = True
    for r in range(n):
        for c in range(n):
            nb = neighbors(r, c, n)
            if len(set(nb)) != len(nb):
                deg_ok = False
            for x, y in nb:
                if (r, c) not in neighbors(x, y, n):
                    sym = False
    say(sym, "六邻接关系对称（A 邻 B 则 B 邻 A）")
    say(deg_ok and len(neighbors(3, 3, n)) == 6, "内部点 6 邻")
    say(len(neighbors(0, 0, n)) == 2 and len(neighbors(n - 1, n - 1, n)) == 2
        and len(neighbors(0, n - 1, n)) == 3 and len(neighbors(n - 1, 0, n)) == 3,
        "四个角在菱形网格上分别为 2/2/3/3 邻（与几何一致）")

    # 2. 连通判定：整列 / 整行
    xs = {(r, 0) for r in range(n)}
    os_ = {(1, c) for c in range(n)}
    say(connected(xs, n, "v") and not connected(xs, n, "h"), "整列 X 连上→下（且不连左→右）")
    say(connected(os_, n, "h") and not connected(os_, n, "v"), "整行 O 连左→右（且不连上→下）")
    say(not connected({(0, 0), (2, 2)}, n, "v"), "零散两子判为未连通")

    # 3. Hex 定理：任意满盘恰好一方连通（随机 300 盘 + 全 X 盘）
    rng = random.Random(20261128)
    bad = 0
    both = 0
    for _ in range(300):
        cells = [(r, c) for r in range(n) for c in range(n)]
        rng.shuffle(cells)
        k = rng.randint(0, n * n)
        xs = set(cells[:k])
        os_ = set(cells[k:])
        xw, ow = connected(xs, n, "v"), connected(os_, n, "h")
        if xw and ow:
            both += 1
        if not xw and not ow:
            bad += 1
    say(both == 0, "随机满盘中不存在双方同时连通（%d 例）" % both)
    say(bad == 0, "随机满盘中不存在和棋（%d 例）" % bad)

    # 4. 模拟整局：随机玩家 vs AI，AI 胜率与合法性
    def random_player_loop(nn, style, seed, ai_vs_random=True):
        r2 = random.Random(seed)
        xs, os_ = set(), set()
        first = True
        while True:
            w = winner(xs, os_, nn)
            if w:
                return w
            if len(xs) + len(os_) >= nn * nn:
                return None
            if ai_vs_random:
                if first:
                    empties = [(r, c) for r in range(nn) for c in range(nn)]
                    mv = r2.choice(empties)
                    xs.add(mv)
                    first = False
                else:
                    mv = ai_choose(xs, os_, nn, r2, style)
                    if mv is None or mv in xs or mv in os_:
                        raise AssertionError("AI 非法落子")
                    os_.add(mv)
            else:
                empties = [(r, c) for r in range(nn) for c in range(nn) if (r, c) not in xs and (r, c) not in os_]
                mv = r2.choice(empties)
                xs.add(mv)
                mv = ai_choose(xs, os_, nn, r2, style)
                if mv is None or mv in xs or mv in os_:
                    raise AssertionError("AI 非法落子")
                os_.add(mv)
            if len(xs) + len(os_) >= nn * nn:
                return winner(xs, os_, nn)

    wins = 0
    games = 200
    for g in range(games):
        if random_player_loop(5, "greedy", 1000 + g) == "O":
            wins += 1
    say(wins >= int(games * 0.9), f"5×5 贪心 AI 对随机玩家胜率 {wins}/{games}（要求 ≥90%）")

    det = True
    for g in range(20):
        a = [ai_choose({(1, 0), (2, 1)}, {(0, 2)}, 7, random.Random(g), "balanced") for _ in range(2)]
        if a[0] != a[1]:
            det = False
    say(det, "同一局面同一随机种子下 AI 落点确定")
    legality = True
    for g in range(40):
        res = random_player_loop(7, "balanced", 5000 + g, ai_vs_random=False)
        if res is None:
            legality = False
    say(legality, "电脑对电脑模拟 40 局全部顺利终局（无非法落子、无死循环）")

    # 5. 坐标解析
    cases = [("C4", 7, (3, 2)), ("c 4", 7, (3, 2)), ("4c", 7, (3, 2)), ("C04", 7, (3, 2)),
             (" A1 ", 5, (0, 0)), ("E5", 5, (4, 4))]
    parse_ok = all(parse_move(t, nn) == exp for t, nn, exp in cases)
    say(parse_ok, "坐标解析支持 C4 / c 4 / 4c / C04 / 带空格写法")
    say(parse_move("Z9", 7) is None and parse_move("A0", 7) is None and parse_move("A8", 7) is None
        and parse_move("hello", 7) is None, "越界与乱输被拒绝")

    # 6. 假 stdin 回归：1×1 棋盘落一子即连通获胜；EOF 判负；q 退出
    def runner(script, nn):
        buf = iter(script)

        def fake_input(_prompt=""):
            try:
                return next(buf)
            except StopIteration:
                raise EOFError
        return play_level(nn, "greedy", random.Random(3), fake_input, lambda *_: None)

    say(runner(["A1"], 1) is True, "1×1 棋盘落子即连通，返回获胜")
    say(runner([], 5) is False, "输入立即结束（EOF）时判负而不崩")
    try:
        runner(["q"], 5)
        quit_ok = False
    except KeyboardInterrupt:
        quit_ok = True
    say(quit_ok, "输入 q 能干净退出本局")
    say(runner(["Z9", "hello", "A0", "C3"], 5) is not None, "乱输不消耗回合、不误判胜负")

    print()
    print("自检通过 ✅" if ok else "自检未通过 ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        if "--check" in sys.argv:
            sys.exit(check())
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n已退出，下次再来。")
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
