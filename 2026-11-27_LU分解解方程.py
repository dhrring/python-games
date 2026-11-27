#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《LU 分解解方程》—— 每天一个 Python 交互小游戏 · 2026-11-27

说明
----
解 Ax = b 最省手算的路子，是先把 A 化成上三角（这一步就是 LU 分解里的 L，
中间可能要换行，也就是带主元交换的 PA = LU），再自下而上回代，把 x 求出来。
本游戏给你 5 个 3×3 方程组，要你亲手走一遍这个过程。

玩法
----
共 5 关，每关给一个方程组，回答两个问题：
  ① 解：按 x1, x2, x3 的顺序输入三个整数，用逗号或空格分开，如 1,0,-1
  ② 行列式：输入 |A| 的整数值

每题满分 10 分，5 关 × 2 题 = 100 分。
每题 3 次机会，答错一次扣 3 分；用提示扣 10 分（每题只能提示一次）。
所有解都是绝对值不超过 7 的整数，行列式也都是整数，可以用分数精确验算。

命令
----
  hint / h / 提示 / ?    看当前题的提示（扣 10 分）
  直接回车               重新显示题面
  q / quit / exit / 退出  随时退出
  Ctrl+C / Ctrl+D        安全退出

运行
----
  python3 2026-11-27_LU分解解方程.py            # 开始玩
  python3 2026-11-27_LU分解解方程.py --check    # 自检，不开玩

自检内容（--check）
------------------
  1. 每个矩阵用「代数余子式展开」和「消元法」两种方式算行列式，结果必须一致；
  2. 每个方程组用「Cramer 法则（分数）」和「带主元交换的高斯消元」两种方式求解，结果必须一致；
  3. 解必须是三个整数、且回代 A·x = b 残差为 0；
  4. 题目答案必须与关卡数据一致，行列式都不能为 0，五关互不相同；
  5. 解析器能正确吃掉各种输入格式，也能拒绝非法输入。
