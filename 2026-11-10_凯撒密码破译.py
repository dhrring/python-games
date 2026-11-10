# -*- coding: utf-8 -*-
"""
凯撒密码破译（Caesar Cipher 解密挑战）
=========================================
凯撒密码：把每个字母在字母表上向后移动固定位数（位移量 k），
比如位移 3 时，A→D、B→E、……、Z→C。
程序给你一段英文名言的「密文」，你的任务是找出位移量、还原出明文。

游玩方法（看清楚，这是关键）：
  直接输入答案      例如： HELLO WORLD   （会当作你的破译结果，忽略大小写和标点比较）
  k 数字            例如： k 5         显示「位移 5」解密后的预览，方便你对比
  freq              统计密文里各字母出现的次数（可以辅助猜位移，看哪个字母最像 E）
  hint              花提示：告诉你一句明文的开头几个词
  q                 退出
  每关直接提交答案最多 3 次，提交越少、分数越高。共 3 关。
运行：python3 2026-11-10_凯撒密码破译.py
"""

import string
import re

ALPHABET = string.ascii_uppercase

LEVELS = [
    {
        "title": "第 1 关 · 入门",
        "plain": "HELLO WORLD",
        "shift": 3,
        "hint": "明文是一句常见的打招呼语，两个单词，共 11 个字母。",
        "score": 100,
    },
    {
        "title": "第 2 关 · 进阶",
        "plain": "TIME IS MONEY",
        "shift": 7,
        "hint": "一句话谚语，关于时间与金钱，三个单词。",
        "score": 150,
    },
    {
        "title": "第 3 关 · 挑战",
        "plain": "STAY HUNGRY STAY FOOLISH",
        "shift": 11,
        "hint": "乔布斯那句著名的「求知若饥，虚心若愚」的英文原句。",
        "score": 200,
    },
]


def shift_text(text, k, decode=False):
    """k 为加密时的位移量；decode=True 表示反向解密。"""
    step = k if not decode else -k
    out = []
    for ch in text.upper():
        if ch in ALPHABET:
            idx = (ALPHABET.index(ch) + step) % 26
            out.append(ALPHABET[idx])
        else:
            out.append(ch)
    return "".join(out)


def cipher_of(plain, shift):
    return shift_text(plain, shift, decode=False)


def normalize(s):
    return re.sub(r"[^A-Z]", "", s.upper())


def freq_report(cipher):
    text = normalize(cipher)
    counts = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    top = sorted(counts.items(), key=lambda x: -x[1])
    return "、".join(f"{ch}({n})" for ch, n in top[:6])


def play_level(lvl, idx):
    plain = lvl["plain"]
    cipher = cipher_of(plain, lvl["shift"])
    tries = 0
    used_hint = False

    print("\n" + "=" * 52)
    print(lvl["title"])
    print("=" * 52)
    print(f"密文：\n  {cipher}")
    print(f"（明文共 {len(normalize(plain))} 个字母，位移量未知）")

    while True:
        raw = input("\n你的操作（直接输入明文 / k 数字 / freq / hint / q）：").strip()
        if not raw:
            print("需要输入内容。")
            continue
        low = raw.lower()
        if low in ("q", "quit", "exit"):
            return None, 0

        if low.startswith("k "):
            part = raw[2:].strip()
            if not part.lstrip("-").isdigit():
                print("用法：k 5")
                continue
            k = int(part) % 26
            print(f"位移 {k} 解出：\n  {shift_text(cipher, k, decode=True)}")
            continue

        if low in ("freq", "f", "频率"):
            print(f"密文字母频率前 6 位：{freq_report(cipher)}")
            print("（英语里 E 最常见，最频繁的那个密文字母很可能就是 E，从而推出位移）")
            continue

        if low in ("hint", "h", "提示"):
            if not used_hint:
                used_hint = True
            print(f"提示：{lvl['hint']}")
            continue

        # 视为答案
        if normalize(raw) == normalize(plain):
            base = lvl["score"]
            penalty = 30 * (tries - 1 if tries > 0 else 0) + (25 if used_hint else 0)
            earned = max(20, base - penalty)
            print(f"\n✅ 破译成功！明文就是：{plain}")
            print(f"   位移量 k = {lvl['shift']}（原始加密把每个字母向后移了 {lvl['shift']} 位）")
            print(f"   提交次数 {tries + 1} 次{('，用了提示' if used_hint else '')}，本关得分 {earned}")
            return True, earned

        tries += 1
        if tries >= 3:
            print(f"\n❌ 三次机会用完了。正确答案是：{plain}（位移 k = {lvl['shift']}）")
            print(f"   验证：位移 {lvl['shift']} 解密 = {shift_text(cipher, lvl['shift'], decode=True)}")
            return False, 0
        print(f"❌ 不对，还剩 {3 - tries} 次提交机会（也可以先用 k 数字 逐个尝试位移）")


def main():
    print("=" * 52)
    print("      🔐 凯撒密码破译 Caesar Cipher")
    print("=" * 52)
    print("给你密文，靠「试位移 + 猜词」还原明文。")
    print("小技巧：先用 k 1 ~ k 25 扫一遍，总有一个位移会读出通顺的英文。")

    total = 0
    passed = 0
    for i, lvl in enumerate(LEVELS):
        ok, score = play_level(lvl, i)
        if ok is None:
            print("\n你已退出。")
            break
        total += score
        if ok:
            passed += 1

    print("\n" + "=" * 52)
    print(f"  通关 {passed}/{len(LEVELS)} 关，总得分 {total}")
    if passed == len(LEVELS):
        print("  🏆 全部破译，密码学嗅觉不错！")
        if total >= 400:
            print("  🌟 几乎没靠提示，直接看出位移，很强。")
    print("  冷知识：凯撒密码只有 25 种可能位移，属于「可暴力破解」的古典密码，")
    print("  现代密码（AES）密钥空间是 2^128 级别，靠试是试不出来的。")
    print("=" * 52)


if __name__ == "__main__":
    main()
