# -*- coding: utf-8 -*-
"""
历史年代排序（History Timeline Challenge）
============================================
每轮给出 4 个中国历史事件，请按时间从早到晚排出先后顺序。
输入 4 个编号（空格分隔），如「3 1 4 2」，表示第 3 个最早、第 2 个最晚。
共 5 轮，按年份自动核对答案。纯标准库实现。
运行：python3 2026-11-07_历史年代排序.py
"""

import random

# (事件, 年份)：负数表示公元前
EVENTS = [
    ("秦统一六国", -221),
    ("陈胜吴广起义", -209),
    ("张骞出使西域", -138),
    ("赤壁之战", 208),
    ("隋朝统一全国", 589),
    ("玄武门之变", 626),
    ("安史之乱爆发", 755),
    ("王安石变法", 1069),
    ("蒙古灭南宋", 1279),
    ("郑和首次下西洋", 1405),
    ("鸦片战争爆发", 1840),
    ("甲午中日战争", 1894),
    ("辛亥革命", 1911),
    ("五四运动", 1919),
    ("中华人民共和国成立", 1949),
    ("改革开放开始", 1978),
]


def year_text(y):
    return f"公元前 {abs(y)} 年" if y < 0 else f"公元 {y} 年"


def play_round(items, ridx, total):
    print(f"\n第 {ridx}/{total} 轮，请把下面 4 个事件按时间从早到晚排序：")
    for i, (name, _) in enumerate(items, 1):
        print(f"  {i}. {name}")
    raw = input("按从早到晚的顺序输入编号（空格分隔）：").strip()
    if raw.lower() in ("q", "quit", "exit"):
        return None
    parts = raw.replace("，", " ").replace(",", " ").split()
    if len(parts) != 4 or sorted(parts) != ["1", "2", "3", "4"]:
        print("❌ 输入无效：需要恰好给出 4 个不重复的编号 1~4。")
        return False

    user_order = [int(p) for p in parts]
    correct_order = [i for i, _ in sorted(enumerate(items, 1), key=lambda kv: kv[1][1])]
    if user_order == correct_order:
        print("✅ 完全正确！")
        return True

    print("❌ 顺序不对。正确顺序（从早到晚）是：")
    for i in correct_order:
        name, y = items[i - 1]
        print(f"  {i}. {name} —— {year_text(y)}")
    return False


def main():
    print("=" * 52)
    print("      🕰️ 历史年代排序 History Timeline")
    print("=" * 52)
    print("每轮 4 个历史事件，按时间从早到晚排序，输入编号即可（可用 q 退出）。")

    total = 5
    correct = 0
    done = 0
    for ridx in range(1, total + 1):
        items = random.sample(EVENTS, 4)
        r = play_round(items, ridx, total)
        if r is None:
            print("提前结束。")
            break
        done = ridx
        if r:
            correct += 1

    print("\n" + "=" * 52)
    if done == 0:
        print("        没有完成任何一轮。")
    else:
        print(f"        结果：{correct}/{done} 轮排序正确")
        if correct == done:
            print("        🏆 全对！历史时间线高手！")
        elif correct * 2 >= done:
            print("        👍 不错，年代感很强！")
        else:
            print("        📖 再翻翻历史年表吧！")
    print("=" * 52)


if __name__ == "__main__":
    main()
