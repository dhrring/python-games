# -*- coding: utf-8 -*-
"""
化学方程式配平 · Balance the Equation
====================================================
配平是什么意思？——在化学方程式两边，**每种元素的原子个数必须相等**。
例如  H₂ + O₂ → H₂O  左边 2 个 H、2 个 O，右边只有 2 个 H、1 个 O，没平。
写成 2 H₂ + O₂ → 2 H₂O 才平。

它其实是道线性代数题：
  设每个物质的系数为 x₁、x₂ …，对每种元素列一个方程「左边原子数 = 右边原子数」，
  得到一个齐次方程组。它的解空间如果只有 1 维，就唯一确定各物质的**最简整数比**。

本游戏共 5 关，每关一个方程式。你输入各物质的系数（按方程式里从左到右的顺序），
程序会真的去数每一种元素的原子，告诉你哪边多了、还差多少。
最简整数系数（系数之间没有公因数）才算对。

命令：hint（提示第一个系数，−6 分）　q（退出）
格式：系数之间用空格或逗号隔开，例如  2 1 2

运行：python3 2026-11-19_化学方程式配平.py
"""

from fractions import Fraction
from math import gcd


LEVELS = [
    {
        "left": ["H2", "O2"], "right": ["H2O"],
        "note": "最基本的燃烧反应，水是唯一的产物。",
    },
    {
        "left": ["Fe", "O2"], "right": ["Fe2O3"],
        "note": "铁生锈（生成三氧化二铁）。注意 O 在右边是 3 个。",
    },
    {
        "left": ["C3H8", "O2"], "right": ["CO2", "H2O"],
        "note": "丙烷完全燃烧。先配 C，再配 H，最后用 O 收尾最省心。",
    },
    {
        "left": ["KMnO4", "HCl"], "right": ["KCl", "MnCl2", "Cl2", "H2O"],
        "note": "实验室制氯气。有 6 个物质、5 种元素，Cl 在右边出现三次，别漏。",
    },
    {
        "left": ["Cu", "HNO3"], "right": ["Cu(NO3)2", "NO", "H2O"],
        "note": "铜与稀硝酸反应。带括号的 Cu(NO3)2 要按 1 个 Cu、2 个 N、6 个 O 来数。",
    },
]


def parse_formula(s):
    """把化学式解析成 {元素: 原子个数}，支持括号与下标。"""
    stack = [{}]
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "(":
            stack.append({})
            i += 1
        elif ch == ")":
            if len(stack) < 2:
                raise ValueError(f"括号不匹配：{s}")
            group = stack.pop()
            i += 1
            num = ""
            while i < len(s) and s[i].isdigit():
                num += s[i]
                i += 1
            mult = int(num) if num else 1
            for el, v in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + v * mult
        elif ch.isupper():
            el = ch
            i += 1
            while i < len(s) and s[i].islower():
                el += s[i]
                i += 1
            num = ""
            while i < len(s) and s[i].isdigit():
                num += s[i]
                i += 1
            stack[-1][el] = stack[-1].get(el, 0) + (int(num) if num else 1)
        else:
            raise ValueError(f"化学式里有看不懂的字符「{ch}」：{s}")
    if len(stack) != 1:
        raise ValueError(f"括号不匹配：{s}")
    return stack[0]


def atom_table(left, right, coeffs):
    """按系数统计两边各元素的原子数，返回 {元素: (左, 右)}。"""
    n = len(left)
    table = {}
    for i, sp in enumerate(left + right):
        sign = +1 if i < n else -1
        for el, cnt in parse_formula(sp).items():
            l, r = table.get(el, (0, 0))
            if sign > 0:
                l += cnt * coeffs[i]
            else:
                r += cnt * coeffs[i]
            table[el] = (l, r)
    return table


