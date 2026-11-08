# -*- coding: utf-8 -*-
"""
四子棋（Connect 4）
====================
7 列 × 6 行的竖立棋盘，棋子从顶部投入、落到该列最低的空位。
谁先在同一行、同一列或同一斜线上连成 4 个同色棋子谁获胜，棋盘填满则平局。
你执红 X，电脑执黄 O，你先手。
纯标准库实现。

电脑策略：能四连就四连 → 挡你的四连 → 否则按中心优先打分选列。

游玩方法：
  输入列号 1~7 落子，例如 4 表示棋子落到第 4 列；
  输入 s 查看棋盘，q 退出。
运行：python3 2026-11-08_四子棋.py
"""

ROWS = 6
COLS = 7
EMPTY = "·"
RED = "X"
YELLOW = "O"
WIN = 4
CENTERS = [3, 2, 4, 1, 5, 0, 6]


def new_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]


def drop(board, col, color):
    """在 col 列落子，返回落点行号；列满返回 None。"""
    if not (0 <= col < COLS):
        return None
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == EMPTY:
            board[r][col] = color
            return r
    return None


def remove_top(board, col):
    for r in range(ROWS):
        if board[r][col] != EMPTY:
            board[r][col] = EMPTY
            return


def check_win(board, color):
    """返回是否已有 4 连。"""
    dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != color:
                continue
            for dr, dc in dirs:
                cnt = 0
                rr, cc = r, c
                while 0 <= rr < ROWS and 0 <= cc < COLS and board[rr][cc] == color:
                    cnt += 1
                    if cnt >= WIN:
                        return True
                    rr, cc = rr + dr, cc + dc
    return False


def col_free(board, col):
    return board[0][col] == EMPTY


def draw(board):
    print("\n  1 2 3 4 5 6 7")
    for r in range(ROWS):
        print("  " + " ".join(board[r]))
    print("  " + " ".join(str(i) for i in range(1, COLS + 1)) + "  ← 列号")


def ai_choose(board, me, opp):
    """1) 自己能赢；2) 挡对手；3) 中心优先打分。"""
    free = [c for c in range(COLS) if col_free(board, c)]
    if not free:
        return None
    # 1. 直接获胜
    for c in free:
        r = drop(board, c, me)
        win = check_win(board, me)
        remove_top(board, c)
        if win:
            return c
    # 2. 阻挡对手
    for c in free:
        r = drop(board, c, opp)
        win = check_win(board, opp)
        remove_top(board, c)
        if win:
            return c
    # 3. 启发式：靠近中心 + 该列已有同色棋子
    best, best_score = None, -1
    for c in free:
        score = 10 - abs(3 - c)
        for r in range(ROWS - 1, -1, -1):
            if board[r][c] == me:
                score += 2
            elif board[r][c] == opp:
                score -= 1
            else:
                break
        score += 0.5 - 0.1 * CENTERS.index(c)
        if score > best_score:
            best, best_score = c, score
    return best


def main():
    print("=" * 46)
    print("        🔴🟡 四子棋 Connect 4")
    print("=" * 46)
    print("你执 X 先手，从顶部投子，先连成 4 个同色棋子者胜。")
    print("输入列号 1~7 落子，s 看棋盘，q 退出。")

    board = new_board()
    turn = RED
    moves = 0

    while True:
        draw(board)
        if turn == RED:
            free = [c for c in range(COLS) if col_free(board, c)]
            if not free:
                break
            print("你可选的列：" + "、".join(str(c + 1) for c in free))
            raw = input("请选择列号：").strip().lower()
            if raw in ("q", "quit", "exit"):
                print("你已退出对局。")
                return
            if raw == "s":
                continue
            if not raw.isdigit() or int(raw) - 1 not in free:
                print("请输入可选的列号（1~7 中尚未填满的列）。")
                continue
            col = int(raw) - 1
            r = drop(board, col, RED)
            moves += 1
            print(f"你落子：第 {col + 1} 列，第 {ROWS - r} 行（自下往上）。")
            if check_win(board, RED):
                draw(board)
                print("\n" + "=" * 46)
                print("🎉 你连成四子，赢了！")
                print("=" * 46)
                return
            turn = YELLOW
        else:
            col = ai_choose(board, YELLOW, RED)
            if col is None:
                break
            r = drop(board, col, YELLOW)
            moves += 1
            print(f"电脑落子：第 {col + 1} 列。")
            if check_win(board, YELLOW):
                draw(board)
                print("\n" + "=" * 46)
                print("😢 电脑连成四子，你输了。")
                print("=" * 46)
                return
            turn = RED

        if moves >= ROWS * COLS:
            break

    draw(board)
    print("\n" + "=" * 46)
    print("🤝 棋盘填满，平局！")
    print("=" * 46)


if __name__ == "__main__":
    main()
