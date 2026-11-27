#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《卡诺图化简》—— 每天一个 Python 交互小游戏 · 2026-11-27

说明
----
给你一个三变量布尔函数（变量 A、B、C，最小项按 ABC 的二进制编号，
例如 m5 = 101 = A·B'·C），让你判断它的「最简与或式」长什么样。

「最简与或式」的约定：只用素蕴含项（已经不能再合并的乘积项）去覆盖所有
最小项，并且乘积项个数最少。若存在多种同样最少的结果，只要答得对就算对。

玩法
----
共 5 关，每关回答两个问题：
  ① 最少需要几个乘积项？
  ② 是否存在某个最简与或式包含指定的那一项？（答 是 / 否）

每题满分 10 分，5 关 × 2 题 = 100 分。
每题 3 次机会，答错一次扣 3 分；用提示扣 10 分（每题只能提示一次）。

命令
----
  hint / h / 提示 / ?     看当前题的提示（扣 10 分）
  直接回车                重画卡诺图
  q / quit / exit / 退出   随时退出
  Ctrl+C / Ctrl+D         安全退出

运行
----
  python3 2026-11-27_卡诺图化简.py
  python3 2026-11-27_卡诺图化简.py --check    # 自检，不开玩

自检内容（--check）
------------------
  1. Quine–McCluskey「逐对合并」求素蕴含项，与「暴力判素」（枚举全部 26 个
     乘积项、看有没有严格更大的覆盖仍在函数内）两种方法结果必须一致；
  2. 最少项数用两种搜索各自穷举：QM 素蕴含项组合 × 全乘积项组合（不限制为
     素项），二者最少项数必须相同；
  3. 每一个最简式都必须真值表全等（8 行逐行比对），少一项就盖不全；
  4. 「是否存在某个最简式包含某项」的答案必须与穷举结果一致；
  5. 卡诺图画法与最小项列表必须自洽（每格的值 = 是否属于最小项集合）。
