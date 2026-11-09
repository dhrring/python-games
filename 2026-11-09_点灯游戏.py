# -*- coding: utf-8 -*-
"""
点灯游戏（Lights Out）
=======================
5×5 的灯阵，有些灯亮着。你点任意一盏灯，它自己以及上下左右相邻的 4 盏灯
会一起翻转（亮变灭、灭变亮）。目标：把所有灯都熄灭。
纯标准库实现。

难点：点灯的顺序与次数有讲究，同一盏灯点两次等于白点。
小提示：每一行怎么点，往往由上一行的亮灯情况决定（自上而下逐行消灯）。

游玩方法：
  输入「行 列」（1~5）点击该灯，例如 3 2；
  输入 r 重置本关，n 换一道新局，q 退出。
  每局都保证有解（由已解状态随机点击生成）。
运行：python3 2026-11-09_点灯游戏.py
"""

import random

SIZE = 5
ON, OFF = "■", "□"


def new_puzzle(min_clicks=6, max_clicks=12):
    """从全灭棋盘随机点若干次生成一局，保证一定有解。"""
    board = [[0] * SIZE for _ in range(SIZE)]
    times = random.randint(min_clicks, max_clicks)
    for _ in range(times):
        click(board, random.randrange(SIZE), random.randrange(SIZE))
    if all(v == 0 for row in board for v in row):
        click(board, 2, 2)
    return board


def click(board, r, c):
    for dr, dc in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        rr, cc = r + dr, c + dc
        if 0 <= rr < SIZE and 0 <= cc < SIZE:
            board[rr][cc] ^= 1


def solved(board):
    return all(v == 0 for row in board for v in row)


def show(board, steps):
    print(f"\n点灯次数：{steps}    剩余亮灯：{sum(sum(r) for r in board)}")
    print("    1 2 3 4 5")
    for r in range(SIZE):
        print(f" {r + 1}  " + "".join(ON if board[r][c] else OFF for c in range(SIZE)))


def main():
    print("=" * 46)
    print("        💡 点灯游戏 Lights Out")
    print("=" * 46)
    print("点一盏灯，它和上下左右 4 盏一起翻转。把 ■ 全部变回 □ 即获胜。")

    board = new_puzzle()
    steps = 0
    while True:
        show(board, steps)
        if solved(board):
            print("\n" + "=" * 46)
            print(f"🎉 全部熄灭，你用了 {steps} 次点击通关！")
            print("=" * 46)
            again = input("再来一局？(y/n)：").strip().lower()
            if again.startswith("y"):
                board, steps = new_puzzle(), 0
                continue
            return
        raw = input("输入「行 列」点击（1~5），r 重置，n 新局，q 退出：").strip().lower()
        if raw in ("q", "quit", "exit"):
            print("你已退出。")
            return
        if raw == "r":
            board, steps = new_puzzle(6, 12), 0
            print("已重置为一道新局。")
            continue
        if raw == "n":
            board, steps = new_puzzle(), 0
            print("换了一道新局。")
            continue
        parts = raw.replace("，", " ").replace(",", " ").split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("格式：行 列（都是 1~5），例如 3 2。")
            continue
        r, c = int(parts[0]) - 1, int(parts[1]) - 1
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            print("行列都必须在 1~5 之间。")
            continue
        click(board, r, c)
        steps += 1


if __name__ == "__main__":
    main()
