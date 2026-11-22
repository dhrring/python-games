"""
====================================================
 硬币找零收银台 —— 贪心与动态规划小游戏
====================================================

【游戏简介】
收银台最日常的问题：要找给顾客 N 分钱，怎样用**最少的硬币**？
很多人第一反应是"能用大面额就用大面额"（贪心），这在人民币、美元等
常见币制里恰好正确，但换成某些面额（比如 1、3、4 分）就会翻车。

本游戏共 5 关：你只报"最少需要几枚硬币"，程序会用动态规划验证。

【游玩方法】
1. 运行：python 2026-11-22_硬币找零收银台.py
2. 每关给出硬币面额与金额，输入最少硬币枚数（整数）。
3. 输入 hint 或 h：看提示（-10 分，每关最低保留 4 分）。
4. 输入 q / quit / 退出：结束本局；直接回车：重看题目。
5. 每关 20 分，答错扣 8 分（不低于 4 分），满分 100。
   如果输入的恰是"贪心法"的错误答案，程序会单独提醒你。

【自检】
python 2026-11-22_硬币找零收银台.py --check
会用动态规划与暴力枚举两种方式互相校验答案。
"""

import sys

LEVELS = [
    dict(
        title="便利店找零",
        coins=[1, 5, 10, 25],
        amount=63,
        answer=6,
        hint="25 分最多用两枚（50），剩 13；13 再想 10 + 1 + 1 + 1。"
             "试试看能不能比 6 枚更少。",
        note="面额 1/5/10/25 是美元硬币体系，贪心法在这里恰好最优。",
    ),
    dict(
        title="怪币制（上）",
        coins=[1, 3, 4],
        amount=6,
        answer=2,
        hint="先按贪心走一遍：4 + 1 + 1 = 3 枚。再看看 3 + 3 呢？"
             "面额里有 4 却偏不用它，这就是贪心的陷阱。",
        note="面额 1/3/4 的经典反例：6 分钱贪心要 3 枚，最优只要 2 枚。",
    ),
    dict(
        title="怪币制（下）",
        coins=[1, 3, 4],
        amount=18,
        answer=5,
        hint="贪心：4×4 = 16，再补 1 + 1，一共 6 枚。"
             "换条路：把 16 换成 15（4+4+4），剩下 3 用一枚 3 —— 3+3+3+4+4 是多少枚？",
        note="18 分钱：贪心 6 枚，最优 5 枚（4+4+4+3+3），差额随金额变大而扩大。",
    ),
    dict(
        title="人民币零钱罐",
        coins=[1, 2, 5, 10, 20, 50, 100],
        amount=288,
        answer=8,
        hint="从 100 分开始：288 → 2 枚 100 剩 88；88 用 50 剩 38；"
             "38 用 20 剩 18；18 用 10 剩 8；8 用 5 剩 3；3 用 2 剩 1；最后 1 枚 1 分。",
        note="人民币分币体系是「规范币制」，贪心法每一步都最优。",
    ),
    dict(
        title="外国硬币挑战",
        coins=[1, 4, 5, 10],
        amount=27,
        answer=5,
        hint="贪心：10 + 10 + 5 + 1 + 1 = 5 枚，先记着这个数。"
             "再试 10 + 4 + 4 + 4 + 4 + 1 会不会更少？"
             "或者 5×5 + 1 + 1 = 7 枚？比较一下谁最少。",
        note="面额 1/4/5/10 时贪心仍最优，但 27 这个金额很考验你是不是真的在比。",
    ),
]


# -----------------------------------------------------------
# 求解：动态规划（游戏内给示例用）与暴力枚举（check 用）
# -----------------------------------------------------------
def dp_solve(coins, amount):
    """返回 (最少枚数, 一种最优组合列表)。"""
    inf = 10 ** 9
    best = [0] + [inf] * amount
    pick = [0] * (amount + 1)
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and best[x - c] + 1 < best[x]:
                best[x] = best[x - c] + 1
                pick[x] = c
    if best[amount] >= inf:
        return None, []
    used, x = [], amount
    while x > 0:
        used.append(pick[x])
        x -= pick[x]
    return best[amount], used


def greedy_solve(coins, amount):
    """贪心法：每次用最大面额。无法凑整时返回 None。"""
    n = 0
    for c in sorted(coins, reverse=True):
        n += amount // c
        amount %= c
    return n if amount == 0 else None


def brute_solve(coins, amount):
    """暴力枚举全部组合，返回最少枚数。"""
    best = [10 ** 9]

    def rec(i, rem, cnt):
        if i == len(coins):
            if rem == 0:
                best[0] = min(best[0], cnt)
            return
        c = coins[i]
        k = 0
        while k * c <= rem:
            if cnt + k >= best[0]:
                break
            rec(i + 1, rem - k * c, cnt + k)
            k += 1

    rec(0, amount, 0)
    return best[0]


