# -*- coding: utf-8 -*-
"""
康威生命游戏 · 沙盒（元胞自动机）
====================================================
一片细胞世界，规则只有四条（B3/S23）：
  1. 活细胞周围有 2 或 3 个活邻居 → 下一代继续活
  2. 活细胞周围少于 2 个活邻居 → 孤独而死
  3. 活细胞周围多于 3 个活邻居 → 拥挤而死
  4. 死细胞周围恰好 3 个活邻居 → 复活

先做 4 道预测题（每道问你「下一代有几个活细胞」），答完进入自由沙盒。

沙盒命令：
  p   载入预设图案（滑翔机 / 脉冲星 / 高斯帕机枪 / 随机种子）
  s   单步演化一代
  r   自动演化（输入代数）
  e   编辑：输入两个坐标切换该格生死，行 列 从 0 开始
  c   清空
  g   显示图例与当前代数、活细胞数
  q   退出

运行：python3 2026-11-14_生命游戏.py
"""

ROWS, COLS = 16, 34
ALIVE, DEAD = "█", "·"


def blank():
    return [[DEAD] * COLS for _ in range(ROWS)]


def neighbors(grid, r, c):
    n = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            rr, cc = r + dr, c + dc
            if 0 <= rr < ROWS and 0 <= cc < COLS and grid[rr][cc] == ALIVE:
                n += 1
    return n


def step(grid):
    nxt = blank()
    for r in range(ROWS):
        for c in range(COLS):
            n = neighbors(grid, r, c)
            if grid[r][c] == ALIVE:
                nxt[r][c] = ALIVE if n in (2, 3) else DEAD
            else:
                nxt[r][c] = ALIVE if n == 3 else DEAD
    return nxt


def count(grid):
    return sum(row.count(ALIVE) for row in grid)


def render(grid, gen=0):
    print(f"  第 {gen} 代 · 活细胞 {count(grid)} 个")
    print("    " + "".join(str(c % 10) for c in range(COLS)))
    for r in range(ROWS):
        print(f"  {r:2d}" + "".join(grid[r]))


def put(grid, r, c, alive=True):
    if 0 <= r < ROWS and 0 <= c < COLS:
        grid[r][c] = ALIVE if alive else DEAD


def make_pulsar(g):
    """标准 13×13 脉冲星，周期 3（膨胀 - 收缩 - 复原）。"""
    base = [
        "..OOO...OOO..",
        ".............",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        "..OOO...OOO..",
        ".............",
        "..OOO...OOO..",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        ".............",
        "..OOO...OOO..",
    ]
    for r, line in enumerate(base):
        for c, ch in enumerate(line):
            if ch == "O":
                put(g, 1 + r, 1 + c)
    return g


def make_gun(g):
    # 高斯帕滑翔机枪（36 列宽，9 行高）
    pattern = [
        "........................O...........",
        "......................O.O...........",
        "............OO......OO............OO",
        "...........O...O....OO............OO",
        "OO........O.....O...OO..............",
        "OO........O...O.OO....O.O...........",
        "..........O.....O.......O...........",
        "...........O...O....................",
        "............OO......................",
    ]
    for r, line in enumerate(pattern):
        for c, ch in enumerate(line):
            if ch == "O":
                put(g, 1 + r, 1 + c)
    return g


def make_random(g, density=0.28):
    import random
    for r in range(ROWS):
        for c in range(COLS):
            if random.random() < density:
                put(g, r, c)
    return g


def load_preset(g):
    print("  预设：1 滑翔机  2 脉冲星  3 高斯帕机枪  4 随机种子")
    k = input("  选择 > ").strip()
    for r in range(ROWS):
        g[r] = [DEAD] * COLS
    if k == "1":
        for (r, c) in [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]:
            put(g, r, c)
        print("  已放置滑翔机：它每 4 代向右下平移一格。")
    elif k == "2":
        make_pulsar(g)
        print("  已放置脉冲星：周期 3，会反复膨胀收缩。")
    elif k == "3":
        make_gun(g)
        print("  已放置高斯帕机枪：每 30 代发射一艘滑翔机。")
    elif k == "4":
        make_random(g)
        print("  已随机撒下种子。")
    else:
        print("  没听懂，保持不变。")


