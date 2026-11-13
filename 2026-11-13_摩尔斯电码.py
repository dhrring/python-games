# -*- coding: utf-8 -*-
"""
摩尔斯电码训练营（6 关 · 双向训练：先译码，再编码）
====================================================
电报时代的 SOS 只有三个点三个划，但真正收发报的人要背下 36 个符号。
这个游戏让你两边都练：

  译码关：屏幕给你一串摩尔斯码，你把它还原成文字。
  编码关：屏幕给你一段文字，你把它写成摩尔斯码。

摩尔斯码书写约定（本游戏通用）：
  一个字母内部的点划连写，例如 A 是 .-
  字母与字母之间用 1 个空格分隔
  单词与单词之间用 / 分隔
  数字与字母同一套规则

游戏内命令：
  hint   看提示（本题扣 30 分）
  table  查摩尔斯速查表（不扣分，但会一直显示在屏幕上）
  skip   跳过本题（本题 0 分）
  q      退出

计分：每题基准 100 分，看提示 −30，答错一次 −10（保底 20 分）。
运行：python3 2026-11-13_摩尔斯电码.py
"""

import random

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
}
REVERSE = {v: k for k, v in MORSE.items()}


def encode(text):
    words = text.upper().split()
    return ' / '.join(' '.join(MORSE.get(ch, '') for ch in w if ch in MORSE) for w in words)


def decode(code):
    out_words = []
    for word in code.strip().split('/'):
        letters = []
        for token in word.split():
            if token not in REVERSE:
                return None
            letters.append(REVERSE[token])
        out_words.append(''.join(letters))
    return ' '.join(out_words) if out_words and all(out_words) else None


def show_table():
    print("\n  摩尔斯速查表")
    items = list(MORSE.items())
    for i in range(0, len(items), 4):
        row = items[i:i + 4]
        print("   " + "   ".join(f"{k}={v}" for k, v in row))


def normalize_answer(s):
    return ' '.join(s.upper().split()).replace(' / ', '/').replace('/ ', '/').replace(' /', '/')


LEVELS = [
    {"kind": "decode", "prompt": "SOS", "hint": "最著名的求救信号：三个点、三个划、三个点。"},
    {"kind": "decode", "prompt": "HELLO", "hint": "第一个字母是 H（四个点）。"},
    {"kind": "encode", "prompt": "PYTHON", "hint": "P 是 .--.，Y 是 -.--，注意每个字母之间要加空格。"},
    {"kind": "decode", "prompt": "2026 NOV", "hint": "数字是五个符号一组，单词之间记得用 / 。"},
    {"kind": "encode", "prompt": "GITHUB GAME", "hint": "两个单词之间用 / 分隔。"},
    {"kind": "decode", "prompt": "KEEP CODING", "hint": "第一个 K 是 -.-，最后一个 G 是 --."},
]


def play():
    print("=" * 62)
    print("      📡 摩尔斯电码训练营")
    print("=" * 62)
    print("六道题：前三道译码、后三道编码。输入 table 可以看速查表。")
    total = 0
    correct_count = 0

    for idx, lv in enumerate(LEVELS, 1):
        text = lv["prompt"]
        score = 100
        print("\n" + "-" * 62)
        if lv["kind"] == "decode":
            print(f"  第 {idx} 关 · 译码")
            print(f"  摩尔斯码：{encode(text)}")
            print("  请还原成文字（字母之间可直接连着写）：")
        else:
            print(f"  第 {idx} 关 · 编码")
            print(f"  原文：{text}")
            print("  请写成摩尔斯码（字母间 1 个空格，单词间用 / ）：")

        tries = 0
        while True:
            try:
                raw = input("  > ").strip()
            except EOFError:
                print("\n输入中断，提前结束。")
                return summary(total, correct_count)
            low = raw.lower()
            if low in ("q", "quit", "exit"):
                print("\n你放下电报机走了。")
                return summary(total, correct_count)
            if low == "table":
                show_table()
                continue
            if low == "hint":
                if score > 30:
                    score -= 30
                print(f"  提示：{lv['hint']}（本题剩 {score} 分）")
                continue
            if low == "skip":
                print("  跳过，本题 0 分。答案：" + (encode(text) if lv["kind"] == "decode" else text))
                score = 0
                break

            if lv["kind"] == "decode":
                answer = raw.upper().replace(' ', '')
                expect = text.replace(' ', '')
                ok = answer == expect
            else:
                ok = normalize_answer(raw) == normalize_answer(encode(text))

            if ok:
                print(f"  ✅ 正确！本题得 {score} 分")
                total += score
                correct_count += 1
                break
            else:
                tries += 1
                if score >= 30:
                    score -= 10
                print(f"  ❌ 不对。再想想（本题剩 {score} 分，已答错 {tries} 次）")
                if tries >= 3:
                    ans = encode(text) if lv["kind"] == "decode" else text
                    print(f"  三次机会用完了，正确答案：{ans}")
                    total += score
                    break

    return summary(total, correct_count)


def summary(total, correct):
    print("\n" + "=" * 62)
    print(f"  训练结束：答对 {correct}/{len(LEVELS)} 题，总分 {total}/{len(LEVELS) * 100}")
    if total >= 560:
        print("  🏆 一级报务员：36 个符号已经刻在脑子里了。")
    elif total >= 420:
        print("  👍 熟练，复杂码的边界再练练。")
    elif total >= 250:
        print("  🙂 入门了，建议先背 E T A O I N（英文里出现频率最高的六个字母）。")
    else:
        print("  😅 建议从「E=. T=- A=.- N=-.」这四个开始，它们是摩尔斯码的骨架。")
    print("=" * 62)
    return total


if __name__ == "__main__":
    play()
