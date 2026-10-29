# -*- coding: utf-8 -*-
"""
数字黑洞（Kaprekar 6174）
========================
经典 Kaprekar 常数游戏：选一个四位数（至少两位数字不同），
每次把它各位数字降序排 - 升序排，结果继续重复，最终会掉进 6174。
看几步能到达黑洞。纯标准库实现。
运行：python3 2026-10-29_数字黑洞.py
"""


def kaprekar_step(n):
    """对四位数做一次 Kaprekar 变换，返回结果"""
    s = f"{n:04d}"
    desc = int("".join(sorted(s, reverse=True)))
    asc = int("".join(sorted(s)))
    return desc - asc


def main():
    print("=" * 40)
    print("        🔢 数字黑洞 Kaprekar 6174")
    print("=" * 40)
    print("随便选一个四位数（至少两位数字不同），")
    print("把各位数字降序排减去升序排，反复进行，最终都会到 6174。")
    print("q 退出，随机 输入 random 随机生成一个数。")

    while True:
        cmd = input("\n输入一个四位数（或 random / q）：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if cmd == "random":
            import random
            n = random.randint(1000, 9998)
            # 保证至少两位不同
            while len(set(f"{n:04d}")) < 2:
                n = random.randint(1000, 9998)
        else:
            if not cmd.isdigit() or len(cmd) != 4:
                print("请输入4位数字。")
                continue
            n = int(cmd)
        if len(set(f"{n:04d}")) < 2:
            print("四位数至少要有两位数字不同，否则直接归0。")
            continue

        print(f"\n开始：{n}")
        steps = 0
        seen = set()
        while True:
            s = f"{n:04d}"
            desc = int("".join(sorted(s, reverse=True)))
            asc = int("".join(sorted(s)))
            n = desc - asc
            steps += 1
            print(f"第{steps}步：{desc} - {asc} = {n}")
            if n == 6174:
                print(f"🎉 到达数字黑洞 6174！共用了 {steps} 步。")
                break
            if n in seen:
                print(f"进入循环，重复数 {n}。")
                break
            seen.add(n)


if __name__ == "__main__":
    main()
