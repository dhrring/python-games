'''矩阵链乘最优化 —— 每日交互小游戏 2026-11-24（第 32 天）

【游戏简介】
你要把一串矩阵连乘 A1×A2×…×An 算出来，矩阵乘法不满足交换律，但「先乘哪两个」
可以随便选——不同的括号方式，计算量能差出几十倍。

复习一下代价：A(p×q) 乘 B(q×r) 需要 p·q·r 次标量乘法，结果是 p×r。
所以整条链的总代价取决于你从哪里「切刀」。

每一关给出各矩阵的尺寸，你要回答：**最少需要多少次标量乘法**。

【怎么玩】
1. 直接运行：python 2026-11-24_矩阵链乘最优化.py
2. 每关输入一个整数（最少标量乘法次数），答对 +20 分。
3. 命令：
   hint / h / 提示 / ?    给提示（每次扣 10 分，每关最多 2 次）
   直接回车              重新显示本关尺寸
   q / quit / exit / 退出  中途退出
4. 答错扣 8 分，会告诉你是偏大还是偏小，每关保底 4 分。5 关满分 100。

【思路】
· 暴力枚举所有括号方式是卡特兰数：n=6 时 42 种、n=10 时 4862 种，手算不现实。
· 正解是区间 DP：dp[i][j] = min over k in [i,j) { dp[i][k] + dp[k+1][j] + d[i-1]*d[k]*d[j] }，
  其中 d 是尺寸序列，边界 dp[i][i] = 0。n=6 只有 20 来个状态，纸笔也能推。
· 手感提示：先把「特别宽的矩阵」乘成小尺寸，往往能省掉大量乘法。

【自检】python 2026-11-24_矩阵链乘最优化.py --check
（用记忆化 DP、无记忆递归、枚举全部括号方式三种方法交叉验算，并核对提示里的切分点）
'''

import sys

LEVELS = [
    [10, 5, 20, 15],          # 第1关：3 个矩阵，两种括号方式
    [5, 10, 3, 12, 5],        # 第2关：4 个矩阵
    [30, 35, 15, 5, 10, 20],  # 第3关：5 个矩阵
    [100, 2, 80, 3, 60, 5],   # 第4关：细长矩阵，先乘窄的能省一大截
    [40, 20, 30, 10, 50, 25, 60],  # 第5关：6 个矩阵，42 种括号方式
]

MAX_SCORE = 20
HINT_COST = 10
WRONG_COST = 8
FLOOR = 4


def mcm(dims):
    '''区间 DP：返回 (最小代价, 最优切分表)。'''
    n = len(dims) - 1
    dp = [[0] * (n + 1) for _ in range(n + 1)]
    cut = [[0] * (n + 1) for _ in range(n + 1)]
    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            best, best_k = None, i
            for k in range(i, j):
                cost = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if best is None or cost < best:
                    best, best_k = cost, k
            dp[i][j] = best
            cut[i][j] = best_k
    return dp[1][n], cut


def left_assoc(dims):
    '''从左往右硬乘（(((A1A2)A3)A4…)）的代价，作为参照上界。

    累乘结果始终是 dims[0] × dims[k]，所以每次乘以 A(k+1) 的代价是
    dims[0] * dims[k] * dims[k+1]。
    '''
    n = len(dims) - 1
    return sum(dims[0] * dims[k] * dims[k + 1] for k in range(1, n))


def naive_recursive(dims):
    '''无记忆化递归：独立算法，用来交叉验算 DP。'''
    n = len(dims) - 1

    def rec(i, j):
        if i == j:
            return 0
        best = None
        for k in range(i, j):
            c = rec(i, k) + rec(k + 1, j) + dims[i - 1] * dims[k] * dims[j]
            if best is None or c < best:
                best = c
        return best

    return rec(1, n)


def enumerate_all(dims):
    '''枚举全部括号方式计数（生成器），用于第三重交叉验证。'''
    n = len(dims) - 1
    seen = []

    def rec(i, j):
        if i == j:
            return [0]
        out = []
        for k in range(i, j):
            for a in rec(i, k):
                for b in rec(k + 1, j):
                    out.append(a + b + dims[i - 1] * dims[k] * dims[j])
        return out

    seen = rec(1, n)
    return len(seen) * (len(seen) > 0), min(seen)


def shape_text(dims):
    n = len(dims) - 1
    parts = []
    for k in range(n):
        parts.append('A%d(%d×%d)' % (k + 1, dims[k], dims[k + 1]))
    return ' × '.join(parts)


def paren_text(dims, cut, i, j):
    if i == j:
        return 'A%d' % i
    k = cut[i][j]
    return '(' + paren_text(dims, cut, i, k) + '×' + paren_text(dims, cut, k + 1, j) + ')'


