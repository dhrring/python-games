'''拉丁方阵拼图 —— 每日交互小游戏 2026-11-24（第 32 天）

【游戏简介】
拉丁方阵是 N×N 的表格，每格填 1..N 的数字，要求「每一行不重复、每一列也不重复」。
棋盘上已经给了一些数字，你要把空格补齐。每一关的答案都是唯一的。

【怎么玩】
1. 直接运行：python 2026-11-24_拉丁方阵拼图.py
2. 输入格式：r c v —— 意思是「第 r 行第 c 列填数字 v」（行列都从 1 开始数）。
   例如  3 1 5   表示第 3 行第 1 列填 5。
3. 想清空某一格：输入   r c 0
4. 空行回车 = 提交本关，系统检查每行每列是否都是 1..N 齐全。
5. 命令：
   hint / h / 提示 / ?    揭晓一个空格（每次扣 10 分，每关最多 3 次）
   q / quit / exit / 退出  中途退出
6. 5 关共 100 分（4×4 两关、5×5 两关、6×6 一关），填错提交扣 8 分可重填，每关保底 4 分。

【技巧】
· 先找只剩一个空的行或列，答案立刻唯一。
· 数一数某行还缺哪几个数字，再看对应列缺什么，取交集。
· 拉丁方阵可以用「数对」推理：两行里同样的两个数字如果在同样的两列，就会在这两列形成锁定。

【自检】python 2026-11-24_拉丁方阵拼图.py --check
（会检查每关给定数字是否与答案一致、答案是否为合法拉丁方阵、每个谜题是否只有唯一解）
'''

import sys

# (阶数, {(行,列): 数字}, 完整答案)
LEVELS = [
    (4, {(1, 2): 1, (1, 3): 4, (1, 4): 2, (2, 2): 4, (3, 1): 2, (3, 3): 1, (3, 4): 4},
     [[3, 1, 4, 2], [1, 4, 2, 3], [2, 3, 1, 4], [4, 2, 3, 1]]),
    (4, {(1, 1): 3, (1, 2): 4, (2, 1): 1, (3, 2): 2, (3, 3): 3, (4, 3): 4},
     [[3, 4, 1, 2], [1, 3, 2, 4], [4, 2, 3, 1], [2, 1, 4, 3]]),
    (5, {(1, 2): 5, (1, 4): 4, (2, 1): 4, (2, 2): 2, (2, 4): 5, (3, 1): 3,
         (3, 2): 4, (3, 4): 1, (3, 5): 5, (4, 5): 1, (5, 2): 1},
     [[1, 5, 3, 4, 2], [4, 2, 1, 5, 3], [3, 4, 2, 1, 5], [5, 3, 4, 2, 1], [2, 1, 5, 3, 4]]),
    (5, {(1, 2): 4, (1, 5): 3, (2, 5): 5, (3, 1): 5, (3, 2): 1, (4, 1): 1,
         (4, 2): 2, (4, 5): 4, (5, 1): 3, (5, 3): 2},
     [[2, 4, 5, 1, 3], [4, 3, 1, 2, 5], [5, 1, 4, 3, 2], [1, 2, 3, 5, 4], [3, 5, 2, 4, 1]]),
    (6, {(1, 1): 1, (1, 2): 6, (1, 5): 4, (1, 6): 3, (2, 2): 3, (3, 4): 1, (3, 6): 4,
         (4, 1): 6, (4, 3): 3, (4, 5): 5, (4, 6): 2, (5, 1): 5, (5, 4): 2, (5, 5): 3,
         (6, 2): 5, (6, 3): 1},
     [[1, 6, 2, 5, 4, 3], [2, 3, 4, 6, 1, 5], [3, 2, 5, 1, 6, 4],
      [6, 1, 3, 4, 5, 2], [5, 4, 6, 2, 3, 1], [4, 5, 1, 3, 2, 6]]),
]

MAX_SCORE = 20
HINT_COST = 10
WRONG_COST = 8
FLOOR = 4


