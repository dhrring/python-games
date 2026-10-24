# -*- coding: utf-8 -*-
"""
井字棋（Tic-Tac-Toe）
=====================
经典 3x3 井字棋，支持：
  玩家 vs 玩家（双人同机对战）
  玩家 vs 电脑（简单 AI：优先赢、其次堵、再走中间/角落）
纯标准库实现：python3 2026-10-24_井字棋.py
"""

EMPTY = "."
PLAYER_X = "X"
PLAYER_O = "O"


def print_board(board):
    print("\n  1 2 3")
    for r in range(3):
        print(f"{r+1} " + " ".join(board[r * 3:(r + 1) * 3]))


def check_winner(board):
    """返回获胜者字符或 None"""
    lines = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 行
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 列
        [0, 4, 8], [2, 4, 6],             # 对角
    ]
    for a, b, c in lines:
        if board[a] == board[b] == board[c] and board[a] != EMPTY:
            return board[a]
    return None


def board_full(board):
    return EMPTY not in board


def available_moves(board):
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def ai_move(board, ai_char):
    """简单 AI：赢 > 堵 > 中 > 角 > 边"""
    human_char = PLAYER_X if ai_char == PLAYER_O else PLAYER_O
    # 1. 自己能赢就赢
    for m in available_moves(board):
        tmp = board[:]; tmp[m] = ai_char
        if check_winner(tmp) == ai_char:
            return m
    # 2. 堵住对手
    for m in available_moves(board):
        tmp = board[:]; tmp[m] = human_char
        if check_winner(tmp) == human_char:
            return m
    # 3. 中心
    if board[4] == EMPTY:
        return 4
    # 4. 角落
    corners = [0, 2, 6, 8]
    for c in corners:
        if board[c] == EMPTY:
            return c
    # 5. 任意可用
    return available_moves(board)[0]


def human_move(board, char):
    while True:
        try:
            cell = int(input(f"玩家 {char}，请输入位置(1-9，左上到右下)："))
            if cell < 1 or cell > 9:
                print("位置需在 1~9 之间。")
                continue
            idx = cell - 1
            if board[idx] != EMPTY:
                print("这个位置已被占用。")
                continue
            return idx
        except ValueError:
            print("请输入数字 1-9。")


def play(board, is_ai, ai_char):
    turn = 0
    while True:
        print_board(board)
        current = PLAYER_X if turn % 2 == 0 else PLAYER_O
        if is_ai and current == ai_char:
            idx = ai_move(board, ai_char)
            print(f"电脑选择位置 {idx + 1}")
        else:
            idx = human_move(board, current)
        board[idx] = current
        winner = check_winner(board)
        if winner:
            print_board(board)
            print(f"🏆 玩家 {winner} 获胜！")
            return
        if board_full(board):
            print_board(board)
            print("🤝 平局！")
            return
        turn += 1


def main():
    print("=" * 40)
    print("        ⭕ 井字棋 Tic-Tac-Toe")
    print("=" * 40)
    board = [EMPTY] * 9
    mode = input("选择模式：1) 双人对战  2) 人机对战（你执 X）：").strip()
    if mode == "1":
        play(board, is_ai=False, ai_char=None)
    else:
        play(board, is_ai=True, ai_char=PLAYER_O)


if __name__ == "__main__":
    main()
