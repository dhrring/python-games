'''水库调度 · 最大流最小割

【简介】
暴雨过后，山上的水库 S 要把水送到山下的城市 T。中间村庄之间铺着水管，
每根管子都有容量上限。请你算出整张管网每分钟最多能往城市送多少水——
这就是图论里的「最大流问题」，它等于「最小割」：找一组最便宜的管子把它们全切断。

【玩法】
5 关，每关 20 分，满分 100。管网是单向的，水只能顺着箭头走；
中间节点不增不减（流入多少就能流出多少），也不会倒流。
输入一个整数，表示 S 到 T 的最大流量。

【命令】
hint / h / 提示 / ?   ：给一条提示（每次扣 10 分，最低保底 4 分）
q / quit / exit / 退出 ：退出
回车                   ：重看题目

【运行】
    python 2026-11-23_水库调度.py
自检：
    python 2026-11-23_水库调度.py --check
纯标准库，Python 3.6+ 可直接运行。
'''

import sys
from collections import deque
from itertools import combinations

LEVELS = [
    ('两条支流',
     [('S', 'A', 4), ('S', 'B', 3), ('A', 'T', 3), ('B', 'T', 3), ('A', 'B', 2)], 6,
     '最朴素的一张图。先看 S 一共能放出多少，再看 T 能吃下多少。'),
    ('中间村庄',
     [('S', 'A', 5), ('S', 'C', 4), ('A', 'B', 4), ('A', 'T', 2),
      ('B', 'T', 4), ('B', 'C', 3), ('C', 'T', 5)], 9,
     'A 有一部分水要经 B 转运，注意 A→B 与 B→T 的搭配。'),
    ('分流与汇流',
     [('S', 'A', 6), ('S', 'B', 4), ('A', 'C', 5), ('A', 'D', 2), ('B', 'C', 3),
      ('B', 'D', 4), ('C', 'T', 6), ('D', 'T', 5), ('C', 'D', 2)], 10,
     '六个节点，A、B 分流后在 C、D 汇合，别把同一份水算两遍。'),
    ('瓶颈在哪里',
     [('S', 'A', 8), ('S', 'B', 6), ('A', 'B', 2), ('A', 'C', 5), ('B', 'C', 4),
      ('B', 'D', 5), ('C', 'D', 3), ('C', 'T', 6), ('D', 'T', 7)], 13,
     'S 的总出水能力超过 13，真正卡住的是一组更小的管子。'),
    ('七村管网',
     [('S', 'A', 10), ('S', 'B', 8), ('A', 'C', 6), ('A', 'D', 4), ('B', 'C', 3),
      ('B', 'D', 7), ('C', 'E', 5), ('C', 'F', 4), ('D', 'E', 6), ('D', 'F', 5),
      ('E', 'T', 7), ('F', 'T', 9), ('E', 'F', 2)], 16,
     '最复杂的一张图。先想每条边能分到多少，再想总量。'),
]

HELP = '''【水库调度 · 玩法】
管网单向，水从 S 流向 T，每根管子有容量上限；中间节点不增不减。
输入一个整数 = S 到 T 每分钟的最大流量。
命令：hint 或 h 求提示（扣 10 分）；q 退出。'''


def nodes_of(edges):
    out = []
    for u, v, _ in edges:
        for x in (u, v):
            if x not in out:
                out.append(x)
    return out


def build(edges):
    cap = {}
    ns = nodes_of(edges)
    for u, v, c in edges:
        cap[(u, v)] = cap.get((u, v), 0) + c
        cap.setdefault((v, u), 0)
    return cap, ns


def max_flow(edges, s='S', t='T'):
    cap, ns = build(edges)
    total = 0
    while True:
        parent = {s: None}
        q = deque([s])
        while q and t not in parent:
            u = q.popleft()
            for v in ns:
                if cap.get((u, v), 0) > 0 and v not in parent:
                    parent[v] = u
                    q.append(v)
        if t not in parent:
            return total
        f = float('inf')
        v = t
        while parent[v] is not None:
            f = min(f, cap[(parent[v], v)])
            v = parent[v]
        v = t
        while parent[v] is not None:
            cap[(parent[v], v)] -= f
            cap[(v, parent[v])] += f
            v = parent[v]
        total += int(f)


def min_cut(edges, s='S', t='T'):
    mid = [x for x in nodes_of(edges) if x not in (s, t)]
    best = None
    best_set = None
    for r in range(len(mid) + 1):
        for comb in combinations(mid, r):
            part = set(comb) | {s}
            c = sum(w for u, v, w in edges if u in part and v not in part)
            if best is None or c < best:
                best, best_set = c, part
    return best, best_set


