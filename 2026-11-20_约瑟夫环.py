# -*- coding: utf-8 -*-
"""
约瑟夫环 · Josephus Problem
====================================================
公元 67 年，约瑟夫斯和 40 名战友被罗马军团围在一处洞穴里。他们决定集体自尽：
所有人围成一圈，从 1 号开始报数，报到 3 的人出局，下一个人接着从 1 报，
如此循环，直到只剩最后一个人。

这个问题流传了一千九百年，今天它有精确的递推解：
    记 J(n, k) 为「n 人、报到 k 出局」时最后幸存者的编号（编号从 1 开始）
    J(1, k) = 1
    J(n, k) = (J(n-1, k) + k) mod n　　（取余后若为 0 则记作 n）

含义很漂亮：把「n 人」拆成「第一个出局的人」和「剩下的 n-1 人重新编号」，
幸存者在 n-1 人里的编号，只要整体后移 k 位，就换回了 n 人里的原始编号。

四关：前三关求幸存者 / 反求报数，第四关要你算出局顺序。
  hint  递推公式（−15 分）
  sim   看前 3 个出局的人（−10 分，只对 12 人以内有效）
  q     退出
每关 25 分，满分 100。

运行：python3 2026-11-20_约瑟夫环.py
"""

import math

LEVELS = [
    {"mode": "survivor", "n": 10, "k": 3, "answer": None,
     "note": "入门：10 个人，报到 3 出局。先手算一遍，再用公式核对。"},
    {"mode": "survivor", "n": 41, "k": 3, "answer": None,
     "note": "约瑟夫斯与 40 名战友的典故。41 人、报 3，最后剩下的编号是他自己算出来的。"},
    {"mode": "find_k", "n": 12, "k": None, "answer": None,
     "note": "反问题：我想让 5 号活下来，最小的报数 k 应该设成多少？（k ≥ 1，越小越公平）"},
    {"mode": "kth_out", "n": 20, "k": 7, "index": 5, "answer": None,
     "note": "不只要活下来：20 人、报 7，第 5 个出局的是几号？"},
]


def josephus_last(n, k):
    """递推求最后幸存者编号（1-based）。"""
    r = 0
    for i in range(2, n + 1):
        r = (r + k) % i
    return r + 1


def elimination_order(n, k):
    """用循环列表真实模拟，返回完整出局顺序（1-based 编号）。"""
    people = list(range(1, n + 1))
    idx = 0
    out = []
    while people:
        idx = (idx + k - 1) % len(people)
        out.append(people.pop(idx))
    return out


def smallest_k_for(n, target, limit=500):
    """反求最小的 k，使 n 人局里 target 号成为幸存者。"""
    for k in range(1, limit + 1):
        if josephus_last(n, k) == target:
            return k
    return None


def resolve_answers():
    for lv in LEVELS:
        if lv["mode"] == "survivor":
            lv["answer"] = josephus_last(lv["n"], lv["k"])
        elif lv["mode"] == "find_k":
            lv["answer"] = smallest_k_for(lv["n"], 5)
        elif lv["mode"] == "kth_out":
            lv["answer"] = elimination_order(lv["n"], lv["k"])[lv["index"] - 1]