def solve_coeffs(left, right):
    """解齐次方程组，得到最简正整数系数；解空间不唯一时报错。"""
    species = left + right
    n = len(species)
    parsed = [parse_formula(s) for s in species]
    elements = sorted({e for p in parsed for e in p})

    M = []
    for e in elements:
        row = []
        for j, p in enumerate(parsed):
            v = Fraction(p.get(e, 0))
            row.append(v if j < len(left) else -v)
        M.append(row)

    # 高斯-约当消元（分数精确运算）
    rows = len(M)
    pivots = []
    r = 0
    for c in range(n):
        piv = None
        for i in range(r, rows):
            if M[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        M[r], M[piv] = M[piv], M[r]
        pv = M[r][c]
        M[r] = [v / pv for v in M[r]]
        for i in range(rows):
            if i != r and M[i][c] != 0:
                f = M[i][c]
                M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        pivots.append(c)
        r += 1
        if r == rows:
            break

    free = [c for c in range(n) if c not in pivots]
    if len(free) != 1:
        raise ValueError(f"该方程式配平不唯一（自由度为 {len(free)}）")

    x = [Fraction(0)] * n
    x[free[0]] = Fraction(1)
    for i, pc in enumerate(pivots):
        x[pc] = -sum(M[i][j] * x[j] for j in range(n) if j != pc)

    den = 1
    for v in x:
        den = den * v.denominator // gcd(den, v.denominator)
    ints = [int(v * den) for v in x]
    g = 0
    for v in ints:
        g = gcd(g, abs(v))
    ints = [v // g for v in ints]
    if all(v < 0 for v in ints):
        ints = [-v for v in ints]
    if any(v <= 0 for v in ints):
        raise ValueError("求解出的系数不是全正数，方程式可能有误")
    return ints


def show(eq, coeffs=None):
    parts = []
    for i, sp in enumerate(eq["left"]):
        c = "" if coeffs is None or coeffs[i] == 1 else str(coeffs[i])
        parts.append(f"{c}{sp}")
    left_txt = " + ".join(parts)
    parts = []
    for j, sp in enumerate(eq["right"]):
        k = len(eq["left"]) + j
        c = "" if coeffs is None or coeffs[k] == 1 else str(coeffs[k])
        parts.append(f"{c}{sp}")
    return f"    {left_txt}  →  " + " + ".join(parts)


def imbalance_report(eq, coeffs):
    table = atom_table(eq["left"], eq["right"], coeffs)
    bad = []
    for el, (l, r) in sorted(table.items()):
        if l != r:
            bad.append(f"{el}：左边 {l} 个，右边 {r} 个（{'多' if l > r else '少'} {abs(l - r)} 个）")
    return bad


def run_level(idx, eq):
    n = len(eq["left"]) + len(eq["right"])
    ref = solve_coeffs(eq["left"], eq["right"])

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关　（{n} 个物质）")
    print("=" * 62)
    print("  " + eq["note"])
    print(show(eq))
    print(f"\n  请依次输入 {n} 个系数（最简整数比）。")

    score = 20
    hinted = False
    while True:
        try:
            raw = input("  系数 > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "hint":
            if not hinted:
                hinted = True
                score = max(6, score - 6)
            print(f"  提示：第一个系数是 {ref[0]}。（本关上限 {score} 分）")
            continue

        parts = raw.replace(",", " ").replace("，", " ").split()
        if len(parts) != n:
            print(f"  要输入 {n} 个系数，现在给了 {len(parts)} 个。")
            continue
        if any(not p.isdigit() for p in parts):
            print("  系数必须是正整数（分子式里的下标不用你输入）。")
            continue
        vals = [int(p) for p in parts]
        if any(v <= 0 for v in vals):
            print("  系数必须 ≥ 1。")
            continue

        bad = imbalance_report(eq, vals)
        if bad:
            print("  ❌ 原子数不平衡：")
            for b in bad[:5]:
                print("    · " + b)
            score = max(6, score - 4)
            print(f"  （本关当前上限 {score} 分）")
            continue

        g = 0
        for v in vals:
            g = gcd(g, v)
        if g != 1:
            print(f"  ⚠ 原子数平了，但系数 {vals} 还能同时除以 {g}，不是最简整数比。")
            score = max(6, score - 4)
            continue

        if vals != ref:
            print(f"  ❌ 原子数虽然平了，但标准解是 {ref}。检查一下是不是同一组比例的等价写法？")
            score = max(6, score - 4)
            continue

        print(f"  ✅ 配平正确！{show(eq, vals).strip()}")
        print(f"  本关 {score} 分。")
        return score, True


def play():
    print("=" * 62)
    print("      🧪 化学方程式配平")
    print("=" * 62)
    print("让等号两边每种元素的原子个数都相等，并且系数取最简整数比。")

    # 开局自检：全部方程式的标准系数必须全正、互质、逐元素守恒
    for i, eq in enumerate(LEVELS, 1):
        ref = solve_coeffs(eq["left"], eq["right"])
        assert all(v >= 1 for v in ref), f"第 {i} 关系数不全为正：{ref}"
        g = 0
        for v in ref:
            g = gcd(g, v)
        assert g == 1, f"第 {i} 关系数不是最简：{ref}"
        table = atom_table(eq["left"], eq["right"], ref)
        for el, (l, r) in table.items():
            assert l == r, f"第 {i} 关 {el} 不平衡：{l} vs {r}"
            assert l > 0
        print(f"  自检 L{i}：{ref}  →  " + show(eq, ref).strip())

    total = 0
    for i, eq in enumerate(LEVELS):
        sc, finished = run_level(i, eq)
        total += sc
        if finished is None:
            break

    print("\n" + "=" * 62)
    print(f"  结算：总分 {total}/100")
    if total >= 88:
        print("  🏆 你用「元素守恒 + 最简整数比」稳稳配平了所有方程式。")
    elif total >= 60:
        print("  👍 技巧：先配出现在最少的元素（常是 C、H），最后用 O 收尾。")
    else:
        print("  🙂 记住顺序：先看每种元素在两边各几个，再找最小公倍数。")
    print("=" * 62)


if __name__ == "__main__":
    play()