def source_out(edges):
    return sum(c for u, v, c in edges if u == 'S')


def ask():
    try:
        return input('  > ')
    except (EOFError, KeyboardInterrupt):
        print('\n\n游戏结束，再见。')
        raise SystemExit(0)


score = 0


def render(idx, title, edges, note):
    print('\n' + '=' * 56)
    print('第 %d 关 · %s      （当前总分 %d / 100）' % (idx, title, score))
    print('-' * 56)
    print('管网（单向，括号内为每分钟容量）：')
    rows = {}
    for u, v, c in edges:
        rows.setdefault(u, []).append('%s→%s(%d)' % (u, v, c))
    for u in sorted(rows):
        print('  %-2s  ' % u + '  '.join(rows[u]))
    print('\n题目：从 S 到 T 的最大流量是多少？（输入一个整数）')
    print('说明：%s' % note)


def play_level(idx, title, edges, answer, note):
    global score
    lv = 20
    render(idx, title, edges, note)
    while True:
        raw = ask().strip()
        if raw == '':
            render(idx, title, edges, note)
            continue
        low = raw.lower()
        if low in ('q', 'quit', 'exit', '退出'):
            print('\n已退出。本局得分 %d 分。' % score)
            raise SystemExit(0)
        if low in ('hint', 'h', '提示', '?'):
            print('提示：从 S 直接流出的管子合计 %d；再想想到 T 的管子合计多少，两者取小是一阶近似。'
                  % source_out(edges))
            lv = max(4, lv - 10)
            continue
        if low in ('help', 'rules', '规则'):
            print(HELP)
            continue
        try:
            val = int(low)
        except ValueError:
            print('（请输入一个整数，比如 12）')
            continue
        if val < 0:
            print('（流量不可能是负数）')
            continue
        if val == answer:
            print('√ 正确！最大流 = %d。本关满分。' % val)
            return lv
        lv = max(4, lv - 8)
        if val > answer:
            print('× 偏大了：卡住它的不是 S 的总出水能力，而是某组更小的管子。再试：')
        else:
            print('× 偏小了：水还没流满，看看有没有被忽略的管道。再试：')
        if lv <= 4:
            print('（已到保底分，公布正确答案：%d）' % answer)
            return lv


def play():
    global score
    print(HELP)
    for i, (title, edges, ans, note) in enumerate(LEVELS, 1):
        gained = play_level(i, title, edges, ans, note)
        score += gained
        print('本关得分：%d；累计 %d 分。' % (gained, score))
    print('\n全部通关！总分 %d / 100。' % score)
    if score == 100:
        print('满分！你已经掌握了「最大流 = 最小割」的直觉。')
    elif score >= 80:
        print('很强，瓶颈识别得很准。')
    elif score >= 60:
        print('不错。记住：先看割，再看流。')
    else:
        print('最大流的关键是「残余网络」：每送出一份水，都要留一条能反悔的余地。')
    print('感谢游玩，明天见。')


def check():
    print('【自检】水库调度 · 最大流最小割')
    errs = []
    for i, (title, edges, ans, note) in enumerate(LEVELS, 1):
        mf = max_flow(edges)
        mc, cutset = min_cut(edges)
        print('第 %d 关 %s：最大流 %d，枚举最小割 %d（割集 %s），内置 %d' %
              (i, title, mf, mc, sorted(cutset), ans))
        if mf != ans:
            errs.append('第 %d 关：最大流 %d ≠ 内置 %d' % (i, mf, ans))
        if mc != mf:
            errs.append('第 %d 关：最小割 %d ≠ 最大流 %d' % (i, mc, mf))
        pairs = [(u, v) for u, v, _ in edges]
        if len(pairs) != len(set(pairs)):
            errs.append('第 %d 关：存在重复同向边' % i)
        if any(u == v for u, v, _ in edges):
            errs.append('第 %d 关：存在自环' % i)
        for u, v, c in edges:
            if not isinstance(c, int) or c <= 0:
                errs.append('第 %d 关：边 %s→%s 容量非法' % (i, u, v))
        ns = nodes_of(edges)
        if 'S' not in ns or 'T' not in ns:
            errs.append('第 %d 关：缺少 S 或 T' % i)
    if errs:
        print('\n发现 %d 个问题：' % len(errs))
        for x in errs:
            print('  × ' + x)
        return 1
    print('\n全部通过：5 关最大流与最小割枚举一致，且与内置答案相同。')
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c', 'check'):
        sys.exit(check())
    play()
