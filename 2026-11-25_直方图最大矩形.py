'''直方图最大矩形 —— 在柱状图里圈出最大的矩形

玩法
  共 5 关，每关给一张 ASCII 直方图：每根柱子宽 1 格、高度见左侧刻度。
  你的任务：在这张图里找出一个「完全落在柱子里」的矩形，使它的格子数最大，
            然后填这个最大面积（单位是「格」，= 高度 × 宽度）。
  每关 20 分，最多猜 3 次；猜错扣 8 分并提示偏大还是偏小。
  提示命令：hint（或 h、提示、?），每关一次，扣 10 分，只讲思路不给答案。
  直接回车可重画这张图；q 退出。

运行
  python 2026-11-25_直方图最大矩形.py
  python 2026-11-25_直方图最大矩形.py --check   # 自检：单调栈与暴力枚举交叉验证、面积可达性
'''

import sys

LEVELS = [
    ([2, 1, 5, 6, 2, 3], '经典题：最高的那根不一定是答案，想一想「把矮柱子当高度」怎么横扫。'),
    ([6, 2, 5, 4, 5, 1, 6], '中间那根 1 高的柱子把画面切成两半，答案可能在某一半里。'),
    ([4, 2, 0, 3, 2, 5], '高度为 0 的柱子等于一堵墙，任何矩形都不能跨过它。'),
    ([3, 3, 3, 1, 3, 3, 3], '把高度 1 的柱子纳进来会让面积变大还是变小？算一下两边。'),
    ([1, 2, 3, 4, 5, 4, 3, 2, 1], '高度像山坡：以某根柱子的高度为准，向左向右各能延伸多远？'),
]


def max_area_stack(heights):
    stack = []
    best = 0
    h = heights + [0]
    for i, x in enumerate(h):
        start = i
        while stack and stack[-1][1] > x:
            idx, hh = stack.pop()
            best = max(best, hh * (i - idx))
            start = idx
        stack.append((start, x))
    return best


def max_area_brute(heights):
    best = 0
    n = len(heights)
    for l in range(n):
        low = heights[l]
        for r in range(l, n):
            low = min(low, heights[r])
            best = max(best, low * (r - l + 1))
    return best


def best_rect(heights):
    best = (0, 0, 0)
    n = len(heights)
    for l in range(n):
        low = heights[l]
        for r in range(l, n):
            low = min(low, heights[r])
            if low * (r - l + 1) > best[0]:
                best = (low * (r - l + 1), l, r)
    return best


def draw(heights):
    top = max(heights) if heights else 0
    width = len(heights)
    print('    ' + ''.join(str((i + 1) % 10) for i in range(width)) + '  ← 列号')
    for row in range(top, 0, -1):
        line = ''
        for h in heights:
            line += '█' if h >= row else ' '
        print('  %2d %s|' % (row, line))
    print('     ' + '-' * width + '+')


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


def play():
    score = 0
    print('=' * 58)
    print('  直方图最大矩形 · 5 关 · 满分 100')
    print('  h 提示（每关一次，-10）  q 退出  空行重画')
    print('=' * 58)
    for no, (heights, tip) in enumerate(LEVELS, 1):
        ans = max_area_stack(heights)
        _, l, r = best_rect(heights)
        print()
        print('  【第 %d 关】柱子高度: %s' % (no, ' '.join(str(x) for x in heights)))
        draw(heights)
        print('  当前得分: %d' % score)
        hint_used = False
        tries = 0
        while True:
            s = ask('  最大矩形面积 > ')
            if s is None:
                print('中途退出，当前得分 %d。' % score)
                return
            if s == '':
                draw(heights)
                continue
            if s.lower() in ('h', 'hint', '提示', '?'):
                if hint_used:
                    print('  本关提示已经用过了。')
                else:
                    hint_used = True
                    score = max(0, score - 10)
                    print('  💡 ' + tip + '（-10，当前 %d 分）' % score)
                continue
            if not s.isdigit():
                print('  请输入一个非负整数（格子数）。')
                continue
            k = int(s)
            tries += 1
            if k == ans:
                score += 20
                print('  ✅ 正确，最大面积就是 %d 格 +20（当前 %d 分）' % (ans, score))
                print('  最优矩形：第 %d~%d 列，高度 %d，宽 %d → %d 格'
                      % (l + 1, r + 1, ans // (r - l + 1), r - l + 1, ans))
                break
            score = max(0, score - 8)
            if k > ans:
                print('  ❌ %d 太大了，图里没有这么大的矩形（-8，当前 %d 分）' % (k, score))
            else:
                print('  ❌ %d 太小了，还能圈得更大（-8，当前 %d 分）' % (k, score))
            if tries >= 3:
                print('  本题正确答案是 %d 格。' % ans)
                break
    print()
    print('=' * 58)
    print('  本轮结束，总分 %d / 100' % score)
    if score >= 85:
        print('  评语：一眼就能看出「以谁为高度、向两边延伸」，很强。')
    elif score >= 60:
        print('  评语：能找对方向，偶尔漏掉更宽的区间。')
    elif score >= 30:
        print('  评语：记住面积 = 区间内最矮那根 × 区间宽度，逐段试。')
    else:
        print('  评语：先把「每一列向右延伸、记录最矮高度」这条笨办法练熟。')
    print('=' * 58)


def check():
    ok = True
    for heights, tip in LEVELS:
        a1 = max_area_stack(heights)
        a2 = max_area_brute(heights)
        if a1 != a2:
            ok = False
            print('✗ 单调栈与暴力枚举不一致', heights, a1, a2)
        area, l, r = best_rect(heights)
        if area != a1:
            ok = False
            print('✗ 最优矩形定位不上', heights, area, a1)
        if min(heights[l:r + 1]) * (r - l + 1) != area:
            ok = False
            print('✗ 最优矩形面积算法有误', heights)
        if any(x < 0 for x in heights):
            ok = False
            print('✗ 出现负高度', heights)
        if not tip:
            ok = False
            print('✗ 缺少提示文本', heights)
    # 边界用例：单柱、全零、递增、递减
    cases = [[5], [0, 0, 0], [1, 2, 3, 4], [4, 3, 2, 1], [2, 2], [1, 0, 1]]
    for c in cases:
        if max_area_stack(c) != max_area_brute(c):
            ok = False
            print('✗ 边界用例不一致', c)
    # 关卡之间不应出现相同图形
    shapes = [tuple(h) for h, _ in LEVELS]
    if len(set(shapes)) != len(shapes):
        ok = False
        print('✗ 有重复的关卡图形')
    # 满分路径：5 关 ×20 = 100
    total = 20 * len(LEVELS)
    if total != 100:
        ok = False
        print('✗ 满分不是 100，实为', total)
    print('自检通过 ✅ 5 关：单调栈 O(n) 与暴力枚举 O(n²) 结果一致、最优矩形可定位、边界用例通过、满分 100' if ok else '自检失败 ❌')
    return ok


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    try:
        play()
    except (BrokenPipeError, KeyboardInterrupt):
        print()
