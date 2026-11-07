# -*- coding: utf-8 -*-
"""
古诗接龙（Poem Chain）
========================
给出古诗的上句，接出下一句。共 8 题，答错会给出出处提示。
系统会自动忽略标点与空格，只需写出诗句内容。
纯标准库实现。
运行：python3 2026-11-06_古诗接龙.py
"""

import random

# (上句, 下句, 出处)
POEMS = [
    ("床前明月光", "疑是地上霜", "李白《静夜思》"),
    ("举头望明月", "低头思故乡", "李白《静夜思》"),
    ("春眠不觉晓", "处处闻啼鸟", "孟浩然《春晓》"),
    ("夜来风雨声", "花落知多少", "孟浩然《春晓》"),
    ("白日依山尽", "黄河入海流", "王之涣《登鹳雀楼》"),
    ("欲穷千里目", "更上一层楼", "王之涣《登鹳雀楼》"),
    ("锄禾日当午", "汗滴禾下土", "李绅《悯农》"),
    ("谁知盘中餐", "粒粒皆辛苦", "李绅《悯农》"),
    ("两个黄鹂鸣翠柳", "一行白鹭上青天", "杜甫《绝句》"),
    ("窗含西岭千秋雪", "门泊东吴万里船", "杜甫《绝句》"),
    ("朝辞白帝彩云间", "千里江陵一日还", "李白《早发白帝城》"),
    ("千山鸟飞绝", "万径人踪灭", "柳宗元《江雪》"),
    ("孤舟蓑笠翁", "独钓寒江雪", "柳宗元《江雪》"),
    ("独在异乡为异客", "每逢佳节倍思亲", "王维《九月九日忆山东兄弟》"),
    ("桃花潭水深千尺", "不及汪伦送我情", "李白《赠汪伦》"),
    ("大漠孤烟直", "长河落日圆", "王维《使至塞上》"),
    ("山重水复疑无路", "柳暗花明又一村", "陆游《游山西村》"),
    ("海内存知己", "天涯若比邻", "王勃《送杜少府之任蜀州》"),
    ("会当凌绝顶", "一览众山小", "杜甫《望岳》"),
    ("野火烧不尽", "春风吹又生", "白居易《赋得古原草送别》"),
]


def normalize(text):
    """去掉标点与空格，便于比对。"""
    return "".join(c for c in text if c.strip() and c not in "，。、？！；：·“”‘’《》")


def ask(first, second, source, idx, total):
    print(f"\n第 {idx}/{total} 题：接出下一句 ——「{first}，______」")
    for chance in range(1, 3):
        got = input(f"第{chance}次：").strip()
        if got.lower() in ("q", "quit", "exit"):
            return None
        if normalize(got) == normalize(second):
            print("✅ 接对了！")
            return True
        if chance == 1:
            print(f"提示①：出自 {source}。")
        else:
            print(f"❌ 正确答案是：「{second}」（{source}）")
    return False


def main():
    print("=" * 50)
    print("         📜 古诗接龙 Poem Chain")
    print("=" * 50)
    print("给出古诗上句，请接出下一句（标点可省略）。每题 2 次机会。")
    print("输入 q 提前结束。")

    total = 8
    picked = random.sample(POEMS, total)
    correct = 0
    done = 0
    for i, (first, second, source) in enumerate(picked, 1):
        r = ask(first, second, source, i, total)
        if r is None:
            print("提前结束。")
            break
        done = i
        if r:
            correct += 1

    print("\n" + "=" * 50)
    if done == 0:
        print("        没有完成任何一题。")
    else:
        acc = correct / done * 100
        print(f"        结果：{correct}/{done}  正确率 {acc:.1f}%")
        if acc == 100:
            print("        🏆 满分！诗词小才子！")
        elif acc >= 60:
            print("        👍 不错，古诗背得挺熟！")
        else:
            print("        📖 多背几首古诗吧！")
    print("=" * 50)


if __name__ == "__main__":
    main()
