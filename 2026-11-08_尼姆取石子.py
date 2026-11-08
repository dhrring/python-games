# -*- coding: utf-8 -*-
"""
尼姆取石子（Nim Game）
=======================
三堆石子（默认 3 / 5 / 7），双方轮流从「其中一堆」取走任意多颗（至少 1 颗）。
取走最后一颗石子的人获胜。
你执「你」，电脑执「电脑」。
纯标准库实现。

核心数学：尼姆和 = 各堆石子数的按位异或（XOR）。
若当前尼姆和不为 0，则存在一步走法把它变成 0，把「必败局面」留给对手。

游玩方法：
  开局选择难度；
  你输入「堆号 数量」，例如 2 3 表示从第 2 堆取 3 颗；
  输入 s 看局面，输入 q 退出。
  难度：开局会让你选 1=轻松（电脑常走随机）/ 2=困难（电脑走最优策略）。

运行：python3 2026-11-08_尼姆取石子.py
"""

import random

START_HEAPS = [3, 5, 7]


def nim_sum(heaps):
    x = 0
    for h in heaps:
        x ^= h
    return x


def show(heaps):
    print("\n当前石子：")
    for i, h in enumerate(heaps, 1):
        bar = "●" * h if h <= 20 else f"●×{h}"
        print(f"  {i} 号堆（{h} 颗）：{bar}")
    print(f"  尼姆和（异或）= {nim_sum(heaps)}")


def ai_move(heaps, difficulty):
    """返回 (堆索引0基, 取走数量)。"""
    total = sum(heaps)
    if difficulty == 2:
        xs = nim_sum(heaps)
        if xs != 0:
            for i, h in enumerate(heaps):
                target = h ^ xs
                if target < h:
                    return i, h - target
    # 轻松模式，或困难模式遇到必败局面：随机合法走法
    candidates = [(i, n) for i, h in enumerate(heaps) for n in range(1, h + 1)]
    return random.choice(candidates)


def main():
    print("=" * 46)
    print("        🪨 尼姆取石子 Nim Game")
    print("=" * 46)
    print("规则：轮流从某一堆取石子（至少 1 颗，可全取），取走最后一颗者获胜。")
    print("提示：把「各堆数量的异或和」变成 0，就能把必败局面留给对手。")

    while True:
        raw = input("\n选择难度 1=轻松 / 2=困难：").strip()
        if raw in ("1", "2"):
            difficulty = int(raw)
            break
        print("请输入 1 或 2。")

    heaps = list(START_HEAPS)
    show(heaps)
    print("\n你先手。请输入「堆号 数量」，例如 2 3。")

    while True:
        if sum(heaps) == 0:
            # 不会走到这里（取完即判胜负），保险起见
            break

        # ---- 玩家回合 ----
        while True:
            raw = input("你取：").strip().lower()
            if raw in ("q", "quit", "exit"):
                print("你已退出对局。")
                return
            if raw == "s":
                show(heaps)
                continue
            parts = raw.replace("，", " ").replace(",", " ").split()
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                print("格式：堆号 数量，例如 2 3。")
                continue
            idx, num = int(parts[0]) - 1, int(parts[1])
            if idx < 0 or idx >= len(heaps):
                print(f"堆号只能是 1~{len(heaps)}。")
                continue
            if num < 1 or num > heaps[idx]:
                print(f"第 {idx + 1} 堆只有 {heaps[idx]} 颗，请取 1~{heaps[idx]} 颗。")
                continue
            heaps[idx] -= num
            print(f"你从 {idx + 1} 号堆取走 {num} 颗。")
            break

        if sum(heaps) == 0:
            print("\n" + "=" * 46)
            print("🎉 你取走了最后一颗石子，你赢了！")
            print("=" * 46)
            return

        # ---- 电脑回合 ----
        idx, num = ai_move(heaps, difficulty)
        heaps[idx] -= num
        print(f"电脑从 {idx + 1} 号堆取走 {num} 颗。")
        if sum(heaps) == 0:
            print("\n" + "=" * 46)
            print("😢 电脑取走了最后一颗石子，你输了。")
            print("=" * 46)
            return
        show(heaps)


if __name__ == "__main__":
    main()
