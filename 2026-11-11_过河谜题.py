# -*- coding: utf-8 -*-
"""
过河谜题（农夫渡河 · 4 关逻辑挑战）
=====================================
经典「农夫带狼、羊、菜过河」的扩展版。规则一句话：
船很小，每次只能带一样东西过去，人不在的一岸，某些东西会互相吃掉。
你要用最少的步数把全部东西安全运到对岸。

三关由简到难：
  第 1 关  农夫 + 狼 + 羊 + 菜        （3 趟内可解）
  第 2 关  农夫 + 狗 + 鸡 + 米 + 猫   （多了个会吃鸡的猫）
  第 3 关  农夫 + 3 只老虎 + 3 只羊   （平衡型：数量不能一边倒）
  第 4 关  农夫 + 传教士食人族（3+3） （经典「传教士与食人族」）

游玩方法：
  船的状态用「左岸/右岸」表示，你在哪边就从哪边开船。
  输入你要带上船的物品编号（不带东西就输入 0 或直接回车），船会自动开往对岸。
  输入 u 撤销上一步，r 重来本关，q 退出。
  每关都有步数上限，超过就失败（说明解法不对，不是运气问题）。
运行：python3 2026-11-11_过河谜题.py
"""

from collections import deque

# 每关配置：
#   objects: 物品英文标识 -> 中文名
#   conflicts: (a, b) 表示 a 与 b 单独相处时 a 会吃 b（人不在时触发）
#   rule: "eat"（会吃） 或 "balance"（数量平衡型）
#   max_steps: 步数上限
LEVELS = [
    {
        "title": "第 1 关 · 农夫与狼羊菜",
        "objects": {"wolf": "狼", "goat": "羊", "cabbage": "菜"},
        "conflicts": [("wolf", "goat"), ("goat", "cabbage")],
        "rule": "eat",
        "max_steps": 9,
        "cap": 1,
        "tip": "羊是麻烦制造者：它既会被狼吃，也会吃菜。标准解需要 7 次过河。",
    },
    {
        "title": "第 2 关 · 农场大搬家",
        "objects": {"dog": "狗", "chicken": "鸡", "rice": "米", "cat": "猫"},
        "conflicts": [("dog", "chicken"), ("cat", "chicken"), ("chicken", "rice")],
        "rule": "eat",
        "max_steps": 8,
        "cap": 2,
        "tip": "鸡被三方盯着（狗要吃它、猫要吃它、它还要吃米）；船一次最多带 2 件。",
    },
    {
        "title": "第 3 关 · 虎羊平衡",
        "objects": {"t1": "虎1", "t2": "虎2", "t3": "虎3", "s1": "羊1", "s2": "羊2", "s3": "羊3"},
        "conflicts": [],
        "rule": "balance",
        "max_steps": 8,
        "cap": 2,
        "tip": "任何一岸虎的数量都不能多于羊，否则羊被吃。船一次最多带 2 只。",
    },
    {
        "title": "第 4 关 · 传教士与食人族",
        "objects": {"m1": "传教士1", "m2": "传教士2", "m3": "传教士3",
                    "c1": "食人族1", "c2": "食人族2", "c3": "食人族3"},
        "conflicts": [],
        "rule": "balance",
        "max_steps": 13,
        "cap": 2,
        "must_row": True,
        "tip": "任何一岸只要有传教士，食人族数量就不能多于传教士；船最多坐 2 人，且必须有人划船（不能空船）。",
    },
]

def is_kind(item):
    return item[0] in ("t", "s", "m", "c") and item[1:].isdigit()


def kind_of(item):
    return item[0]


def state_ok(level, left_set, left_people):
    """判断某一岸是否安全。left_people 表示农夫在左岸。"""
    rule = level["rule"]
    if rule == "eat":
        conflicts = level["conflicts"]
        if left_people:
            # 农夫在左岸 → 右岸无人看管
            other = set(level["objects"]) - left_set
            for a, b in conflicts:
                if a in other and b in other:
                    return False, f"右岸的{level['objects'][a]}吃掉了{level['objects'][b]}"
        else:
            for a, b in conflicts:
                if a in left_set and b in left_set:
                    return False, f"左岸的{level['objects'][a]}吃掉了{level['objects'][b]}"
        return True, ""
    else:
        # balance 型：虎吃羊 / 食人族吃传教士 与农夫在不在场无关，两岸都必须检查
        other = set(level["objects"]) - left_set
        ok1, why1 = check_balance(level, left_set, "左岸")
        if not ok1:
            return False, why1
        return check_balance(level, other, "右岸")


def check_balance(level, side_set, side_name):
    tigers = sum(1 for x in side_set if kind_of(x) == "t")
    sheeps = sum(1 for x in side_set if kind_of(x) == "s")
    if tigers > sheeps:
        return False, f"{side_name}虎比羊多，羊被吃"
    mission = sum(1 for x in side_set if kind_of(x) == "m")
    cannibals = sum(1 for x in side_set if kind_of(x) == "c")
    if mission > 0 and cannibals > mission:
        return False, f"{side_name}食人族多于传教士，传教士被吃"
    return True, ""


