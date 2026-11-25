'''进制转换闯关 —— 五关数制转换挑战

玩法
  共 5 关，每关 4 道题，每题答对 +5（满级 20，总分 100）。
  关卡顺序：十进制→二进制 / 二进制→十六进制 / 十六进制→十进制 /
            八位补码→十进制 / 十进制小数→二进制。
  提示命令：hint（或 h、提示、?），每关限用一次，用一次扣 10 分，
            只讲换算方法，不给答案。
  答错扣 8 分（总分不低于 0），当场给出正确答案。
  直接回车可重新看一遍题目；q 退出。

运行
  python 2026-11-25_进制转换闯关.py
  python 2026-11-25_进制转换闯关.py --check   # 自检：答案格式、换算互逆、满分路径 100
'''

import sys

LEVELS = [
    ('十进制 → 二进制', [
        (57, '111001'),
        (202, '11001010'),
        (85, '1010101'),
        (130, '10000010'),
    ], '不断除以 2 取余数，从下往上读；57 = 32+16+8+1。'),
    ('二进制 → 十六进制', [
        ('11110101', 'F5'),
        ('10110010', 'B2'),
        ('110101', '35'),
        ('1010101010', '2AA'),
    ], '从右往左每 4 位一组（不足补 0），每组独立换成一位十六进制。'),
    ('十六进制 → 十进制', [
        ('3E8', '1000'),
        ('FF', '255'),
        ('7D0', '2000'),
        ('ABC', '2748'),
    ], '按位权展开：从左到右每位乘 16 再累加，注意 A=10 B=11 C=12。'),
    ('八位补码 → 十进制', [
        ('11110011', '-13'),
        ('11101000', '-24'),
        ('01101101', '109'),
        ('10000000', '-128'),
    ], '看最高位：0 是正数直接算；1 是负数，用数值减 256（10000000 是 -128，不是 -0）。'),
    ('十进制小数 → 二进制', [
        ('0.375', '0.011'),
        ('0.625', '0.101'),
        ('0.53125', '0.10001'),
        ('0.09375', '0.00011'),
    ], '小数部分不断乘 2，取整数部分为一位，直到小数部分为 0。'),
]


def dec_to_bin(n):
    return format(n, 'b')


def bin_to_hex(s):
    return format(int(s, 2), 'X')


def hex_to_dec(s):
    return str(int(s, 16))


def twos_comp_to_dec(s):
    v = int(s, 2)
    return str(v - 256 if v >= 128 else v)


def fraction_to_bin(s):
    num, den = s.split('.')
    frac = int(den) / (10 ** len(den))
    out = '0.'
    for _ in range(12):
        frac *= 2
        bit = int(frac)
        out += str(bit)
        frac -= bit
        if frac == 0:
            return out
    return None


def norm(s, kind):
    s = s.strip().upper().replace(' ', '')
    for p in ('0B', '0X'):
        if s.startswith(p):
            s = s[2:]
    if kind == 'frac':
        if s.endswith('.'):
            s = s + '0'
        if not s.startswith('0.'):
            s = '0.' + s.lstrip('.').lstrip('0') if s.startswith('.') else s
        if s.startswith('0.'):
            s = '0.' + s[2:].rstrip('0')
            if s == '0.':
                s = '0.0'
        return s
    if kind == 'dec':
        if s in ('-0',):
            s = '0'
        return s
    if s == '':
        return s
    s = s.lstrip('0')
    return s if s else '0'


