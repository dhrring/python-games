# -*- coding: utf-8 -*-
"""
猜谜语（Riddle Quiz）
======================
随机出一道经典中文谜语，你有 3 次作答机会，答错会逐步给出线索。
最后统计正确率。纯标准库实现。
运行：python3 2026-11-03_猜谜语.py
"""

import random

RIDDLES = [
    ("身披花衣裳，爱在树上唱，夏天来到叫喳喳，冬天不知去哪藏。", "蝉"),
    ("小黑人儿细又长，穿着木头花衣裳。画画写字它全会，就是不会把歌唱。", "铅笔"),
    ("有面没有口，有脚没有手，虽有四只脚，自己不会走。", "桌子"),
    ("五个兄弟，住在一起，名字不同，高矮不齐。", "手指"),
    ("上边毛，下边毛，中间一颗黑葡萄。", "眼睛"),
    ("身穿绿衣裳，肚里水汪汪，生的子儿多，个个黑脸膛。", "西瓜"),
    ("弟兄七八个，围着柱子坐，只要一分开，衣服就扯破。", "蒜"),
    ("白天睡大觉，晚上才出动，提着一盏灯，捉虫本领高。", "萤火虫"),
    ("一根柱子好些梁，没有门窗没有墙，好像一座小亭子，用它挡雨遮太阳。", "伞"),
    ("千条线，万条线，落到水里看不见。", "雨"),
    ("麻屋子，红帐子，里面住个白胖子。", "花生"),
    ("一物生来真奇怪，身穿百件衣，每天脱一件，脱完就剩皮。", "日历"),
    ("圆头圆脑小东西，没骨没肉只有皮，一打跳得三尺高，肚里憋着一包气。", "皮球"),
    ("兄弟三人排队走，个子一个比一个高，每天挨个来上班，谁先谁后都知晓。", "台阶"),
    ("有城不能进，有箭不能射，有马不能骑，有路不能走。", "棋盘"),
    ("小小姑娘黑又黑，秋天走了春天回，带着一把小剪刀，半天空里飞呀飞。", "燕子"),
]


def main():
    print("=" * 44)
    print("        🧩 猜谜语 Riddle Quiz")
    print("=" * 44)
    print("出一道谜语，输入你的答案。每题 3 次机会，答错给线索。")
    print("输入 'q' 提前结束。")
    n = int(input("想做几题？(默认5)：").strip() or "5")
    n = max(1, min(16, n))

    riddles = list(RIDDLES)
    random.shuffle(riddles)
    correct = 0
    for i in range(n):
        riddle, answer = riddles[i]
        print(f"\n第 {i+1}/{n} 题：{riddle}")
        for chance in range(1, 4):
            got = input(f"第{chance}次尝试：").strip()
            if got.lower() in ("q", "quit", "exit"):
                print("提前结束。")
                n = i
                print_summary(correct, n)
                return
            if got == answer:
                correct += 1
                print("✅ 答对了！")
                break
            if chance < 3:
                hints = {1: f"提示：谜底是 {len(answer)} 个字。",
                         2: f"再提示：谜底以「{answer[0]}」开头。"}
                print(hints[chance])
            else:
                print(f"❌ 三次都没猜中，谜底是：{answer}")

    print_summary(correct, n)


def print_summary(correct, n):
    if n == 0:
        print("\n没有完成任何一题。")
        return
    acc = correct / n * 100
    print("\n" + "=" * 44)
    print(f"        结果：{correct}/{n}  正确率 {acc:.1f}%")
    print("=" * 44)
    if acc == 100:
        print("🧠 谜语大师，全部猜中！")
    elif acc >= 60:
        print("👍 不错，继续加油！")
    else:
        print("💡 多积累，下次更准！")


if __name__ == "__main__":
    main()
