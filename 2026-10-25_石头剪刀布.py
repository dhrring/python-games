# -*- coding: utf-8 -*-
"""
石头剪刀布（Rock-Paper-Scissors）
================================
经典石头剪刀布，含计分与多轮对战。
纯标准库实现，可直接运行：python3 2026-10-25_石头剪刀布.py
"""

import random

CHOICES = {"石头": "✊", "剪刀": "✌️", "布": "🖐️"}
RULES = {("石头", "剪刀"): 1, ("剪刀", "布"): 1, ("布", "石头"): 1}


def judge(player, computer):
    """返回 1 玩家胜，-1 电脑胜，0 平局"""
    if player == computer:
        return 0
    if (player, computer) in RULES:
        return 1
    return -1


def main():
    print("=" * 40)
    print("        ✊ 石头剪刀布 ✌️")
    print("=" * 40)
    player_score = 0
    computer_score = 0
    rounds = 0
    while True:
        rounds += 1
        print(f"\n[第{rounds}局] 比分：你 {player_score} : {computer_score} 电脑")
        p = input("请出招（石头/剪刀/布，输入 q 退出）：").strip()
        if p.lower() in ("q", "quit", "exit"):
            break
        if p not in CHOICES:
            print("请输入 石头 / 剪刀 / 布。")
            continue
        c = random.choice(list(CHOICES))
        print(f"你出 {p} {CHOICES[p]}，电脑出 {c} {CHOICES[c]}")
        result = judge(p, c)
        if result == 1:
            player_score += 1
            print("🎉 你赢了！")
        elif result == -1:
            computer_score += 1
            print("😢 电脑赢了。")
        else:
            print("🤝 平局。")
    print("=" * 40)
    print(f"游戏结束：最终比分 你 {player_score} : {computer_score} 电脑（共 {rounds} 局）")
    if player_score > computer_score:
        print("🏆 总冠军：你！")
    elif player_score < computer_score:
        print("总冠军：电脑。再接再厉！")
    else:
        print("平局收官。")


if __name__ == "__main__":
    main()
