# -*- coding: utf-8 -*-
"""
汉明码实验室 · Hamming(7,4)
====================================================
1960 年代的计算机用穿孔纸带存程序，纸带一破洞就会有一位 0 变成 1。
汉明想了个便宜的办法：多存 3 位「校验位」，就能自动找出并修正 1 位错误。

本游戏用的是最经典的 (7,4) 汉明码：
  7 位码字，其中 4 位是数据，3 位是校验位。
  位置从 1 数到 7，**2 的幂次位置（1、2、4）放校验位**，其余 3、5、6、7 放数据。

  校验规则（偶校验，每组的 1 的个数要为偶数）：
    第 1 组：位置 1、3、5、7
    第 2 组：位置 2、3、6、7
    第 4 组：位置 4、5、6、7

  接错时把三组校验各算一次，得到 3 个比特的「伴随式」s1 s2 s4：
    它的二进制值正好就是出错位置（0 表示没有错位）——这就是汉明码最漂亮的地方。

三关玩法：
  第 1 关：给你 4 位数据，请算出 7 位码字
  第 2 关：给你 7 位收到的码，请指出错在哪一位（没错填 0）
  第 3 关：给你 7 位收到的码，请你纠错后还原出 4 位原始数据
  每关 5 题，每题 20 分。命令：hint（看校验分组规则，−30 分）、q（退出）

运行：python3 2026-11-19_汉明码实验室.py
"""

import random

PARITY_POS = [1, 2, 4]          # 校验位所在的 1-based 位置
DATA_POS = [3, 5, 6, 7]        # 数据位所在的 1-based 位置
GROUPS = {1: [1, 3, 5, 7], 2: [2, 3, 6, 7], 4: [4, 5, 6, 7]}


def encode(data):
    """4 位数据 -> 7 位码字（列表，下标 0 对应位置 1）。"""
    word = [0] * 7
    for pos, bit in zip(DATA_POS, data):
        word[pos - 1] = bit
    for p in PARITY_POS:
        s = 0
        for pos in GROUPS[p]:
            if pos != p:
                s ^= word[pos - 1]
        word[p - 1] = s
    return word


def syndrome(word):
    """三组校验结果拼成的伴随式（十进制），0 表示无错。"""
    s = 0
    for p in PARITY_POS:
        v = 0
        for pos in GROUPS[p]:
            v ^= word[pos - 1]
        if v:
            s += p
    return s


def fix(word):
    """纠正 1 位错误，返回 (纠正后的码字, 出错位置)。"""
    w = word[:]
    pos = syndrome(w)
    if pos:
        w[pos - 1] ^= 1
    return w, pos


def decode(word):
    """7 位收到码 -> 4 位数据（先纠 1 位错）。"""
    w, _ = fix(word)
    return [w[p - 1] for p in DATA_POS]


def bits_to_str(bits):
    return "".join(str(b) for b in bits)


def parse_bits(raw, length):
    cleaned = "".join(ch for ch in raw if ch in "01")
    if len(cleaned) != length or any(ch not in "01" for ch in raw if ch.strip()):
        raise ValueError(f"请输入 {length} 位，只含 0 和 1（可以连续写，也可以拿空格隔开）")
    return [int(ch) for ch in cleaned]


def hint_text():
    print("  校验分组（偶校验：每组 1 的个数必须为偶数）：")
    print("    位置 1、3、5、7  → 得到 s1")
    print("    位置 2、3、6、7  → 得到 s2")
    print("    位置 4、5、6、7  → 得到 s4")
    print("    出错位置 = s1 + 2×s2 + 4×s4（0 表示没错）")


