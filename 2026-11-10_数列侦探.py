# -*- coding: utf-8 -*-
"""
数列侦探（找规律填下一项）
============================
给你一串按某种规律排列的数字，找出规律并写出下一项。
每题有 2 次机会，答对得 100 分（第二次才答对得 60 分），答错会给出解析。
规律涵盖：等差、等比、平方、立方、质数、斐波那契、三角数、阶乘、
         交错序列、递增差等。

游玩方法：
  按题目提示输入下一个数（整数即可），输入 skip 跳过，q 退出。
  答完后会给出该题的规律解析，共 10 题。
运行：python3 2026-11-10_数列侦探.py
"""

import math

# (数列前若干项, 正确答案, 规律解析, 难度)
PUZZLES = [
    ([2, 4, 8, 16], 32, "等比数列，每项 ×2。", "★"),
    ([1, 4, 9, 16], 25, "平方数：1², 2², 3², 4², 下一项 5²=25。", "★"),
    ([4, 7, 10, 13], 16, "等差数列，公差 +3。", "★"),
    ([1, 1, 2, 3, 5, 8], 13, "斐波那契：后一项 = 前两项之和。", "★★"),
    ([2, 3, 5, 7, 11], 13, "质数序列：2,3,5,7,11 之后是 13。", "★★"),
    ([1, 3, 6, 10, 15], 21, "三角数：+2, +3, +4, +5, 下一项 +6 → 21。", "★★"),
    ([3, 7, 15, 31], 63, "每项 ×2 +1（即 2ⁿ⁺¹−1）：31×2+1=63。", "★★"),
    ([5, 8, 14, 23], 35, "相邻差为 +3, +6, +9, 下一差 +12 → 35。", "★★★"),
    ([1, 8, 27, 64], 125, "立方数：1³,2³,3³,4³，下一项 5³=125。", "★★★"),
    ([2, 6, 12, 20, 30], 42, "n(n+1)：1×2,2×3,3×4,4×5,5×6，下一项 6×7=42。", "★★★"),
    ([1, 2, 6, 24, 120], 720, "阶乘：1!,2!,3!,4!,5!，下一项 6! = 720。", "★★★"),
    ([81, 27, 9, 3], 1, "每项 ÷3，3÷3=1。", "★★"),
]


def check_answer(raw):
    """允许输入整数或小数（如 12.5），返回 (是否合法, 数值)。"""
    try:
        v = float(raw)
    except ValueError:
        return False, None
    if v != int(v):
        return True, v
    return True, int(v)


def main():
    print("=" * 52)
    print("      🔍 数列侦探 Number Sequence Detective")
    print("=" * 52)
    print(f"共 {len(PUZZLES)} 题。规律可能藏在差、比、平方、质数、阶乘里。")

    total = 0
    correct = 0
    for i, (seq, ans, why, level) in enumerate(PUZZLES, 1):
        print("\n" + "-" * 52)
        print(f"第 {i} 题（难度 {level}）：" + ", ".join(str(x) for x in seq) + ", ?")
        for attempt in (1, 2):
            raw = input("  下一项 = ").strip().lower()
            if raw in ("q", "quit", "exit"):
                print("\n你已退出。")
                print(f"当前得分：{total}")
                return
            if raw in ("skip", "s", "跳过"):
                print(f"  ➜ 跳过。答案：{ans}｜{why}")
                break
            ok, val = check_answer(raw)
            if not ok:
                print("  请输入一个数字。")
                continue
            if val == ans:
                pts = 100 if attempt == 1 else 60
                total += pts
                correct += 1
                print(f"  ✅ 正确！+{pts} 分｜{why}")
                break
            if attempt == 1:
                print("  ❌ 不对，再想想（提示：看看相邻两项的差或比）。")
            else:
                print(f"  ❌ 两次都没答对。答案：{ans}｜{why}")

    print("\n" + "=" * 52)
    print(f"  答对 {correct}/{len(PUZZLES)} 题，得分 {total}")
    if correct == len(PUZZLES):
        print("  🏆 全对！你对数字规律的直觉相当准。")
    elif correct >= 8:
        print("  👍 很稳，基础数列几乎都认得出来。")
    else:
        print("  🙂 多做几次「看差分、看比值」的练习会很快进步。")
    print("=" * 52)


if __name__ == "__main__":
    main()
