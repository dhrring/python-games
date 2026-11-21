"""
====================================================
 光纤布线 —— 最小生成树小游戏
====================================================

【中文说明】
你是县里的通信工程师：要把 N 个城镇用光缆连成一网，任意两镇之间都能通信，
但总预算越省越好。这就是「最小生成树」（MST）问题：
  用 N−1 条边把所有点连通、且不成环，让总造价最小。

贪心即可拿到最优解——克鲁斯卡尔（Kruskal）算法：
  1. 把所有候选光缆按造价从小到大排队；
  2. 依次考虑每一条：若它的两端还不连通（不成环），就铺；否则跳过；
  3. 选满 N−1 条时收工，此时总价一定最小。
（另一种做法是普里姆 Prim：从一个镇出发，每次接上离已连区域最近的那个镇。）

【游玩方法】
  · 直接运行：python 2026-11-21_光纤布线.py
  · 共 5 关，每关 20 分，满分 100。
  · 屏幕上给出城镇与候选光缆（两端 : 造价，单位万元），输入「最小总造价」这个整数。
  · 命令：hint 看算法提示（−10 分）｜ q 退出
  · 答错一次 −8 分，每关保底 4 分。

【知识点】
  图论、生成树、贪心算法（Kruskal / Prim）、并查集、环与连通分量。
====================================================
"""

PER_LEVEL = 20
WRONG_COST = 8
HINT_COST = 10
FLOOR = 4

LEVELS = [
    {
        "title": "第一关：五镇小网",
        "cities": ["开封", "郑州", "洛阳", "新乡", "焦作"],
        "edges": [
            ("开封", "郑州", 60), ("开封", "洛阳", 140), ("郑州", "洛阳", 70),
            ("郑州", "新乡", 40), ("洛阳", "新乡", 110), ("洛阳", "焦作", 90),
            ("新乡", "焦作", 30),
        ],
    },
    {
        "title": "第二关：多了一条便宜的岔路",
        "cities": ["开封", "郑州", "洛阳", "新乡", "焦作", "商丘"],
        "edges": [
            ("开封", "商丘", 85), ("郑州", "开封", 50), ("开封", "洛阳", 95),
            ("郑州", "新乡", 45), ("郑州", "洛阳", 120), ("洛阳", "新乡", 65),
            ("新乡", "焦作", 35), ("洛阳", "焦作", 150),
        ],
    },
    {
        "title": "第三关：一串短线路",
        "cities": ["开封", "郑州", "洛阳", "新乡", "商丘", "焦作"],
        "edges": [
            ("开封", "郑州", 10), ("洛阳", "新乡", 10), ("郑州", "洛阳", 20),
            ("开封", "新乡", 25), ("商丘", "焦作", 10), ("郑州", "商丘", 15),
        ],
    },
    {
        "title": "第四关：七镇大网",
        "cities": ["开封", "郑州", "洛阳", "新乡", "焦作", "商丘", "许昌"],
        "edges": [
            ("开封", "许昌", 130), ("郑州", "开封", 55), ("郑州", "洛阳", 80),
            ("郑州", "许昌", 45), ("洛阳", "新乡", 60), ("新乡", "焦作", 25),
            ("新乡", "许昌", 95), ("洛阳", "许昌", 110), ("焦作", "商丘", 70),
            ("许昌", "商丘", 50), ("商丘", "新乡", 100),
        ],
    },
    {
        "title": "第五关：最便宜的三角形是个陷阱",
        "cities": ["开封", "郑州", "洛阳", "新乡", "焦作", "商丘", "许昌"],
        "multi": True,
        "edges": [
            ("开封", "郑州", 30), ("郑州", "洛阳", 30), ("洛阳", "开封", 25),
            ("新乡", "焦作", 20), ("商丘", "许昌", 22), ("郑州", "新乡", 60),
            ("洛阳", "新乡", 55), ("开封", "商丘", 90), ("焦作", "商丘", 40),
            ("许昌", "开封", 85), ("洛阳", "商丘", 70), ("新乡", "许昌", 75),
        ],
    },
]