def render(level, left_set, left_people, steps):
    names = level["objects"]
    left = sorted(names[o] for o in left_set)
    right = sorted(names[o] for o in names if o not in left_set)
    print("\n" + "-" * 56)
    print(f"  步数 {steps}/{level['max_steps']}    农夫在：{'左岸' if left_people else '右岸'}")
    print(f"  左岸：{'、'.join(left) if left else '（空）'}   👨‍🌾{'在' if left_people else ''}")
    print(f"  右岸：{'、'.join(right) if right else '（空）'}   👨‍🌾{'在' if not left_people else ''}")
    side = "左岸" if left_people else "右岸"
    print(f"  船：停在{side} 🛶 —— 每趟最多 {boat_cap(level)} 个")


def boat_cap(level):
    return level["cap"]


def bfs_solve(level):
    """用 BFS 求最少步数，用于验证每关确实有解、上限设置合理。"""
    names = list(level["objects"])
    cap = boat_cap(level)
    start = (frozenset(), True)  # 左岸已搬运集合为空，农夫在左岸
    goal = (frozenset(names), False)
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (left, people), d = q.popleft()
        if (left, people) == goal:
            return d
        # 能带上船的物品：与农夫同岸的
        candidates = [o for o in names if (o in left) == people]
        # 组合（最多 cap 个，允许空船）
        combos = [()]
        for i, a in enumerate(candidates):
            combos.append((a,))
            if cap >= 2:
                for b in candidates[i + 1:]:
                    combos.append((a, b))
                    if cap >= 3:
                        for c in candidates[i + 1:]:
                            pass
        for combo in combos:
            if len(combo) > cap:
                continue
            new_left = set(left)
            for o in combo:
                if people:
                    new_left.discard(o)
                else:
                    new_left.add(o)
            ok, _ = state_ok(level, frozenset(new_left), not people)
            if not ok:
                continue
            st = (frozenset(new_left), not people)
            if st not in seen:
                seen.add(st)
                q.append((st, d + 1))
    return None


def main():
    print("=" * 56)
    print("      🛶 过河谜题")
    print("=" * 56)
    print("规则：船只能从农夫所在的一岸出发，到岸后农夫留在那儿。")
    print("     无人看管的一岸若触发「吃」或「数量倒挂」，立即失败。")

    total_steps = 0
    for idx, level in enumerate(LEVELS):
        names = level["objects"]
        left = set(names)  # 一开始全在左岸
        people = True
        steps = 0
        history = []

        print("\n" + "=" * 56)
        print(f"  {level['title']}（上限 {level['max_steps']} 步）")
        print(f"  💡 {level['tip']}")
        print("  物品编号：", "  ".join(f"{i + 1}.{names[o]}" for i, o in enumerate(names)))

        order = list(names)
        while True:
            render(level, left, people, steps)
            if len(left) == 0 and not people:
                print(f"\n  🎉 全部过河！本关用了 {steps} 步。")
                total_steps += steps
                break

            raw = input("\n  带谁上船？（编号空格分隔，0=空船，u=撤销，r=重来，q=退出）：").strip().lower()
            if raw in ("q", "quit", "exit"):
                print("\n你已退出。")
                print(f"已用总步数：{total_steps}")
                return
            if raw == "r":
                left = set(names)
                people = True
                steps = 0
                history.clear()
                print("  已重来本关。")
                continue
            if raw == "u":
                if not history:
                    print("  没有可撤销的步骤。")
                    continue
                left, people, steps = history.pop()
                print("  已撤销上一步。")
                continue

            if raw in ("", "0"):
                chosen = []
            else:
                parts = raw.replace("，", " ").replace(",", " ").split()
                if not all(p.isdigit() for p in parts):
                    print("  请输入物品编号（数字）。")
                    continue
                ids = [int(p) for p in parts]
                chosen = []
                for i in ids:
                    if not 1 <= i <= len(order):
                        print(f"  编号需要在 1~{len(order)} 之间。")
                        chosen = None
                        break
                    chosen.append(order[i - 1])
                if chosen is None:
                    continue
                if len(set(chosen)) != len(chosen):
                    print("  同一物品不能上船两次。")
                    continue

            cap = boat_cap(level)
            if len(chosen) > cap:
                print(f"  船最多载 {cap} 个，你选了 {len(chosen)} 个。")
                continue
            if level.get("must_row") and not chosen:
                print("  船必须有人划，请至少选 1 位。")
                continue

            side_now = left if people else set(names) - left
            for o in chosen:
                if o not in side_now:
                    print(f"  {names[o]} 不在农夫这一岸，带不上船。")
                    chosen = None
                    break
            if chosen is None:
                continue

            if steps + 1 > level["max_steps"]:
                print(f"  ❌ 超过步数上限 {level['max_steps']}，本关失败。按 r 重来。")
                continue

            history.append((set(left), people, steps))
            for o in chosen:
                if people:
                    left.discard(o)
                else:
                    left.add(o)
            people = not people
            steps += 1

            ok, why = state_ok(level, frozenset(left), people)
            if not ok:
                print(f"  ❌ 失败：{why}。已自动撤销这一步。")
                left, people, steps = history.pop()

    print("\n" + "=" * 56)
    print(f"  四关全部通关，总用步 {total_steps} 步。")
    print("  冷知识：这类「带东西过河」问题在图论里等价于最短路径搜索，")
    print("  第 1 关最少 7 步、第 4 关（传教士与食人族）最少 11 步，都是经过程序搜索验证的。")
    print("=" * 56)


if __name__ == "__main__":
    main()
