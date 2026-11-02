# -*- coding: utf-8 -*-
"""
猜国家首都（Capital Quiz）
==========================
随机抽一个国家，考你它的首都。答错会给出首都首字母提示。
输入 'q' 提前结束，最后统计正确率。纯标准库实现。
运行：python3 2026-11-02_猜国家首都.py
"""

import random

COUNTRIES = {
    "中国": "北京",
    "日本": "东京",
    "韩国": "首尔",
    "美国": "华盛顿",
    "英国": "伦敦",
    "法国": "巴黎",
    "德国": "柏林",
    "俄罗斯": "莫斯科",
    "意大利": "罗马",
    "西班牙": "马德里",
    "澳大利亚": "堪培拉",
    "加拿大": "渥太华",
    "印度": "新德里",
    "巴西": "巴西利亚",
    "埃及": "开罗",
    "泰国": "曼谷",
    "越南": "河内",
    "新加坡": "新加坡",
    "土耳其": "安卡拉",
    "阿根廷": "布宜诺斯艾利斯",
    "墨西哥": "墨西哥城",
    "瑞典": "斯德哥尔摩",
    "瑞士": "伯尔尼",
    "希腊": "雅典",
    "葡萄牙": "里斯本",
}


def main():
    print("=" * 44)
    print("        🌍 猜国家首都 Capital Quiz")
    print("=" * 44)
    print("显示一个国家名，输入其首都。答错给首字母提示。")
    print("输入 'q' 提前结束。")
    n = int(input("想做几题？(默认10)：").strip() or "10")
    n = max(1, min(25, n))

    countries = list(COUNTRIES.keys())
    correct = 0
    for i in range(1, n + 1):
        country = random.choice(countries)
        cap = COUNTRIES[country]
        print(f"\n第 {i}/{n} 题:  {country} 的首都是？")
        got = input("你的答案：").strip()
        if got.lower() in ("q", "quit", "exit"):
            print("提前结束。")
            n = i - 1
            break
        if got == cap:
            correct += 1
            print("✅ 正确！")
        else:
            print(f"❌ 错误，正确答案: {cap}（首字母：{cap[0]}）")

    if n == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / n * 100
    print("\n" + "=" * 44)
    print(f"        结果：{correct}/{n}  正确率 {acc:.1f}%")
    print("=" * 44)
    if acc == 100:
        print("🌏 地理达人，满分通关！")
    elif acc >= 80:
        print("👍 知识丰富，很棒！")
    else:
        print("💡 多看看地图，下次会更好！")


if __name__ == "__main__":
    main()