"""

import sys

VARS = ("A", "B", "C")
ALL_MINTERMS = tuple(range(8))
N_LEVELS_SHOWN = 5

LEVELS = [
    {
        "ones": [0, 1, 3, 7],
        "k": 2,
        "term": "BC",
        "contains": True,
        "note": "先认认卡诺图的列顺序",
        "hint_k": "看 BC=11 那一整列（上下两格都是 1），四个格能合成一项。",
        "hint_t": "BC 在卡诺图上就是整列 BC=11；这关最简式只有一个，答得出来。",
    },
    {
        "ones": [0, 1, 2, 3, 6],
        "k": 2,
        "term": "BC'",
        "contains": True,
        "note": "整行都是 1 的时候最省事",
        "hint_k": "A=0 那一整行四个格全是 1，一行就能合成一个只有两个字母的项。",
        "hint_t": "剩下那个孤零零的 1 在哪一行、哪一列？它自己就够组成第二个项。",
    },
    {
        "ones": [0, 1, 2, 5, 7],
        "k": 3,
        "term": "B'C",
        "contains": True,
        "note": "开始出现多种最简式",
        "hint_k": "这关有三个 1 落单，必须三项才能盖住；先找最大的圈。",
        "hint_t": "认真想：两个不同的三项最简式，可能一项相同、另一项不同。",
    },
    {
        "ones": [1, 3, 4, 6, 7],
        "k": 3,
        "term": "A'B'",
        "contains": False,
        "note": "有的项看着顺眼，却不属于任何最简式",
        "hint_k": "先数 1 的个数：五个 1，至少得三项才盖得住。",
        "hint_t": "A'B' 覆盖的格子里有没有 0？只要被它覆盖的格不全为 1，它就不能用。",
    },
    {
        "ones": [0, 2, 3, 4, 5, 7],
        "k": 3,
        "term": "AB'",
        "contains": True,
        "note": "左右边界也要能圈起来",
        "hint_k": "六个 1，少数几项就够；注意卡诺图左右是相邻的。",
        "hint_t": "AB' 覆盖的是哪两列？把它们在图上标出来，再看剩下的 1。",
    },
]

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}
YES_WORDS = {"是", "y", "yes", "1", "true", "有", "存在", "对", "包含"}
NO_WORDS = {"否", "n", "no", "0", "false", "没有", "不存在", "不", "错", "不含"}


# ---------------------------------------------------------------- 布尔运算

def minterm_bits(m):
    """最小项编号 -> (A, B, C)。"""
    return ((m >> 2) & 1, (m >> 1) & 1, m & 1)


def bits_to_val(bits):
    """(A, B, C) -> 蕴含项里的取值编码（第 0 位是 A）。"""
    return bits[0] | (bits[1] << 1) | (bits[2] << 2)


def val_to_bits(val):
    return (val & 1, (val >> 1) & 1, (val >> 2) & 1)


def imp_cover(imp):
    """一个蕴含项覆盖哪些最小项。imp = (mask, val)。"""
    mask, val = imp
    bits = val_to_bits(val)
    out = set()
    for m in ALL_MINTERMS:
        ok = True
        for i in range(3):
            if mask >> i & 1:
                if minterm_bits(m)[i] != bits[i]:
                    ok = False
                    break
        if ok:
            out.add(m)
    return frozenset(out)


def imp_label(imp):
    """(mask, val) -> "A'B'C" 这样的字符串。"""
    mask, val = imp
    bits = val_to_bits(val)
    parts = []
    for i, name in enumerate(VARS):
        if mask >> i & 1:
            parts.append(name if bits[i] else name + "'")
    return "".join(parts)


def label_to_imp(label):
    """字符串 -> (mask, val)，用于核对关卡里手写的项。"""
    label = label.replace(" ", "").replace("·", "").replace("*", "").replace(" ", "")
    mask = 0
    val = 0
    i = 0
    while i < len(label):
        ch = label[i].upper()
        if ch not in VARS:
            return None
        idx = VARS.index(ch)
        mask |= 1 << idx
        if i + 1 < len(label) and label[i + 1] == "'":
            i += 2
        else:
            val |= 1 << idx
            i += 1
    return (mask, val) if mask else None


def all_products():
    """全部 26 个非空乘积项。"""
    out = []
    for mask in range(1, 8):
        n = bin(mask).count("1")
        for val in range(8):
            if any(((val >> i) & 1) and not (mask >> i & 1) for i in range(3)):
                continue
            out.append((mask, val))
    return out


def primes_by_merge(ones):
    """Quine–McCluskey：逐对合并，合不动的就是素蕴含项。"""
    ones = set(ones)
    work = [(7, bits_to_val(minterm_bits(m))) for m in sorted(ones)]
    merged_any = set()
    primes = []
    while work:
        used = set()
        new = []
        for i in range(len(work)):
            for j in range(i + 1, len(work)):
                a, b = work[i], work[j]
                if a[0] != b[0]:
                    continue
                diff = a[1] ^ b[1]
                if bin(diff).count("1") == 1 and (a[0] & diff):
                    m = (a[0] & ~diff, a[1] & ~diff)
                    used.add(i)
                    used.add(j)
                    if m not in new:
                        new.append(m)
        for idx, imp in enumerate(work):
            if idx not in used and imp_cover(imp) <= ones:
                primes.append(imp)
        work = new
    # 去重、去掉被别的素项严格包含的
    uniq = []
    for p in primes:
        if p not in uniq:
            uniq.append(p)
    out = []
    for p in uniq:
        c = imp_cover(p)
        if any(q != p and c < imp_cover(q) for q in uniq):
            continue
        out.append(p)
    return sorted(out, key=lambda x: (-len(imp_cover(x)), imp_label(x)))


def primes_bruteforce(ones):
    """另一种判素法：枚举全部乘积项，看谁的覆盖严格包含它。"""
    ones = set(ones)
    prods = [p for p in all_products() if imp_cover(p) <= ones]
    out = []
    for p in prods:
        c = imp_cover(p)
        if not any(q != p and c < imp_cover(q) for q in prods):
            out.append(p)
    return sorted(set(out), key=lambda x: (-len(imp_cover(x)), imp_label(x)))


def min_covers(ones, primes):
    """在素蕴含项里穷举覆盖，返回 (最小项数, 全部最简式)。"""
    ones = set(ones)
    from itertools import combinations
    for k in range(1, len(primes) + 1):
        found = []
        for comb in combinations(range(len(primes)), k):
            cov = set()
            for i in comb:
                cov |= imp_cover(primes[i])
            if cov == ones:
                found.append([primes[i] for i in comb])
        if found:
            return k, found
    return None, []


def min_size_all_products(ones):
    """不限制素项，穷举全部乘积项的最少项数。"""
    from itertools import combinations
    ones = set(ones)
    cands = [p for p in all_products() if imp_cover(p) <= ones]
    if not ones:
        return 0, []
    for k in range(1, len(cands) + 1):
        for comb in combinations(range(len(cands)), k):
            cov = set()
            for i in comb:
                cov |= imp_cover(cands[i])
            if cov == ones:
                return k, [cands[i] for i in comb]
    return None, []


def evaluate(expr, m):
    """在最小项 m 处的值：任一乘积项满足即为 1。"""
    bits = minterm_bits(m)
    for imp in expr:
        mask, val = imp
        vb = val_to_bits(val)
        if all(not (mask >> i & 1) or bits[i] == vb[i] for i in range(3)):
            return 1
    return 0


# ---------------------------------------------------------------- 界面部分

def bar(ch="─", n=60):
    print(ch * n)


def kmap_string(ones):
    """画 2×4 的卡诺图，列顺序 00 / 01 / 11 / 10（格雷码）。"""
    order = [0, 1, 3, 2]  # BC 的取值顺序
    lines = []
    lines.append("        BC=00  01  11  10")
    for a in (0, 1):
        cells = []
        for bc in order:
            m = (a << 2) | bc
            cells.append(" %s " % ("1" if m in ones else "0"))
        lines.append("   A=%d  " % a + " ".join(cells) + "   ")
    return "\n".join(lines)


def show_level(idx, lv):
    ones = set(lv["ones"])
    bar()
    print("第 %d / %d 关    %s" % (idx, len(LEVELS), lv["note"]))
    bar()
    print("F(A,B,C) = Σm(%s)" % ", ".join(str(m) for m in lv["ones"]))
    print("变量顺序 A B C，最小项编号 = ABC 的二进制值")
    print()
    print(kmap_string(ones))
    print()
    print("卡诺图相邻关系：左右相邻（00 与 10），上下相邻（A=0 与 A=1）")


def read_line(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\n（检测到中断，游戏结束）")
        raise SystemExit(0)


def parse_int(raw):
    t = raw.strip().replace("，", "").replace(" ", "")
    try:
        return int(t)
    except ValueError:
        return None


def parse_bool(raw):
    t = raw.strip().replace("。", "").replace("！", "").lower()
    if t in YES_WORDS:
        return True
    if t in NO_WORDS:
        return False
    return None


def ask_k(idx, lv):
    best = 10
    tries = 3
    hinted = False
    while True:
        raw = read_line("  最少需要几个乘积项？ ").strip()
        low = raw.lower()
        if low in QUIT_WORDS:
            raise SystemExit(0)
        if not raw:
            show_level(idx, lv)
            continue
        if low in HINT_WORDS:
            if hinted:
                print("  提示只能用一次。")
                continue
            hinted = True
            best -= 10
            print("  提示：%s" % lv["hint_k"])
            continue
        n = parse_int(raw)
        if n is None:
            print("  请输入一个整数。")
            continue
        if n == lv["k"]:
            print("  正确！最少 %d 项。" % lv["k"])
            k, covers = min_covers(lv["ones"], primes_by_merge(lv["ones"]))
            print("  最简式之一： F = %s" % " + ".join(imp_label(i) for i in covers[0]))
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 3
        if tries == 0:
            print("  机会用完了。正确答案是 %d 项。" % lv["k"])
            return 0
        tip = "偏多，还能再合" if n > lv["k"] else "偏少，这样盖不全所有 1"
        print("  不对，%s；还剩 %d 次机会。" % (tip, tries))


def ask_term(idx, lv):
    imp = label_to_imp(lv["term"])
    best = 10
    tries = 3
    hinted = False
    while True:
        raw = read_line("  是否存在某个最简式包含 %s ？(是/否) " % lv["term"]).strip()
        low = raw.lower()
        if low in QUIT_WORDS:
            raise SystemExit(0)
        if not raw:
            show_level(idx, lv)
            continue
        if low in HINT_WORDS:
            if hinted:
                print("  提示只能用一次。")
                continue
            hinted = True
            best -= 10
            print("  提示：%s" % lv["hint_t"])
            continue
        ans = parse_bool(raw)
        if ans is None:
            print("  请回答 是 或 否。")
            continue
        if ans == lv["contains"]:
            print("  正确！ %s" % ("存在这样的最简式。" if ans else "任何最简式都不会包含它。"))
            k, covers = min_covers(lv["ones"], primes_by_merge(lv["ones"]))
            print("  本关全部最简式共 %d 种：" % len(covers))
            for cov in covers:
                print("    F = %s" % " + ".join(imp_label(i) for i in cov))
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 3
        if tries == 0:
            print("  机会用完了。正确答案是：%s" % ("存在" if lv["contains"] else "不存在"))
            return 0
        print("  不对；还剩 %d 次机会。%s" % (
            tries, "" if hinted else "想想它覆盖的那些格子是不是全为 1。"))


def rating(score):
    if score >= 95:
        return "满分在望，素蕴含项和最小覆盖都被你吃透了。"
    if score >= 80:
        return "很稳，卡诺图的相邻关系没看错。"
    if score >= 60:
        return "及格，建议把每关的最简式手推一遍再对照。"
    return "别急：先画图，再圈最大块，最后检查有没有多余的项。"


def play():
    bar("═")
    print("  卡诺图化简 · 每天一个 Python 交互小游戏")
    bar("═")
    print("共 %d 关，每关两题：最少乘积项数 + 某一项是否可能出现在最简式里。" % len(LEVELS))
    print("输入 hint 看提示（扣 10 分），回车重画卡诺图，q 退出。")
    print()
    total = 0
    try:
        for idx, lv in enumerate(LEVELS, 1):
            show_level(idx, lv)
            print("【问题 1】最简与或式最少需要几个乘积项？")
            total += ask_k(idx, lv)
            print()
            print("【问题 2】是否存在某个最简与或式，其中包含项 %s ？" % lv["term"])
            total += ask_term(idx, lv)
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

    print("自检：卡诺图化简")
    need(len(LEVELS) == N_LEVELS_SHOWN, "共 5 关")
    need(len({tuple(sorted(lv["ones"])) for lv in LEVELS}) == 5, "五个函数互不相同")

    for i, lv in enumerate(LEVELS, 1):
        ones = set(lv["ones"])
        pm = primes_by_merge(ones)
        pb = primes_bruteforce(ones)
        need([imp_label(p) for p in pm] == [imp_label(p) for p in pb],
             "L%d 两种判素法一致：%s" % (i, [imp_label(p) for p in pm]))

        k, covers = min_covers(ones, pm)
        need(k == lv["k"], "L%d 最少项数 = %d（穷举得 %d）" % (i, lv["k"], k))
        kb, _ = min_size_all_products(ones)
        need(kb == k, "L%d 不限制素项的最少项数也等于 %d" % (i, k))

        # 每个最简式必须真值表全等，且任意去掉一项都盖不全
        for cov in covers:
            need(all(evaluate(cov, m) == (1 if m in ones else 0) for m in ALL_MINTERMS),
                 "L%d 最简式 %s 真值表全等" % (i, " + ".join(imp_label(c) for c in cov)))
            for drop in range(len(cov)):
                sub = cov[:drop] + cov[drop + 1:]
                miss = [m for m in ones if evaluate(sub, m) != 1]
                need(bool(miss), "L%d 去掉任一项都会盖不全（缺 %s）" % (i, miss))

        # 项是否可能出现在某个最简式里
        tgt = label_to_imp(lv["term"])
        need(tgt is not None, "L%d 关卡里的项 %s 能解析" % (i, lv["term"]))
        exists = any(tgt in cov for cov in covers)
        need(exists == lv["contains"],
             "L%d 「含 %s」的答案 = %s（穷举 %d 种最简式）" % (
                 i, lv["term"], lv["contains"], len(covers)))
        # 被问的项如果不存在于任何最简式，必须是因为它不是素蕴含项（覆盖了 0）
        if not exists:
            need(not (imp_cover(tgt) <= ones),
                 "L%d 项 %s 之所以进不了最简式，是因为它盖到了 0" % (i, lv["term"]))
        else:
            need(imp_cover(tgt) <= ones, "L%d 项 %s 覆盖的格子都在函数内" % (i, lv["term"]))
        need(len(covers) >= 1, "L%d 至少有一种最简式" % i)

    # 卡诺图渲染必须与最小项集合自洽
    for i, lv in enumerate(LEVELS, 1):
        s = kmap_string(set(lv["ones"]))
        lines = s.splitlines()
        order = [0, 1, 3, 2]
        good = True
        for a in (0, 1):
            cells = lines[a + 1].split()[-4:]
            for j, bc in enumerate(order):
                m = (a << 2) | bc
                if cells[j] != ("1" if m in set(lv["ones"]) else "0"):
                    good = False
        need(good, "L%d 卡诺图与最小项列表一致" % i)

    # 标注答案必须一真一假都有
    need(any(lv["contains"] for lv in LEVELS) and any(not lv["contains"] for lv in LEVELS),
         "存在性和不存在性的题目都有，不能全是同一个答案")

    # 解析器
    need(label_to_imp("A'B'C") == (7, 4), "项解析：A'B'C -> (7,4)")
    need(label_to_imp("BC") == (6, 6), "项解析：BC -> (6,6)")
    need(label_to_imp("A'B'") == (3, 0), "项解析：A'B'")
    need(label_to_imp("") is None and label_to_imp("D") is None, "非法项会被拒绝")
    need(label_to_imp("A·B'·C") == (7, 5), "带分隔符的写法也能解析")
    need(parse_bool("是") and parse_bool("Y") and parse_bool("存在")
         and parse_bool("否") is False and parse_bool("不存在") is False,
         "是/否 解析器覆盖多种写法")
    need(parse_bool("maybe") is None, "模糊回答会被拒绝")

    # 交互回归
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
        answers.append(str(lv["k"]))
        answers.append("是" if lv["contains"] else "否")
    out = fake_run(answers)
    need("总分 100 / 100" in out, "全部答对时得满 100 分")

    answers = []
    for lv in LEVELS:
        wrong_bool = "否" if lv["contains"] else "是"
        answers += [str(lv["k"] + 1)] * 3 + [wrong_bool] * 3
    out = fake_run(answers)
    need("总分 0 / 100" in out, "全错时得 0 分")

    answers = ["", "hint", str(LEVELS[0]["k"]), "hint", "是"]
    answers += [a for lv in LEVELS[1:] for a in (str(lv["k"]), "是" if lv["contains"] else "否")]
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
