# -*- coding: utf-8 -*-
"""
扑克24点（24 Game）
==================
随机给4张牌（点数1~13），用 + - * / 和括号让结果等于24。
每张牌必须用且仅用一次。可挑战无解局直接过。纯标准库实现。
运行：python3 2026-10-29_扑克24点.py
"""

import random
import itertools

# 点数映射
def points():
    return list(range(1, 14))  # A=1 ... K=13


def make_nums():
    return [random.randint(1, 13) for _ in range(4)]


def find_solution(nums):
    """尝试用 + - * / 和括号凑出 24，返回一个可行算式或 None"""
    for a, b, c, d in itertools.permutations(nums):
        for op1, op2, op3 in itertools.product("+-*/", repeat=3):
            # 各种括号结构
            exprs = [
                f"(({a}{op1}{b}){op2}{c}){op3}{d}",
                f"({a}{op1}({b}{op2}{c})){op3}{d}",
                f"({a}{op1}{b}){op2}({c}{op3}{d})",
                f"{a}{op1}(({b}{op2}{c}){op3}{d})",
                f"{a}{op1}({b}{op2}({c}{op3}{d}))",
            ]
            for e in exprs:
                try:
                    if abs(eval(e) - 24) < 1e-9:
                        return e.replace("*", "×").replace("/", "÷")
                except ZeroDivisionError:
                    continue
    return None


def main():
    print("=" * 40)
    print("        🃏 扑克24点 24 Game")
    print("=" * 40)
    print("给出4张牌，用 + - × ÷ 和括号凑出 24，每张牌只用一次。")
    print("输入算式（如 6*(8-5)+6），输入 提示 看一种解法，q 退出。")

    score = 0
    rounds = 5
    for rd in range(1, rounds + 1):
        while True:
            nums = make_nums()
            sol = find_solution(nums)
            if sol:  # 保证出可解的题
                break
        shown = [str(n) if n not in (1, 11, 12, 13) else {1:"A",11:"J",12:"Q",13:"K"}[n] for n in nums]
        print(f"\n[第{rd}/{rounds}轮] 你的牌：{' '.join(shown)}")
        while True:
            cmd = input("算式/提示/过/q：").strip()
            if cmd.lower() in ("q", "quit", "exit"):
                print(f"退出游戏。得分 {score}。")
                return
            if cmd == "提示":
                print(f"一种解法：{sol}")
                break
            if cmd in ("过", "pass"):
                print(f"答案：{sol}")
                break
            # 校验用户算式
            used = [str(n) if n not in (1,11,12,13) else {1:"A",11:"J",12:"Q",13:"K"}[n] for n in nums]
            import re
            tokens = re.findall(r"\d+|A|J|Q|K", cmd)
            mapped = [t if t not in "AJQK" else {"A":"1","J":"11","Q":"12","K":"13"}[t] for t in tokens]
            if sorted(mapped) != sorted([str(n) for n in nums]):
                print("必须用且只用这4张牌。")
                continue
            # 判断是否等于24
            e = cmd
            e = e.replace("A", "1").replace("J", "11").replace("Q", "12").replace("K", "13")
            e = e.replace("×", "*").replace("÷", "/")
            try:
                val = eval(e)
            except Exception:
                print("算式无法解析。")
                continue
            if abs(val - 24) < 1e-9:
                print("✅ 正确！凑出24！")
                score += 1
                break
            else:
                print(f"❌ 结果是 {val}，不是24。")
    print(f"\n🎉 游戏结束，得分 {score}/{rounds}")


if __name__ == "__main__":
    main()
