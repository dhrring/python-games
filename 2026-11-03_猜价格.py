# -*- coding: utf-8 -*-
"""
猜价格（Guess the Price）
===========================
随机选一件商品，你猜它的价格（元），根据"高了/低了"提示，
在有限次数内猜中。价格区间随机生成。纯标准库实现。
运行：python3 2026-11-03_猜价格.py
"""

import random

ITEMS = [
    "一瓶矿泉水", "一杯奶茶", "一个汉堡", "一本练习册", "一双运动鞋",
    "一部智能手机", "一台笔记本电脑", "一辆自行车", "一张电影票",
    "一份外卖", "一个西瓜", "一斤鸡蛋",
]

PRICE_RANGES = {
    "一瓶矿泉水": (1, 10), "一杯奶茶": (8, 30), "一个汉堡": (10, 35),
    "一本练习册": (5, 25), "一双运动鞋": (100, 1000), "一部智能手机": (800, 8000),
    "一台笔记本电脑": (2000, 20000), "一辆自行车": (200, 3000),
    "一张电影票": (20, 100), "一份外卖": (15, 80), "一个西瓜": (5, 60),
    "一斤鸡蛋": (3, 15),
}


def main():
    print("=" * 44)
    print("        💰 猜价格 Guess the Price")
    print("=" * 44)
    print("随机商品，猜它的价格（整数元），根据高低提示逼近。")
    print("输入 'q' 提前结束。")

    item = random.choice(ITEMS)
    lo, hi = PRICE_RANGES[item]
    price = random.randint(lo, hi)
    max_guesses = 8

    print(f"\n商品：{item}")
    print(f"提示：价格在 {lo}~{hi} 元之间，你有 {max_guesses} 次机会。")

    for turn in range(1, max_guesses + 1):
        got = input(f"第{turn}次猜测：").strip()
        if got.lower() in ("q", "quit", "exit"):
            print(f"提前结束，答案是 {price} 元。")
            return
        try:
            g = int(got)
        except ValueError:
            print("请输入数字。")
            continue
        if g == price:
            print(f"🎉 猜中啦！{item} 就是 {price} 元，用了 {turn} 次。")
            if turn == 1:
                print("🏆 一击即中，运气爆棚！")
            return
        if turn == max_guesses:
            print(f"❌ 次数用完了，答案是 {price} 元。")
            return
        print("高了" if g > price else "低了")


if __name__ == "__main__":
    main()
