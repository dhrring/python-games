# -*- coding: utf-8 -*-
"""
扫雷（Minesweeper）
==================
经典扫雷：9x9 棋盘布 10 颗雷，翻开格子直到排除所有雷。
数字表示周围 8 格地雷数。第一次点击保证安全。纯标准库实现。
运行：python3 2026-10-31_扫雷.py
"""

import random

W, H = 9, 9
MINES = 10


def neighbors(r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < H and 0 <= nc < W:
                yield nr, nc


def init_board(first_r, first_c):
    board = [[0] * W for _ in range(H)]  # -1=雷
    # 布雷，避开第一次点击及其周围
    safe = {(first_r, first_c)}
    for nr, nc in neighbors(first_r, first_c):
        safe.add((nr, nc))
    cells = [(r, c) for r in range(H) for c in range(W) if (r, c) not in safe]
    random.shuffle(cells)
    for i in range(MINES):
        r, c = cells[i]
        board[r][c] = -1
    # 计算数字
    for r in range(H):
        for c in range(W):
            if board[r][c] == -1:
                continue
            board[r][c] = sum(1 for nr, nc in neighbors(r, c) if board[nr][nc] == -1)
    return board


def reveal(board, shown, r, c):
    if not (0 <= r < H and 0 <= c < W) or shown[r][c]:
        return
    shown[r][c] = True
    if board[r][c] == 0:
        for nr, nc in neighbors(r, c):
            reveal(board, shown, nr, nc)


def print_board(board, shown, flagged):
    print("   " + " ".join(str(c % 10) for c in range(W)))
    for r in range(H):
        row = [f"{r%10:2d}"]
        for c in range(W):
            if flagged[r][c]:
                row.append("⚑")
            elif not shown[r][c]:
                row.append("·")
            elif board[r][c] == -1:
                row.append("💣")
            elif board[r][c] == 0:
                row.append(" ")
            else:
                row.append(str(board[r][c]))
        print(" ".join(row))


def all_non_mines_revealed(board, shown):
    return all(shown[r][c] or board[r][c] == -1 for r in range(H) for c in range(W))


def main():
    print("=" * 40)
    print("        💣 扫雷 Minesweeper")
    print("=" * 40)
    print(f"9x9 棋盘 {MINES} 颗雷。输入坐标翻开，如 4 4；f 加旗，如 f 4 4。q退出。")
    board = None
    shown = [[False] * W for _ in range(H)]
    flagged = [[False] * W for _ in range(H)]
    first = True

    while True:
        print_board(board if board else [[0]*W for _ in range(H)], shown, flagged)
        cmd = input("开/旗(行 列)：").strip()
        if cmd.lower() in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        flag = False
        if cmd.startswith("f "):
            flag = True
            cmd = cmd[2:]
        parts = cmd.split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("格式：行 列 或 f 行 列。")
            continue
        r, c = int(parts[0]), int(parts[1])
        if not (0 <= r < H and 0 <= c < W):
            print(f"范围0~{H-1}。")
            continue
        if first:
            board = init_board(r, c)
            first = False
            reveal(board, shown, r, c)
            if all_non_mines_revealed(board, shown):
                print_board(board, shown, flagged)
                print("🎉 第一手就赢了！")
                return
            continue
        if flag:
            flagged[r][c] = not flagged[r][c]
            continue
        if flagged[r][c]:
            print("该格已插旗，先 f 取消。")
            continue
        if shown[r][c]:
            print("该格已翻开。")
            continue
        if board[r][c] == -1:
            print_board(board, [[True]*W for _ in range(H)], flagged)
            print("💥 踩到雷了！游戏结束。")
            return
        reveal(board, shown, r, c)
        if all_non_mines_revealed(board, shown):
            print_board(board, shown, flagged)
            print("🎉 排除了所有雷，你赢了！")
            return


if __name__ == "__main__":
    main()