"""

import sys
from fractions import Fraction

LEVELS = [
    {
        "A": [[1, 3, 2], [1, 4, 0], [1, 2, 1]],
        "b": [-1, 1, 0],
        "x": [1, 0, -1],
        "det": -3,
        "note": "先热热身",
        "hint_vec": "第 1 行分别从第 2、3 行里减掉，x3 立刻现形。",
        "hint_det": "按第 3 列展开，那里有个 0，能少算一项。",
    },
    {
        "A": [[0, 2, -2], [-2, 2, 1], [-1, 4, 0]],
        "b": [2, 12, 14],
        "x": [-2, 3, 2],
        "det": 10,
        "note": "左上角是 0，必须换行",
        "hint_vec": "左上角是 0，先把第 1 行和第 2 行交换（部分主元法）。",
        "hint_det": "第 1 行有个 0，就按第 1 行展开。",
    },
    {
        "A": [[2, 1, -2], [-1, -2, 2], [4, -1, 0]],
        "b": [-6, 10, 10],
        "x": [2, -2, 4],
        "det": -6,
        "note": "消元时会出现分数",
        "hint_vec": "第 2 行 ×2 加到第 1 行、×4 加到第 3 行，第一列就消干净了。",
        "hint_det": "第 3 行末尾是 0，按第 3 行展开只有两项。",
    },
    {
        "A": [[-2, -1, 1], [1, 2, 0], [-1, 4, 1]],
        "b": [-6, 4, -2],
        "x": [4, 0, 2],
        "det": 3,
        "note": "有一个分量为 0",
        "hint_vec": "第 2 行是 x1 + 2x2 = 4，x2 很快就能定下来。",
        "hint_det": "第 2 行有个 0，按第 2 行展开。",
    },
    {
        "A": [[2, 0, -1], [3, 4, 2], [2, 3, 3]],
        "b": [-14, 12, 19],
        "x": [-4, 3, 6],
        "det": 11,
        "note": "最后一关，解的分量跨度最大",
        "hint_vec": "用第 1 行把第 2、3 行的首列消掉，再回代。",
        "hint_det": "第 1 行中间是 0，按第 1 行展开只有两项。",
    },
]

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}


# ---------------------------------------------------------------- 数学部分

def det_cofactor(A):
    """按第 1 行代数余子式展开。"""
    return (A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
            - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
            + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0]))


def det_elim(A):
    """消元法算行列式（分数运算，带行交换）。"""
    M = [[Fraction(v) for v in row] for row in A]
    det = Fraction(1)
    for k in range(3):
        pivot = None
        for i in range(k, 3):
            if M[i][k] != 0:
                pivot = i
                break
        if pivot is None:
            return Fraction(0)
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
            det = -det
        det *= M[k][k]
        for i in range(k + 1, 3):
            f = M[i][k] / M[k][k]
            for j in range(k, 3):
                M[i][j] -= f * M[k][j]
    return det


def solve_gauss(A, b):
    """带部分主元的高斯消元 + 回代，返回 Fraction 解向量。"""
    M = [[Fraction(A[r][c]) for c in range(3)] + [Fraction(b[r])] for r in range(3)]
    for k in range(3):
        pivot = None
        for i in range(k, 3):
            if M[i][k] != 0:
                pivot = i
                break
        if pivot is None:
            return None
        if pivot != k:
            M[k], M[pivot] = M[pivot], M[k]
        for i in range(k + 1, 3):
            f = M[i][k] / M[k][k]
            for j in range(k, 4):
                M[i][j] -= f * M[k][j]
    x = [None, None, None]
    for k in range(2, -1, -1):
        s = M[k][3] - sum(M[k][j] * x[j] for j in range(k + 1, 3))
        x[k] = s / M[k][k]
    return x


def solve_cramer(A, b):
    """Cramer 法则：x_i = det(A_i) / det(A)。"""
    d = det_cofactor(A)
    if d == 0:
        return None
    out = []
    for i in range(3):
        M = [row[:] for row in A]
        for r in range(3):
            M[r][i] = b[r]
        out.append(Fraction(det_cofactor(M), d))
    return out


def residual(A, x, b):
    """回代验证：A·x − b 的最大绝对值。"""
    worst = Fraction(0)
    for r in range(3):
        s = sum(A[r][c] * x[c] for c in range(3)) - b[r]
        if abs(s) > worst:
            worst = abs(s)
    return worst


# ---------------------------------------------------------------- 界面部分

def bar(ch="─", n=60):
    print(ch * n)


def show_system(idx, lv):
    A, b = lv["A"], lv["b"]
    bar()
    print("第 %d / %d 关    %s" % (idx, len(LEVELS), lv["note"]))
    bar()
    print("                 A                      x   =    b")
    labels = ("x1", "x2", "x3")
    for r in range(3):
        row = "  ".join("%4d" % A[r][c] for c in range(3))
        print("   [ %s ]   [ %s ]   [ %4d ]" % (row, labels[r].rjust(2), b[r]))
    print()


def parse_vec(text):
    """把 1,0,-1 / 1 0 -1 / (1,0,-1) / 1，0，-1 统一解析成三个整数。"""
    t = text.strip()
    for a, bb in (("（", "("), ("）", ")"), ("，", ","), ("－", "-"), ("−", "-")):
        t = t.replace(a, bb)
    t = t.strip("()[]{}")
    for ch in ",;/|、":
        t = t.replace(ch, " ")
    parts = [p for p in t.split() if p]
    if len(parts) != 3:
        return None
    try:
        return [int(p) for p in parts]
    except ValueError:
        return None


def parse_int(text):
    t = text.strip().replace("，", ",").replace("−", "-").replace("－", "-")
    t = t.replace(",", "").replace(" ", "")
    try:
        return int(t)
    except ValueError:
        return None


def read_line(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n（检测到中断，游戏结束）")
        raise SystemExit(0)


def ask_vector(idx, lv):
    """解向量题：返回本题得分。"""
    best = 10
    tries = 3
    hinted = False
    while True:
        raw = read_line("  解 (x1, x2, x3) = ").strip()
        low = raw.lower()
        if low in QUIT_WORDS:
            raise SystemExit(0)
        if not raw:
            show_system(idx, lv)
            continue
        if low in HINT_WORDS:
            if hinted:
                print("  提示只能用一次。")
                continue
            hinted = True
            best -= 10
            print("  提示：%s" % lv["hint_vec"])
            continue
        vec = parse_vec(raw)
        if vec is None:
            print("  格式不对，请输入三个整数，比如 1,0,-1")
            continue
        if vec == lv["x"]:
            print("  正确！ x = (%d, %d, %d)" % tuple(lv["x"]))
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 3
        if tries == 0:
            print("  机会用完了。正确答案是 x = (%d, %d, %d)。" % tuple(lv["x"]))
            return 0
        k = next(i for i in range(3) if vec[i] != lv["x"][i])
        way = "偏小" if vec[k] < lv["x"][k] else "偏大"
        print("  不对。第 %d 个分量%s；还剩 %d 次机会。" % (k + 1, way, tries))


def ask_det(idx, lv):
    """行列式题：返回本题得分。"""
    best = 10
    tries = 3
    hinted = False
    while True:
        raw = read_line("  det(A) = ").strip()
        low = raw.lower()
        if low in QUIT_WORDS:
            raise SystemExit(0)
        if not raw:
            show_system(idx, lv)
            continue
        if low in HINT_WORDS:
            if hinted:
                print("  提示只能用一次。")
                continue
            hinted = True
            best -= 10
            print("  提示：%s" % lv["hint_det"])
            continue
        val = parse_int(raw)
        if val is None:
            print("  请输入一个整数。")
            continue
        if val == lv["det"]:
            print("  正确！ det(A) = %d" % lv["det"])
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 3
        if tries == 0:
            print("  机会用完了。正确答案是 det(A) = %d。" % lv["det"])
            return 0
        way = "偏小" if val < lv["det"] else "偏大"
        print("  不对，%s；还剩 %d 次机会。%s" % (
            way, tries,
            "" if hinted else "（符号别丢，展开时注意正负号）"))


def rating(score):
    if score >= 95:
        return "满分在望，消元流程你已经吃透了。"
    if score >= 80:
        return "熟练，主元交换和回代都稳。"
    if score >= 60:
        return "及格，分数运算那一步可以再练两遍。"
    return "别急，先把「换行主元 + 回代」这两步手写一遍再来。"


def play():
    bar("═")
    print("  LU 分解解方程 · 每天一个 Python 交互小游戏")
    bar("═")
    print("共 %d 关，每关两题：解向量 + 行列式。" % len(LEVELS))
    print("输入 hint 看提示（扣 10 分），回车重看题面，q 退出。")
    print()
    total = 0
    try:
        for idx, lv in enumerate(LEVELS, 1):
            show_system(idx, lv)
            print("【问题 1】求这个方程组的解。")
            total += ask_vector(idx, lv)
            print()
            print("【问题 2】求系数矩阵 A 的行列式。")
            total += ask_det(idx, lv)
            print()
    except SystemExit:
        print()
        print("已退出，当前得分 %d / 100。" % total)
        return
    bar("═")
    print("  全部完成！总分 %d / 100" % total)
    print("  " + rating(total))
    bar("═")


# ---------------------------------------------------------------- 自检部分

def run_check():
    ok = True

    def need(cond, msg):
        nonlocal ok
        if cond:
            print("  [OK] " + msg)
        else:
            ok = False
            print("  [FAIL] " + msg)

    print("自检：LU 分解解方程")
    seen = []
    for i, lv in enumerate(LEVELS, 1):
        A, b, x = lv["A"], lv["b"], lv["x"]
        d1, d2 = det_cofactor(A), det_elim(A)
        need(Fraction(d1) == d2, "L%d 行列式两种算法一致（%s / %s）" % (i, d1, d2))
        need(d1 != 0, "L%d 行列式非零" % i)
        need(int(d1) == lv["det"], "L%d 存入的 det 与实算一致（%s）" % (i, lv["det"]))
        gx = solve_gauss(A, b)
        cx = solve_cramer(A, b)
        need(gx == cx, "L%d 高斯消元与 Cramer 解一致：%s" % (i, [str(v) for v in gx]))
        need(all(v.denominator == 1 for v in gx), "L%d 解都是整数" % i)
        need([int(v) for v in gx] == x, "L%d 关卡答案与实算一致：%s" % (i, x))
        need(residual(A, x, b) == 0, "L%d 回代残差为 0" % i)
        need(max(abs(v) for v in x) <= 7, "L%d 解分量绝对值不超过 7" % i)
        seen.append(tuple(tuple(r) for r in A))

    need(len(set(seen)) == len(seen), "五个矩阵互不相同")
    need(len(LEVELS) == 5, "共 5 关")

    # 解析器
    cases = ["1,0,-1", "1 0 -1", "(1,0,-1)", "1，0，-1", " 1, 0, -1 ", "1、0、-1"]
    need(all(parse_vec(c) == [1, 0, -1] for c in cases), "解向量解析器兼容 6 种写法")
    bad = ["1,0", "1,0,-1,2", "a,b,c", "", "1 0", "1,2"]
    need(all(parse_vec(c) is None for c in bad), "解向量解析器会拒绝非法输入")
    need(parse_int("-3") == -3 and parse_int(" 11 ") == 11 and parse_int("abc") is None,
         "整数解析器行为正常（负号可识别，非数字会被拒绝）")

    # 交互回归：用假 stdin 走一遍正确路径
    import io

    def fake_run(answers):
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin = io.StringIO("\n".join(answers) + "\n")
        sys.stdout = io.StringIO()
        try:
            play()
            return sys.stdout.getvalue()
        finally:
            sys.stdin, sys.stdout = old_in, old_out

    answers = []
    for lv in LEVELS:
        answers.append("%d,%d,%d" % tuple(lv["x"]))
        answers.append(str(lv["det"]))
    out = fake_run(answers)
    need("总分 100 / 100" in out, "全部答对时得满 100 分")

    # 全错路径
    answers = []
    for lv in LEVELS:
        answers += ["9,9,9", "9,9,9", "9,9,9", "999", "999", "999"]
    out = fake_run(answers)
    need("总分 0 / 100" in out, "全错时得 0 分（每题 3 次机会后揭晓答案）")

    # 提示 + 空行 + 非法输入
    answers = ["", "??", "hint", "%d,%d,%d" % tuple(LEVELS[0]["x"]),
               "hint", str(LEVELS[0]["det"])]
    answers += [a for lv in LEVELS[1:] for a in ("%d,%d,%d" % tuple(lv["x"]), str(lv["det"]))]
    out = fake_run(answers)
    need("总分 80 / 100" in out, "第 1 关两题都用提示，得 80 分")

    print()
    print("自检通过 ✅" if ok else "自检失败 ❌")
    return 0 if ok else 1


def main():
    if "--check" in sys.argv:
        raise SystemExit(run_check())
    play()


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        try:
            sys.stdout.close()
        except Exception:
            pass
