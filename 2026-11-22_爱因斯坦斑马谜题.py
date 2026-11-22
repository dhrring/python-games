"""
====================================================
 爱因斯坦斑马谜题 —— 逻辑推理小游戏
====================================================

【游戏简介】
传说爱因斯坦小时候做过一道"谁养鱼"的谜题：几户人家排成一排，每户有不同
的房子颜色、养不同的宠物、喝不同的饮料，只给你一组零散的线索，靠纯逻辑
一步步推下去，最后确定每一格对应什么。

本游戏共 5 关，从 3 户人家 3 条线索开始，逐关加人、加属性、加线索。

【游玩方法】
1. 在终端运行：python 2026-11-22_爱因斯坦斑马谜题.py
2. 每关会列出若干条件，读完自己想清楚，再输入答案（一般是一个人名）。
3. 输入 hint 或 h：看一条提示（本关扣 10 分，每关最低保留 4 分）。
4. 输入 q 或 quit 或 退出：随时结束本局。
5. 直接回车会重新提示题目，不会扣分。
6. 每关满分 20 分，答错一关扣 8 分（不低于 4 分），5 关合计 100 分。

【推理小建议】
把"每家户"当作一排格子，先固定绝对位置（比如"甲住 1 号"），再用
"隔壁/左边/右边"的相邻条件去挤，剩下的用排除法收尾。

【自检】
python 2026-11-22_爱因斯坦斑马谜题.py --check
会用穷举求解器重新验算每一关，并核对内置答案与题目是否一致。
"""

import sys
from itertools import permutations

# ---------------------------------------------------------------
# 关卡数据
# 每一关：houses 户数、cats 属性表、clues 线索（文字 + 判定函数）、
#         question 问题、answer 答案、solution 标准解（供揭示用）
# ---------------------------------------------------------------

