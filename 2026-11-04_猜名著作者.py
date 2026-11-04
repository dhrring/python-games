# -*- coding: utf-8 -*-
"""
猜名著作者（Guess the Author）
================================
随机给出一部世界名著的书名，猜出它的作者。
每题最多 3 次机会，答错会给出作者的国籍/朝代等线索。
共 5 题，统计正确率。纯标准库实现。
运行：python3 2026-11-04_猜名著作者.py
"""

import random

BOOKS = [
    ("红楼梦", "曹雪芹", "清代"),
    ("西游记", "吴承恩", "明代"),
    ("三国演义", "罗贯中", "明代"),
    ("水浒传", "施耐庵", "明代"),
    ("呐喊", "鲁迅", "现代中国"),
    ("骆驼祥子", "老舍", "现代中国"),
    ("边城", "沈从文", "现代中国"),
    ("围城", "钱锺书", "现代中国"),
    ("活着", "余华", "当代中国"),
    ("百年孤独", "加西亚·马尔克斯", "哥伦比亚"),
    ("战争与和平", "列夫·托尔斯泰", "俄国"),
    ("老人与海", "海明威", "美国"),
    ("巴黎圣母院", "雨果", "法国"),
    ("哈姆雷特", "莎士比亚", "英国"),
    ("堂吉诃德", "塞万提斯", "西班牙"),
]


def main():
    print("=" * 46)
    print("        📚 猜名著作者 Guess the Author")
    print("=" * 46)
    print("给出一部名著的名称，猜出它的作者。每题 3 次机会，答错给线索。")
    print("输入 'q' 提前结束。")

    books = list(BOOKS)
    random.shuffle(books)
    total = min(5, len(books))
    correct = 0
    for i in range(total):
        title, author, region = books[i]
        print(f"\n第 {i+1}/{total} 题：《{title}》的作者是谁？")
        for chance in range(1, 4):
            got = input(f"第{chance}次尝试：").strip()
            if got.lower() in ("q", "quit", "exit"):
                print("提前结束。")
                total = i
                print_summary(correct, total)
                return
            if got == author:
                correct += 1
                print("✅ 答对了！")
                break
            if chance < 3:
                hints = {1: f"线索一：作者是【{region}】人。",
                         2: f"线索二：作者的名字是 {len(author)} 个字。"}
                print(hints[chance])
            else:
                print(f"❌ 三次都没猜中，作者是：{author}")

    print_summary(correct, total)


def print_summary(correct, total):
    if total == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / total * 100
    print("\n" + "=" * 46)
    print(f"        结果：{correct}/{total}  正确率 {acc:.1f}%")
    print("=" * 46)
    if acc == 100:
        print("🏆 满分！文学大家！")
    elif acc >= 60:
        print("👍 不错，博览群书！")
    else:
        print("📖 多读名著，下次更好！")


if __name__ == "__main__":
    main()
