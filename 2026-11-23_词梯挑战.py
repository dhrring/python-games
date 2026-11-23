'''词梯挑战 · Word Ladder

【简介】
词梯（Word Ladder）由 Lewis Carroll 在 1878 年发明：每一步只改上一个词里的一个字母，
改完必须仍是一个合法的英文单词。本游戏给出起点词与终点词，请你用最少的步数把它们连起来。
例：lead → load → goad → gold（3 步）。

【玩法】
5 关，每关 20 分，满分 100。依次输入词链，每行一个四字母英文单词，输入空行提交：
    lead
    load
    goad
    gold
    （空行）
相邻两词只能差一个字母，且所有词必须在本游戏内置词典里。
链路合法但比最优更长时，按超出的步数扣分；非法则给保底分并展示参考答案。

【命令】
hint / h / 提示 / ?   ：提示当前这一级的下一词（每次扣 10 分，最低保底 4 分）
q / quit / exit / 退出 ：退出
回车                   ：重看题目

【运行】
    python 2026-11-23_词梯挑战.py
自检：
    python 2026-11-23_词梯挑战.py --check
纯标准库，Python 3.6+ 可直接运行。
'''

import sys
from collections import deque

WORDS = '''
cold cord word ward warm lead load goad gold head heal teal tell tall tail
able acid back bald ball band bank bare barn base bath bead beak beam bean bear beat
bell belt bend best bike bill bird blue boat body bold bolt bone book boot born boss bowl
burn bush cake calf call calm came camp cane card care cart case cash cast cave cell
cent chip city clam clay clip club coal coat code coin come cook cool cope copy core
corn cost crew crop cube cure curl dark dart data date dawn deal dear debt deed deep
deer desk dial dice dirt dish disk dive done door dose dove down draw drew drop
drug drum dual duck dull dumb dust duty each earn ease east easy edge else even ever
evil exam exit face fact fade fail fair fall fame farm fast fate fear feat feed feel
feet fell felt fern file fill film find fine fire firm fish fist five flag flat flea
fled flex flow foam foil fold folk food fool foot ford fork form fort four free frog
from fuel full fund gain game gang gate gave gear gene gift girl give glad
glow goal goat goes golf gone good grew grim grin grip grow gulf hail hair half
hall hand hang hard hare harm harp hate have hawk heap hear heat heel
held hell helm help herb herd hero hide high hike hill hint hire hive hold hole holy
home hood hook hope horn hose host hour huge hunt hurt husk hymn icon idea idle inch
into iron item jack jade jail jazz jeep join joke jump june junk just keen keep kept
kilo kind king kiss knee knew knit knot know lace lack lady lake lamb lame lamp land
lane lark last late lava lawn lazy leaf lean leap left lend lens less liar lice
lick life lift like lily limb lime line link lion list live loaf loan lob lock
loft logo lone long look loop lord lose loss lost loud love luck lump lung lure lush
made mail main make male mall mane many mark mars mask mass mast mate math maze
meal mean meat meek meet meld melt memo mend menu mesh mess mild mile milk mill mind
mine mint miss mist mite moat mock mode mold mole monk mood moon more moss most moth
move much mule myth nail name nape navy near neat neck need neon nest news next nice
nine node none noon nose note noun oath obey odds okra once only onto open oral
oven over pace pack page paid pail pain pair pale palm pane park part pass past path
pave peak pear peat peck peel peer pelt pent perk pest pick pile pill pine pink
pint pipe pity plan play plea plod plot plow plug plum plus poem poet pole poll pond
pony pool poor pore pork port pose post pour pray prey prim prom prop pull pulp
pump punk pure push quay quit quiz race rack rage raid rail rain rake ramp rang rank
rare rash rate rave read real ream reap rear reed reef reel rein rely rent rest rice
rich ride rife ring rink riot ripe rise risk road roam roar robe rock rode role roll
roof room root rope rose ruin rule rush rust sack safe sage said sail sale salt same
sand sane sang sank save scan scar seal seam seat seed seek seem seen seep self sell
send sent test text than that thaw thee them then they thin this thus tide
tidy tile till tilt time tiny tire toad toll tomb tone tool toot tore torn toss
tour town tree trim trio trip trod true tube tuck tuna tune turf turn twin type ugly
undo unit upon urge user vale vane vary vase vast veal veer veil vein vent verb
very vest veto vice view vine visa void volt vote wade wage wait wake walk wall wand
want ward warn warp wart wasp wave ways weak wean wear weed week weep weld well
went were west what when whim whip whom wick wide wife wild will wilt wind wine wing
wink wipe wire wise wish with wolf wood wool wore work worm worn wove wrap wren
yard yarn yawn year yell yoga your zero zinc zone zoom
'''

