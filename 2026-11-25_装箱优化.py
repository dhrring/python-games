'''装箱优化 —— 用最少的箱子装走全部货物

玩法
  共 5 关，每关一车货：给出箱子容量和每件货物的重量。
  你的任务：算出「至少需要几个箱子」才能全部装下（每箱不超容量）。
  每关 20 分，最多猜 3 次；猜错扣 8 分并告诉你方向（偏多/偏少）。
  提示命令：hint（或 h、提示、?），每关一次，扣 10 分，给出总重与理论下限。
  直接回车可重新看一遍关卡；q 退出。

运行
  python 2026-11-25_装箱优化.py
  python 2026-11-25_装箱优化.py --check   # 自检：子集DP 与 分支限界求解器交叉验证、装法回灌
'''

import sys

LEVELS = [
    (10, [6, 6, 4, 4, 3, 3], '先把 6 和 4 配对最省。'),
    (12, [5, 5, 5, 5, 4, 4, 4], '别急着把两个 5 塞一起，剩下的空间可能谁都进不去。'),
    (12, [7, 7, 6, 6, 5, 5, 4, 4], '总重 44：先按容量下限估个数，再看能不能把每箱都拼到 10 以上。'),
    (15, [9, 8, 8, 7, 6, 6, 5, 5, 4, 3], '总重 61，容量 15：总空间比货重多出的余量极少，几乎每箱都得接近装满。'),
    (20, [11, 9, 8, 7, 6, 5, 4, 4, 3, 3], '10 件货，容量 20：先凑出整 20 的箱子最省事。'),
]


def lower_bound(items, cap):
    total = sum(items)
    return (total + cap - 1) // cap


def min_bins_dp(items, cap):
    n = len(items)
    full = (1 << n) - 1
    sums = [0] * (1 << n)
    for mask in range(1, 1 << n):
        low = mask & -mask
        idx = low.bit_length() - 1
        sums[mask] = sums[mask ^ low] + items[idx]
    fits = [sums[mask] <= cap for mask in range(1 << n)]
    INF = n + 1
    f = [INF] * (1 << n)
    choice = [0] * (1 << n)
    f[0] = 0
    for mask in range(1, 1 << n):
        sub = mask
        while sub:
            if fits[sub] and f[mask ^ sub] + 1 < f[mask]:
                f[mask] = f[mask ^ sub] + 1
                choice[mask] = sub
            sub = (sub - 1) & mask
    return f[full], choice, full


def exact_bins_dfs(items, cap):
    order = sorted(items, reverse=True)
    best = [len(order)]
    lb = lower_bound(order, cap)

    def dfs(i, loads, used):
        if used >= best[0]:
            return
        if i == len(order):
            best[0] = used
            return
        w = order[i]
        seen = set()
        for b in range(used):
            if loads[b] in seen:
                continue
            seen.add(loads[b])
            if loads[b] + w <= cap:
                loads[b] += w
                dfs(i + 1, loads, used)
                loads[b] -= w
        if used + 1 <= cap and used + 1 < best[0]:
            loads.append(w)
            dfs(i + 1, loads, used + 1)
            loads.pop()

    dfs(0, [], 0)
    return best[0], lb


def ffd(items, cap):
    bins = []
    for w in sorted(items, reverse=True):
        for i, load in enumerate(bins):
            if load + w <= cap:
                bins[i] += w
                break
        else:
            bins.append(w)
    return len(bins)


def reconstruct(items, cap):
    ans, choice, full = min_bins_dp(items, cap)
    packs = []
    mask = full
    while mask:
        sub = choice[mask]
        packs.append([items[i] for i in range(len(items)) if sub >> i & 1])
        mask ^= sub
    return ans, packs


def ask(prompt):
    try:
        s = input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None
    s = s.strip()
    if s.lower() in ('q', 'quit', 'exit', '退出'):
        return None
    return s


def show_level(no, cap, items):
    print('  箱子容量: %d   货物 %d 件: %s' % (cap, len(items), ' '.join(str(x) for x in sorted(items, reverse=True))))
    print('  货物总重: %d' % sum(items))
    print('  【第 %d 关】至少要几个箱子？' % no)


