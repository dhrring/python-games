# -*- coding: utf-8 -*-
"""
双色球模拟（Lottery Simulator）
================================
模拟福彩双色球：从 33 个红球选 6 个 + 16 个蓝球选 1 个。
电脑随机开奖，你机选或自选号码，比对比对等级。纯标准库实现。
运行：python3 2026-11-02_双色球模拟.py
"""

import random


def draw():
    reds = random.sample(range(1, 34), 6)
    blue = random.randint(1, 16)
    return sorted(reds), blue


def grade(reds, blue, draw_reds, draw_blue):
    """按双色球规则判等级。"""
    r = len(set(reds) & set(draw_reds))
    b = blue == draw_blue
    table = {
        (6, True): "一等奖",
        (6, False): "二等奖",
        (5, True): "三等奖",
        (5, False): "四等奖",
        (4, True): "四等奖",
        (4, False): "五等奖",
        (3, True): "五等奖",
        (2, True): "六等奖",
        (1, True): "六等奖",
        (0, True): "六等奖",
    }
    return table.get((r, b), "未中奖")


def pick_numbers(auto=True):
    if auto:
        return draw()
    print("请在 1~33 选 6 个不重复红球，1~16 选 1 个蓝球。")
    while True:
        try:
            reds = sorted({int(x) for x in input("红球(空格分隔6个): ").split()})
            blue = int(input("蓝球(1个): ").strip())
            if len(reds) == 6 and all(1 <= x <= 33 for x in reds) and 1 <= blue <= 16:
                return reds, blue
            print("输入无效，请重新输入。")
        except ValueError:
            print("输入无效，请重新输入。")


def main():
    print("=" * 44)
    print("        🎱 双色球模拟 Lottery")
    print("=" * 44)
    print("红球 1~33 选 6，蓝球 1~16 选 1。")
    auto = input("机选(y)还是自选(n)？(默认y)：").strip().lower()
    my_reds, my_blue = pick_numbers(auto != "n")
    print(f"\n你的号码：红 {' '.join(f'{x:02d}' for x in my_reds)} + 蓝 {my_blue:02d}")

    # 开奖
    print("\n开奖中……")
    draw_reds, draw_blue = draw()
    print(f"开奖号码：红 {' '.join(f'{x:02d}' for x in draw_reds)} + 蓝 {draw_blue:02d}")

    prize = grade(my_reds, my_blue, draw_reds, draw_blue)
    print(f"\n结果：{prize}")
    if prize == "一等奖":
        print("🏆 天选之人！恭喜！")
    elif prize == "未中奖":
        print("😅 下次再来！请理性购彩，量力而行。")


if __name__ == "__main__":
    main()
