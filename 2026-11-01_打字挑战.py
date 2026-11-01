# -*- coding: utf-8 -*-
"""
打字挑战（Typing Challenge）
============================
随机出英文单词，尽快输入并回车。每轮记录正确与否、耗时，
最终统计正确率与打字速度（字符/分钟）。纯标准库实现。
运行：python3 2026-11-01_打字挑战.py
"""

import random
import time

WORDS = [
    "python", "banana", "computer", "keyboard", "window", "garden",
    "mountain", "river", "star", "cloud", "ocean", "school",
    "house", "apple", "orange", "monkey", "tiger", "dragon",
    "pencil", "bottle", "bicycle", "train", "rabbit", "music",
    "sunshine", "rainbow", "forest", "castle", "island", "winter",
]


def main():
    print("=" * 42)
    print("        ⌨️  打字挑战 Typing Challenge")
    print("=" * 42)
    print("随机显示单词，输入后回车。输入 'q' 提前结束。")
    n = int(input("想挑战几个单词？(默认10)：").strip() or "10")
    n = max(1, min(50, n))

    correct = 0
    total_chars = 0
    total_time = 0.0
    for i in range(1, n + 1):
        word = random.choice(WORDS)
        print(f"\n第 {i}/{n} 题  请输入: {word}")
        t0 = time.time()
        ans = input("你的输入：").strip()
        dt = time.time() - t0
        total_time += dt
        if ans.lower() in ("q", "quit", "exit"):
            print("提前结束。")
            n = i - 1
            break
        total_chars += len(word)
        if ans == word:
            correct += 1
            print(f"✅ 正确！用时 {dt:.2f}s")
        else:
            print(f"❌ 错误！正确应为: {word}")

    if n == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / n * 100
    cpm = total_chars / total_time * 60 if total_time > 0 else 0
    print("\n" + "=" * 42)
    print("        统计结果")
    print("=" * 42)
    print(f"完成题目：{correct}/{n}")
    print(f"正确率：{acc:.1f}%")
    print(f"总输入量：{total_chars} 字符")
    print(f"打字速度：约 {cpm:.0f} 字符/分钟")
    if acc == 100:
        print("🎉 完美！全对！")
    elif acc >= 80:
        print("👍 表现不错，继续加油！")
    else:
        print("💪 多练习，你会更快的！")


if __name__ == "__main__":
    main()
