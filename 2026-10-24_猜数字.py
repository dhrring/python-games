# -*- coding: utf-8 -*-
"""
猜数字（Guess the Number）
======================
一个经典的双模式数字猜测游戏：
  模式1：玩家猜电脑想的数字
  模式2：电脑猜玩家想的数字（二分法）
纯标准库实现，可直接运行：python3 2026-10-24_猜数字.py
"""

import random


def player_guesses(max_val: int = 100):
    """玩家猜电脑想的数字"""
    answer = random.randint(1, max_val)
    attempts = 0
    print(f"我已经想好了一个 1~{max_val} 之间的数字，来猜猜看吧！")
    while True:
        attempts += 1
        try:
            guess = int(input(f"[第{attempts}次] 请输入你的猜测 (1~{max_val})："))
        except ValueError:
            print("请输入一个整数哦。")
            continue
        if guess < 1 or guess > max_val:
            print(f"范围在 1~{max_val} 之间，重新输入。")
            continue
        if guess < answer:
            print("太小了，再往上猜。")
        elif guess > answer:
            print("太大了，往下降一点。")
        else:
            print(f"🎉 恭喜！答案就是 {answer}，你用了 {attempts} 次猜中。")
            return attempts


def computer_guesses(max_val: int = 100):
    """电脑用二分法猜玩家想的数字"""
    low, high = 1, max_val
    attempts = 0
    print(f"请你心里想好一个 1~{max_val} 之间的数字，我来猜。")
    print("我每次猜完，请你输入：'大' 表示猜大了，'小' 表示猜小了，'对' 表示猜中了。")
    while low <= high:
        attempts += 1
        mid = (low + high) // 2
        print(f"[第{attempts}次] 我猜是 {mid}，对吗？")
        answer = input("请输入 大 / 小 / 对 ：").strip()
        if answer == "对":
            print(f"🎉 我猜中啦！你的数字是 {mid}，共猜了 {attempts} 次。")
            return attempts
        elif answer == "大":
            high = mid - 1
        elif answer == "小":
            low = mid + 1
        else:
            print("请输入'大''小''对'中的一个。")
            attempts -= 1
    print("你给我的提示有矛盾哦，可能记错数字了？")


def main():
    print("=" * 40)
    print("        🎯 猜数字游戏")
    print("=" * 40)
    print("请选择模式：")
    print("  1) 我来猜电脑的数字")
    print("  2) 电脑猜我的数字")
    choice = input("请输入 1 或 2：").strip()
    if choice == "1":
        player_guesses()
    elif choice == "2":
        computer_guesses()
    else:
        print("无效输入，默认进入模式1。")
        player_guesses()


if __name__ == "__main__":
    main()