def run_check():
    print("硬币找零自检（动态规划 vs 暴力枚举，并核对内置答案与贪心对照）\n")
    ok = True
    for i, lv in enumerate(LEVELS, 1):
        dp, used = dp_solve(lv["coins"], lv["amount"])
        brute = brute_solve(lv["coins"], lv["amount"])
        greedy = greedy_solve(lv["coins"], lv["amount"])
        sane = dp == brute == lv["answer"] and sum(used) == lv["amount"] and len(used) == dp
        ok &= sane
        print(f"[{'OK' if sane else 'FAIL'}] 第 {i} 关 {lv['title']}："
              f"面额 {lv['coins']}，金额 {lv['amount']}")
        print(f"      动态规划 {dp} 枚，暴力枚举 {brute} 枚，内置答案 {lv['answer']} 枚；"
              f"贪心法 {greedy} 枚；示例组合 {used}")
    print("\n自检结果：", "全部通过" if ok else "存在不一致")
    return 0 if ok else 1


# -----------------------------------------------------------
# 游戏流程
# -----------------------------------------------------------
def show_level(lv, idx):
    print("\n" + "=" * 52)
    print(f"第 {idx} 关 · {lv['title']}（{idx}/{len(LEVELS)}，20 分）")
    print("=" * 52)
    print(f"  可用硬币面额：{'、'.join(str(c) for c in lv['coins'])}（单位：分，每种无限多）")
    print(f"  要找零金额：{lv['amount']} 分")
    print("\n求：最少需要几枚硬币？（输入整数）")
    print("（h = 提示（-10 分）；q = 退出；回车 = 重看题目）")


def play():
    print("=" * 52)
    print(" 硬币找零收银台 —— 贪心与动态规划小游戏")
    print("=" * 52)
    print("5 关，每关 20 分，共 100 分。只需回答「最少几枚」。")
    print("命令：hint/h 提示（-10 分）｜q/quit/退出 结束｜回车 重看｜Ctrl+C 退出\n")

    score, hints = 0, 0
    for idx, lv in enumerate(LEVELS, 1):
        level_score, hint_used = 20, False
        show_level(lv, idx)
        greedy_count = greedy_solve(lv["coins"], lv["amount"])
        while True:
            try:
                raw = input("\n你的答案（枚）> ")
            except (EOFError, KeyboardInterrupt):
                print("\n\n已退出，当前累计得分 {} 分。".format(score))
                return
            cmd = raw.strip()
            if not cmd:
                show_level(lv, idx)
                continue
            low = cmd.lower()
            if low in ("q", "quit", "exit", "退出"):
                print("\n已退出，当前累计得分 {} 分。".format(score))
                return
            if low in ("h", "hint", "提示", "?"):
                if not hint_used:
                    hint_used = True
                    hints += 1
                    level_score = max(4, level_score - 10)
                print(f"\n[提示] {lv['hint']}")
                print(f"（本关当前 {level_score} 分）")
                continue

            try:
                val = int(cmd)
            except ValueError:
                print("请输入一个整数枚数，或 h 要提示。")
                continue

            if val == lv["answer"]:
                cnt, used = dp_solve(lv["coins"], lv["amount"])
                print(f"\n✅ 正确！最少就是 {cnt} 枚。")
                print(f"   一种最优组合：{' + '.join(str(c) for c in used)} = {lv['amount']}")
                print(f"   {lv['note']}")
                if greedy_count is not None and greedy_count != cnt:
                    print(f"   （贪心法在这一关会给出 {greedy_count} 枚，多用了 {greedy_count - cnt} 枚）")
                score += level_score
                print(f"本关得分 {level_score}，累计 {score}")
                break

            level_score = max(4, level_score - 8)
            print(f"\n❌ 不对（本关当前 {level_score} 分）。")
            if greedy_count is not None and val == greedy_count:
                print(f"   注意：{val} 枚正是「贪心法」（每次都用最大面额）的结果，"
                      f"但贪心不一定最优 —— 换一换最大面额试试。")
            else:
                print("   思路：先尽量用大面额，但别死守；比较几种组合的枚数。")

    print("\n" + "=" * 52)
    print(f"全部通关！总分 {score}/100（用过 {hints} 次提示）")
    if score >= 95:
        print("评级：零钱魔法师 —— 贪心的边界你摸得比收银台还清。")
    elif score >= 80:
        print("评级：资深收银员 —— 会主动验证贪心是否最优。")
    elif score >= 60:
        print("评级：实习生 —— 会用大面额，但偶尔被面额组合坑到。")
    else:
        print("评级：找零新手 —— 下次先把「最大面额不一定是解」记在心里。")
    print("=" * 52)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(run_check())
    play()
