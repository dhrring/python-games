# -*- coding: utf-8 -*-
"""
二进制猜生日（数学魔术）
========================
你只回答 5 个「是 / 否」，我就能算出你心里想的 1~31 之间的一个数字
（可以当成「猜你的生日是几号」来玩）。
原理：1~31 都能写成 5 位二进制，第 k 张卡片上放的是「二进制第 k 位为 1」
的所有数字。你说「在」，就把该卡片的基数加上去，加完正好是这个数。
纯标准库实现。

游玩方法：
  1. 在心里想一个 1~31 的整数（或生日的「日」）；
  2. 程序逐张显示 5 张卡片，你输入 y 表示这个数在卡片上，n 表示不在；
  3. 程序立刻说出答案，并展示二进制原理。
  输入 q 可随时退出。
运行：python3 2026-11-09_二进制猜生日.py
"""

MAX_NUM = 31
BITS = 5

CARDS = [[n for n in range(1, MAX_NUM + 1) if (n >> k) & 1] for k in range(BITS)]


def show_card(card, idx):
    print(f"\n—— 第 {idx + 1} 张卡片 ——")
    # 每行 6 个数，排整齐
    for i in range(0, len(card), 6):
        print("   " + "  ".join(f"{n:2d}" for n in card[i:i + 6]))
    print(f"   （这张卡片共 {len(card)} 个数）")


def ask_yes_no(prompt):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("y", "yes", "是", "1"):
            return True
        if raw in ("n", "no", "否", "0"):
            return False
        if raw in ("q", "quit", "exit"):
            return None
        print("请输入 y（在）/ n（不在）。")


def main():
    print("=" * 50)
    print("        🎩 二进制猜生日 Binary Magic")
    print("=" * 50)
    print("在心里想一个 1~31 的数字（比如你生日的「日」），别告诉我。")
    print("我会给你看 5 张卡片，你只要回答这个数在不在卡片上。")
    print("（y = 在，n = 不在，q = 退出）")

    guess = 0
    bits = []
    for k in range(BITS):
        show_card(CARDS[k], k)
        ans = ask_yes_no(f"你想的数在第 {k + 1} 张卡片上吗？(y/n)：")
        if ans is None:
            print("你已退出。")
            return
        bits.append(1 if ans else 0)
        if ans:
            guess += 1 << k

    print("\n" + "=" * 50)
    if guess == 0:
        print("你没有选中任何卡片……这个数应该是 0 或者不在 1~31 范围内。")
        print("=" * 50)
        return
    print(f"        ✨ 你想的数是：{guess}")
    print("=" * 50)
    print("\n原理：每张卡片对应二进制的一位（1 / 2 / 4 / 8 / 16）")
    for k in range(BITS):
        mark = "✔ 加" if bits[k] else "  跳过"
        print(f"  第 {k + 1} 张卡（权值 {1 << k:2d}）：{mark}")
    expr = " + ".join(str(1 << k) for k in range(BITS) if bits[k]) or "0"
    bstr = "".join(str(bits[k]) for k in reversed(range(BITS)))
    print(f"\n  {expr} = {guess}，二进制写作 {bstr}")
    print("  所以只要知道「哪几位是 1」，就能唯一还原这个数。")


if __name__ == "__main__":
    main()