DICT = set(w.lower() for w in WORDS.split() if len(w) == 4)

LEVELS = [
    ('铅变金', 'lead', 'gold', 3, '炼金术士的第一步：先把铅变成……一条词链。'),
    ('由冷到暖', 'cold', 'warm', 4, '冬天最难熬的不是冷，是差一步就到暖。'),
    ('爱恨之间', 'love', 'hate', 4, '四个字母的距离，有时比想象中短。'),
    ('火中取金', 'fire', 'gold', 5, '从火到金，中间得绕几步路。'),
    ('书桌夜读', 'book', 'lamp', 6, '五关最长的一条链，慢慢来。'),
]

HELP = '''【词梯挑战 · 玩法】
每步只改一个字母，改完必须仍是词典里的四字母英文单词。
逐行输入词链，空行提交。例：lead / load / goad / gold / 空行
命令：hint 或 h 求提示（扣 10 分）；q 退出。'''


def differ(a, b):
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def neighbours(w):
    return [x for x in DICT if differ(w, x)]


def bfs(start, end):
    if start not in DICT or end not in DICT:
        return None
    parent = {start: None}
    q = deque([start])
    while q:
        u = q.popleft()
        if u == end:
            path = []
            while u is not None:
                path.append(u)
                u = parent[u]
            return list(reversed(path))
        for v in neighbours(u):
            if v not in parent:
                parent[v] = u
                q.append(v)
    return None


def hint_of(start, end, last):
    path = bfs(start, end)
    if not path or last not in path:
        return None
    i = path.index(last)
    return path[i + 1] if i + 1 < len(path) else None


def validate(start, end, chain):
    if not chain:
        return False, '词链是空的。'
    if chain[0] != start:
        return False, '词链必须从起点「%s」开始。' % start
    if chain[-1] != end:
        return False, '词链必须以终点「%s」结束。' % end
    for w in chain:
        if w not in DICT:
            return False, '「%s」不在内置词典里（只收四字母常见英文单词）。' % w
    for a, b in zip(chain, chain[1:]):
        if not differ(a, b):
            return False, '「%s」和「%s」不是只差一个字母，接不上。' % (a, b)
    if len(chain) != len(set(chain)):
        return False, '词链里出现了重复单词。'
    return True, '共 %d 步。' % (len(chain) - 1)


def ask(prompt='  > '):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print('\n\n游戏结束，再见。')
        raise SystemExit(0)


score = 0


def render(idx, title, start, end, note):
    print('\n' + '=' * 56)
    print('第 %d 关 · %s      （当前总分 %d / 100）' % (idx, title, score))
    print('-' * 56)
    print('起点：%s      终点：%s' % (start.upper(), end.upper()))
    print('提示语：%s' % note)
    print('请输入词链（每行一个四字母单词，空行提交，hint 求助）：')


