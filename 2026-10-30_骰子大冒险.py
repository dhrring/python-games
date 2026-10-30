# -*- coding: utf-8 -*-
"""
骰子大冒险（Dice Adventure）
============================
简化版大富翁式冒险：掷骰子前进，触发不同格子的随机事件
（得金币、扣血、抽卡、休息、到达终点），目标是到达终点。纯标准库实现。
运行：python3 2026-10-30_骰子大冒险.py
"""

import random

BOARD_LEN = 20


def event(pos, gold, hp):
    """返回 (新金币, 新血, 事件描述)"""
    r = random.random()
    if r < 0.25:
        g = random.randint(5, 15)
        return gold + g, hp, f"💰 捡到金币 +{g}（金币{gold+g}）"
    elif r < 0.40:
        d = random.randint(3, 8)
        return gold, hp - d, f"⚔️ 遭遇怪兽，生命 -{d}（生命{hp-d}）"
    elif r < 0.55:
        if gold >= 10:
            return gold - 10, hp, f"🛒 抽卡花费10金币（金币{gold-10}）"
        return gold, hp, "🛒 想抽卡但金币不足"
    elif r < 0.70:
        h = random.randint(5, 12)
        return gold, hp + h, f"🌳 在驿站休息，生命 +{h}（生命{hp+h}）"
    else:
        return gold + random.randint(2, 6), hp, "✨ 发现隐藏宝箱 +金币"


def main():
    print("=" * 40)
    print("        🎲 骰子大冒险 Dice Adventure")
    print("=" * 40)
    print(f"从起点掷骰子走到终点（{BOARD_LEN}格）。路上有金币、怪兽、事件。")
    print("r 掷骰子，q 退出。生命归0则游戏结束。")
    pos = 0
    gold = 20
    hp = 50
    max_hp = 50

    while pos < BOARD_LEN:
        print(f"\n位置 {pos}/{BOARD_LEN}   金币 {gold}   生命 {hp}/{max_hp}")
        cmd = input("r=掷骰子 q=退出：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if cmd != "r":
            print("输入 r 掷骰子。")
            continue
        dice = random.randint(1, 6)
        pos += dice
        if pos > BOARD_LEN:
            pos = BOARD_LEN
        print(f"🎲 掷出 {dice}，前进到 {pos}。")
        gold, hp, desc = event(pos, gold, hp)
        print(f"   {desc}")
        if hp <= 0:
            print("💀 生命耗尽，冒险失败！")
            return
    print(f"\n🎉 到达终点！最终金币 {gold}，生命 {hp}。冒险成功！")


if __name__ == "__main__":
    main()
