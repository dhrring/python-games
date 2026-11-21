"""
====================================================
 模运算保险箱 —— 数论与 RSA 入门小游戏
====================================================

【中文说明】
保险箱有 5 道电子锁，每道锁都问一个「模运算」问题。
密码学的大厦就建在这些看似幼稚的算式上：求逆元、欧拉函数、快速幂取模、RSA。

  ① 模逆元：若 a·x ≡ 1 (mod m)，称 x 是 a 在模 m 下的逆元。
     （等价于求整数 x、让 a·x 除以 m 余 1；m 是质数且 a 不是 m 的倍数时必有唯一解。）
  ② 欧拉函数 φ(n)：1..n 中与 n 互质的数的个数。
     若 n = p₁^{a₁} p₂^{a₂}…，则 φ(n) = n·(1−1/p₁)(1−1/p₂)…。
  ③ 快速幂取模：a^b mod m，用「平方再乘」把 b 次乘法压到 log b 次。
     配合费马小定理 a^{m−1} ≡ 1 (mod m)（m 为质数、a 与 m 互质），可先把指数对 m−1 取余。
  ④ RSA：选质数 p、q，令 n = p q、φ(n) = (p−1)(q−1)，公开 e，私钥 d 满足 e·d ≡ 1 (mod φ(n))。

【游玩方法】
  · 直接运行：python 2026-11-21_模运算保险箱.py
  · 共 5 道锁，每道 20 分，满分 100。
  · 每题输入一个小于模数的非负整数。
  · 命令：hint 看方法提示（−10 分）｜ q 退出
  · 答错一次 −8 分，每道锁保底 4 分。

【知识点】
  同余、模逆元、欧拉函数、快速幂、费马小定理、RSA 公私钥。
====================================================
"""

PER_LEVEL = 20
WRONG_COST = 8
HINT_COST = 10
FLOOR = 4

LEVELS = [
    {
        "name": "第 1 道锁 · 逆元",
        "question": "求 x，使 3 x ≡ 1 (mod 7)。x = ?（0 ≤ x < 7）",
        "answer": 5,
        "hint": "把 x 从 0 试到 6，看哪个让 3x 除以 7 余 1（3×5 = 15 = 2×7+1）。",
    },
    {
        "name": "第 2 道锁 · 欧拉函数",
        "question": "求 φ(36)，即 1 到 36 中与 36 互质的数的个数。φ(36) = ?",
        "answer": 12,
        "hint": "36 = 2²·3²，用 φ(n) = n(1−1/p₁)(1−1/p₂) = 36×(1/2)×(2/3)。",
    },
    {
        "name": "第 3 道锁 · 快速幂",
        "question": "求 7^2026 mod 13。（模数是质数 13，指数可先对 12 取余）",
        "answer": 4,
        "hint": "2026 mod 12 = 10，所以 7^2026 ≡ 7^10 (mod 13)。再把 7^10 拆成 7^8·7^2，"
                "用 7² ≡ 10、7⁴ ≡ 9、7⁸ ≡ 3 逐步平方。",
    },
    {
        "name": "第 4 道锁 · RSA 私钥",
        "question": "RSA：取 p = 5、q = 11，则 n = 55、φ(n) = 40，公钥 e = 3。私钥 d = ?（0 < d < 40）",
        "answer": 27,
        "hint": "解 3d ≡ 1 (mod 40)，即 3d = 40k+1。逐个试 k：k=2 时 81/3 = 27 正好整除。",
    },
    {
        "name": "第 5 道锁 · 一次同余方程",
        "question": "求最小的非负整数 x，使 11 x ≡ 4 (mod 17)。x = ?",
        "answer": 5,
        "hint": "先求 11 在模 17 下的逆元：11×14 = 154 = 9×17+1，所以逆元是 14；"
                "再算 x ≡ 14×4 = 56 ≡ 5 (mod 17)。",
    },
]


def euler_phi(n):
    result, m, p = n, n, 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            result -= result // p
        p += 1
    if m > 1:
        result -= result // m
    return result


def brute_inverse(a, m):
    for x in range(m):
        if a * x % m == 1:
            return x
    return None


def show_level(idx, level):
    print()
    print("─" * 48)
    print(f"【{level['name']}】  第 {idx + 1}/{len(LEVELS)} 道")
    print(level["question"])


def play():
    print(__doc__.split("【中文说明】")[0].strip())
    print("输入整数开锁；hint 看方法，q 退出。")
    total_score = 0
    for idx, level in enumerate(LEVELS):
        show_level(idx, level)
        penalty = 0
        hinted = False
        while True:
            try:
                cmd = input("  输入密码 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  已退出。")
                return
            if not cmd:
                continue
            low = cmd.lower()
            if low in ("q", "quit", "exit", "退出"):
                print("  已退出。")
                return
            if low in ("hint", "h", "提示", "?"):
                if hinted:
                    print("  本关提示已经用过啦。")
                else:
                    print("  💡 " + level["hint"])
                    hinted = True
                    penalty += HINT_COST
                continue
            if not cmd.lstrip("-").isdigit():
                print("  请输入整数，或 hint / q。")
                continue
            ans = int(cmd)
            if ans == level["answer"]:
                score = max(FLOOR, PER_LEVEL - penalty)
                total_score += score
                print(f"  ✅ 锁开了！答案 {level['answer']}，本关得 {score} 分。")
                break
            penalty += WRONG_COST
            print(f"  ❌ {ans} 打不开这把锁，再想想。")

    print()
    print("═" * 48)
    print(f"结算：{len(LEVELS)}/{len(LEVELS)} 道锁全部处理，总分 {min(100, total_score)}/100")
    if total_score >= 90:
        print("评级：密码学家 —— 你已能徒手玩转模运算。")
    elif total_score >= 60:
        print("评级：开锁匠 —— 只差一点熟练度。")
    else:
        print("评级：门外汉 —— 记住：逆元就是「乘起来余 1」的那个数。")
    print("═" * 48)
    print("小知识：φ(36) 与 RSA 里的 φ(n) 是同一个函数；RSA 的安全性来自"
          "「大数分解很难，但求逆元很容易」。")


if __name__ == "__main__":
    play()
