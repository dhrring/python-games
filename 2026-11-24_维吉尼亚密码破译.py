'''维吉尼亚密码破译 —— 每日交互小游戏 2026-11-24（第 32 天）

【游戏简介】
每一关给你一段用维吉尼亚密码加密过的英文密文（已去掉空格、全大写）。
你要找出加密用的「密钥单词」，把它敲进去，就能把密文还原成人话。

维吉尼亚密码的规则：密钥循环使用，第 i 个明文字母向后移动「密钥第 i 位」格。
例如密钥 CAT：C=2、A=0、T=19，明文第一位移 2 格，第二位不移，第三位移 19 格……

【怎么玩】
1. 直接运行：python 2026-11-24_维吉尼亚密码破译.py
2. 每关输入一个英文密钥（不区分大小写），猜对得 20 分进下一关。
3. 命令：
   hint / h / 提示 / ?    查看提示（每次扣 10 分，每关最多 3 次）
   直接回车              重新显示本关密文
   q / quit / exit / 退出  中途退出
4. 猜错会扣 8 分，并把你这次的解密结果前 40 个字母印出来，方便你看「错在哪」。
5. 5 关共 100 分，每关保底 4 分。

【破译思路（自己先试试，再看提示）】
· 维吉尼亚密码破坏了单字母频率，但密钥长度会留下周期痕迹。
· 计算密文的「重合指数」IC = Σ f(f-1) / N(N-1)：随机英文约 0.038，正常英文约 0.066。
  按猜测的密钥长度把密文分列，每列单独算 IC，哪一组的 IC 明显升高，长度就对上。
· 知道长度后，每一列其实就是一个凯撒密码，用字母频率（E/T/A/O…）逐个破就行。

【自检】python 2026-11-24_维吉尼亚密码破译.py --check
（会重新加密比对、校验 5 关答案、验算重合指数与满分路径）
'''

import sys

LEVELS = [
    ('CAT', 'THE CAKE IS A LIE BUT THE RECIPE IS SIMPLE'),
    ('LEMON', 'EVERY LONG JOURNEY BEGINS WITH A SINGLE STEP'),
    ('MUSIC', 'THE PIANO IN THE HALL PLAYS ITSELF AT MIDNIGHT'),
    ('GARDEN', 'A BOTTLE OF LEMON JUICE IS WAITING BY THE OLD GATE'),
    ('PUZZLE', 'SOME SECRETS ARE HIDDEN IN PLAIN SIGHT FOR THOSE WHO LOOK TWICE'),
]

MAX_SCORE = 20
HINT_COST = 10
WRONG_COST = 8
FLOOR = 4


def shift(text, key, sign):
    '''维吉尼亚移位；只处理英文字母，密钥按字母位置循环。'''
    out = []
    k = key.upper()
    i = 0
    for ch in text:
        up = ch.upper()
        if 'A' <= up <= 'Z':
            s = ord(k[i % len(k)]) - 65
            out.append(chr(65 + (ord(up) - 65 + sign * s) % 26))
            i += 1
        else:
            out.append(ch)
    return ''.join(out)


def encrypt(plain, key):
    return shift(plain, key, 1)


def decrypt(cipher, key):
    return shift(cipher, key, -1)


def squeeze(text):
    '''去掉非字母并转大写——加密前后的统一形态。'''
    return ''.join(c for c in text.upper() if 'A' <= c <= 'Z')


def ic(text):
    '''重合指数，保留 4 位小数。'''
    n = len(text)
    if n < 2:
        return 0.0
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    return sum(v * (v - 1) for v in freq.values()) / (n * (n - 1))


def hints_for(key, plain):
    n = len(key)
    core = squeeze(plain)
    return [
        '密钥长度是 %d 个字母，密文重合指数约 %.4f（英文正文约 0.066，纯随机约 0.038）。' % (n, ic(core)),
        '密钥第一个字母是 %s，最后一个字母是 %s。' % (key[0], key[-1]),
        '正确解密后的明文开头是：%s……' % plain[:16],
    ]


def show_cipher(cipher):
    groups = ' '.join(cipher[i:i + 5] for i in range(0, len(cipher), 5))
    print('\n密文（共 %d 个字母）：' % len(cipher))
    for i in range(0, len(groups), 60):
        print('  ' + groups[i:i + 60])


