# -*- coding: utf-8 -*-
"""
心算挑战（Mental Math Challenge）
==================================
连续出加减乘除算式，你在限定时间内心算作答。
最后统计正确率与总用时。纯标准库实现。
运行：python3 2026-11-02_心算挑战.py
"""

import random
import time


def make_question():
    """生成一道随机的加减乘除题，返回 (表达式, 答案)。"""
    op = random.choice(["+", "-", "*", "/"])
    if op == "+":
        a, b = random.randint(10, 99), random.randint(10, 99)
        return f"{a} + {b}", a + b
    if op == "-":
        a = random.randint(20, 99)
        b = random.randint(1, a - 1)
        return f"{a} - {b}", a - b
    if op == "*":
        a, b = random.randint(2, 12), random.randint(2, 12)
        return f"{a} × {b}", a * b
    # 除法：保证整除
    b = random.randint(2, 12)
    q = random.randint(2, 12)
    a = b * q
    return f"{a} ÷ {b}", q


def main():
    print("=" * 44)
    print("        🧮 心算挑战 Mental Math")
    print("=" * 44)
    print("计算下面算式的值，输入整数后回车。输入 'q' 提前结束。")
    n = int(input("想做几道题？(默认10)：").strip() or "10")
    n = max(1, min(30, n))

    correct = 0
    start = time.time()
    for i in range(1, n + 1):
        expr, ans = make_question()
        print(f"\n第 {i}/{n} 题:  {expr} = ?")
        got = input("你的答案：").strip()
        if got.lower() in ("q", "quit", "exit"):
            print("提前结束。")
            n = i - 1
            break
        try:
            if int(got) == ans:
                correct += 1
                print("✅ 正确！")
            else:
                print(f"❌ 错误，正确答案: {ans}")
        except ValueError:
            print(f"❌ 请输入数字，正确答案: {ans}")

    if n == 0:
        print("\n没有完成任何一题。")
        return
    elapsed = time.time() - start
    acc = correct / n * 100
    print("\n" + "=" * 44)
    print("        统计结果")
    print("=" * 44)
    print(f"完成题目：{correct}/{n}")
    print(f"正确率：{acc:.1f}%")
    print(f"总用时：{elapsed:.1f} 秒")
    if acc == 100:
        print("🏆 满分！心算大师！")
    elif acc >= 80:
        print("👍 很厉害，继续加油！")
    else:
        print("💪 多练习，熟能生巧！")


if __name__ == "__main__":
    main()