def count_solutions(n, givens, limit=2):
    '''回溯数解（MRV 启发式），满 limit 个就停。'''
    grid = [[0] * (n + 1) for _ in range(n + 1)]
    for (r, c), v in givens.items():
        grid[r][c] = v
    found = [0]

    def fits(r, c, v):
        for j in range(1, n + 1):
            if j != c and grid[r][j] == v:
                return False
            if j != r and grid[j][c] == v:
                return False
        return True

    def rec():
        best = None
        for r in range(1, n + 1):
            for c in range(1, n + 1):
                if grid[r][c] == 0:
                    cand = [v for v in range(1, n + 1) if fits(r, c, v)]
                    if not cand:
                        return
                    if best is None or len(cand) < len(best[2]):
                        best = (r, c, cand)
        if best is None:
            found[0] += 1
            return
        r, c, cand = best
        for v in cand:
            grid[r][c] = v
            rec()
            grid[r][c] = 0
            if found[0] >= limit:
                return

    rec()
    return found[0]


def conflicts(n, board):
    '''返回棋盘里行列重复的说明列表（只看已填格子）。'''
    msgs = []
    for r in range(1, n + 1):
        seen = {}
        for c in range(1, n + 1):
            v = board[r][c]
            if v:
                if v in seen:
                    msgs.append('第 %d 行：数字 %d 出现了两次（第 %d、%d 列）' % (r, v, seen[v], c))
                seen[v] = c
    for c in range(1, n + 1):
        seen = {}
        for r in range(1, n + 1):
            v = board[r][c]
            if v:
                if v in seen:
                    msgs.append('第 %d 列：数字 %d 出现了两次（第 %d、%d 行）' % (c, v, seen[r], r))
                seen[v] = r
    return msgs


def draw(n, board):
    width = len(str(n))
    header = '     ' + ' '.join(str(c).rjust(width) for c in range(1, n + 1))
    print(header)
    print('    ' + '-' * (len(header) - 4))
    for r in range(1, n + 1):
        cells = []
        for c in range(1, n + 1):
            v = board[r][c]
            cells.append(str(v).rjust(width) if v else '·'.rjust(width))
        print(' %2d | %s' % (r, ' '.join(cells)))
    blanks = sum(1 for r in range(1, n + 1) for c in range(1, n + 1) if not board[r][c])
    print('  （还剩 %d 个空格 · 输入 r c v 填数，空行提交）' % blanks)


