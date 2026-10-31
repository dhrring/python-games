# -*- coding: utf-8 -*-
"""
五子棋（Gomoku）
===============
15x15 棋盘，玩家执黑（●）与电脑执白（○）对战，
率先在横/竖/斜方向连成五子者胜。电脑用简单攻防策略。纯标准库实现。
运行：python3 2026-10-31_五子棋.py
"""

import random

SIZE = 15
EMPTY = "."
BLACK = "●"
WHITE = "○"


def new_board():
    return [[EMPTY] * SIZE for _ in range(SIZE)]


def print_board(b):
    print("   " + " ".join(f"{c%10}" for c in range(SIZE)))
    for r in range(SIZE):
        print(f"{r%10:2d} " + " ".join(b[r]))


def directions():
    return [(0, 1), (1, 0), (1, 1), (1, -1)]


def count_run(b, r, c, dr, dc, stone):
    """从(r,c)沿方向数连续同色棋子数"""
    n = 0
    rr, cc = r, c
    while 0 <= rr < SIZE and 0 <= cc < SIZE and b[rr][cc] == stone:
        n += 1
        rr += dr
        cc += dc
    return n


def find_winner(b):
    for r in range(SIZE):
        for c in range(SIZE):
            if b[r][c] == EMPTY:
                continue
            stone = b[r][c]
            for dr, dc in directions():
                # 只从"起点"判断（防止重复）
                if 0 <= r - dr < SIZE and 0 <= c - dc < SIZE and b[r - dr][c - dc] == stone:
                    continue
                if count_run(b, r, c, dr, dc, stone) >= 5:
                    return stone
    return None


def is_full(b):
    return all(b[r][c] != EMPTY for r in range(SIZE) for c in range(SIZE))


def empty_cells(b):
    return [(r, c) for r in range(SIZE) for c in range(SIZE) if b[r][c] == EMPTY]


def cpu_move(b):
    """电脑：优先能赢→堵玩家→抢中心→随机"""
    def score_cell(r, c, stone):
        """评估在(r,c)放stone的价值"""
        s = 0
        for dr, dc in directions():
            run = count_run(b, r, c, dr, dc, stone)
            # 落子后两方向总连子数
            total = run + count_run(b, r + dr, c + dc, dr, dc, stone) - 1
            s += total
        return s

    # 1. 自己能成五子
    for r, c in empty_cells(b):
        b[r][c] = WHITE
        if find_winner(b) == WHITE:
            b[r][c] = EMPTY
            return r, c
        b[r][c] = EMPTY
    # 2. 堵玩家成五子
    for r, c in empty_cells(b):
        b[r][c] = BLACK
        if find_winner(b) == BLACK:
            b[r][c] = EMPTY
            return r, c
        b[r][c] = EMPTY
    # 3. 中心附近高价值位
    center = SIZE // 2
    if b[center][center] == EMPTY:
        return center, center
    # 4. 按攻防得分选最好位
    best, br, bc = -1, 0, 0
    for r, c in empty_cells(b):
        atk = score_cell(r, c, WHITE)
        dfn = score_cell(r, c, BLACK)
        val = atk + 1.5 * dfn
        if val > best:
            best, br, bc = val, r, c
    return br, bc


def main():
    print("=" * 40)
    print("        ⚫⚪ 五子棋 Gomoku")
    print("=" * 40)
    print(f"15x15 棋盘，你执 {BLACK}（黑），电脑执 {WHITE}（白）。")
    print("输入落子坐标，如 7 7 表示第7行第7列。q 退出。")
    b = new_board()
    turn = 0  # 0玩家 1电脑
    b[SIZE // 2][SIZE // 2] = BLACK
    turn = 1
    print("（电脑让先，你先落一子）")

    while True:
        print_board(b)
        w = find_winner(b)
        if w:
            print(f"{'🎉 你赢了！' if w==BLACK else '😢 电脑赢了。'}")
            return
        if is_full(b):
            print("🤝 平局。")
            return
        if turn == 1:
            r, c = cpu_move(b)
            b[r][c] = WHITE
            print(f"电脑落子：{r} {c}")
            turn = 0
            continue
        cmd = input("你落子(行 列)：").strip()
        if cmd.lower() in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        parts = cmd.split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("格式：行 列，如 7 7。")
            continue
        r, c = int(parts[0]), int(parts[1])
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            print(f"范围0~{SIZE-1}。")
            continue
        if b[r][c] != EMPTY:
            print("这个位置已有棋子。")
            continue
        b[r][c] = BLACK
        turn = 1


if __name__ == "__main__":
    main()
