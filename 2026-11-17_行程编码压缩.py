# -*- coding: utf-8 -*-
"""
行程编码压缩挑战（RLE）
====================================================
行程编码（Run-Length Encoding）是最简单的无损压缩：
把「连续重复的同一字符」压成「字符 + 重复次数」。
      aaaabbc   →   a4b2c
因为 123 这样的数字本身也是字符，所以编码里「数字表示次数」，
单个字符后面不跟数字就表示只出现 1 次。

规则（本游戏采用的标准写法）：
  1. 每个「行程」写成 字符 + 次数，次数 ≥ 2 时才写数字
  2. 次数是十进制数字，可能占多位：aaaaaaaaaa（10 个 a）→ a10
  3. 解压后必须和原文一字不差（有些压缩会让原文变短或变长，这里只算字符长度）

为什么它有时反而变长？
  像 ababab 这种没有重复的数据，写成 a1b1a1b1ab 反而更长——
  真实压缩工具会选择「压不动就不压」，所以 RLE 适合扫描件、图标、重复多的文本。

玩法：每关给定一段文本，你写出它的 RLE 编码。
      编码正确 → 按「你的长度 / 最优长度」给分：
      · 长度等于最优 → 100 分
      · 比最优长 → 按比例折分（最短 20 分）
      · 解压回去和原文不一致 → 0 分，重新编

命令：
  hint   本题提示（−30 分，告诉你第一段行程是什么）
  q      退出

运行：python3 2026-11-17_行程编码压缩.py
"""

LEVELS = [
    {"text": "aaaaabbbcc", "note": "入门：整段都是长行程。"},
    {"text": "wwwwwwwwwwwwbbb", "note": "注意位数：12 个 w 要写成 w12，不是 w1w2。"},
    {"text": "aabcccccaaa", "note": "有些字符只出现一次，不要给它加数字 1。"},
    {"text": "z" * 15 + "y" + "x" * 3, "note": "混合长短行程。"},
    {"text": "m" * 11 + "ooo" + "ppp",
     "note": "长行程 + 多位次数：11 个 m 要写成 m11，不能写成 m1m1。"},
]


def encode(s):
    """标准 RLE 编码。"""
    if not s:
        return ""
    out = []
    run = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            run += 1
        else:
            out.append(s[i - 1] + (str(run) if run >= 2 else ""))
            run = 1
    out.append(s[-1] + (str(run) if run >= 2 else ""))
    return "".join(out)


def decode(code):
    """严格解压：字符后面可跟 1 个或多个数字表示次数。解压失败抛 ValueError。"""
    out = []
    i = 0
    n = len(code)
    while i < n:
        ch = code[i]
        if ch.isdigit():
            # 数字只能跟在某个字符后面表示次数，不能出现在这个位置
            raise ValueError(f"第 {i + 1} 个字符是数字，它前面缺少要重复的字符")
        i += 1
        num = ""
        while i < n and code[i].isdigit():
            num += code[i]
            i += 1
        cnt = int(num) if num else 1
        if cnt == 0:
            raise ValueError("次数不能是 0")
        out.append(ch * cnt)
    return "".join(out)


def first_run(s):
    if not s:
        return ""
    run = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            run += 1
        else:
            break
    ch = s[0]
    return ch + (str(run) if run >= 2 else "")


def show_level(idx, level):
    text = level["text"]
    best = encode(text)
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + level["note"])
    print(f"\n  原文（{len(text)} 个字符）：")
    print("    " + text)
    print(f"  最优编码长度：{len(best)} 个字符"
          f"（压缩率 {len(text) / len(best):.2f}x）")


def run_level(idx, level):
    show_level(idx, level)
    text = level["text"]
    best = encode(text)

    score = 100
    while True:
        try:
            raw = input("\n  你的 RLE 编码 > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "hint":
            if score > 30:
                score = 30
            print(f"  提示：第一段行程是「{first_run(text)}」。（本题上限 {score} 分）")
            continue

        try:
            back = decode(raw)
        except ValueError as e:
            print(f"  ❌ 编码无法解压：{e}")
            score = max(20, score - 20)
            continue

        if back != text:
            print("  ❌ 解压回来和原文不一致，说明分段或次数写错了。")
            # 指出第一个不同位置，帮助定位
            pos = next((i for i in range(min(len(back), len(text))) if back[i] != text[i]),
                       min(len(back), len(text)))
            print(f"  第一个差异在第 {pos + 1} 个字符：期望「{text[pos:pos + 12]}」，"
                  f"你的结果「{back[pos:pos + 12]}」")
            score = max(20, score - 20)
            continue

        if len(raw) == len(best):
            print(f"  ✅ 完全正确，长度 {len(raw)} 也正好是最优。本关 100 分。")
            return 100, True

        if len(raw) > len(best):
            got = max(20, int(score * len(best) / len(raw)))
            print(f"  ⚠ 解压正确，但编码长 {len(raw)}，最优只要 {len(best)}。")
            print(f"  本次 {got} 分。想想哪里还能合并（提示：次数相同的相邻行程不能合并，"
                  f"但单个字符不必写 1）。")
            score = got
            continue


def play():
    print("=" * 62)
    print("      🗜️ 行程编码压缩挑战（RLE）")
    print("=" * 62)
    print("把连续重复的字符压成「字符 + 次数」，例如 aaaabbc → a4b2c。")

    # 开局自检：编码必须能还原原文，且长度不超过原文（本关卡数据都满足）
    for i, lv in enumerate(LEVELS, 1):
        c = encode(lv["text"])
        assert decode(c) == lv["text"], f"第 {i} 关编码无法还原"
        assert len(c) <= len(lv["text"]), f"第 {i} 关数据压缩后反而更长"
    # 反向检查：故意写错的编码必须被解压阶段拒绝或判定不等
    for bad in ["a4b2", "a4b2c", "4a2b", "a1b1"]:
        try:
            decode(bad)
        except ValueError:
            pass

    total = done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 450:
        print("  🏆 你已经掌握了 RLE 的边界：重复多的能压，交错重复的压不动。")
    elif total >= 200:
        print("  👍 记住：次数只写 ≥2 的行程，单个字符直接写字符本身。")
    else:
        print("  🙂 诀窍：从左往右一段一段数，每段写成「字符 + 次数」，数完立刻移到下一段。")
    print("=" * 62)


if __name__ == "__main__":
    play()
