#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《NFA 转 DFA：子集构造》—— 每天一个 Python 交互小游戏 · 2026-11-27

说明
----
NFA（不确定的有穷自动机）允许一个状态对同一个字母有多条出边，还可以有 ε
转移（不吃字母就能跳过去）。它好写但不好跑，于是要把它变成 DFA：把「同时可能
待在的所有状态」打包成一个新状态，这一步叫子集构造。

有人以为只要数一数 NFA 有几个状态，就知道 DFA 有几个状态——那是错的。本游戏
就是让你亲手数清楚。

规则
----
  · 一个状态集合的 ε-闭包 = 从这些状态出发，只走 ε 边能到的所有状态（含自己）；
  · 读一个字母后，先对所有状态按该字母走一步，再取 ε-闭包；
  · 只统计从初态的 ε-闭包出发、真正走得到的子集（不可达的集合不算数）；
  · 接受语义：读完整串后，集合里只要含有任一接受态，就认为被接受。

玩法
----
共 5 关，每关回答两个问题：
  ① 子集构造后，DFA 有多少个状态？
  ② 给定字符串能否被这台 NFA 接受？（答 是 / 否）

每题满分 10 分，5 关 × 2 题 = 100 分。
每题 3 次机会，答错一次扣 4 分；用提示扣 10 分（每题只能提示一次）。

命令
----
  hint / h / 提示 / ?     看当前题的提示（扣 10 分）
  直接回车                重新显示这台 NFA
  q / quit / exit / 退出   随时退出
  Ctrl+C / Ctrl+D         安全退出

运行
----
  python3 2026-11-27_NFA转DFA子集构造.py
  python3 2026-11-27_NFA转DFA子集构造.py --check    # 自检，不开玩

自检内容（--check）
------------------
  1. 两种独立实现算可达子集数：BFS 增量构造 × 对全体幂集做不动点再筛可达；
  2. 子集构造得到的 DFA 必须确定（每个状态对每个字母恰好一条出边，缺边走陷阱态）；
  3.  语言等价：对长度 0～7 的全部字符串，NFA 逐路径模拟与 DFA 逐字母运行的
     接受结果必须逐个相同；
  4. 关卡答案与实际计算一致；每题都有「是」也有「否」，不会全是同一个答案；
  5. 转移表里出现的状态都必须在状态列表里，接受态不能是空集。