def play():
    print('=' * 62)
    print('        矩阵链乘最优化  ·  5 关 · 满分 100')
    print('=' * 62)
    print('算出「最少标量乘法次数」。输入 hint 要提示（-10），q 退出，空行重看题目。\n')

    total = 0
    for idx, dims in enumerate(LEVELS, 1):
        best, cut = mcm(dims)
        print('-' * 62)
        print('第 %d 关（%d 个矩阵）' % (idx, len(dims) - 1))
        print('  ' + shape_text(dims))
        print('  从左到右硬乘需要 %d 次；能不能更省？' % left_assoc(dims))
        print('输入最少乘法次数：')

        level_score = MAX_SCORE
        hint_i = 0
        while True:
            try:
                raw = input('> ').strip()
            except (EOFError, KeyboardInterrupt):
                print('\n已退出，本次得分：%d' % total)
                return
            low = raw.lower()
            if low in ('q', 'quit', 'exit', '退出'):
                print('已退出，本次得分：%d' % total)
                return
            if low in ('hint', 'h', '提示', '?'):
                if hint_i >= 2:
                    print('本关提示已用完。')
                    continue
                level_score = max(FLOOR, level_score - HINT_COST)
                if hint_i == 0:
                    print('提示 1：最优解一定比从左到右的 %d 小（或相等），答案不会超过它。'
                          % left_assoc(dims))
                else:
                    print('提示 2：最优方案里，第一次「切」在 A%d 与 A%d 之间。'
                          % (cut[1][len(dims) - 1], cut[1][len(dims) - 1] + 1))
                hint_i += 1
                print('  本关最高可得 %d 分。' % level_score)
                continue
            if not raw:
                print('  ' + shape_text(dims))
                continue

            digits = ''.join(ch for ch in raw if ch.isdigit())
            if not digits or any(not (ch.isdigit() or ch in ' ,，_') for ch in raw):
                print('请输入一个整数（可以带千分位逗号）。')
                continue
            guess = int(digits)
            if guess == best:
                total += level_score
                print('✔ 正确！最少 %d 次乘法。' % best)
                print('  一种最优括号方式：%s' % paren_text(dims, cut, 1, len(dims) - 1))
                print('  本关得分 %d，累计 %d 分。\n' % (level_score, total))
                break

            level_score = max(FLOOR, level_score - WRONG_COST)
            if guess > best:
                print('✘ 偏大了。%d 只是众多括号方式里的次优结果，还有更省的路。' % guess)
            else:
                print('✘ 偏小了。%d 比理论下界还低，检查一下是不是漏算了某次乘法。' % guess)
            print('  当前本关最高可得 %d 分。\n' % level_score)

    print('=' * 62)
    print('通关！总分 %d / 100' % total)
    if total >= 90:
        print('评语：区间 DP 已经刻进脑子里了吧。')
    elif total >= 70:
        print('评语：能看出瓶颈矩阵了，稳。')
    elif total >= 40:
        print('评语：别暴力枚举，记得「切一刀分两段」。')
    else:
        print('评语：先记住 p·q·r，再想切分。')
    print('=' * 62)


def check():
    print('[自检] 矩阵链乘最优化')
    ok = True
    for idx, dims in enumerate(LEVELS, 1):
        if any(d <= 0 for d in dims):
            ok = False
            print('  ✘ 第%d关 尺寸含非正数' % idx)
        best, cut = mcm(dims)
        naive = naive_recursive(dims)
        cnt, enum_best = enumerate_all(dims)
        la = left_assoc(dims)
        cond = [
            ('DP 与无记忆递归一致', best == naive),
            ('DP 与枚举全部括号一致', best == enum_best),
            ('括号方式总数等于卡特兰数', cnt == count_parens(len(dims) - 1)),
            ('最优不劣于从左到右', best <= la),
            ('最优切分点给出等值代价', _cost_at(dims, cut, 1, len(dims) - 1) == best),
            ('答案为正整数', best > 0),
        ]
        for name, good in cond:
            if not good:
                ok = False
                print('  ✘ 第%d关：%s 失败（%s）' % (idx, name, ''))
        print('  第%d关 %d矩阵 答案=%d 从左到右=%d 括号方式=%d 种'
              % (idx, len(dims) - 1, best, la, cnt))

    # 满分路径
    sim = 0
    for dims in LEVELS:
        best, _ = mcm(dims)
        if best == mcm(dims)[0]:
            sim += MAX_SCORE
    if sim != 100:
        ok = False
        print('  ✘ 满分路径得分异常：%d' % sim)

    # 提示切分点必须真的落在最优解里
    for idx, dims in enumerate(LEVELS, 1):
        best, cut = mcm(dims)
        k = cut[1][len(dims) - 1]
        if not (1 <= k < len(dims) - 1):
            ok = False
            print('  ✘ 第%d关 提示切分点越界：%d' % (idx, k))

    print('[结果]', '全部通过 ✔' if ok else '有问题 ✘')
    return 0 if ok else 1


def count_parens(n):
    '''n 个矩阵的括号方式总数（卡特兰数）：递归计数，独立于代价公式。'''
    if n <= 1:
        return 1
    return sum(count_parens(k) * count_parens(n - k) for k in range(1, n))


def _cost_at(dims, cut, i, j):
    if i == j:
        return 0
    k = cut[i][j]
    return _cost_at(dims, cut, i, k) + _cost_at(dims, cut, k + 1, j) + dims[i - 1] * dims[k] * dims[j]


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c'):
        sys.exit(check())
    try:
        play()
    except (EOFError, KeyboardInterrupt):
        print('\n已退出。')