QUIZ = [
    ("闪烁器（三个横排的细胞）", [(1, 1), (1, 2), (1, 3)]),
    ("方块（2×2 的四个细胞）", [(1, 1), (1, 2), (2, 1), (2, 2)]),
    ("滑翔机", [(1, 2), (2, 3), (3, 1), (3, 2), (3, 3)]),
    ("一排四个细胞", [(1, 1), (1, 2), (1, 3), (1, 4)]),
]


def quiz_mode():
    print("\n" + "=" * 62)
    print("      🧫 康威生命游戏")
    print("=" * 62)
    print("规则 B3/S23：活邻居 2~3 个继续活，死邻居恰好 3 个则复活。")
    print("先做 4 道预测题：看图案，猜「下一代有几个活细胞」。")
    score = 0
    for idx, (name, cells) in enumerate(QUIZ, 1):
        g = blank()
        for (r, c) in cells:
            put(g, r + 2, c + 3)
        print("\n" + "-" * 62)
        print(f"  第 {idx} 题：{name}")
        render(g, 0)
        nxt = step(g)
        ans = count(nxt)
        try:
            raw = input("  下一代有 ? 个活细胞 > ").strip()
        except EOFError:
            print("\n输入中断。")
            return score
        if raw.lower() in ("q", "quit"):
            return score
        if raw.isdigit() and int(raw) == ans:
            print(f"  ✅ 正确，下一代确实是 {ans} 个。")
            score += 100
        else:
            print(f"  ❌ 不对，答案是 {ans} 个。")
            render(nxt, 1)
    print(f"\n  预测题得分：{score}/400")
    return score


def sandbox():
    g = blank()
    make_random(g, 0.25)
    gen = 0
    render(g, gen)
    while True:
        try:
            cmd = input("\n  [p]预设 [s]单步 [r]自动 [e]编辑 [c]清空 [g]信息 [q]退出 > ").strip().lower()
        except EOFError:
            return
        if cmd in ("q", "quit"):
            return
        if cmd == "s":
            g = step(g)
            gen += 1
            render(g, gen)
        elif cmd == "r":
            try:
                n = int(input("  演化多少代 > ").strip())
            except ValueError:
                print("  请输入整数。")
                continue
            for _ in range(max(0, min(n, 500))):
                g = step(g)
                gen += 1
            render(g, gen)
        elif cmd == "e":
            try:
                r, c = input("  输入 行 列 > ").strip().split()
                r, c = int(r), int(c)
            except ValueError:
                print("  格式：行 列，例如 3 5")
                continue
            if 0 <= r < ROWS and 0 <= c < COLS:
                g[r][c] = DEAD if g[r][c] == ALIVE else ALIVE
                render(g, gen)
            else:
                print("  超出边界。")
        elif cmd == "c":
            for r in range(ROWS):
                g[r] = [DEAD] * COLS
            gen = 0
            print("  已清空。")
            render(g, gen)
        elif cmd == "p":
            load_preset(g)
            gen = 0
            render(g, gen)
        elif cmd == "g":
            print(f"  代数 {gen}，活细胞 {count(g)} 个。█=活 ·=死")
        else:
            print("  命令：p / s / r / e / c / g / q")


def main():
    quiz_mode()
    print("\n" + "=" * 62)
    print("  进入沙盒模式：可以自由播种、单步观察、连续演化。")
    print("  试试看：滑翔机 4 代后是否整体平移了一格？脉冲星是不是 3 代一轮回？")
    sandbox()
    print("\n  退出沙盒。想看更多图案，可以把预设里的坐标改一改。")


if __name__ == "__main__":
    main()
