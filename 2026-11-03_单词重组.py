# -*- coding: utf-8 -*-
"""
单词重组（Anagram Quiz）
=========================
给出一个打乱字母的英文单词及其中文释义，猜出正确的英文单词。
共 10 题，输入 'q' 提前结束，最后统计正确率。纯标准库实现。
运行：python3 2026-11-03_单词重组.py
"""

import random

WORDS = {
    "apple": "苹果", "banana": "香蕉", "orange": "橙子", "grape": "葡萄",
    "lemon": "柠檬", "melon": "甜瓜", "water": "水", "bread": "面包",
    "milk": "牛奶", "sugar": "糖", "chair": "椅子", "table": "桌子",
    "window": "窗户", "school": "学校", "student": "学生", "teacher": "老师",
    "pencil": "铅笔", "paper": "纸", "book": "书", "house": "房子",
    "river": "河流", "mountain": "山", "flower": "花", "animal": "动物",
    "music": "音乐", "color": "颜色", "number": "数字", "family": "家庭",
}


def shuffle(word):
    chars = list(word)
    while chars == list(word):
        random.shuffle(chars)
    return "".join(chars)


def main():
    print("=" * 44)
    print("        🔤 单词重组 Anagram Quiz")
    print("=" * 44)
    print("根据打乱的字母和中文释义，拼出正确的英文单词。")
    print("输入 'q' 提前结束。")

    words = list(WORDS.keys())
    random.shuffle(words)
    correct = 0
    total = min(10, len(words))
    for i in range(total):
        word = words[i]
        scrambled = shuffle(word)
        print(f"\n第 {i+1}/{total} 题：{scrambled}  （{WORDS[word]}）")
        got = input("你的答案：").strip().lower()
        if got in ("q", "quit", "exit"):
            print("提前结束。")
            total = i
            break
        if got == word:
            correct += 1
            print("✅ 正确！")
        else:
            print(f"❌ 错误，正确答案：{word}")

    if total == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / total * 100
    print("\n" + "=" * 44)
    print(f"        结果：{correct}/{total}  正确率 {acc:.1f}%")
    print("=" * 44)
    if acc == 100:
        print("🏆 满分！词汇达人！")
    elif acc >= 70:
        print("👍 很棒，继续加油！")
    else:
        print("💪 多背单词，下次更好！")


if __name__ == "__main__":
    main()
