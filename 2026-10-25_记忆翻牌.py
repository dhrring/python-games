# -*- coding: utf-8 -*-
"""
记忆翻牌（Memory Match）
=======================
经典翻牌记忆配对游戏：4x4 共 16 张牌，8 对图案，轮流翻牌，全部配对完成即胜利。
纯标准库实现，可直接运行：python3 2026-10-25_记忆翻牌.py
"""

import random

SIZE = 4
PAIRS = SIZE * SIZE // 2
SYMBOLS = ["🍎", "🍌", "🍇", "🍉", "🍓", "🥝", "🍑", "🍒"]


def new_board():
    cards = SYMBOLS[:PAIRS] * 2
    random.shuffle(cards)
    return cards


def display(cards, revealed):
    print("\n    1  2  3  4")
    for r in range(SIZE):
        row = [f"{r+1}"]
        for c in range(SIZE):
            i = r * SIZE + c
            row.append(cards[i] if revealed[i] else "▢")
        print("  ".join(row))


def main():
    print("=" * 40)
    print("        🧠 记忆翻牌 Memory Match")
    print("=" * 40)
    cards = new_board()
    revealed = [False] * (SIZE * SIZE)
    matched = set()
    attempts = 0

    while len(matched) < PAIRS:
        display(cards, revealed)
        print(f"\n已配对 {len(matched)}/{PAIRS} 对，尝试次数 {attempts}")
        picks = []
        for turn in range(2):
            while True:
                try:
                    pos = input(f"选择第{turn+1}张牌（行列，如 12 表示第1行第2列）：").strip()
                    if len(pos) != 2 or not pos.isdigit():
                        print("请输入两位数字，如 12。")
                        continue
                    r, c = int(pos[0]) - 1, int(pos[1]) - 1
                    i = r * SIZE + c
                    if r < 0 or c < 0 or i >= SIZE * SIZE:
                        print("位置超出范围。")
                        continue
                    if revealed[i]:
                        print("这张牌已翻开，换一张。")
                        continue
                    revealed[i] = True
                    picks.append(i)
                    display(cards, revealed)
                    break
                except Exception:
                    print("输入无效。")
        attempts += 1
        a, b = picks
        if cards[a] == cards[b]:
            matched.add(cards[a])
            print(f"✅ 配对成功！{cards[a]} {cards[b]}")
        else:
            print(f"❌ 不匹配（{cards[a]} 和 {cards[b]}），记一下位置。")
            revealed[a] = revealed[b] = False

    display(cards, revealed)
    print("\n" + "=" * 40)
    print(f"🎉 全部配对完成！共用了 {attempts} 次尝试。")


if __name__ == "__main__":
    main()
