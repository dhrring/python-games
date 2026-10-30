# -*- coding: utf-8 -*-
"""
时钟益智（Clock Math）
=====================
随机给一个钟面时间，问指针夹角、时针分针重合/相反等趣味数学题，
考验角度计算。每题可作答，答对得分，可看解析。纯标准库实现。
运行：python3 2026-10-30_时钟益智.py
"""

import random


def clock_angle(hour, minute):
    """计算时针分针夹角（0~180度）"""
    if hour >= 12:
        hour -= 12
    ha = (hour * 60 + minute) * 0.5   # 时针角度
    ma = minute * 6                   # 分针角度
    diff = abs(ha - ma)
    if diff > 180:
        diff = 360 - diff
    return diff


def main():
    print("=" * 40)
    print("        🕐 时钟益智 Clock Math")
    print("=" * 40)
    print("看钟面时间，算时针分针夹角（取较小角，0~180度）。")
    print("输入角度（如 30），输入 解析 看解法，q 退出。")
    score = 0
    total = 5

    for i in range(1, total + 1):
        hour = random.randint(1, 12)
        minute = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
        ans = clock_angle(hour, minute)
        # 允许小幅容差取整
        print(f"\n[第{i}/{total}题] 时间 {hour:02d}:{minute:02d}，时针和分针的夹角是多少度？")
        cmd = input("你的答案（度）/解析/q：").strip()
        if cmd.lower() in ("q", "quit", "exit"):
            print(f"你退出游戏。得分 {score}/{i-1}。")
            return
        if cmd == "解析":
            ha = ((hour % 12) * 60 + minute) * 0.5
            ma = minute * 6
            diff = abs(ha - ma)
            if diff > 180:
                diff = 360 - diff
            print(f"解析：时针角度 {ha:.1f}°，分针角度 {ma}°，夹角 = |{ha:.1f}-{ma}| = {diff:.1f}°（取较小角）")
            continue
        if not cmd.replace(".", "", 1).isdigit():
            print("请输入角度数字、'解析'或'q'。")
            continue
        guess = float(cmd)
        if abs(guess - ans) < 0.5:
            print(f"✅ 正确！夹角是 {ans:.1f}°")
            score += 1
        else:
            print(f"❌ 不对。夹角是 {ans:.1f}°")
    print(f"\n🎉 游戏结束，得分 {score}/{total}")


if __name__ == "__main__":
    main()
