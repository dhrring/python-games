# -*- coding: utf-8 -*-
"""
电脑猜数字（Reverse Guess）
============================
你心里想一个 1~100 的整数，电脑用二分法猜。
你只需回答 大 / 小 / 对，电脑会在 log2(100)≈7 次内猜中。纯标准库实现。
运行：python3 2026-11-01_电脑猜数字.py
"""


def main():
    print("=" * 42)
    print("        🤖 电脑猜数字 Reverse Guess")
    print("=" * 42)
    print("想一个 1~100 的整数，电脑来猜。")
    print("猜的数：回答 '大' 表示你心中的数更大，'小' 表示更小，'对' 表示猜中。")
    print("输入 'q' 退出。")

    low, high = 1, 100
    tries = 0
    while low <= high:
        mid = (low + high) // 2
        tries += 1
        print(f"\n第 {tries} 次：电脑猜 {mid}")
        ans = input("(大/小/对)：").strip().lower()
        if ans in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if ans == "对":
            print(f"🎉 电脑第 {tries} 次猜中了你心里的数字 {mid}！")
            return
        if ans == "大":
            low = mid + 1
        elif ans == "小":
            high = mid - 1
        else:
            print("请输入 大/小/对。")
            tries -= 1
            continue
    print("😅 你说的小/大与之前矛盾，电脑找不到这个数了。请重新开始。")


if __name__ == "__main__":
    main()
