# -*- coding: utf-8 -*-
"""
猜单词（Word Guess / 猜成语）
============================
一个中文成语 + 英语单词混合的猜词游戏。
每一轮会显示字母/汉字长度与已猜对的字符位置，限定的错误次数内猜出即获胜。
纯标准库实现：python3 2026-10-24_猜单词.py
"""

import random

# 词库：每个条目是 (提示分类, 答案字符串)
WORDS = [
    ("成语", "一帆风顺"),
    ("成语", "画蛇添足"),
    ("成语", "亡羊补牢"),
    ("成语", "守株待兔"),
    ("成语", "井底之蛙"),
    ("英文", "python"),
    ("英文", "github"),
    ("英文", "algorithm"),
    ("英文", "keyboard"),
    ("英文", "sunshine"),
]

MAX_WRONG = 6  # 允许猜错的最大次数


def display_state(word: str, revealed: list, wrongs: int):
    """打印当前已知字符与错误次数"""
    shown = " ".join(revealed)
    print(f"\n当前进度：{shown}")
    print(f"已猜错 {wrongs}/{MAX_WRONG} 次")


def play_one(word: str, category: str):
    revealed = ["_" if ch.isalnum() else ch for ch in word]
    guessed = set()
    wrongs = 0
    print(f"\n本次题目分类：{category}，共 {len(word)} 个字符。")

    while "_" in revealed and wrongs < MAX_WRONG:
        display_state(word, revealed, wrongs)
        guess = input("猜一个字符（输入单个汉字或字母）：").strip().lower()
        if len(guess) != 1:
            print("请输入单个字符。")
            continue
        if guess in guessed:
            print("这个字符你已经猜过了。")
            continue
        guessed.add(guess)
        hit = False
        for i, ch in enumerate(word.lower()):
            if ch == guess:
                revealed[i] = word[i]
                hit = True
        if hit:
            print(f"✅ 猜对了！出现了字符“{guess}”。")
        else:
            wrongs += 1
            print(f"❌ 没有这个字符，错误次数 +1。")

    if "_" not in revealed:
        print(f"\n🎉 恭喜你猜出了完整答案：{word}")
        return True
    else:
        print(f"\n😢 很遗憾，答案是：{word}")
        return False


def main():
    print("=" * 40)
    print("        🧩 猜单词 / 猜成语")
    print("=" * 40)
    score = 0
    total = 5
    for _ in range(total):
        category, word = random.choice(WORDS)
        if play_one(word, category):
            score += 1
    print("=" * 40)
    print(f"本轮结束：答对 {score}/{total} 题。")
    again = input("是否再来一轮？(y/n)：").strip().lower()
    if again in ("y", "yes", "是"):
        main()


if __name__ == "__main__":
    main()