def play():
    print('=' * 62)
    print('        维吉尼亚密码破译  ·  5 关 · 满分 100')
    print('=' * 62)
    print('每关给一段密文，找出加密用的密钥单词。输入 hint 要提示（-10），')
    print('q 退出，直接回车重看本关密文。\n')

    total = 0
    for idx, (key, plain) in enumerate(LEVELS, 1):
        cipher = encrypt(squeeze(plain), key)
        print('-' * 62)
        print('第 %d 关' % idx)
        show_cipher(cipher)
        print('\n输入密钥：')

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
                if hint_i >= 3:
                    print('本关提示已用完。')
                    continue
                level_score = max(FLOOR, level_score - HINT_COST)
                print('提示 %d：%s' % (hint_i + 1, hints_for(key, plain)[hint_i]))
                hint_i += 1
                continue
            if not raw:
                show_cipher(cipher)
                continue

            guess = squeeze(raw)
            if guess == key:
                level_score = max(FLOOR, level_score)
                total += level_score
                print('✔ 正确！明文是：%s' % plain)
                print('本关得分 %d，累计 %d 分。\n' % (level_score, total))
                break

            level_score = max(FLOOR, level_score - WRONG_COST)
            preview = decrypt(cipher, guess if guess else 'A')[:40]
            print('✘ 不对。按你的密钥解密，开头是：%s' % preview)
            print('  当前本关最高可得 %d 分。\n' % level_score)

    print('=' * 62)
    print('通关！总分 %d / 100' % total)
    if total >= 90:
        print('评语：密码分析员的料，密钥长度和频率都用上了。')
    elif total >= 70:
        print('评语：稳，中途靠提示也没耽误。')
    elif total >= 40:
        print('评语：入门了，下次试试先算重合指数再猜长度。')
    else:
        print('评语：别急，维吉尼亚密码靠的是耐心和统计。')
    print('=' * 62)


def check():
    print('[自检] 维吉尼亚密码破译')
    ok = True
    cores = []
    for idx, (key, plain) in enumerate(LEVELS, 1):
        core = squeeze(plain)
        cipher = encrypt(core, key)
        back = decrypt(cipher, key)
        cond = [
            ('明文全为英文字母', core.isalpha()),
            ('明文与密钥均大写', core == core.upper() and key == key.upper()),
            ('加密后无空格', ' ' not in cipher),
            ('解密可还原', back == core),
            ('密文长度等于明文', len(cipher) == len(core)),
            ('密钥为纯字母', key.isalpha()),
            ('答案明文不含本关密钥', key not in core),
            ('重合指数在合理区间', 0.02 < ic(cipher) < 0.09),
            ('明文长度足够(>30)', len(core) > 30),
        ]
        for name, good in cond:
            if not good:
                ok = False
                print('  ✘ 第%d关：%s 失败' % (idx, name))
        print('  第%d关 密钥=%s 长度=%d 明文字母数=%d IC=%.4f 解回前20=%s'
              % (idx, key, len(key), len(core), ic(cipher), back[:20]))
        cores.append(core)

    if len(set(k for k, _ in LEVELS)) != len(LEVELS):
        ok = False
        print('  ✘ 存在重复密钥')
    if len(set(cores)) != len(cores):
        ok = False
        print('  ✘ 存在重复明文')

    # 已知答案串检验：用答案密钥必须能解出原明文（模拟满分路径）
    sim_total = 0
    for key, plain in LEVELS:
        cipher = encrypt(squeeze(plain), key)
        if decrypt(cipher, key) == squeeze(plain):
            sim_total += MAX_SCORE
    if sim_total != 100:
        ok = False
        print('  ✘ 满分路径得分异常：%d' % sim_total)

    # 错误密钥必须解不出原文（防止密钥碰撞误判）
    for key, plain in LEVELS:
        cipher = encrypt(squeeze(plain), key)
        fake = 'B' * len(key)
        if fake != key and decrypt(cipher, fake) == squeeze(plain):
            ok = False
            print('  ✘ 第%d关 错误密钥也能解出答案' % LEVELS.index((key, plain)))

    print('[结果]', '全部通过 ✔' if ok else '有问题 ✘')
    return 0 if ok else 1


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('--check', '-c'):
        sys.exit(check())
    try:
        play()
    except (EOFError, KeyboardInterrupt):
        print('\n已退出。')