def play():
    score = 0
    print('=' * 58)
    print('  装箱优化 · 5 关 · 满分 100')
    print('  h 提示（每关一次，-10）  q 退出  空行重看关卡')
    print('=' * 58)
    for no, (cap, items, tip) in enumerate(LEVELS, 1):
        print()
        show_level(no, cap, items)
        print('  当前得分: %d' % score)
        ans, packs = reconstruct(items, cap)
        hint_used = False
        tries = 0
        while True:
            s = ask('  开几个箱子 > ')
            if s is None:
                print('中途退出，当前得分 %d。' % score)
                return
            if s == '':
                show_level(no, cap, items)
                continue
            if s.lower() in ('h', 'hint', '提示', '?'):
                if hint_used:
                    print('  本关提示已经用过了。')
                else:
                    hint_used = True
                    score = max(0, score - 10)
                    print('  💡 总重 %d，理论下限 ceil(总重/容量) = %d。%s（-10，当前 %d 分）' % (sum(items), lower_bound(items, cap), tip, score))
                continue
            if not s.isdigit():
                print('  请输入一个正整数（箱子数量）。')
                continue
            k = int(s)
            tries += 1
            if k == ans:
                score += 20
                print('  ✅ 正是最优解 %d 箱 +20（当前 %d 分）' % (ans, score))
                print('  一种装法:')
                for i, p in enumerate(packs, 1):
                    print('    箱%d: %s（共 %d/%d）' % (i, ' + '.join(str(x) for x in p), sum(p), cap))
                break
            score = max(0, score - 8)
            if k > ans:
                print('  ❌ %d 箱能装下，但不是最省（-8，当前 %d 分）' % (k, score))
            else:
                print('  ❌ %d 箱装不下这么多货（-8，当前 %d 分）' % (k, score))
            if tries >= 3:
                print('  本题正确答案是 %d 箱。' % ans)
                break
    print()
    print('=' * 58)
    print('  本轮结束，总分 %d / 100' % score)
    if score >= 85:
        print('  评语：直觉就是最优解，装箱问题难不倒你。')
    elif score >= 60:
        print('  评语：思路对了，偶尔浪费一箱空间。')
    elif score >= 30:
        print('  评语：先找「能装满的组合」，再谈箱数。')
    else:
        print('  评语：记住先算总重下限，再验证能不能拼到那么省。')
    print('=' * 58)


def check():
    ok = True
    for cap, items, tip in LEVELS:
        dp_ans, choice, full = min_bins_dp(items, cap)
        dfs_ans, lb = exact_bins_dfs(items, cap)
        ffd_ans = ffd(items, cap)
        if dp_ans != dfs_ans:
            ok = False
            print('✗ 两种精确算法不一致', items, dp_ans, dfs_ans)
        if lb > dfs_ans:
            ok = False
            print('✗ 下限大于答案，说明装法有问题', items, lb, dfs_ans)
        if ffd_ans < dfs_ans:
            ok = False
            print('✗ 贪心结果优于最优解，不可能', items, ffd_ans, dfs_ans)
        if sum(items) > cap * dfs_ans:
            ok = False
            print('✗ 容量装不下', items)
        # 回灌：把 DP 给出的装法逐箱检查，并确认所有货物恰好用到一次
        ans2, packs = reconstruct(items, cap)
        used = []
        for p in packs:
            if sum(p) > cap:
                ok = False
                print('✗ 某箱超重', p, cap)
            used.extend(p)
        if sorted(used) != sorted(items):
            ok = False
            print('✗ 装法没覆盖全部货物', items, used)
        if len(packs) != dp_ans:
            ok = False
            print('✗ 装法箱数与答案不符', len(packs), dp_ans)
        # 分支限界证伪：ans-1 箱确实装不下
        if dp_ans - 1 > 0:
            best = [dp_ans - 1]
            order = sorted(items, reverse=True)

            def dfs(i, loads, used, best=best, order=order):
                if used >= best[0]:
                    return False
                if i == len(order):
                    return True
                w = order[i]
                seen = set()
                for b in range(used):
                    if loads[b] in seen:
                        continue
                    seen.add(loads[b])
                    if loads[b] + w <= cap:
                        loads[b] += w
                        if dfs(i + 1, loads, used):
                            return True
                        loads[b] -= w
                if used + 1 < best[0] + 1 and used + 1 <= best[0]:
                    loads.append(w)
                    if dfs(i + 1, loads, used + 1):
                        return True
                    loads.pop()
                return False

            if dfs(0, [], 0):
                ok = False
                print('✗ 声称最优 %d 箱，但 %d 箱也能装下' % (dp_ans, dp_ans - 1))
    print('自检通过 ✅ 5 关：子集 DP 与分支限界一致，FFD 不小于最优，装法回灌无超重、无漏件、无重复' if ok else '自检失败 ❌')
    return ok


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    try:
        play()
    except (BrokenPipeError, KeyboardInterrupt):
        print()
