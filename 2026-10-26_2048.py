# -*- coding: utf-8 -*-
"""
2048
====
经典 2048 方块合并游戏。通过方向键（用 w/a/s/d 或方向词）滑动合并相同数字，
目标凑出 2048。纯标准库实现，可直接运行：python3 2026-10-26_2048.py
"""

import random

SIZE = 4
TARGET = 2048


def new_board():
    return [[0] * SIZE for _ in range(SIZE)]


def spawn(board):
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if board[r][c] == 0]
    if not empty:
        return
    r, c = random.choice(empty)
    board[r][c] = 2 if random.random() < 0.9 else 4


def slide_row(row):
    """左移一行，返回 (新行, 是否变化)"""
    row = [x for x in row if x != 0]
    new = []
    i = 0
    while i < len(row):
        if i + 1 < len(row) and row[i] == row[i + 1]:
            new.append(row[i] * 2)
            i += 2
        else:
            new.append(row[i])
            i += 1
    new += [0] * (SIZE - len(new))
    changed = new != row + [0] * (SIZE - len(row)) if False else True
    return new


def move(board, direction):
    """direction: 0左 1右 2上 3下"""
    def left(b):
        changed = False
        for r in range(SIZE):
            row = [x for x in b[r] if x != 0]
            new = []
            i = 0
            while i < len(row):
                if i + 1 < len(row) and row[i] == row[i + 1]:
                    new.append(row[i] * 2)
                    i += 2
                else:
                    new.append(row[i])
                    i += 1
            new += [0] * (SIZE - len(new))
            if new != b[r]:
                changed = True
            b[r] = new
        return changed

    if direction == 0:   # 左
        return left(board)
    elif direction == 1:  # 右
        for r in range(SIZE):
            board[r].reverse()
        changed = left(board)
        for r in range(SIZE):
            board[r].reverse()
        return changed
    elif direction in (2, 3):  # 上/下 转置后当左右处理
        trans = [[board[r][c] for r in range(SIZE)] for c in range(SIZE)]
        if direction == 3:  # 下 = 上+反转
            for c in range(SIZE):
                trans[c].reverse()
        changed = left(trans)
        if direction == 3:
            for c in range(SIZE):
                trans[c].reverse()
        for r in range(SIZE):
            for c in range(SIZE):
                board[r][c] = trans[c][r]
        return changed
    return False


def game_over(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                return False
            if c + 1 < SIZE and board[r][c] == board[r][c + 1]:
                return False
            if r + 1 < SIZE and board[r][c] == board[r + 1][c]:
                return False
    return True


def print_board(board):
    print("\n+----+----+----+----+")
    for r in range(SIZE):
        print("|" + "|".join(str(board[r][c]).center(4) if board[r][c] else "    " for c in range(SIZE)) + "|")
        print("+----+----+----+----+")


def max_tile(board):
    return max(max(row) for row in board)


def main():
    print("=" * 40)
    print("        🔢 2048")
    print("=" * 40)
    print("操作：w/a/s/d 或 上/下/左/右 移动，q 退出")
    board = new_board()
    spawn(board)
    spawn(board)
    moves = {"a": 0, "left": 0, "左": 0, "d": 1, "right": 1, "右": 1,
             "w": 2, "up": 2, "上": 2, "s": 3, "down": 3, "下": 3}
    while True:
        print_board(board)
        print(f"最大方块：{max_tile(board)}")
        cmd = input("移动(w/a/s/d)：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。")
            break
        if cmd not in moves:
            print("无效输入。")
            continue
        changed = move(board, moves[cmd])
        if changed:
            spawn(board)
        if max_tile(board) >= TARGET:
            print_board(board)
            print("🎉 达成 2048！你赢了！")
            break
        if game_over(board):
            print_board(board)
            print(f"😢 没有可移动的格子，游戏结束。最大方块 {max_tile(board)}")
            break


if __name__ == "__main__":
    main()
