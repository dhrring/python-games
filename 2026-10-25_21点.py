# -*- coding: utf-8 -*-
"""
21点（Blackjack）
================
经典 21 点纸牌游戏，你和电脑各执一手牌，目标是点数尽量接近 21 且不超过 21。
A 计 1 或 11，J/Q/K 计 10，其余按面值。
纯标准库实现，可直接运行：python3 2026-10-25_21点.py
"""

import random

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["♠", "♥", "♦", "♣"]


def new_deck():
    return [(rank, suit) for suit in SUITS for rank in RANKS]


def hand_value(hand):
    """计算一手牌的点数（A 自适应）"""
    value = 0
    aces = 0
    for rank, _ in hand:
        if rank == "A":
            aces += 1
            value += 11
        elif rank in ("J", "Q", "K"):
            value += 10
        else:
            value += int(rank)
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value


def show(hand):
    return " ".join(f"{rank}{suit}" for rank, suit in hand)


def main():
    print("=" * 40)
    print("        🃏 21 点 Blackjack")
    print("=" * 40)
    deck = new_deck()
    random.shuffle(deck)
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]

    print(f"\n你的牌：{show(player)}  （点数 {hand_value(player)}）")
    print(f"庄家明牌：{show(dealer[:1])}")

    # 玩家回合
    while hand_value(player) < 21:
        action = input("要牌(h) 还是 停牌(s)？").strip().lower()
        if action in ("h", "hit", "要"):
            player.append(deck.pop())
            print(f"你抽到 {player[-1][0]}{player[-1][1]}，现在 {show(player)}（{hand_value(player)}）")
            if hand_value(player) > 21:
                print("💥 爆了！点数超过 21。")
                print("你输了。庄家获胜。")
                return
        elif action in ("s", "stand", "停"):
            break
        else:
            print("请输入 h（要牌）或 s（停牌）。")

    # 庄家回合：至少 17 点
    print(f"\n庄家翻开：{show(dealer)}（{hand_value(dealer)}）")
    while hand_value(dealer) < 17:
        dealer.append(deck.pop())
        print(f"庄家要牌，现在 {show(dealer)}（{hand_value(dealer)}）")

    pv, dv = hand_value(player), hand_value(dealer)
    print("\n" + "=" * 40)
    print(f"你的点数：{pv}    庄家点数：{dv}")
    if dv > 21 or pv > dv:
        print("🎉 你赢了！")
    elif pv < dv:
        print("😢 庄家赢了。")
    else:
        print("🤝 平局。")


if __name__ == "__main__":
    main()
