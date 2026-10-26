# -*- coding: utf-8 -*-
"""
珠玑妙算（Mastermind / 猜四位数字）
=================================
经典逻辑推理游戏：电脑想一个不重复的 4 位数字（每位 1~9），
你猜数字，电脑反馈「几 A 几 B」（A=位置和数字都对，B=数字对但位置不对）。
纯标准库实现，可直接运行：python3 2026-10-26_珠玑妙算.py
"""

import random


def generate_secret():
    digits = list("123456789")
    random.shuffle(digits)
    return digits[:4]


def evaluate(secret, guess):
    """返回 (A, B)：A=数字位置都对，B=数字对位置错"""
    a = sum(1 for s, g in zip(secret, guess) if s == g)
    b = sum(1 for g in guess if g in secret) - a
    return a, b


def main():
    print("=" * 40)
    print("        🔐 珠玑妙算 Mastermind")
    print("=" * 40)
    print("电脑想了一个不重复的4位数字（每位1~9）。")
    print("你每次猜4个数字，反馈 X A Y B（A=位置对，B=数字对但位置错）。")
    secret = generate_secret()
    attempts = 0

    while True:
        attempts += 1
        guess = input(f"[第{attempts}次] 猜一个4位不重复数字（1~9，如 1234）：").strip()
        if guess.lower() in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if len(guess) != 4 or not guess.isdigit():
            print("请输入4位数字。")
            continue
        if len(set(guess)) != 4:
            print("数字不能重复。")
            continue
        if any(d == "0" for d in guess):
            print("每位是1~9，不能含0。")
            continue
        a, b = evaluate(secret, list(guess))
        print(f"        → {a}A {b}B")
        if a == 4:
            print(f"🎉 猜中了！答案是 {''.join(secret)}，共用了 {attempts} 次。")
            return


if __name__ == "__main__":
    main()