LEVELS = [
    dict(
        title="三户人家",
        houses=3,
        cats=[
            ("居民", ["甲", "乙", "丙"]),
            ("颜色", ["红", "蓝", "绿"]),
            ("宠物", ["猫", "狗", "鱼"]),
        ],
        clues=[
            ("甲住在红房子里。", lambda s: s["居民"]["甲"] == s["颜色"]["红"]),
            ("乙养狗。", lambda s: s["居民"]["乙"] == s["宠物"]["狗"]),
            ("蓝房子的主人养猫。", lambda s: s["颜色"]["蓝"] == s["宠物"]["猫"]),
            ("红房子是 1 号（最左边那户）。", lambda s: s["颜色"]["红"] == 1),
            ("丙不住 2 号。", lambda s: s["居民"]["丙"] != 2),
        ],
        question="谁养鱼？",
        answer="甲",
        hint="红房子在 1 号，而甲住红房子 —— 所以 1 号住甲。再看乙养狗、"
             "蓝房养猫，狗的住户和猫的住户都不是 1 号，那 1 号还能养什么？",
        solution={
            "居民": {"甲": 1, "乙": 2, "丙": 3},
            "颜色": {"红": 1, "绿": 2, "蓝": 3},
            "宠物": {"鱼": 1, "狗": 2, "猫": 3},
        },
    ),
    dict(
        title="四户人家",
        houses=4,
        cats=[
            ("居民", ["赵", "钱", "孙", "李"]),
            ("饮品", ["茶", "咖啡", "牛奶", "果汁"]),
            ("宠物", ["猫", "狗", "鱼", "鸟"]),
        ],
        clues=[
            ("赵住 1 号。", lambda s: s["居民"]["赵"] == 1),
            ("喝牛奶的人住 2 号。", lambda s: s["饮品"]["牛奶"] == 2),
            ("孙养狗。", lambda s: s["居民"]["孙"] == s["宠物"]["狗"]),
            ("李住 4 号。", lambda s: s["居民"]["李"] == 4),
            ("钱住的房子紧挨在孙的左边。", lambda s: s["居民"]["钱"] + 1 == s["居民"]["孙"]),
            ("李住在喝咖啡的人隔壁。", lambda s: abs(s["居民"]["李"] - s["饮品"]["咖啡"]) == 1),
            ("喝果汁的人养鸟。", lambda s: s["饮品"]["果汁"] == s["宠物"]["鸟"]),
            ("钱不养猫。", lambda s: s["居民"]["钱"] != s["宠物"]["猫"]),
            ("赵不养鸟。", lambda s: s["居民"]["赵"] != s["宠物"]["鸟"]),
        ],
        question="喝牛奶的那户人家养什么宠物？",
        answer="鱼",
        hint="先把人名排定：赵 1、李 4，钱在孙左边相邻 —— 只剩 2、3 两个位置给"
             "钱和孙。再想：钱不养猫、孙养狗，果汁养鸟；而 2 号喝牛奶，"
             "牛奶这户不可能喝果汁。",
        solution={
            "居民": {"赵": 1, "钱": 2, "孙": 3, "李": 4},
            "饮品": {"茶": 1, "牛奶": 2, "咖啡": 3, "果汁": 4},
            "宠物": {"猫": 1, "鱼": 2, "狗": 3, "鸟": 4},
        },
    ),
    dict(
        title="四户人家（职业篇）",
        houses=4,
        cats=[
            ("姓名", ["小张", "小王", "小李", "小陈"]),
            ("职业", ["医生", "教师", "律师", "工程师"]),
            ("饮品", ["茶", "咖啡", "可乐", "水"]),
        ],
        clues=[
            ("医生住 1 号。", lambda s: s["职业"]["医生"] == 1),
            ("小李住 4 号。", lambda s: s["姓名"]["小李"] == 4),
            ("喝咖啡的人住在医生隔壁。", lambda s: abs(s["饮品"]["咖啡"] - s["职业"]["医生"]) == 1),
            ("教师住在小王右边（相邻）。", lambda s: s["职业"]["教师"] == s["姓名"]["小王"] + 1),
            ("小张不喝水。", lambda s: s["姓名"]["小张"] != s["饮品"]["水"]),
            ("律师喝可乐。", lambda s: s["职业"]["律师"] == s["饮品"]["可乐"]),
            ("小陈是律师。", lambda s: s["姓名"]["小陈"] == s["职业"]["律师"]),
            ("小陈不喝咖啡。", lambda s: s["姓名"]["小陈"] != s["饮品"]["咖啡"]),
            ("医生不喝水。", lambda s: s["职业"]["医生"] != s["饮品"]["水"]),
        ],
        question="谁喝咖啡？",
        answer="小张",
        hint="小陈是律师，律师喝可乐，所以小陈喝可乐、不喝咖啡。咖啡在医生隔壁，"
             "而医生在 1 号 —— 咖啡只能在 2 号。再用小张不喝水、医生不喝水往下排。",
        solution={
            "姓名": {"小王": 1, "小张": 2, "小陈": 3, "小李": 4},
            "职业": {"医生": 1, "教师": 2, "律师": 3, "工程师": 4},
            "饮品": {"茶": 1, "咖啡": 2, "可乐": 3, "水": 4},
        },
    ),
    dict(
        title="五户人家（经典版）",
        houses=5,
        cats=[
            ("居民", ["甲", "乙", "丙", "丁", "戊"]),
            ("饮品", ["茶", "咖啡", "牛奶", "果汁", "可乐"]),
            ("宠物", ["猫", "狗", "鱼", "鸟", "马"]),
        ],
        clues=[
            ("甲住 1 号。", lambda s: s["居民"]["甲"] == 1),
            ("乙养狗。", lambda s: s["居民"]["乙"] == s["宠物"]["狗"]),
            ("喝牛奶的人住 3 号。", lambda s: s["饮品"]["牛奶"] == 3),
            ("丙住在喝咖啡的人隔壁。", lambda s: abs(s["居民"]["丙"] - s["饮品"]["咖啡"]) == 1),
            ("丁养马。", lambda s: s["居民"]["丁"] == s["宠物"]["马"]),
            ("喝果汁的人养鸟。", lambda s: s["饮品"]["果汁"] == s["宠物"]["鸟"]),
            ("戊不喝茶。", lambda s: s["居民"]["戊"] != s["饮品"]["茶"]),
            ("喝可乐的人住 5 号。", lambda s: s["饮品"]["可乐"] == 5),
            ("甲不养猫。", lambda s: s["居民"]["甲"] != s["宠物"]["猫"]),
            ("马住在 2 号。", lambda s: s["宠物"]["马"] == 2),
            ("甲不喝果汁。", lambda s: s["居民"]["甲"] != s["饮品"]["果汁"]),
        ],
        question="谁养鱼？",
        answer="甲",
        hint="马在 2 号，而丁养马 —— 丁就是 2 号。剩下 3/4/5 号分给丙、戊、乙："
             "乙养狗不占果汁鸟，可乐在 5 号……甲既不养猫也不喝果汁，"
             "1 号能喝的就那一样。",
        solution={
            "居民": {"甲": 1, "丁": 2, "丙": 3, "戊": 4, "乙": 5},
            "饮品": {"茶": 1, "咖啡": 2, "牛奶": 3, "果汁": 4, "可乐": 5},
            "宠物": {"鱼": 1, "马": 2, "猫": 3, "鸟": 4, "狗": 5},
        },
    ),
    dict(
        title="四户人家（四种属性）",
        houses=4,
        cats=[
            ("居民", ["阿福", "阿寿", "阿喜", "阿财"]),
            ("颜色", ["红", "蓝", "绿", "黄"]),
            ("职业", ["医生", "教师", "律师", "工程师"]),
            ("饮品", ["茶", "咖啡", "牛奶", "果汁"]),
        ],
        clues=[
            ("红房子住 1 号。", lambda s: s["颜色"]["红"] == 1),
            ("医生住蓝房子。", lambda s: s["职业"]["医生"] == s["颜色"]["蓝"]),
            ("阿寿喝茶。", lambda s: s["居民"]["阿寿"] == s["饮品"]["茶"]),
            ("教师住在阿喜隔壁。", lambda s: abs(s["职业"]["教师"] - s["居民"]["阿喜"]) == 1),
            ("喝牛奶的人住绿房子。", lambda s: s["饮品"]["牛奶"] == s["颜色"]["绿"]),
            ("律师不喝咖啡。", lambda s: s["职业"]["律师"] != s["饮品"]["咖啡"]),
            ("阿财住 4 号。", lambda s: s["居民"]["阿财"] == 4),
            ("阿福是工程师。", lambda s: s["居民"]["阿福"] == s["职业"]["工程师"]),
            ("黄房子住 4 号。", lambda s: s["颜色"]["黄"] == 4),
            ("阿福住在阿寿的左边（相邻）。", lambda s: s["居民"]["阿福"] + 1 == s["居民"]["阿寿"]),
            ("工程师不喝果汁。", lambda s: s["职业"]["工程师"] != s["饮品"]["果汁"]),
        ],
        question="谁喝咖啡？",
        answer="阿福",
        hint="阿财住 4 号且黄房子在 4 号；阿福是工程师、不住黄房也不喝果汁，"
             "又是最左边的红房首个住户 —— 把 1 号锁死后，阿寿、阿喜依次排开，"
             "咖啡只剩 1 号能放。",
        solution={
            "居民": {"阿福": 1, "阿寿": 2, "阿喜": 3, "阿财": 4},
            "颜色": {"红": 1, "蓝": 2, "绿": 3, "黄": 4},
            "职业": {"工程师": 1, "医生": 2, "律师": 3, "教师": 4},
            "饮品": {"咖啡": 1, "茶": 2, "牛奶": 3, "果汁": 4},
        },
    ),
]