class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.parent[ra] = rb
        return True


def kruskal(cities, edges):
    """返回 (选中边列表, 总造价)。"""
    uf = UnionFind(cities)
    chosen = []
    total = 0
    for a, b, w in sorted(edges, key=lambda e: e[2]):
        if uf.union(a, b):
            chosen.append((a, b, w))
            total += w
            if len(chosen) == len(cities) - 1:
                break
    return chosen, total


def connected(cities, edges):
    uf = UnionFind(cities)
    for a, b, _ in edges:
        uf.union(a, b)
    return len({uf.find(c) for c in cities}) == 1


def mst_total(cities, edges):
    return kruskal(cities, edges)[1]


for _lv in LEVELS:
    _lv["answer"] = mst_total(_lv["cities"], _lv["edges"])


def show_level(idx, level):
    print()
    print("─" * 48)
    print(f"【{level['title']}】  第 {idx + 1}/{len(LEVELS)} 关")
    print(f"城镇（{len(level['cities'])} 个）：" + "、".join(level["cities"]))
    print("候选光缆（两端 : 造价 万元）：")
    for a, b, w in level["edges"]:
        print(f"    {a} — {b} : {w}")
    print(f"问：把这 {len(level['cities'])} 个城镇连成一片，最少要花多少万元？"
          f"（需要 {len(level['cities']) - 1} 条线，填总价整数）")


def show_hint(level):
    print("  💡 提示（Kruskal）：")
    print("     把上面所有线路按造价排序，从小往大挑；")
    print("     每挑一条都检查：两端会不会已经在同一个连通块里？")
    print("     会 → 这条是环，跳过；不会 → 选它。选够 N−1 条就停。")
    cheapest = sorted(level["edges"], key=lambda e: e[2])[:4]
    print("     最便宜的四条是：" + "，".join(f"{a}-{b}({w})" for a, b, w in cheapest)
          + "。其中可能有环边，留意。")


def play():
    print(__doc__.split("【中文说明】")[0].strip())
    print("每关输入一个整数总价；hint 看提示，q 退出。")
    total_score = 0
    for idx, level in enumerate(LEVELS):
        show_level(idx, level)
        penalty = 0
        hinted = False
        while True:
            try:
                cmd = input("  最小总造价 > ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  已退出。")
                return
            if not cmd:
                continue
            low = cmd.lower()
            if low in ("q", "quit", "exit", "退出"):
                print("  已退出。")
                return
            if low in ("hint", "h", "提示", "?"):
                if hinted:
                    print("  本关提示已经用过啦。")
                else:
                    show_hint(level)
                    hinted = True
                    penalty += HINT_COST
                continue
            if not cmd.isdigit():
                print("  请输入整数（万元），或 hint / q。")
                continue
            ans = int(cmd)
            if ans == level["answer"]:
                score = max(FLOOR, PER_LEVEL - penalty)
                total_score += score
                chosen, tot = kruskal(level["cities"], level["edges"])
                print(f"  ✅ 正确！最小总造价 {tot} 万元，本关得 {score} 分。")
                print("     一组最优方案：" +
                      "，".join(f"{a}-{b}({w})" for a, b, w in chosen) + f" = {tot}")
                if level.get("multi"):
                    print("     注意：本关的最优方案不止一组，总价相同、选边不同都算对。")
                break
            penalty += WRONG_COST
            print(f"  ❌ 不是 {ans}。想想是否漏掉了更便宜的跨区线路，或者多选了一条成环的贵线。")

    print()
    print("═" * 48)
    print(f"结算：{len(LEVELS)}/{len(LEVELS)} 关完成，总分 {min(100, total_score)}/100")
    if total_score >= 90:
        print("评级：布线总工 —— 你已经会「贪心 + 避环」了。")
    elif total_score >= 60:
        print("评级：施工队长 —— 再练练就能一眼看出环边。")
    else:
        print("评级：学徒 —— 记住：N 个点只需 N−1 条边，多一条必成环。")
    print("═" * 48)


if __name__ == "__main__":
    play()
