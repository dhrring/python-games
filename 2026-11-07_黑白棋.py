# -*- coding: utf-8 -*-
"""
黑白棋（Reversi / Othello）
============================
8×8 棋盘，你执黑（X）先手，电脑执白（O）。
在一条直线上夹住对方的棋子即可把中间全部翻成自己的颜色。
双方都无法落子时游戏结束，子多者胜。
纯标准库实现。
游玩方法：
  输入两个数字「行 列」（均为 1~8，如 3 4 表示第 3 行第 4 列）落子；
  输入 p 表示无棋可下（仅在你确实没有合法点时才允许）；
  输入 s 查看双方比分；输入 q 退出。
运行：python3 2026-11-07_黑白棋.py
"""

import random

SIZE = 8
EMPTY = "·"
BLACK = "X"
WHITE = "O"
DIRS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def new_board():
    b = [[EMPTY] * SIZE for _ in range(SIZE)]
    b[3][3] = WHITE
    b[4][4] = WHITE
    b[3][4] = BLACK
    b[4][3] = BLACK
    return b


def other(color):
    return WHITE if color == BLACK else BLACK


def in_board(r, c):
    return 0 <= r < SIZE and 0 <= c < SIZE


def flips_for(board, r, c, color):
    """若在 (r,c) 落 color 子，返回会被翻转的位置列表（空列表=非法落子）。"""
    if not in_board(r, c) or board[r][c] != EMPTY:
        return []
    opp = other(color)
    total = []
    for dr, dc in DIRS:
        line = []
        rr, cc = r + dr, c + dc
        while in_board(rr, cc) and board[rr][cc] == opp:
            line.append((rr, cc))
            rr, cc = rr + dr, cc + dc
        if line and in_board(rr, cc) and board[rr][cc] == color:
            total.extend(line)
    return total


def valid_moves(board, color):
    moves = []
    for r in range(SIZE):
        for c in range(SIZE):
            if flips_for(board, r, c, color):
                moves.append((r, c))
    return moves


def apply_move(board, r, c, color):
    flips = flips_for(board, r, c, color)
    if not flips:
        return 0
    board[r][c] = color
    for fr, fc in flips:
        board[fr][fc] = color
    return len(flips)


def score(board):
    b = sum(row.count(BLACK) for row in board)
    w = sum(row.count(WHITE) for row in board)
    return b, w


def draw(board):
    print("\n     " + " ".join(str(i + 1) for i in range(SIZE)))
    for r in range(SIZE):
        print(f"  {r + 1}  " + " ".join(board[r]))
    b, w = score(board)
    print(f"  黑(X) 你：{b}    白(O) 电脑：{w}")


def parse_input(text):
    parts = text.replace("，", " ").replace(",", " ").split()
    if len(parts) != 2:
        return None
    try:
        r = int(parts[0]) - 1
        c = int(parts[1]) - 1
    except ValueError:
        return None
    return (r, c) if in_board(r, c) else None


def ai_choose(board, color):
    """贪心：选翻转数最多的合法落子，同分随机。"""
    moves = valid_moves(board, color)
    if not moves:
        return None
    best, best_score = [], -1
    for r, c in moves:
        n = len(flips_for(board, r, c, color))
        if n > best_score:
            best, best_score = [(r, c)], n
        elif n == best_score:
            best.append((r, c))
    return random.choice(best)


def main():
    print("=" * 40)
    print("        ⚫⚪ 黑白棋 Reversi")
    print("=" * 40)
    print("你执黑 X 先手，电脑执白 O。夹住对方棋子即可翻转。")
    print("输入「行 列」落子（1~8），s 看比分，q 退出。")

    board = new_board()
    player_color, ai_color = BLACK, WHITE
    turn = BLACK
    passes = 0

    while True:
        b, w = score(board)
        if b + w == SIZE * SIZE:
            break
        if passes >= 2:
            break

        if turn == player_color:
            draw(board)
            moves = valid_moves(board, player_color)
            if not moves:
                print("⚠️ 你没有合法落子点，跳过一轮。")
                turn = ai_color
                passes += 1
                continue
            print("你的可选位置：" + "、".join(f"({r + 1},{c + 1})" for r, c in moves))
            raw = input("请落子：").strip()
            if raw.lower() in ("q", "quit", "exit"):
                print("你已退出对局。")
                return
            if raw.lower() == "s":
                print(f"当前比分 黑 {b} : 白 {w}")
                continue
            if raw.lower() == "p":
                print("你还有合法落子点，不能跳过。")
                continue
            pos = parse_input(raw)
            if pos is None:
                print("输入格式不对，请用「行 列」，例如 3 4。")
                continue
            flips = apply_move(board, pos[0], pos[1], player_color)
            if flips == 0:
                print("这里无法夹住对方棋子，换个位置吧。")
                continue
            print(f"你落子 ({pos[0] + 1},{pos[1] + 1})，翻转 {flips} 枚。")
            passes = 0
            turn = ai_color
        else:
            mv = ai_choose(board, ai_color)
            if mv is None:
                print("电脑没有合法落子点，跳过一轮。")
                turn = player_color
                passes += 1
                continue
            flips = apply_move(board, mv[0], mv[1], ai_color)
            print(f"电脑落子 ({mv[0] + 1},{mv[1] + 1})，翻转 {flips} 枚。")
            passes = 0
            turn = player_color

    draw(board)
    b, w = score(board)
    print("\n" + "=" * 40)
    if b > w:
        print(f"🏆 你赢了！黑 {b} : 白 {w}")
    elif b < w:
        print(f"😢 电脑赢了。黑 {b} : 白 {w}")
    else:
        print(f"🤝 平局！黑 {b} : 白 {w}")
    print("=" * 40)


if __name__ == "__main__":
    main()