def play():
    print('=' * 62)
    print('        拉丁方阵拼图  ·  5 关 · 满分 100')
    print('=' * 62)
    print('每行每列都要 1..N 各出现一次。输入形如  3 2 4  表示第3行第2列填4；')
    print('清空用 r c 0，空行回车提交，hint 要提示（-10），q 退出。\n')

    total = 0
    for idx, (n, givens, solution) in enumerate(LEVELS, 1):
        board = [[0] * (n + 1) for _ in range(n + 1)]
        for (r, c), v in givens.items():
            board[r][c] = v

        print('-' * 62)
        print('第 %d 关 · %d×%d（已给 %d 个数字，答案唯一）' % (idx, n, n, len(givens)))
        draw(n, board)

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
                blanks = [(r, c) for r in range(1, n + 1) for c in range(1, n + 1) if not board[r][c]]
                if not blanks:
                    print('已经填满了，直接空行提交吧。')
                    continue
                if hint_i >= 3:
                    print('本关提示已用完。')
                    continue
                r, c = blanks[0]
                board[r][c] = solution[r - 1][c - 1]
                level_score = max(FLOOR, level_score - HINT_COST)
                hint_i += 1
                print('提示 %d：第 %d 行第 %d 列是 %d。（本关最高可得 %d 分）'
                      % (hint_i, r, c, board[r][c], level_score))
                draw(n, board)
                continue
            if not raw:
                bad = conflicts(n, board)
                missing = sum(1 for r in range(1, n + 1) for c in range(1, n + 1) if not board[r][c])
                if bad:
                    level_score = max(FLOOR, level_score - WRONG_COST)
                    print('✘ 提交失败，行列有重复：')
                    for m in bad[:4]:
                        print('   · ' + m)
                    print('  本关最高可得 %d 分，改完再提交。' % level_score)
                    continue
                if missing:
                    print('还差 %d 个空格，填满再提交。' % missing)
                    continue
                total += level_score
                print('✔ 完成！本关得分 %d，累计 %d 分。\n' % (level_score, total))
                break

            parts = raw.replace(',', ' ').split()
            if len(parts) != 3 or not all(p.lstrip('-').isdigit() for p in parts):
                print('格式不对。请用  r c v （三个数字，空格分开），例如 2 3 5。')
                continue
            r, c, v = (int(p) for p in parts)
            if not (1 <= r <= n and 1 <= c <= n):
                print('行列必须在 1..%d 之间。' % n)
                continue
            if not (0 <= v <= n):
                print('数字必须在 1..%d（填 0 表示清空）。' % n)
                continue
            if v == 0:
                if (r, c) in givens:
                    print('这一格是题目给的，不能清空。')
                    continue
                board[r][c] = 0
                draw(n, board)
                continue
            for j in range(1, n + 1):
                if j != c and board[r][j] == v:
                    print('✘ 第 %d 行第 %d 列已经是 %d 了，换个数。' % (r, j, v))
                    break
                if j != r and board[j][c] == v:
                    print('✘ 第 %d 行第 %d 列已经是 %d 了，换个数。' % (j, c, v))
                    break
            else:
                board[r][c] = v
            draw(n, board)

    print('=' * 62)
    print('通关！总分 %d / 100' % total)
    if total >= 90:
        print('评语：推理干净，几乎没动提示。')
    elif total >= 70:
        print('评语：稳，锁定数对用得不错。')
    elif total >= 40:
        print('评语：会做单空格了，下次试试两格联立。')
    else:
        print('评语：别乱试，每行先算「还缺哪几个数」。')
    print('=' * 62)


def check():
    print('[自检] 拉丁方阵拼图')
    ok = True
    for idx, (n, givens, solution) in enumerate(LEVELS, 1):
        # 1) 答案本身是合法拉丁方阵
        rows_ok = all(sorted(row) == list(range(1, n + 1)) for row in solution)
        cols_ok = all(sorted(solution[r][c] for r in range(n)) == list(range(1, n + 1)) for c in range(n))
        # 2) 给定数字与答案一致
        giv_ok = all(solution[r - 1][c - 1] == v for (r, c), v in givens.items())
        # 3) 唯一解
        uniq = count_solutions(n, givens, 2) == 1
        # 4) 空棋盘上的解数应远大于 1（确保谜题不是随便就能蒙）
        many = count_solutions(n, {}, 2) >= 2
        cond = [('答案行合法', rows_ok), ('答案列合法', cols_ok), ('给定与答案一致', giv_ok),
                ('谜题唯一解', uniq), ('无给定时可多解', many)]
        for name, good in cond:
            if not good:
                ok = False
                print('  ✘ 第%d关：%s 失败' % (idx, name))
        print('  第%d关 %d×%d 给定%d格 唯一解=%s 空格%d'
              % (idx, n, n, len(givens), uniq, n * n - len(givens)))

    # 满分路径：按答案逐格填满并走校验逻辑
    sim = 0
    for n, givens, solution in LEVELS:
        board = [[0] * (n + 1) for _ in range(n + 1)]
        for (r, c), v in givens.items():
            board[r][c] = v
        for r in range(1, n + 1):
            for c in range(1, n + 1):
                if not board[r][c]:
                    board[r][c] = solution[r - 1][c - 1]
        if conflicts(n, board) != []:
            ok = False
            print('  ✘ 满分路径仍报冲突')
        else:
            sim += MAX_SCORE
    if sim != 100:
        ok = False
        print('  ✘ 满分路径得分异常：%d' % sim)

    print('[结果]', '全部通过 ✔' if ok else '有问题 ✘')
    return 0 if ok else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c'):
        sys.exit(check())
    try:
        play()
    except (EOFError, KeyboardInterrupt):
        print('\n已退出。')