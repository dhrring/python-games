# -*- coding: utf-8 -*-
"""
数独（Sudoku）
=============
标准 9x9 数独：用回溯算法自动生成一个可解的数独并挖空成题，
你逐格填入 1~9，行/列/宫不重复。纯标准库实现。
运行：python3 2026-10-27_数独.py
"""

import random

SIZE = 9
BOX = 3


def new_board():
    return [[0] * SIZE for _ in range(SIZE)]


def valid(board, r, c, num):
    for i in range(SIZE):
        if board[r][i] == num or board[i][c] == num:
            return False
    br, bc = (r // BOX) * BOX, (c // BOX) * BOX
    for i in range(br, br + BOX):
        for j in range(bc, bc + BOX):
            if board[i][j] == num:
                return False
    return True


def solve(board):
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == 0:
                nums = list(range(1, 10))
                random.shuffle(nums)
                for num in nums:
                    if valid(board, r, c, num):
                        board[r][c] = num
                        if solve(board):
                            return True
                        board[r][c] = 0
                return False
    return True


def generate_puzzle(clues=30):
    board = new_board()
    solve(board)  # 先得到一个完整解
    solution = [row[:] for row in board]
    # 随机挖空，保持唯一解（简单做法：随机挖去，仅保证有解）
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)
    to_remove = SIZE * SIZE - clues
    removed = 0
    for r, c in cells:
        if removed >= to_remove:
            break
        board[r][c] = 0
        removed += 1
    return board, solution


def print_board(board, original=None):
    print("  " + " ".join(str(c + 1) for c in range(SIZE)))
    for r in range(SIZE):
        row = ""
        for c in range(SIZE):
            v = board[r][c]
            if v == 0:
                row += "· "
            elif original and original[r][c] != 0:
                row += f"\033[1m{v}\033[0m "  # 原题加粗
            else:
                row += f"{v} "
            if c in (2, 5):
                row += "| "
        print(f"{r+1} " + row)
        if r in (2, 5):
            print("  " + "-" * 21)


def is_solved(board):
    for r in range(SIZE):
        if sorted(x for x in board[r]) != list(range(1, 10)):
            return False
    for c in range(SIZE):
        if sorted(board[r][c] for r in range(SIZE)) != list(range(1, 10)):
            return False
    return True


def main():
    print("=" * 40)
    print("        🔢 数独 Sudoku")
    print("=" * 40)
    board, solution = generate_puzzle(clues=30)
    original = [row[:] for row in board]
    print("已生成数独，填入数字使每行/列/宫都含1~9。")
    print("输入格式：行 列 数字（如 1 3 5）。q 退出，s 显示答案。")

    while True:
        print_board(board, original)
        cmd = input("> ").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if cmd == "s":
            print("答案：")
            print_board(solution)
            return
        parts = cmd.split()
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            print("请输入：行 列 数字，如 1 3 5。")
            continue
        r, c, num = (int(p) for p in parts)
        if not (1 <= r <= SIZE and 1 <= c <= SIZE and 1 <= num <= 9):
            print("范围：行/列1~9，数字1~9。")
            continue
        r -= 1
        c -= 1
        if original[r][c] != 0:
            print("这是原题给出的格子，不能修改。")
            continue
        if not valid(board, r, c, num):
            print("该数字与同行/列/宫冲突。")
            continue
        board[r][c] = num
        if is_solved(board):
            print_board(board, original)
            print("🎉 恭喜完成数独！")
            return


if __name__ == "__main__":
    main()
