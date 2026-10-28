# -*- coding: utf-8 -*-
"""
单词拼写挑战（Spelling Bee）
============================
给出中文释义，你拼出对应的英文单词。内置常见英文词库，按难度随机抽题，
答对得分，答错给提示。纯标准库实现。
运行：python3 2026-10-28_单词拼写.py
"""

import random

# (英文, 中文, 难度提示)
WORDS = [
    ("apple", "苹果", "一个水果，五个字母"),
    ("water", "水", "生命之源，五个字母"),
    ("school", "学校", "学习的地方，六个字母"),
    ("computer", "电脑", "你正在用它，八个字母"),
    ("teacher", "老师", "教书育人，七个字母"),
    ("music", "音乐", "歌曲、旋律，五个字母"),
    ("orange", "橙子", "橘色水果，六个字母"),
    ("book", "书", "阅读的载体，四个字母"),
    ("family", "家庭", "家人，六个字母"),
    ("friend", "朋友", "陪你的人，六个字母"),
    ("happiness", "幸福", "快乐的感觉，九个字母"),
    ("mountain", "山", "高的地形，八个字母"),
    ("ocean", "海洋", "大片水域，五个字母"),
    ("starlight", "星光", "夜空的光，九个字母"),
    ("chocolate", "巧克力", "甜的食物，九个字母"),
    ("universe", "宇宙", "万物所在，八个字母"),
]


def main():
    print("=" * 40)
    print("        🔤 单词拼写 Spelling Bee")
    print("=" * 40)
    print("看中文，输入对应英文单词。答对+1分，答错提示首字母。q退出。")
    questions = WORDS[:]
    random.shuffle(questions)
    score = 0
    total = min(8, len(questions))

    for i in range(total):
        en, zh, hint = questions[i]
        print(f"\n[第{i+1}/{total}题] {zh}")
        ans = input("英文拼写：").strip().lower()
        if ans in ("q", "quit", "exit"):
            print(f"你退出游戏。得分 {score}/{i}。")
            return
        if ans == en:
            print(f"✅ 正确！{en}")
            score += 1
        else:
            print(f"❌ 错误。提示：以 {en[0].upper()} 开头，共{len(en)}个字母，{hint}")
            ans2 = input("再试一次：").strip().lower()
            if ans2 == en:
                print(f"✅ 这次对了！{en}")
                score += 1
            else:
                print(f"答案：{en}")
    print(f"\n🎉 游戏结束，你的得分：{score}/{total}")


if __name__ == "__main__":
    main()
