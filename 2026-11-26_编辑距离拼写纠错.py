#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""编辑距离拼写纠错（终端交互小游戏）

【玩法】
终端会给你一个拼错的英文单词，以及 4 个候选单词。你要回答两件事：
  1. 哪个候选单词和拼错的词「编辑距离」最小（输入序号 1~4）；
  2. 这个最小编辑距离具体是多少（输入整数）。
每关两部分各 10 分，全部 5 关满分 100。

【编辑距离（Levenshtein 距离）】
把一个词变成另一个词，允许三种操作：插入一个字符、删除一个字符、替换一个字符。
所需的最少操作次数就是编辑距离。

【命令】
  hint / h / 提示 / ?  ：看当前题的思路提示（每题第一次用扣 10 分）
  q / quit / exit / 退出 ：直接退出
  直接回车            ：重新显示当前题目
  Ctrl+C / Ctrl+D     ：安全退出

【运行】
  python3 2026-11-26_编辑距离拼写纠错.py
  python3 2026-11-26_编辑距离拼写纠错.py --check   # 自检（不进入游戏）
"""

import sys

# 每关：拼错的词 + 4 个候选词（第 1 个是真正想表达的词，但答案按距离算，不看位置）
LEVELS = [
    {"typo": "occured", "cands": ["occurred", "cured", "secured", "obscured"]},
    {"typo": "seperate", "cands": ["separate", "desperate", "sedate", "sabotage"]},
    {"typo": "photogragh", "cands": ["photograph", "photography", "paragraph", "photocopy"]},
    {"typo": "tommorow", "cands": ["tomorrow", "tomorrows", "borrow", "narrow"]},
    {"typo": "responsability", "cands": ["responsibility", "responsibly", "possibility", "responsive"]},
]

MAX_TRY = 3          # 每个小问最多试 3 次
WRONG_PENALTY = 3    # 答错一次扣 3 分
HINT_PENALTY = 10    # 用提示扣 10 分
POINTS = 10          # 每个小问满分 10 分

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}


def lev(a, b):
    """Levenshtein 编辑距离（二维 DP，插入/删除/替换代价均为 1）。"""
    m, n = len(a), len(b)
    d = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        d[i][0] = i
    for j in range(n + 1):
        d[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
    return d[m][n]


def distances(level):
    """返回 [(候选词, 距离), ...]，顺序与 cands 一致。"""
    return [(w, lev(level["typo"], w)) for w in level["cands"]]


def best_index(level):
    """距离最小的候选（0 基下标）。数据已保证最小值唯一。"""
    ds = distances(level)
    return min(range(len(ds)), key=lambda i: ds[i][1])


def ask(prompt):
    """读一行输入，返回去空白小写串；EOF 返回 None。"""
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def ask_int(prompt, attempts):
    """反复要一个整数，返回 (值 or None, 剩余次数)。None 表示放弃（退出/次数用尽）。"""
    for _ in range(attempts):
        raw = ask(prompt)
        if raw is None:
            return "EOF", 0
        if raw in QUIT_WORDS:
            return "QUIT", 0
        if raw == "":
            continue
        if raw in HINT_WORDS:
            print("提示：编辑距离 = 插入/删除/替换一个字符的最少次数。")
            print("      可以列一张表：第 i 个前缀变第 j 个前缀要几步，取「删、插、换」三者最小再加。")
            return "HINT", attempts
        try:
            return int(raw), attempts
        except ValueError:
            print("  ✗ 请输入一个整数。")
    return None, 0


def play():
    print("=" * 46)
    print("        编辑距离拼写纠错 · 5 关满分 100")
    print("=" * 46)
    print("找出与拼错的词「编辑距离」最小的候选词，并说出距离。")
    print("命令：hint 提示 ｜ q 退出 ｜ 回车 重看题目")
    print()

    total = 0
    for idx, level in enumerate(LEVELS, 1):
        cands = level["cands"]
        ds = distances(level)
        ans_i = best_index(level)
        ans_d = ds[ans_i][1]
        used_hint = False
        attempts = MAX_TRY
        got_i = None

        while got_i is None:
            print(f"—— 第 {idx} 关 ——")
            print(f"拼错的词：「{level['typo']}」")
            for k, w in enumerate(cands, 1):
                print(f"  {k}. {w}")
            v, attempts = ask_int(f"哪个候选最接近？（1~4，余 {attempts} 次）> ", attempts)
            if v == "QUIT":
                print("\n已退出。")
                return
            if v == "EOF":
                print("输入已结束，游戏退出。")
                return
            if v == "HINT":
                if not used_hint:
                    used_hint = True
                    print("  （提示已用，本关 -10 分）")
                continue
            if v is None:
                print("  ✗ 次数用完了，本关第一问记 0 分。")
                break
            if not 1 <= v <= len(cands):
                print("  ✗ 请输入 1~4 之间的序号。")
                continue
            if v - 1 == ans_i:
                got_i = v - 1
                pts = max(0, POINTS - (HINT_PENALTY if used_hint else 0))
                total += pts
                print(f"  ✓ 正确！就是 {cands[ans_i]}（本问 +{pts} 分）")
            else:
                print(f"  ✗ 不是 {cands[v - 1]}。再想想，它和原词差得更多。")

        # 第二问：距离数值
        attempts = MAX_TRY
        got_d = None
        hint_used_2 = False
        while got_i is not None and got_d is None:
            print(f"「{cands[ans_i]}」与「{level['typo']}」的编辑距离是多少？(输入整数)")
            v, attempts = ask_int(f"编辑距离 = ?（余 {attempts} 次）> ", attempts)
            if v == "QUIT":
                print("\n已退出。")
                return
            if v == "EOF":
                print("输入已结束，游戏退出。")
                return
            if v == "HINT":
                if not hint_used_2:
                    hint_used_2 = True
                    print("  （提示已用，本问 -10 分）")
                    print("  提示：逐位对齐比较，统计最少的插入/删除/替换次数。")
                continue
            if v is None:
                print(f"  ✗ 次数用完，本问记 0 分。正确答案是 {ans_d}。")
                break
            if v == ans_d:
                got_d = v
                pts = max(0, POINTS - (HINT_PENALTY if hint_used_2 else 0))
                total += pts
                print(f"  ✓ 正确！编辑距离 = {ans_d}（本问 +{pts} 分）")
            else:
                print("  ✗ 不对，再数一遍插入/删除/替换的次数。")

        print("  本关各候选的距离：", end="")
        print("  ".join(f"{w}={d}" for w, d in ds))
        print(f"  当前总分：{total}\n")

    print("=" * 46)
    print(f"最终得分：{total} / 100")
    if total >= 90:
        print("评级：S —— 拼写纠错大师，距离算得又快又准。")
    elif total >= 70:
        print("评级：A —— 很稳，个别长词上还能再细抠一下。")
    elif total >= 50:
        print("评级：B —— 基本会了，注意别被「看起来像」的词带偏。")
    else:
        print("评级：C —— 建议先手推两三个小例子，把 DP 表的感觉找回来。")
    print("=" * 46)


def check():
    """自检：换一种实现复算距离 + 校验每关答案唯一 + 校验边界性质。"""
    ok = True

    def lev_rec(a, b):
        from functools import lru_cache

        @lru_cache(maxsize=None)
        def f(i, j):
            if i == 0:
                return j
            if j == 0:
                return i
            if a[i - 1] == b[j - 1]:
                return f(i - 1, j - 1)
            return 1 + min(f(i - 1, j), f(i, j - 1), f(i - 1, j - 1))

        return f(len(a), len(b))

    # 1) 两种实现逐对一致
    for lv in LEVELS:
        for w in lv["cands"]:
            if lev(lv["typo"], w) != lev_rec(lv["typo"], w):
                ok = False
                print("✗ DP 与递归实现不一致：", lv["typo"], w)

    # 2) 每关最小距离唯一，且答案不重复出现
    for idx, lv in enumerate(LEVELS, 1):
        ds = distances(lv)
        m = min(d for _, d in ds)
        winners = [w for w, d in ds if d == m]
        if len(winners) != 1:
            ok = False
            print(f"✗ 第 {idx} 关最小距离不唯一：{ds}")
        if best_index(lv) != ds.index((winners[0], m)):
            ok = False
            print(f"✗ 第 {idx} 关 best_index 与最小距离不一致")
        print(f"  第{idx}关 {lv['typo']:>15} → 答案 {winners[0]}={m}，全部距离 {ds}")

    # 3) 边界性质
    cases = [("", "", 0), ("", "abc", 3), ("abc", "", 3), ("abc", "abc", 0),
             ("kitten", "sitting", 3), ("flaw", "lawn", 2), ("a", "b", 1)]
    for a, b, want in cases:
        if lev(a, b) != want or lev_rec(a, b) != want:
            ok = False
            print(f"✗ 边界用例失败：lev({a!r},{b!r}) 期望 {want}，得 {lev(a, b)}/{lev_rec(a, b)}")

    # 4) 三角不等式（抽样）
    sample = [w for lv in LEVELS for w in lv["cands"]]
    for x in sample[:6]:
        for y in sample[:6]:
            if lev(x, y) > lev(x, "kitten") + lev("kitten", y):
                ok = False
                print("✗ 三角不等式失败：", x, y)

    # 5) 满分路径
    if 5 * 2 * POINTS != 100:
        ok = False
        print("✗ 满分不是 100")

    print("自检通过 ✅" if ok else "自检失败 ❌")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--check", "-c", "check"):
        return check()
    try:
        play()
    except (BrokenPipeError, KeyboardInterrupt):
        # 输出被管道截断（如 | head）时不打印 traceback，安静退出
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