def run_level(idx, kind):
    print("\n" + "=" * 62)
    titles = {
        1: "第 1 关 · 编码：4 位数据 → 7 位码字",
        2: "第 2 关 · 纠错：指出错在第几位",
        3: "第 3 关 · 译码：纠错后还原原始数据",
    }
    print(f"  {titles[kind]}（5 题，每题 20 分）")
    print("=" * 62)

    penalty = 0
    score = 0
    questions = []
    used = set()
    while len(questions) < 5:
        data = [random.randint(0, 1) for _ in range(4)]
        code = encode(data)
        if kind == 1:
            questions.append(("enc", data, code, None))
        elif kind == 2:
            flip = random.choice([None] + list(range(7)))
            received = code[:]
            if flip is not None:
                received[flip] ^= 1
            questions.append(("fix", data, received, (flip + 1) if flip is not None else 0))
        else:
            flip = random.choice([None] + list(range(7)))
            received = code[:]
            if flip is not None:
                received[flip] ^= 1
            questions.append(("dec", data, received, (flip + 1) if flip is not None else 0))
        used.add(bits_to_str(data))

    for qi, (mode, data, word, errpos) in enumerate(questions, 1):
        if mode == "enc":
            print(f"\n  [{qi}/5] 数据（4 位，位置 3、5、6、7）：{bits_to_str(data)}")
            prompt = "  请写出完整的 7 位码字 > "
        elif mode == "fix":
            print(f"\n  [{qi}/5] 收到的 7 位码：{bits_to_str(word)}")
            prompt = "  错在第几位？（没错填 0）> "
        else:
            print(f"\n  [{qi}/5] 收到的 7 位码：{bits_to_str(word)}")
            prompt = "  纠错后原始 4 位数据是？> "

        while True:
            try:
                raw = input(prompt).strip()
            except EOFError:
                print("\n输入中断，提前结束。")
                return score, None
            if not raw:
                continue
            low = raw.lower()
            if low in ("q", "quit"):
                return score, None
            if low == "hint":
                if penalty == 0:
                    penalty = 30
                hint_text()
                print(f"  （本关上限已降为 {max(0, 100 - penalty)} 分）")
                continue

            try:
                if mode == "enc":
                    ans = parse_bits(raw, 7)
                    if ans == word:
                        print("  ✅ 码字正确！")
                        score += 20
                        break
                    # 分清是校验位错还是数据位错
                    diffs = [i + 1 for i in range(7) if ans[i] != word[i]]
                    print(f"  ❌ 位置 {diffs} 和标准码字不一致。"
                          " 检查：每个校验组里 1 的个数要为偶数。")
                elif mode == "fix":
                    if not raw.isdigit():
                        raise ValueError("请输入一个数字（位序 1~7，没错填 0）")
                    g = int(raw)
                    if not (0 <= g <= 7):
                        raise ValueError("位序只能是 0 到 7")
                    if g == errpos:
                        msg = "没错位" if errpos == 0 else f"错在位置 {errpos}"
                        print(f"  ✅ 正确：{msg}！")
                        score += 20
                        break
                    print(f"  ❌ 不对。再算一次三组校验：s1+s2+s4 的二进制值就是出错位置。")
                else:
                    ans = parse_bits(raw, 4)
                    if ans == data:
                        print("  ✅ 还原正确！")
                        score += 20
                        break
                    print("  ❌ 还不对。先把 7 位码纠错，再取位置 3、5、6、7。")
            except ValueError as msg:
                print(f"  {msg}")

    print(f"\n  本关得分 {score}/100" + (f"（含提示扣分 {penalty}）" if penalty else ""))
    return score, True


def play():
    print("=" * 62)
    print("      🧮 汉明码实验室 · Hamming(7,4)")
    print("=" * 62)
    print("7 位码字里藏 4 位数据 + 3 位校验，能自动纠正 1 位翻转。")

    # 开局自检：16 个数据字全部编码-纠错闭环；每种「0~7 位翻转」都能被准确定位
    for val in range(16):
        data = [(val >> (3 - i)) & 1 for i in range(4)]
        code = encode(data)
        assert syndrome(code) == 0, f"码字伴随后非零：{bits_to_str(code)}"
        assert decode(code) == data
        for flip in range(7):
            rec = code[:]
            rec[flip] ^= 1
            fixed, pos = fix(rec)
            assert pos == flip + 1, f"定位错误：翻转 {flip + 1} 位得到 {pos}"
            assert fixed == code, "纠错后未恢复原码字"
            assert decode(rec) == data, "译码失败"
    # 码距自检：任意两个码字至少相差 3 位（这正是能纠 1 位错的原因）
    words = [encode([(v >> (3 - i)) & 1 for i in range(4)]) for v in range(16)]
    mind = min(sum(a != b for a, b in zip(x, y))
               for i, x in enumerate(words) for y in words[i + 1:])
    print(f"  自检：16 个码字两端全部通过，最小码距 {mind}（能纠 1 位错需要 ≥3）。")

    total = 0
    for kind in (1, 2, 3):
        sc, finished = run_level(kind, kind)
        total += sc
        if finished is None:
            break

    print("\n" + "=" * 62)
    print(f"  结算：总分 {total}/300")
    if total >= 240:
        print("  🏆 你已经掌握「伴随式 = 出错位置」这个汉明码核心。")
    elif total >= 120:
        print("  👍 记住：三个校验组各自算奇偶，结果拼起来就是位置。")
    else:
        print("  🙂 先手算一个例子：数据 1011 → 码字 0110011。")
    print("=" * 62)


if __name__ == "__main__":
    play()
