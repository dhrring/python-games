# -*- coding: utf-8 -*-
"""
化学元素猜猜看（Chemical Elements Quiz）
==========================================
从元素周期表常见元素中随机出题：给出元素符号，猜它的中文名称。
答错会给出原子序数与一句话性质提示。共 8 题，统计正确率。
纯标准库实现。
运行：python3 2026-11-06_化学元素猜猜看.py
"""

import random

# (符号, 中文名, 原子序数, 一句话提示)
ELEMENTS = [
    ("H", "氢", 1, "宇宙中最轻、最丰富的元素，能燃烧。"),
    ("He", "氦", 2, "惰性气体，用来充气球，声音会变尖。"),
    ("C", "碳", 6, "有机物骨架，金刚石与石墨都是它。"),
    ("N", "氮", 7, "空气中最多的气体，约占 78%。"),
    ("O", "氧", 8, "呼吸必需，空气中约占 21%。"),
    ("Na", "钠", 11, "活泼金属，与水剧烈反应，食盐的成分之一。"),
    ("Mg", "镁", 12, "燃烧发出耀眼白光，曾用于闪光粉。"),
    ("Al", "铝", 13, "地壳中含量最高的金属，轻而耐腐蚀。"),
    ("Si", "硅", 14, "半导体与芯片的核心材料，沙子的主要成分。"),
    ("P", "磷", 15, "白磷易自燃，火柴与骨头里都有它。"),
    ("S", "硫", 16, "黄色固体，火山口常见，有臭鸡蛋味。"),
    ("Cl", "氯", 17, "黄绿色气体，用于自来水消毒。"),
    ("K", "钾", 19, "植物生长必需，香蕉里含量高。"),
    ("Ca", "钙", 20, "骨骼与牙齿的主要成分，石灰石的组成。"),
    ("Fe", "铁", 26, "最常见的金属，钢铁与血红蛋白的核心。"),
    ("Cu", "铜", 29, "导电导热优良，电线与青铜的成分。"),
    ("Zn", "锌", 30, "镀在铁表面防锈，干电池负极材料。"),
    ("Ag", "银", 47, "导电性最好的金属，镜面镀层与首饰。"),
    ("Au", "金", 79, "化学性质最稳定的贵金属，黄金首饰。"),
    ("Hg", "汞", 80, "常温下唯一的液态金属，温度计常用。"),
]


def ask(sym, name, znum, hint, idx, total):
    print(f"\n第 {idx}/{total} 题：元素符号「{sym}」，它的中文名称是什么？")
    for chance in range(1, 4):
        got = input(f"第{chance}次：").strip()
        if got.lower() in ("q", "quit", "exit"):
            return None
        got = got.replace("元素", "").replace("化", "").strip()
        if got == name:
            print("✅ 答对了！")
            return True
        if chance == 1:
            print(f"提示①：原子序数 {znum}。")
        elif chance == 2:
            print(f"提示②：{hint}")
        else:
            print(f"❌ 正确答案是：{name}（{sym}，原子序数 {znum}）")
    return False


def main():
    print("=" * 48)
    print("      🧪 化学元素猜猜看 Chemical Elements Quiz")
    print("=" * 48)
    print("给出元素符号，猜它的中文名称。每题 3 次机会，答错给提示。")
    print("输入 q 提前结束。")

    total = 8
    picked = random.sample(ELEMENTS, total)
    correct = 0
    done = 0
    for i, (sym, name, znum, hint) in enumerate(picked, 1):
        r = ask(sym, name, znum, hint, i, total)
        if r is None:
            print("提前结束。")
            break
        done = i
        if r:
            correct += 1

    print("\n" + "=" * 48)
    if done == 0:
        print("        没有完成任何一题。")
    else:
        acc = correct / done * 100
        print(f"        结果：{correct}/{done}  正确率 {acc:.1f}%")
        if acc == 100:
            print("        🏆 满分！元素达人！")
        elif acc >= 60:
            print("        👍 不错，化学基础扎实！")
        else:
            print("        📖 多看看元素周期表吧！")
    print("=" * 48)


if __name__ == "__main__":
    main()
