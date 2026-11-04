# -*- coding: utf-8 -*-
"""
战舰猎手（Battleship）
========================
经典海战猜位置游戏。电脑在 7x7 网格里秘密布下 3 艘战舰
（1 艘 3 格 + 2 艘 2 格），你输入坐标（如 A3、E5）进行攻击。
命中标 X，未中标 O，击沉全部战舰即为胜利。纯标准库实现。
运行：python3 2026-11-04_战舰猎手.py
"""

import random

SIZE = 7
COLS = "ABCDEFG"


def build_board():
    """随机布置战舰，返回 7x7 网格（0空 1舰）与舰船格数。"""
    board = [[0] * SIZE for _ in range(SIZE)]
    ships = [3, 2, 2]
    for length in ships:
        placed = False
        while not placed:
            horizontal = random.choice([True, False])
            if horizontal:
                r = random.randint(0, SIZE - 1)
                c = random.randint(0, SIZE - length)
            else:
                r = random.randint(0, SIZE - length)
                c = random.randint(0, SIZE - 1)
            cells = []
            if horizontal:
                cells = [(r, c + i) for i in range(length)]
            else:
                cells = [(r + i, c) for i in range(length)]
            if all(board[rr][cc] == 0 for rr, cc in cells):
                for rr, cc in cells:
                    board[rr][cc] = 1
                placed = True
    total = sum(sum(row) for row in board)
    return board, total


def parse_shot(s):
    """解析 'A3' 式坐标，返回 (行,列) 或 None。"""
    s = s.strip().upper()
    if len(s) < 2:
        return None
    col = s[0]
    if col not in COLS:
        return None
    try:
        row = int(s[1:]) - 1
    except ValueError:
        return None
    if not (0 <= row < SIZE):
        return None
    return row, COLS.index(col)


def main():
    print("=" * 46)
    print("        ⚓ 战舰猎手 Battleship")
    print("=" * 46)
    print(f"7x7 网格（列 A-G，行 1-7，如 A3）。电脑布置了 3 艘战舰。")
    print("输入坐标攻击，命中标 X，未中标 O，全部击沉即胜利。")
    print("输入 'q' 提前结束。\n")

    board, total = build_board()
    remaining = total
    hits = set()
    misses = set()
    attempts = 0

    print("   " + " ".join(COLS))
    for r in range(SIZE):
        print(f"{r+1:2d} " + " ".join("·" for _ in range(SIZE)))

    while remaining > 0:
        shot = input(f"\n剩余舰格 {remaining}，输入坐标：").strip()
        if shot.lower() in ("q", "quit", "exit"):
            print(f"你撤退了。正确答案网格上仍剩 {remaining} 格。")
            return
        pos = parse_shot(shot)
        if pos is None:
            print("格式错误，例：A3、E5。")
            continue
        r, c = pos
        attempts += 1
        if (r, c) in hits or (r, c) in misses:
            print("这个位置你已经攻击过了。")
            continue
        if board[r][c] == 1:
            print("💥 命中！")
            remaining -= 1
            hits.add((r, c))
        else:
            print("🌊 未中。")
            misses.add((r, c))
        # 重新打印网格：命中 X，未中 O，其余 ·
        print("   " + " ".join(COLS))
        for rr in range(SIZE):
            row = []
            for cc in range(SIZE):
                if (rr, cc) in hits:
                    row.append("X")
                elif (rr, cc) in misses:
                    row.append("O")
                else:
                    row.append("·")
            print(f"{rr+1:2d} " + " ".join(row))

    print(f"\n🏆 胜利！你在 {attempts} 次攻击内击沉了全部战舰！")


if __name__ == "__main__":
    main()
