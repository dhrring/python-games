# -*- coding: utf-8 -*-
"""
成语接龙（Idiom Chain）
======================
你和电脑轮流说成语，每个成语的首字必须和上一个成语的末字相同。
内置常见成语词库，超时/重复/接不上则结束。纯标准库实现。
运行：python3 2026-10-27_成语接龙.py
"""

import random

# 常见成语词库
IDIOMS = [
    "一帆风顺", "画蛇添足", "亡羊补牢", "守株待兔", "井底之蛙",
    "一鸣惊人", "百发百中", "千军万马", "万水千山", "天长地久",
    "水落石出", "山清水秀", "风和日丽", "人山人海", "心旷神怡",
    "胸有成竹", "目中无人", "眼高手低", "耳聪目明", "口若悬河",
    "手忙脚乱", "脚踏实地", "头头是道", "面红耳赤", "胆大心细",
    "马到成功", "龙飞凤舞", "虎头蛇尾", "鹤立鸡群", "牛刀小试",
    "鹏程万里", "莺歌燕舞", "鱼跃龙门", "鸟语花香", "风驰电掣",
    "雷厉风行", "电光石火", "光明磊落", "独当一面", "双管齐下",
    "一丝不苟", "三心二意", "四面八方", "五颜六色", "六神无主",
    "七上八下", "九牛一毛", "十全十美", "万无一失", "一举两得",
]


def computer_move(last_char, used):
    """电脑找一个首字=末字的成语"""
    candidates = [i for i in IDIOMS if i[0] == last_char and i not in used]
    if not candidates:
        return None
    return random.choice(candidates)


def main():
    print("=" * 40)
    print("        🀄 成语接龙 Idiom Chain")
    print("=" * 40)
    print("你和电脑轮流接成语，下一词的第一个字必须等于上一词的最后一个字。")
    print("输入 q 退出。重复或接不上则结束。")
    used = set()
    # 随机开始一个成语
    start = random.choice(IDIOMS)
    used.add(start)
    print(f"电脑开局：{start}")
    last_char = start[-1]

    turn = 1
    while True:
        word = input(f"[你] 用“{last_char}”开头接一个成语：").strip()
        if word.lower() in ("q", "quit", "exit"):
            print("你退出游戏。")
            return
        if len(word) != 4 or not all("\u4e00" <= ch <= "\u9fff" for ch in word):
            print("请输入4字成语。")
            continue
        if word[0] != last_char:
            print(f"首字必须是“{last_char}”。")
            continue
        if word in used:
            print("这个成语已经说过了。")
            continue
        # 简化：不校验词典真实性，仅校验格式与接龙规则
        used.add(word)
        print(f"你接：{word}")
        last_char = word[-1]

        comp = computer_move(last_char, used)
        if comp is None:
            print(f"电脑接不上“{last_char}”开头的成语了。")
            print("🎉 你赢了！")
            return
        used.add(comp)
        print(f"电脑接：{comp}")
        last_char = comp[-1]
        turn += 1


if __name__ == "__main__":
    main()
