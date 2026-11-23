"""航班时刻谜题 · 时区穿越

【简介】
同一架飞机，起飞和降落的钟表读数常常对不上：北京 8 点起飞、飞 2 小时到东京，
落地却是 11 点——因为东京比北京早 1 小时。跨过国际日期变更线时，
甚至可能出现「落地时间比起飞时间还早」。请算出降落的当地时间。

【玩法】
5 关，每关 20 分，满分 100。输入 HH:MM（24 小时制），也接受 1420、14：20 这类写法；
不必写日期，跨天由系统判断并告诉你。
换算三步：出发当地时间 − 出发时差 + 飞行时长 + 目的地时差。

【命令】
hint / h / 提示 / ?   ：把出发时刻换算成 UTC（每次扣 10 分，最低保底 4 分）
q / quit / exit / 退出 ：退出
回车                   ：重看题目

【运行】
    python 2026-11-23_航班时刻谜题.py
自检：
    python 2026-11-23_航班时刻谜题.py --check
纯标准库，Python 3.6+ 可直接运行。
"""

import sys

# 时差以分钟为单位（+8 小时 = 480），不依赖系统时区数据库
LEVELS = [
    ('北京 → 东京', '北京', 480, '08:00', 120, '东京', 540, '11:00',
     '热身。两个城市只差 1 小时。'),
    ('成都 → 加德满都', '成都', 480, '14:45', 315, '加德满都', 345, '17:45',
     '尼泊尔用 45 分钟时差，别把 45 分丢掉。'),
    ('上海 → 悉尼', '上海', 480, '22:00', 720, '悉尼', 660, '13:00',
     '夜航，落地已是第二天下午。'),
    ('东京 → 檀香山', '东京', 540, '23:30', 540, '檀香山', -600, '13:30',
     '往东跨日期变更线：飞了 9 小时，落地时钟反而往回走。'),
    ('奥克兰 → 查塔姆群岛', '奥克兰', 780, '20:00', 180, '查塔姆群岛', 765, '22:45',
     '全球少见的 45 分钟时区，比奥克兰晚 15 分钟。'),
]

HELP = """【航班时刻谜题 · 玩法】
降落当地时间 = 出发当地时间 − 出发时差 + 飞行时长 + 目的地时差
输入 HH:MM（如 14:20、1420、9:05）；命令：hint 或 h 求提示（扣 10 分），q 退出。"""


def parse_hhmm(text):
    """把 8:05 / 08:05 / 0805 / 8：05 / 次日 13:00 解析成一天内的分钟数；失败返回 None。"""
    if text is None:
        return None
    s = text.strip().replace('：', ':').replace('．', ':')
    for pre in ('次日', '第二天', '翌日', '当天'):
        if s.startswith(pre):
            s = s[len(pre):].strip()
    s = s.replace(' ', '')
    if not s:
        return None
    if ':' in s:
        parts = s.split(':')
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            return None
        h, m = int(parts[0]), int(parts[1])
    else:
        if not s.isdigit():
            return None
        if len(s) == 4:
            h, m = int(s[:2]), int(s[2:])
        elif len(s) <= 2:
            h, m = int(s), 0
        else:
            return None
    if not (0 <= h <= 23 and 0 <= m <= 59):
        return None
    return h * 60 + m