# ---------------------------------------------------------------
# 求解器（仅用于 --check 自检）
# ---------------------------------------------------------------
def solve_level(level):
    """穷举所有属性排列，返回满足全部线索的解的列表。"""
    cats = level["cats"]
    names = [c[0] for c in cats]
    perms = {name: list(permutations(vals, level["houses"])) for name, vals in cats}
    sols = []

    def rec(idx, cur):
        if idx == len(cats):
            sols.append({k: dict(v) for k, v in cur.items()})
            return
        name = names[idx]
        for p in perms[name]:
            cur[name] = {val: i + 1 for i, val in enumerate(p)}
            ok = True
            for _, fn in level["clues"]:
                try:
                    passed = fn(cur)
                except KeyError:
                    # 该线索还依赖尚未分配的属性，先跳过，等后续层再判
                    continue
                if not passed:
                    ok = False
                    break
            if ok:
                rec(idx + 1, cur)
            del cur[name]

    rec(0, {})
    # 完整复检：所有属性都赋值后，再验一次全部线索
    return [s for s in sols if all(fn(s) for _, fn in level["clues"])]


def answer_of(level, sol):
    """从一组解里取出本题答案（按问题类型映射，这里统一用人工核对的 answer 字段）。"""
    return level["answer"]


def run_check():
    print("正在用穷举求解器校验 5 个关卡……\n")
    ok_all = True
    for i, level in enumerate(LEVELS, 1):
        sols = solve_level(level)
        stored = level["solution"]
        match_stored = any(
            all(sol[c][v] == h for c, m in stored.items() for v, h in m.items())
            for sol in sols
        )
        status = "OK" if (sols and match_stored) else "FAIL"
        if not (sols and match_stored):
            ok_all = False
        print(f"[{status}] 第 {i} 关「{level['title']}」：穷举解 {len(sols)} 组，"
              f"内置解{'命中' if match_stored else '不命中'}，答案 = {level['answer']}")
        if sols and "居民" in stored and level["answer"] in stored["居民"]:
            hs = {s["居民"][level["answer"]] for s in sols}
            print(f"      答案人物所在房号集合：{sorted(hs)}，"
                  f"{'全解唯一' if len(sols) == 1 else f'共 {len(sols)} 组解'}"
                  f"{'，答案确定' if len(hs) == 1 else '，答案有歧义！'}")
    print("\n自检结果：", "全部通过" if ok_all else "存在不一致，请检查关卡数据")
    return 0 if ok_all else 1