def run_level(idx, lv):
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + lv["note"])

    if lv["mode"] == "survivor":
        print(f"\n  {lv['n']} 人围圈，报到 {lv['k']} 的人出局。")
        prompt = "  最后幸存者是几号？> "
    elif lv["mode"] == "find_k":
        print(f"\n  {lv['n']} 人围圈，目标：让 5 号成为最后的幸存者。")
        prompt = "  最小的报数 k 是多少？> "
    else:
        print(f"\n  {lv['n']} 人围圈，报到 {lv['k']} 的人出局。")
        prompt = f"  第 {lv['index']} 个出局的是几号？> "

    penalty = 0
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return 0, None
        if low == "hint":
            penalty = max(penalty, 15)
            print("  递推公式：J(1,k)=1，J(n,k) = (J(n-1,k)+k) mod n（结果为 0 记作 n）。")
            print("  反问题怎么用：把 k 从 1 往上试，直到 J(n,k) 正好等于目标编号。")
            print(f"  （本关封顶 {25 - penalty} 分）")
            continue
        if low == "sim":
            if lv.get("k") is None:
                print("  这一关没有固定的 k，没法模拟。先用 hint 看思路。")
                continue
            if lv["n"] > 12:
                print("  sim 只支持 12 人以内（否则就成抄答案了）。")
                continue
            penalty = max(penalty, 10)
            order = elimination_order(lv["n"], lv["k"])
            print("  前 3 个出局的人：" + " → ".join(str(x) for x in order[:3]))
            print(f"  （本关封顶 {25 - penalty} 分）")
            continue

        if not raw.lstrip("-").isdigit():
            print("  请输入一个整数编号。")
            continue

        guess = int(raw)
        if guess == lv["answer"]:
            print("  ✅ 正确！")
            return max(5, 25 - penalty), True

        if lv["mode"] == "find_k":
            if guess < 1:
                print("  k 至少是 1。")
                continue
            got = josephus_last(lv["n"], guess)
            print(f"  ❌ k={guess} 时，幸存者是 {got} 号，不是 5 号。往哪儿调？"
                  " 试着让 k 大一些或小一些，看幸存者编号怎么跳。")
        elif lv["mode"] == "survivor":
            print(f"  ❌ 不是 {guess} 号。想想：第 1 个出局的是 {lv['k'] if lv['k'] <= lv['n'] else (lv['k'] - 1) % lv['n'] + 1} 号，"
                  "剩下的人怎么重新编号？")
        else:
            order = elimination_order(lv["n"], lv["k"])
            print(f"  ❌ 不对。先自己数前两个出局的：{order[0]} 号、{order[1]} 号，再往下推。")
        penalty = max(penalty, 8)
        print(f"  （本关封顶 {25 - penalty} 分）")


def play():
    print("=" * 62)
    print("      🔄 约瑟夫环 · Josephus Problem")
    print("=" * 62)
    print("一圈人报数，报到 k 的出去，最后剩下的那个人就是幸存者。")

    resolve_answers()

    # 开局自检：递推公式必须与逐个模拟完全一致
    for n in range(1, 41):
        for k in range(1, 21):
            assert josephus_last(n, k) == elimination_order(n, k)[-1], f"递推与模拟不符：n={n}, k={k}"
    # 答案自检
    assert LEVELS[0]["answer"] == 4, LEVELS[0]["answer"]          # 10 人报 3
    assert LEVELS[1]["answer"] == 31, LEVELS[1]["answer"]         # 41 人报 3（约瑟夫斯）
    assert LEVELS[3]["answer"] == 17, LEVELS[3]["answer"]         # 20 人报 7，第 5 个出局
    k = LEVELS[2]["answer"]
    assert k is not None and josephus_last(12, k) == 5, f"反问题无解：{k}"
    for smaller in range(1, k):
        assert josephus_last(12, smaller) != 5, f"k={smaller} 也能让 5 号活，说明不是最小解"
    print(f"  自检：递推公式 vs 真实模拟（n≤40、k≤20）全部一致；"
          f"10人报3→4号，41人报3→31号，20人报7第5个出局→17号，12人让5号活的最小k={k}。")

    total = 0
    done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 25}")
    if total >= 90:
        print("  🏆 你已经会用 J(n,k)=(J(n-1,k)+k) mod n 这把钥匙，正着算、反着算都行。")
    elif total >= 50:
        print("  👍 记住「把一圈人拆成第一个出局者 + 剩下 n-1 人」，递推就是这么来的。")
    else:
        print("  🙂 先手动排 5 个人、k=2 的小例子，看着编号怎么往后挪，公式就不神秘了。")
    print("=" * 62)


if __name__ == "__main__":
    play()
