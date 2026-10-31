# -*- coding: utf-8 -*-
"""
数字华容道（15-Puzzle / 8-Puzzle）
==================================
经典滑块拼图：把乱序数字滑块移回 1~N 顺序。空格可用 w/a/s/d 把相邻滑块移入。
纯标准库实现。运行：python3 2026-10-31_数字华容道.py
"""

import random

ROWS, COLS = 3, 3  # 3x3 = 8-puzzle
# 用 4x4 = 15-puzzle 更经典，这里用 3x3 便于演示；可改 ROWS/COLS
ROWS, COLS = 4, 4


def solved_state():
    """目标状态：1..N-1 顺序排列，最后为 0（空格）"""
    nums = list(range(1, ROWS * COLS)) + [0]
    return [nums[i * COLS:(i + 1) * COLS] for i in range(ROWS)]


def find_zero(b):
    for r in range(ROWS):
        for c in range(COLS):
            if b[r][c] == 0:
                return r, c


def shuffled():
    b = solved_state()
    # 做随机合法移动打乱
    r, c = find_zero(b)
    for _ in range(300):
        moves = []
        if r > 0:
            moves.append((-1, 0))
        if r < ROWS - 1:
            moves.append((1, 0))
        if c > 0:
            moves.append((0, -1))
        if c < COLS - 1:
            moves.append((0, 1))
        dr, dc = random.choice(moves)
        nr, nc = r + dr, c + dc
        b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
        r, c = nr, nc
    return b


def print_board(b):
    n = ROWS * COLS
    width = len(str(n))
    for r in range(ROWS):
        print("   ".join(f"{b[r][c]:>{width}d}" if b[r][c] else " " * width for c in range(COLS)))
    print()


def is_solved(b):
    return b == solved_state()


def main():
    print("=" * 40)
    print(f"        🧩 数字华容道 {ROWS}x{COLS}")
    print("=" * 40)
    print("把数字移回顺序。空格用 w/a/s/d 让相邻滑块移入空位。q退出。")
    b = shuffled()
    moves = 0

    while not is_solved(b):
        print_board(b)
        cmd = input("移动(w/a/s/d)：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        dr = dc = 0
        if cmd == "w":
            dr = -1
        elif cmd == "s":
            dr = 1
        elif cmd == "a":
            dc = -1
        elif cmd == "d":
            dc = 1
        else:
            print("输入 w/a/s/d。")
            continue
        r, c = find_zero(b)
        nr, nc = r + dr, c + dc
        if not (0 <= nr < ROWS and 0 <= nc < COLS):
            print("越界，无法移动。")
            continue
        b[r][c], b[nr][nc] = b[nr][nc], b[r][c]
        moves += 1
    print_board(b)
    print(f"🎉 拼图完成！共用了 {moves} 步。")


if __name__ == "__main__":
    main()