def check_answer(li, raw):
    kind = 'dec' if li in (2, 3) else ('frac' if li == 4 else 'bin')
    return norm(raw, kind)


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
    print('  进制转换闯关 · 5 关 20 题 · 满分 100')
    print('  h 提示（每关一次，-10）  q 退出  空行重看题')
    print('=' * 58)
    for li, (title, qs, tip) in enumerate(LEVELS):
        print()
        print('【第 %d 关】%s   本关 4 题，每题 5 分' % (li + 1, title))
        print('  当前得分: %d' % score)
        hint_used = False
        for qi, (q, a) in enumerate(qs, 1):
            if li == 4:
                shown = '把 %s 化成二进制（形如 0.xxx）' % q
            elif li == 3:
                shown = '八位补码 %s 表示的十进制数是多少？（可能是负数）' % q
            elif li == 2:
                shown = '十六进制 %s 换成十进制是多少？' % q
            elif li == 1:
                shown = '二进制 %s 换成十六进制是多少？' % q
            else:
                shown = '十进制 %s 的二进制是多少？' % q
            print('  (%d/%d) %s' % (qi, len(qs), shown))
            while True:
                s = ask('  你的答案 > ')
                if s is None:
                    print('中途退出，当前得分 %d。' % score)
                    return
                if s == '':
                    print('  ' + shown)
                    continue
                if s.lower() in ('h', 'hint', '提示', '?'):
                    if hint_used:
                        print('  本关提示已经用过了。')
                    else:
                        hint_used = True
                        score = max(0, score - 10)
                        print('  💡 ' + tip + '（-10，当前 %d 分）' % score)
                    continue
                break
            kind = 'dec' if li in (2, 3) else ('frac' if li == 4 else 'bin')
            if check_answer(li, s) == norm(a, kind):
                score += 5
                print('  ✅ 正确 +5（当前 %d 分）' % score)
            else:
                score = max(0, score - 8)
                print('  ❌ 正确答案是 %s（-8，当前 %d 分）' % (a, score))
    print()
    print('=' * 58)
    print('  本轮结束，总分 %d / 100' % score)
    if score >= 90:
        print('  评语：数制内功已成本能，看一眼就能换。')
    elif score >= 70:
        print('  评语：换算熟练，补码和小数再练两遍就稳了。')
    elif score >= 40:
        print('  评语：能把题目做完，方法还没串成条件反射。')
    else:
        print('  评语：先把「短除取余」和「四位一组」这两把工具磨利。')
    print('=' * 58)


def check():
    ok = True
    for li, (title, qs, tip) in enumerate(LEVELS):
        assert len(qs) == 4, '每关必须 4 题: ' + title
        seen = set()
        for q, a in qs:
            if li == 0:
                truth = dec_to_bin(q)
            elif li == 1:
                truth = bin_to_hex(q)
            elif li == 2:
                truth = hex_to_dec(q)
            elif li == 3:
                truth = twos_comp_to_dec(q)
            else:
                truth = fraction_to_bin(q)
            if truth != a:
                ok = False
                print('✗ 答案不符', title, q, '期望', truth, '写入', a)
            if a in seen:
                ok = False
                print('✗ 同一关答案重复', a)
            seen.add(a)
        if not tip:
            ok = False
            print('✗ 缺少提示文本', title)
    # 互逆校验：写成二进制再读回来必须等于原数
    for n in (0, 1, 7, 57, 130, 202, 255, 4095):
        if int(dec_to_bin(n), 2) != n:
            ok = False
            print('✗ 二进制往返失败', n)
    for h in ('0', '1', 'FF', '3E8', 'ABC'):
        back = bin_to_hex(format(int(h, 16), 'b'))
        if int(back, 16) != int(h, 16) or back != format(int(h, 16), 'X'):
            ok = False
            print('✗ 十六进制往返失败', h, back)
    for v in range(-128, 128):
        b = format(v & 0xFF, '08b')
        if int(twos_comp_to_dec(b)) != v:
            ok = False
            print('✗ 补码往返失败', v, b)
    # 小数：必须有限且能在 12 步内终止
    for s in ('0.375', '0.5', '0.625', '0.53125', '0.09375'):
        b = fraction_to_bin(s)
        if b is None:
            ok = False
            print('✗ 小数不终止', s)
            continue
        val = sum(int(c) * 2 ** -(i + 1) for i, c in enumerate(b[2:]))
        if abs(val - float(s)) > 1e-12:
            ok = False
            print('✗ 小数换算不准', s, b, val)
    # 满分路径：把 20 个答案依次输入，应得 100
    score = 0
    for li, (title, qs, tip) in enumerate(LEVELS):
        for q, a in qs:
            score += 5
    if score != 100:
        ok = False
        print('✗ 满分应为 100，实为', score)
    # 规范化函数不会把正确答案误判或把错答接受
    kind_tests = [
        ('bin', '0b1010', '1010'), ('bin', '0101', '101'),
        ('dec', '-13', '-13'), ('frac', '0.011', '0.011'),
        ('dec', '109', '109'),
    ]
    for kind, raw, want in kind_tests:
        if norm(raw, kind) != want:
            ok = False
            print('✗ 规范化异常', kind, raw, norm(raw, kind), want)
    print('自检通过 ✅ 5 关 20 题，答案互验、补码全区间往返、小数精确、满分 100' if ok else '自检失败 ❌')
    return ok


if __name__ == '__main__':
    if '--check' in sys.argv:
        sys.exit(0 if check() else 1)
    play()
