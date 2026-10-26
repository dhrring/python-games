# -*- coding: utf-8 -*-
"""
汉诺塔（Tower of Hanoi）
=======================
经典汉诺塔谜题：三根柱子，把 n 个盘从 A 移到 C，每次只能移一个，
大盘不能压在小盘上。提供两种玩法：手动逐步移动、查看自动求解。
纯标准库实现，可直接运行：python3 2026-10-26_汉诺塔.py
"""

import sys


def print_towers(towers):
    """打印三根柱子的状态"""
    n = max((len(t) for t in towers), default=0)
    labels = ["A", "B", "C"]
    for level in range(n - 1, -1, -1):
        row = []
        for t in towers:
            row.append(str(t[level]).center(6) if level < len(t) else "      ")
        print("   ".join(row))
    print("   ".join(l.center(6) for l in labels))
    print("-" * 30)


def valid_move(towers, src, dst):
    if not towers[src]:
        return False
    if not towers[dst]:
        return True
    return towers[src][-1] < towers[dst][-1]


def solve(n, src, dst, aux, towers, moves_log):
    if n == 0:
        return
    solve(n - 1, src, aux, dst, towers, moves_log)
    towers[dst].append(towers[src].pop())
    moves_log.append((src, dst))
    solve(n - 1, aux, dst, src, towers, moves_log)


def main():
    print("=" * 40)
    print("        🗼 汉诺塔 Tower of Hanoi")
    print("=" * 40)
    try:
        n = int(input("请输入盘子数量（3~6 较合适）："))
    except ValueError:
        n = 3
    n = max(1, min(8, n))

    towers = [list(range(n, 0, -1)), [], []]
    mode = input("选择模式：1) 手动  2) 自动演示：").strip()
    if mode == "2":
        moves_log = []
        solve(n, 0, 2, 1, towers, moves_log)
        print(f"\n自动求解：共 {2**n - 1} 步")
        # 重放
        towers2 = [list(range(n, 0, -1)), [], []]
        for i, (s, d) in enumerate(moves_log, 1):
            towers2[d].append(towers2[s].pop())
            print(f"第{i}步：{chr(65+s)} -> {chr(65+d)}")
            print_towers(towers2)
        print("🎉 完成！")
        return

    # 手动模式
    moves = 0
    print("\n把 A 柱的所有盘移到 C 柱。输入格式：AB 表示从 A 移到 B。q 退出。")
    while towers[0] or towers[1]:
        print_towers(towers)
        cmd = input("移动（如 AB）：").strip().upper()
        if cmd in ("Q", "QUIT", "EXIT"):
            print("退出游戏。")
            return
        if len(cmd) != 2 or cmd[0] not in "ABC" or cmd[1] not in "ABC":
            print("请输入两个字母，如 AB。")
            continue
        src, dst = ord(cmd[0]) - 65, ord(cmd[1]) - 65
        if src == dst:
            print("不能在同一个柱子间移动。")
            continue
        if not valid_move(towers, src, dst):
            print("非法移动：源柱为空或大盘压小盘。")
            continue
        towers[dst].append(towers[src].pop())
        moves += 1
        if not towers[0] and not towers[1]:
            print_towers(towers)
            print(f"🎉 恭喜完成！共用了 {moves} 步（最少 {2**n - 1} 步）。")
            return


if __name__ == "__main__":
    main()
