# -*- coding: utf-8 -*-
"""
逻辑猜牌（Guess the Card）
=========================
经典"二十问"推理游戏：电脑从52张牌里抽一张，
你通过"是/否"问题（颜色、花色、点数大小）缩小范围，最终锁定那张牌。
纯标准库实现。运行：python3 2026-10-29_逻辑猜牌.py
"""

import random

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
COLOR_OF = {"♠": "黑", "♥": "红", "♦": "红", "♣": "黑"}
SUIT_NAME = {"♠": "黑桃", "♥": "红心", "♦": "方块", "♣": "梅花"}


def describe(card):
    suit, rank = card
    return f"{SUIT_NAME[suit]}{rank}"


def main():
    print("=" * 40)
    print("        🃏 逻辑猜牌 Guess the Card")
    print("=" * 40)
    print("电脑从52张牌里抽一张，你用是/否问题缩小范围。")
    print("支持指令：")
    print("  红 / 黑            → 问颜色")
    print("  黑桃 / 红心 / 方块 / 梅花 → 问花色")
    print("  >K / <5 / =Q       → 问点数大小")
    print("  猜 黑桃A           → 直接猜一张牌")
    print("  q 退出，提示 看线索")
    deck = [(s, r) for s in SUITS for r in RANKS]
    card = random.choice(deck)
    remaining = deck[:]
    attempts = 0


    def rank_index(r):
        return RANKS.index(r)

    def apply(filter_fn, question_hit, question_text):
        nonlocal remaining
        # 答"是"保留满足条件的牌；答"否"排除满足条件的牌（保留不满足的）
        remaining = [c for c in remaining if filter_fn(c) == question_hit]
        print(f"{'✅ 是' if question_hit else '❌ 不是'}：{question_text}。剩余 {len(remaining)} 张。")

    while True:
        attempts += 1
        print(f"\n[第{attempts}次] 候选 {len(remaining)} 张")
        cmd = input("问题：").strip()
        if cmd.lower() in ("q", "quit", "exit"):
            print("退出游戏。")
            return
        if cmd == "提示":
            print(f"线索：{COLOR_OF[card[0]]}色，{SUIT_NAME[card[0]]}，点数{card[1]}")
            continue
        if cmd.startswith("猜 "):
            name = cmd[2:].strip()
            target = None
            for s in SUITS:
                if name.startswith(SUIT_NAME[s]):
                    rank = name[len(SUIT_NAME[s]):]
                    if rank in RANKS:
                        target = (s, rank)
            if target:
                if target == card:
                    print(f"🎉 猜中了！就是 {describe(card)}，用了 {attempts} 次。")
                    return
                else:
                    print(f"❌ 不是 {name}。")
                    continue
            print("格式应为：猜 黑桃A。")
            continue
        # 颜色
        if cmd in ("红", "黑"):
            hit = COLOR_OF[card[0]] == cmd
            apply(lambda c: COLOR_OF[c[0]] == cmd, hit, f"{cmd}色")
        # 花色
        elif cmd in SUIT_NAME.values():
            hit = SUIT_NAME[card[0]] == cmd
            apply(lambda c: SUIT_NAME[c[0]] == cmd, hit, f"{cmd}")
        # 大小
        elif len(cmd) >= 2 and cmd[0] in (">", "<", "=") and cmd[1:] in RANKS:
            val = rank_index(cmd[1:])
            cur = rank_index(card[1])
            if cmd[0] == ">":
                hit = cur > val
                apply(lambda c: rank_index(c[1]) > val, hit, f"> {cmd[1:]}")
            elif cmd[0] == "<":
                hit = cur < val
                apply(lambda c: rank_index(c[1]) < val, hit, f"< {cmd[1:]}")
            else:
                hit = cur == val
                apply(lambda c: rank_index(c[1]) == val, hit, f"= {cmd[1:]}")
        else:
            print("看不懂。试试：红 / 黑桃 / >K / 猜 黑桃A / 提示 / q。")
            continue

        if len(remaining) == 1:
            print(f"🎉 锁定！这张牌是 {describe(remaining[0])}，用了 {attempts} 次。")
            return
        if len(remaining) == 0:
            print("候选牌被排除光了，可能答错了。")
            return


if __name__ == "__main__":
    main()
