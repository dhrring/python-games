# -*- coding: utf-8 -*-
"""
银行家算法 · 死锁避免模拟
====================================================
你是银行家，手里有三类资源（A、B、C），借给 5 个客户（P0~P4）。
每个客户事先报了一个最大需求量（Max），已经借走了一部分（Allocation），
剩下的差额就是它还会再借的额度（Need）。

每当有客户提出新的借款请求，你要回答一个问题：
    这笔钱现在能不能借？
借出去的判断标准不是「够不够」，而是「借完之后，全系统还能不能按某种顺序
把所有客户都结清」——如果存在这样的顺序（安全序列），就借；如果借完会
陷入谁都不够、谁都结不了的死局，就必须让它等一等。

游戏内命令：
  state  查看当前资源分配表
  need   查看各客户剩余需求
  help   规则提示
  q      退出

计分：每次判断正确 +100，判断错误 −30，共 5 次请求。
运行：python3 2026-11-14_银行家算法.py
"""

N_PROC, N_RES = 5, 3
RES_NAMES = ["A", "B", "C"]

ALLOCATION = [
    [0, 1, 0],  # P0
    [2, 0, 0],  # P1
    [3, 0, 2],  # P2
    [2, 1, 1],  # P3
    [0, 0, 2],  # P4
]

MAXIMUM = [
    [7, 5, 3],
    [3, 2, 2],
    [9, 0, 2],
    [2, 2, 2],
    [4, 3, 3],
]

TOTAL = [10, 5, 7]


def need_matrix(alloc, mx=None):
    mx = mx or MAXIMUM
    return [[mx[i][j] - alloc[i][j] for j in range(N_RES)] for i in range(N_PROC)]


def available(alloc):
    used = [sum(alloc[i][j] for i in range(N_PROC)) for j in range(N_RES)]
    return [TOTAL[j] - used[j] for j in range(N_RES)]


def is_safe(alloc):
    """安全性算法：能否找到一个让所有进程依次完成的安全序列。"""
    work = available(alloc)
    need = need_matrix(alloc)
    finish = [False] * N_PROC
    seq = []
    while len(seq) < N_PROC:
        found = False
        for i in range(N_PROC):
            if finish[i]:
                continue
            if all(need[i][j] <= work[j] for j in range(N_RES)):
                for j in range(N_RES):
                    work[j] += alloc[i][j]
                finish[i] = True
                seq.append(f"P{i}")
                found = True
                break
        if not found:
            return None
    return seq


def print_state(alloc):
    av = available(alloc)
    need = need_matrix(alloc)
    print("\n  " + "-" * 58)
    print(f"  {'进程':<6}{'Allocation':>16}{'Max':>14}{'Need':>14}")
    for i in range(N_PROC):
        print(f"  P{i:<5}{str(alloc[i]):>16}{str(MAXIMUM[i]):>14}{str(need[i]):>14}")
    print(f"  当前可分配（Available）：A={av[0]} B={av[1]} C={av[2]}")
    print("  " + "-" * 58)


# (进程编号, 请求向量)
REQUESTS = [
    (1, [1, 0, 2]),   # 经典例题：借出后仍安全
    (0, [0, 2, 0]),   # 资源够，但借完会进入不安全状态
    (3, [0, 1, 0]),   # 小额请求，安全
    (4, [2, 0, 1]),   # 需求合法，但当前可分配的资源不够
    (1, [0, 2, 0]),   # 刚好满足 P1 的剩余需求，借完它就能结清
]


def decide(alloc, pid, req):
    """返回 (能否借, 理由)。能否借 = 请求不超需求 且 不超可用 且 借后仍安全。"""
    need = need_matrix(alloc)
    av = available(alloc)
    if any(req[j] > need[pid][j] for j in range(N_RES)):
        return False, "请求超过了它剩余的 Need，属于非法请求"
    if any(req[j] > av[j] for j in range(N_RES)):
        return False, "当前可分配的资源不够，只能让它等待"
    trial = [row[:] for row in alloc]
    for j in range(N_RES):
        trial[pid][j] += req[j]
    seq = is_safe(trial)
    if seq is None:
        return False, "借出去之后系统找不到安全序列，会陷入死锁风险"
    return True, "借出后仍存在安全序列：" + " → ".join(seq)


def play():
    global ALLOCATION
    print("=" * 62)
    print("      🏦 银行家算法 · 死锁避免模拟")
    print("=" * 62)
    print("资源总量：A=10 B=5 C=7。你要判断每一笔请求该不该批准。")
    alloc = [row[:] for row in ALLOCATION]
    print_state(alloc)
    print("  初始状态是安全的，安全序列之一：" + " → ".join(is_safe(alloc)))

    score = 0
    for idx, (pid, req) in enumerate(REQUESTS, 1):
        print("\n" + "-" * 62)
        print(f"  第 {idx} 笔：P{pid} 申请 A={req[0]} B={req[1]} C={req[2]}")
        print("  批准还是拒绝？（y=批准 / n=拒绝，s=看状态，h=看规则）")
        can, reason = decide(alloc, pid, req)
        while True:
            try:
                raw = input("  > ").strip().lower()
            except EOFError:
                print("\n输入中断，提前结算。")
                return report(score)
            if raw in ("y", "yes", "批准", "是"):
                user_yes = True
                break
            if raw in ("n", "no", "拒绝", "否"):
                user_yes = False
                break
            if raw == "s":
                print_state(alloc)
                continue
            if raw == "h":
                print("  规则：请求不能超过 Need；不能超过 Available；借完之后必须仍能排出安全序列。")
                continue
            if raw in ("q", "quit"):
                return report(score)
            print("  输入 y / n（s 看状态，h 看规则，q 退出）。")

        if user_yes == can:
            print("  ✅ 判断正确。" + reason)
            score += 100
        else:
            print(f"  ❌ 判断错误。正确答案：{'批准' if can else '拒绝'}——{reason}")
            score -= 30

        if can:
            for j in range(N_RES):
                alloc[pid][j] += req[j]
            print(f"  已批准，P{pid} 现在持有 {alloc[pid]}。")
        else:
            print(f"  P{pid} 继续等待。")

    print_state(alloc)
    return report(score)


def report(score):
    print("\n" + "=" * 62)
    print(f"  结算：{score} 分（5 笔请求，每对 +100、每错 −30）")
    if score >= 400:
        print("  🏆 稳健的银行家：你分得清「资源够」和「系统安全」。")
    elif score >= 200:
        print("  👍 大致有数，注意「借完以后还安不安全」这一步容易被忽略。")
    else:
        print("  🙂 记住核心：判断依据永远是借出后的安全性检查，不是当下余额。")
    print("=" * 62)
    return score


if __name__ == "__main__":
    play()