def fmt(minutes):
    minutes %= 1440
    return '%02d:%02d' % (minutes // 60, minutes % 60)


def solve(level):
    """返回 (降落当地时刻, 相对出发日的天数偏移)。"""
    _, _, from_off, depart, duration, _, to_off, _, _ = level
    local = parse_hhmm(depart) - from_off + duration + to_off
    return fmt(local), local // 1440


def off_text(off):
    sign = '+' if off >= 0 else '-'
    a = abs(off)
    if a % 60 == 0:
        return '%s%d' % (sign, a // 60)
    return '%s%d:%02d' % (sign, a // 60, a % 60)


def ask():
    try:
        return input('  > ')
    except (EOFError, KeyboardInterrupt):
        print('\n\n游戏结束，再见。')
        raise SystemExit(0)


score = 0


def render(idx, level):
    title, fcity, foff, depart, dur, tcity, toff, ans, note = level
    print('\n' + '=' * 58)
    print('第 %d 关 · %s      （当前总分 %d / 100）' % (idx, title, score))
    print('-' * 58)
    print('出发：%s  当地时间 %s   （时差 UTC%s）' % (fcity, depart, off_text(foff)))
    print('飞行：%d 小时 %02d 分' % (dur // 60, dur % 60))
    print('到达：%s   （时差 UTC%s）' % (tcity, off_text(toff)))
    print('\n题目：降落时，%s的当地钟表是几点？（输入 HH:MM）' % tcity)
    print('说明：%s' % note)


def play_level(idx, level):
    global score
    title, fcity, foff, depart, dur, tcity, toff, ans, note = level
    lv = 20
    render(idx, level)
    while True:
        raw = ask().strip()
        if raw == '':
            render(idx, level)
            continue
        low = raw.lower()
        if low in ('q', 'quit', 'exit', '退出'):
            print('\n已退出。本局得分 %d 分。' % score)
            raise SystemExit(0)
        if low in ('hint', 'h', '提示', '?'):
            utc = parse_hhmm(depart) - foff
            print('提示：出发时刻换成 UTC 是 %s（UTC 日期偏移 %+d 天）。' % (fmt(utc), utc // 1440))
            lv = max(4, lv - 10)
            continue
        if low in ('help', 'rules', '规则'):
            print(HELP)
            continue
        guess = parse_hhmm(raw)
        if guess is None:
            print('（看不懂这个时间，请用 HH:MM，例如 14:20）')
            continue
        real, day = solve(level)
        if fmt(guess) == real:
            print('√ 正确！降落当地时间 %s。' % real)
            if day > 0:
                print('  跨了日期线，落地是出发日之后第 %d 天。' % day)
            elif day < 0:
                print('  注意：落地日期比出发日期还早 %d 天。' % (-day))
            else:
                print('  当天抵达。')
            return lv
        lv = max(4, lv - 8)
        print('× 不对。思路：先减出发时差，加上飞行时长，再加目的地时差。')
        if lv <= 4:
            print('（已到保底分，公布正确答案：%s）' % real)
            return lv


def play():
    global score
    print(HELP)
    for i, level in enumerate(LEVELS, 1):
        gained = play_level(i, level)
        score += gained
        print('本关得分：%d；累计 %d 分。' % (gained, score))
    print('\n全部通关！总分 %d / 100。' % score)
    if score == 100:
        print('满分！你已经能在脑子里做时区换算了。')
    elif score >= 80:
        print('很强。半时区、45 分钟时区都没难住你。')
    elif score >= 60:
        print('不错。记住三步：减出发时差 → 加飞行时长 → 加落地时差。')
    else:
        print('时区的坑主要在半时区和跨日期线，多练两遍就顺了。')
    print('感谢游玩，明天见。')


def check():
    print('【自检】航班时刻谜题')
    errs = []
    for i, level in enumerate(LEVELS, 1):
        title, fcity, foff, depart, dur, tcity, toff, ans, note = level
        if parse_hhmm(depart) is None:
            errs.append('第 %d 关：出发时刻无法解析' % i)
            continue
        if dur <= 0:
            errs.append('第 %d 关：飞行时长必须为正' % i)
        for name, off in (('出发', foff), ('目的地', toff)):
            if not (-720 <= off <= 840):
                errs.append('第 %d 关：%s时差超出合理范围' % (i, name))
        got, day = solve(level)
        # 独立复核：UTC 起飞 + 飞行时长，再折算到目的地
        utc = parse_hhmm(depart) - foff + dur
        got2 = fmt(utc + toff)
        ok = got == ans and got2 == ans
        print('第 %d 关 %s→%s：内置 %s，两法 %s / %s，日期偏移 %+d 天  %s' %
              (i, fcity, tcity, ans, got, got2, day, '√' if ok else '×'))
        if got != ans:
            errs.append('第 %d 关：计算值 %s ≠ 内置 %s' % (i, got, ans))
        if parse_hhmm(ans) is None or fmt(parse_hhmm(ans)) != ans:
            errs.append('第 %d 关：答案 %s 无法被解析器回环' % i)
    cases = {'8:05': 485, '08:05': 485, '0805': 485, '8：05': 485, '9': 540,
             '23:59': 1439, '次日 13:00': 780, '1420': 860}
    for text, want in cases.items():
        if parse_hhmm(text) != want:
            errs.append('解析器「%s」应为 %d，实为 %r' % (text, want, parse_hhmm(text)))
    for text in ('25:00', '12:60', 'abc', '1:2:3', ''):
        if parse_hhmm(text) is not None:
            errs.append('解析器本应拒绝「%s」' % text)
    answers = [lv[7] for lv in LEVELS]
    if len(set(answers)) != len(answers):
        errs.append('存在答案重复的关卡：%s' % answers)
    if errs:
        print('\n发现 %d 个问题：' % len(errs))
        for x in errs:
            print('  × ' + x)
        return 1
    print('\n全部通过：5 关答案与两种算法一致，解析器单元测试通过，答案无重复。')
    return 0


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c', 'check'):
        sys.exit(check())
    play()