def play_level(idx, title, start, end, best, note):
    global score
    lv_score = 20
    chain = []
    valid_words = set()
    render(idx, title, start, end, note)
    while True:
        raw = ask().strip()
        if raw == '':
            if not chain:
                render(idx, title, start, end, note)
                print('（还没输入任何单词）')
                continue
            ok, msg = validate(start, end, chain)
            if not ok:
                print('× ' + msg)
                print('  参考答案：' + ' → '.join(bfs(start, end)))
                return max(4, lv_score - 8), '参考答案已公布'
            steps = len(chain) - 1
            if steps == best:
                print('√ 完美！正好 %d 步，这就是最短解。' % steps)
                return lv_score, '最优解'
            print('√ 合法，但用了 %d 步，比最优（%d 步）多 %d 步。' % (steps, best, steps - best))
            print('  参考答案：' + ' → '.join(bfs(start, end)))
            return max(4, lv_score - 2 * (steps - best)), '非最优'
        low = raw.lower()
        if low in ('q', 'quit', 'exit', '退出'):
            print('\n已退出。本局得分 %d 分。' % score)
            raise SystemExit(0)
        if low in ('hint', 'h', '提示', '?'):
            last = chain[-1] if chain else start
            nxt = hint_of(start, end, last)
            if nxt is None:
                print('（当前词不在最优路径上，先退回正确位置）')
            else:
                print('提示：在「%s」之后可走「%s」。（本次扣 10 分）' % (last, nxt))
            lv_score = max(4, lv_score - 10)
            continue
        if low in ('help', 'rules', '规则'):
            print(HELP)
            continue
        w = low
        if not w.isalpha() or len(w) != 4:
            print('（请输入一个四字母英文单词，或空行提交）')
            continue
        if w not in DICT:
            print('（「%s」不在内置词典里，换一个词试试）' % w)
            continue
        if not chain:
            if w != start:
                print('（第一个词必须是起点「%s」）' % start)
                continue
        elif not differ(chain[-1], w):
            print('（「%s」与「%s」不是只差一个字母）' % (chain[-1], w))
            continue
        chain.append(w)
        print('  [%d] %s' % (len(chain) - 1, w))
        if w == end:
            print('（已到终点，再按一次回车提交）')


def play():
    global score
    print(HELP)
    for i, (title, start, end, best, note) in enumerate(LEVELS, 1):
        gained, kind = play_level(i, title, start, end, best, note)
        score += gained
        print('本关得分：%d（%s）；累计 %d 分。' % (gained, kind, score))
    print('\n全部通关！总分 %d / 100。' % score)
    if score == 100:
        print('满分！你的词感和图搜索直觉都很稳。')
    elif score >= 80:
        print('很强，大部分关卡都找到了最短链。')
    elif score >= 60:
        print('不错，基本能连通；再练几局会更接近最优。')
    else:
        print('诀窍：把中间词想成桥墩，每个字母位置都可能是突破口。')
    print('感谢游玩，明天见。')


def check():
    print('【自检】词梯挑战')
    print('词典规模：%d 个四字母单词' % len(DICT))
    errs = []
    for i, (title, s, e, exp, note) in enumerate(LEVELS, 1):
        for w in (s, e):
            if w not in DICT:
                errs.append('第 %d 关：词「%s」不在词典里' % (i, w))
        path = bfs(s, e)
        if path is None:
            errs.append('第 %d 关：%s 到 %s 不可达' % (i, s, e))
            continue
        got = len(path) - 1
        ok, msg = validate(s, e, path)
        print('第 %d 关 %s→%s：BFS 最短 %d 步（内置 %d 步）%s' %
              (i, s, e, got, exp, '√' if got == exp else '×'))
        print('    参考链：%s' % ' → '.join(path))
        if got != exp:
            errs.append('第 %d 关：最短 %d 步 ≠ 内置 %d 步' % (i, got, exp))
        if not ok:
            errs.append('第 %d 关：内置链不合法（%s）' % (i, msg))
        for a, b in zip(path, path[1:]):
            if not differ(a, b):
                errs.append('第 %d 关：链中 %s→%s 非法' % (i, a, b))
        nxt = hint_of(s, e, s)
        if nxt is None or not differ(s, nxt):
            errs.append('第 %d 关：提示函数异常' % i)
    if errs:
        print('\n发现 %d 个问题：' % len(errs))
        for x in errs:
            print('  × ' + x)
        return 1
    print('\n全部通过：5 关最短步数与内置答案一致，提示函数正常。')
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c', 'check'):
        sys.exit(check())
    play()
