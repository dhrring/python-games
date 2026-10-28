# -*- coding: utf-8 -*-
"""
猜水果（Guess the Fruit）
=========================
电脑随机想一个水果，你通过提问（是/否）缩小范围猜出来。
会给出若干水果特征，用排除法最快锁定。纯标准库实现。
运行：python3 2026-10-28_猜水果.py
"""

import random

FRUITS = {
    "苹果": "圆形、红色或绿色、甜脆",
    "香蕉": "长条形、黄色、皮可剥",
    "西瓜": "很大、绿色外皮、红色果肉多汁",
    "草莓": "小、红色、表面有籽",
    "葡萄": "很小、成串、紫或绿",
    "橙子": "圆形、橙色、酸甜",
    "柠檬": "椭圆形、黄色、很酸",
    "桃子": "圆形、有毛、粉或黄色、有核",
    "芒果": "椭圆形、黄或橙色、香甜",
    "菠萝": "外皮有刺、黄色果肉、很甜",
}


def main():
    print("=" * 40)
    print("        🍎 猜水果 Guess the Fruit")
    print("=" * 40)
    print("电脑想了一个水果，你用是/否提问来猜。")
    print("输入你猜的水果名，或输入'提示'看特征，'列表'看候选，q退出。")
    print(f"候选水果：{'、'.join(FRUITS)}")

    secret = random.choice(list(FRUITS))
    attempts = 0

    while True:
        attempts += 1
        cmd = input(f"\n[第{attempts}次] 猜/提问/提示/列表：").strip()
        if cmd.lower() in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if cmd == "提示":
            print(f"特征：{FRUITS[secret]}")
            continue
        if cmd == "列表":
            print(f"候选：{'、'.join(FRUITS)}")
            continue
        if cmd in FRUITS:
            if cmd == secret:
                print(f"🎉 答对了！就是 {secret}，用了 {attempts} 次。")
                return
            else:
                print(f"❌ 不是 {cmd}。再猜。")
        else:
            print("请输入候选水果名、'提示'或'列表'。")


if __name__ == "__main__":
    main()