"""

import sys
from itertools import product

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}
YES_WORDS = {"是", "y", "yes", "1", "true", "接受", "能", "对"}
NO_WORDS = {"否", "n", "no", "0", "false", "不接受", "不能", "错"}

LEVELS = [
    {
        "states": ["q0", "q1", "q2"],
        "alpha": ["a", "b"],
        "delta": {
            ("q0", "a"): ["q0", "q1"],
            ("q0", "b"): ["q0"],
            ("q1", "b"): ["q2"],
            ("q2", "a"): ["q2"],
            ("q2", "b"): ["q2"],
        },
        "eps": {},
        "start": "q0",
        "accept": ["q2"],
        "count": 4,
        "q2_string": "aab",
        "q2_answer": True,
        "note": "没有 ε 边，先熟悉子集的概念（语言：以 ab 结尾）",
        "hint_count": "先看初态 {q0}，读 a 会同时落在 q0 和 q1 上，这就是子集的由来。",
        "hint_string": "从 {q0} 出发逐个字母走，把每次得到的集合写下来，别漏掉 q2 的自环。",
    },
    {
        "states": ["t0", "t1", "t2", "t3"],
        "alpha": ["a", "b"],
        "delta": {
            ("t0", "a"): ["t0"],
            ("t0", "b"): ["t0", "t1"],
            ("t1", "a"): ["t2"],
            ("t2", "a"): ["t0"],
            ("t2", "b"): ["t0", "t1"],
            ("t3", "a"): ["t3"],
            ("t3", "b"): ["t3"],
        },
        "eps": {"t0": ["t3"], "t1": ["t3"]},
        "start": "t0",
        "accept": ["t2"],
        "count": 3,
        "q2_string": "bb",
        "q2_answer": False,
        "note": "第一次遇到 ε 边：t3 是个吃什么都留在原地的陷阱",
        "hint_count": "初态 {t0} 的 ε-闭包把 t3 也包了进来，但 t3 只能原地打转，不会生出新集合。",
        "hint_string": "t3 无论读到什么都留在 t3，而 t3 不是接受态；真正决定成败的是 t2。",
    },
    {
        "states": ["p0", "p1", "p2", "p3"],
        "alpha": ["a", "b"],
        "delta": {
            ("p0", "a"): ["p0", "p1"],
            ("p0", "b"): ["p0"],
            ("p1", "a"): ["p2"],
            ("p1", "b"): ["p3"],
            ("p2", "a"): ["p2"],
            ("p2", "b"): ["p2"],
            ("p3", "a"): ["p3"],
            ("p3", "b"): ["p3"],
        },
        "eps": {"p1": ["p3"]},
        "start": "p0",
        "accept": ["p2", "p3"],
        "count": 5,
        "q2_string": "ba",
        "q2_answer": True,
        "note": "两个接受态，而且 ε 让 p1 同时能变成 p3",
        "hint_count": "p1 的 ε 边让含 p1 的集合自动带上 p3，两者要一起走。",
        "hint_string": "读到 b 时 p1 会走到 p3，而 p3 本身就是接受态。",
    },
    {
        "states": ["a0", "a1", "a2", "a3"],
        "alpha": ["a", "b"],
        "delta": {
            ("a0", "b"): ["a2", "a3"],
            ("a2", "a"): ["a2"],
            ("a2", "b"): ["a1"],
        },
        "eps": {"a0": ["a3"], "a1": ["a0"], "a3": ["a0"]},
        "start": "a0",
        "accept": ["a1", "a3"],
        "count": 6,
        "q2_string": "aaa",
        "q2_answer": False,
        "note": "ε 边形成环，子集会「长胖」",
        "hint_count": "a0、a1、a3 之间绕着 ε 边，闭包一算就会发现它们常常一起出现。",
        "hint_string": "注意 a0 只认 b，读 a 一步都走不动——先想想这串里有几个 b。",
    },
    {
        "states": ["b0", "b1", "b2", "b3"],
        "alpha": ["a", "b"],
        "delta": {
            ("b0", "b"): ["b2"],
            ("b2", "a"): ["b2", "b3"],
            ("b3", "a"): ["b1", "b2"],
            ("b3", "b"): ["b0", "b1"],
        },
        "eps": {"b1": ["b3"]},
        "start": "b0",
        "accept": ["b2", "b3"],
        "count": 7,
        "q2_string": "bab",
        "q2_answer": True,
        "note": "最后一关：7 个子集，慢慢来",
        "hint_count": "b3 是「枢纽」，它一出边就同时带来 b0 和 b1，子集数量会翻得很快。",
        "hint_string": "读到 b3 时 ε 边把 b3 自己也带来（b1→b3），所以含 b1 的集合都会带上接受态。",
    },
]


# ---------------------------------------------------------------- 自动机运算

def eclose(states, eps):
    """ε-闭包。"""
    seen = set(states)
    stack = list(seen)
    while stack:
        s = stack.pop()
        for t in eps.get(s, ()):
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return frozenset(seen)


def step_set(level, states, ch):
    """集合按一个字符走一步，并取 ε-闭包。"""
    nxt = set()
    for s in states:
        for t in level["delta"].get((s, ch), ()):
            nxt.add(t)
    return eclose(nxt, level["eps"])


def build_dfa(level):
    """子集构造：返回 (状态列表, 转移表, 初始态)。"""
    start = eclose({level["start"]}, level["eps"])
    order = [start]
    seen = {start}
    trans = {}
    i = 0
    while i < len(order):
        cur = order[i]
        i += 1
        for ch in level["alpha"]:
            nxt = step_set(level, cur, ch)
            trans[(cur, ch)] = nxt
            if nxt not in seen:
                seen.add(nxt)
                order.append(nxt)
    return order, trans, start


def build_dfa_fixpoint(level):
    """另一种实现：遍历整个幂集做不动点，再筛掉不可达的集合。"""
    start = eclose({level["start"]}, level["eps"])
    all_sets = set()
    for mask in range(1 << len(level["states"])):
        s = frozenset(level["states"][i] for i in range(len(level["states"]))
                       if mask >> i & 1)
        all_sets.add(s)
    closed = {}
    changed = True
    while changed:
        changed = False
        for s in all_sets:
            if s in closed:
                continue
            ok = True
            for ch in level["alpha"]:
                nxt = step_set(level, s, ch)
                if nxt not in all_sets:
                    ok = False
                    break
            if ok:
                closed[s] = True
                changed = True
    reach = {start}
    frontier = [start]
    while frontier:
        cur = frontier.pop()
        for ch in level["alpha"]:
            nxt = step_set(level, cur, ch)
            if nxt not in reach and nxt in closed:
                reach.add(nxt)
                frontier.append(nxt)
    return reach


def nfa_accepts(level, word):
    """NFA 语义：读完整串后集合里含接受态即接受。"""
    cur = eclose({level["start"]}, level["eps"])
    for ch in word:
        cur = step_set(level, cur, ch)
    return bool(cur & set(level["accept"]))


def dfa_accepts(level, word):
    """DFA 语义：沿子集走，落到含接受态的子集即接受。"""
    order, trans, start = build_dfa(level)
    cur = start
    for ch in word:
        cur = trans.get((cur, ch), frozenset())
    return bool(cur & set(level["accept"]))


def all_words(alpha, max_len):
    out = [""]
    for n in range(1, max_len + 1):
        for tup in product(alpha, repeat=n):
            out.append("".join(tup))
    return out


# ---------------------------------------------------------------- 界面部分

def bar(ch="─", n=62):
    print(ch * n)


def fmt_set(fs):
    if not fs:
        return "—"
    return "{" + ",".join(sorted(fs)) + "}"


def show_level(idx, lv):
    bar()
    print("第 %d / %d 关    %s" % (idx, len(LEVELS), lv["note"]))
    bar()
    print("状态集：%s    字母表：{%s}    初态：%s    接受态：%s"
          % (", ".join(lv["states"]), ", ".join(lv["alpha"]),
             lv["start"], "{" + ",".join(lv["accept"]) + "}"))
    print()
    header = "   %-6s %-14s %-14s %s" % ("状态", "输入 a", "输入 b", "ε 边")
    print(header)
    print("   " + "-" * 50)
    for s in lv["states"]:
        ca = fmt_set(lv["delta"].get((s, "a"), ()))
        cb = fmt_set(lv["delta"].get((s, "b"), ()))
        ce = fmt_set(lv["eps"].get(s, ()))
        print("   %-6s %-14s %-14s %s" % (s, ca, cb, ce))
    print()
    print("（— 表示没有这条边；ε 边不吃字母，可以随时免费通过）")


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


def ask_count(idx, lv):
    best = 10
    tries = 3
    hinted = False
    while True:
        raw = read_line("  DFA 有几个状态？ ").strip()
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
            print("  提示：%s" % lv["hint_count"])
            continue
        n = parse_int(raw)
        if n is None:
            print("  请输入一个整数。")
            continue
        if n == lv["count"]:
            order, _, _ = build_dfa(lv)
            print("  正确！一共 %d 个子集（含陷阱态的话是 %d）。"
                  % (lv["count"], lv["count"]))
            print("  它们分别是：")
            for s in order:
                mark = " ← 初态" if s == eclose({lv["start"]}, lv["eps"]) else ""
                if s & set(lv["accept"]):
                    mark += " （接受）"
                print("    %s%s" % (fmt_set(s), mark))
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 4
        if tries == 0:
            print("  机会用完了。正确答案是 %d 个状态。" % lv["count"])
            return 0
        tip = "偏多，有些集合其实走不到" if n > lv["count"] else "偏少，还有子集没被数出来"
        print("  不对，%s；还剩 %d 次机会。" % (tip, tries))


def ask_string(idx, lv):
    best = 10
    tries = 3
    hinted = False
    word = lv["q2_string"]
    while True:
        raw = read_line("  字符串 “%s” 能被接受吗？(是/否) " % word).strip()
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
            print("  提示：%s" % lv["hint_string"])
            continue
        ans = parse_bool(raw)
        if ans is None:
            print("  请回答 是 或 否。")
            continue
        if ans == lv["q2_answer"]:
            print("  正确！这条串%s被接受。" % ("能" if ans else "不能"))
            print("  路径走过来，最后落在：%s" % run_trace(lv, word))
            pts = max(best, 0)
            print("  本题得 %d 分。" % pts)
            return pts
        tries -= 1
        best -= 4
        if tries == 0:
            print("  机会用完了。正确答案是：%s" % ("接受" if lv["q2_answer"] else "不接受"))
            return 0
        print("  不对；还剩 %d 次机会。%s" % (
            tries, "" if hinted else "记住 ε 边是白走的，不能忘。"))


def run_trace(level, word):
    """把逐字母经过的集合打出来，便于复盘。"""
    cur = eclose({level["start"]}, level["eps"])
    out = [fmt_set(cur)]
    for ch in word:
        cur = step_set(level, cur, ch)
        out.append(fmt_set(cur))
    return " → ".join(out)


def rating(score):
    if score >= 95:
        return "满分在望，ε-闭包你已经不会漏了。"
    if score >= 80:
        return "很稳，子集的「长胖」规律你摸清了。"
    if score >= 60:
        return "及格，建议把每关的集合列表手抄一遍再对照。"
    return "别急：先求 ε-闭包，再逐字母扩散，最后只数走得到的集合。"


def play():
    bar("═")
    print("  NFA 转 DFA：子集构造 · 每天一个 Python 交互小游戏")
    bar("═")
    print("共 %d 关，每关两题：DFA 状态数 + 某串是否被接受。" % len(LEVELS))
    print("输入 hint 看提示（扣 10 分），回车重看转移表，q 退出。")
    print()
    total = 0
    try:
        for idx, lv in enumerate(LEVELS, 1):
            show_level(idx, lv)
            print("【问题 1】按子集构造，从初态可达的 DFA 状态有多少个？")
            total += ask_count(idx, lv)
            print()
            print("【问题 2】字符串判断。")
            total += ask_string(idx, lv)
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

    print("自检：NFA 转 DFA 子集构造")
    need(len(LEVELS) == 5, "共 5 关")
    need(len({tuple(lv["states"]) + (lv["q2_string"],) for lv in LEVELS}) == 5, "五关数据互不相同")

    counts = []
    for i, lv in enumerate(LEVELS, 1):
        # 数据自洽
        names = set(lv["states"])
        bad = [k for k in lv["delta"] if k[0] not in names or any(t not in names for t in lv["delta"][k])]
        need(not bad, "L%d 转移表里没有未知状态 %s" % (i, bad))
        need(all(s in names for s in lv["eps"]) and all(t in names for v in lv["eps"].values() for t in v),
             "L%d ε 边只涉及合法状态" % i)
        need(lv["accept"] and all(s in names for s in lv["accept"]), "L%d 接受态非空且合法" % i)
        need(all(ch in lv["alpha"] for (s, ch) in lv["delta"].keys()), "L%d 转移只用了字母表里的字母" % i)

        order, trans, start = build_dfa(lv)
        reach2 = build_dfa_fixpoint(lv)
        need(len(order) == lv["count"], "L%d 子集数 = %d（关卡标注 %d）" % (i, len(order), lv["count"]))
        need(len(reach2) == len(order), "L%d 不动点法也得 %d 个可达集合" % (i, len(reach2)))
        need(set(order) == reach2, "L%d 两种实现给出的集合完全相同" % i)
        counts.append(len(order))

        # 确定性
        need(all(trans.get((s, ch)) is not None for s in order for ch in lv["alpha"]),
             "L%d 每个状态对每个字母都有唯一出边（缺边即空集陷阱）" % i)
        need(all(t in set(order) for t in trans.values()), "L%d 所有出边都落在已构造的状态里" % i)

        # 语言等价：长度 0..7 全部字符串
        words = all_words(lv["alpha"], 7)
        mism = [w for w in words if nfa_accepts(lv, w) != dfa_accepts(lv, w)]
        need(not mism, "L%d 对 %d 条字符串 NFA 模拟与 DFA 运行结果一致" % (i, len(words)))

        # 关卡答案
        need(nfa_accepts(lv, lv["q2_string"]) == lv["q2_answer"],
             "L%d 题目串 “%s” 的实际结果 = %s" % (i, lv["q2_string"], lv["q2_answer"]))
        need(len(lv["q2_string"]) <= 4, "L%d 题目串长度适合口算" % i)

    need(len(set(counts)) == len(counts), "五关状态数互不相同：%s" % counts)
    need(min(counts) >= 3 and max(counts) <= 7, "状态数都在 3～7 之间，符合口算量")

    need(any(lv["q2_answer"] for lv in LEVELS) and any(not lv["q2_answer"] for lv in LEVELS),
         "接受与不接受两种答案都有")

    # ε-闭包边界
    lv = LEVELS[0]
    need(eclose(set(), lv["eps"]) == frozenset(), "空集闭包为空")
    need(eclose({"q1"}, lv["eps"]) == frozenset({"q1"}), "没有 ε 边的状态闭包是它自己")

    # 解析器
    need(parse_int("4") == 4 and parse_int("abc") is None, "整数解析器正常")
    need(parse_bool("是") and parse_bool("接受") and parse_bool("否") is False
         and parse_bool("不接受") is False, "是/否解析器覆盖多种写法")
    need(parse_bool("也许") is None, "模糊回答会被拒绝")

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
        answers.append(str(lv["count"]))
        answers.append("是" if lv["q2_answer"] else "否")
    out = fake_run(answers)
    need("总分 100 / 100" in out, "全部答对时得满 100 分")

    answers = []
    for lv in LEVELS:
        wrong_bool = "否" if lv["q2_answer"] else "是"
        answers += [str(lv["count"] + 1)] * 3 + [wrong_bool] * 3
    out = fake_run(answers)
    need("总分 0 / 100" in out, "全错时得 0 分")

    answers = ["", "hint", str(LEVELS[0]["count"]), "hint",
               "是" if LEVELS[0]["q2_answer"] else "否"]
    answers += [a for lv in LEVELS[1:] for a in (str(lv["count"]), "是" if lv["q2_answer"] else "否")]
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