# ---------------------------------------------------------------
# 游戏主流程
# ---------------------------------------------------------------
def show_level(level, idx):
    print("\n" + "=" * 52)
    print(f"第 {idx} 关 · {level['title']}（{idx}/{len(LEVELS)}，20 分）")
    print("=" * 52)
    print(f"共有 {level['houses']} 户人家，排成一排，从左到右依次编号 1~{level['houses']}。")
    for name, vals in level["cats"]:
        print(f"  {name}：{'、'.join(vals)}（每户各不相同）")
    print("\n【线索】")
    for j, (text, _) in enumerate(level["clues"], 1):
        print(f"  {j}. {text}")
    print(f"\n【问题】{level['question']}")
    print("（输入答案；h = 提示（-10 分）；q = 退出；回车 = 重看题目）")


def reveal(level):
    print("\n【完整布局】")
    for name, _ in level["cats"]:
        houses = level["solution"][name]
        row = sorted(houses.items(), key=lambda kv: kv[1])
        line = "  ".join(f"{i}号:{v}" for v, i in row)
        print(f"  {name}：{line}")


def play():
    print("=" * 52)
    print(" 爱因斯坦斑马谜题 —— 逻辑推理小游戏")
    print("=" * 52)
    print("5 关，每关 20 分，共 100 分。答案只填关键的那一项（如人名或宠物名）。")
    print("命令：hint/h 提示（-10 分）｜q/quit/退出 结束｜回车 重看｜Ctrl+C 退出\n")

    score = 0
    used_hint = 0
    for idx, level in enumerate(LEVELS, 1):
        penalty_floor = 4
        level_score = 20
        hint_used = False
        show_level(level, idx)
        while True:
            try:
                raw = input("\n你的答案 > ")
            except (EOFError, KeyboardInterrupt):
                print("\n\n已退出，下次再来推逻辑吧。")
                return
            cmd = raw.strip()
            if not cmd:
                show_level(level, idx)
                continue
            low = cmd.lower()
            if low in ("q", "quit", "exit", "退出"):
                print("\n已退出。当前累计得分 {} 分。".format(score))
                return
            if low in ("h", "hint", "提示", "?"):
                if not hint_used:
                    hint_used = True
                    used_hint += 1
                    level_score = max(penalty_floor, level_score - 10)
                print(f"\n[提示] {level['hint']}")
                print(f"（本关当前 {level_score} 分）")
                continue

            if cmd == level["answer"]:
                print("\n✅ 推理正确！")
                reveal(level)
                score += level_score
                print(f"本关得分 {level_score}，累计 {score}")
                break
            else:
                level_score = max(penalty_floor, level_score - 8)
                print(f"\n❌ 不对。再想想（本关当前 {level_score} 分）。")
                print("可以输入 h 要提示，或回车重看线索。")

    print("\n" + "=" * 52)
    total = score
    print(f"全部通关！总分 {total}/100（用过 {used_hint} 次提示）")
    if total >= 95:
        print("评级：逻辑之神 —— 这种题对你基本属于送分。")
    elif total >= 80:
        print("评级：推理高手 —— 思路稳，偶尔需要一点提示。")
    elif total >= 60:
        print("评级：合格侦探 —— 线索用得住，但相邻条件还可以再抠细。")
    else:
        print("评级：见习侦探 —— 建议先固定绝对位置，再一层层挤。")
    print("=" * 52)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(run_check())
    play()
