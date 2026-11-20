# -*- coding: utf-8 -*-
"""
囚徒困境锦标赛 · Prisoner's Dilemma
====================================================
警察抓到两个同伙，分开审讯。两人的处境完全一样：

              他沉默（合作）        他招供（背叛）
你沉默         各判 1 年              你 10 年，他放走
你招供         你放走，他 10 年      各判 3 年

      （本游戏为了好算，把分数换成：合作-合作 3 分、我背叛他合作 5 分、
        他背叛我合作 0 分、互相背叛 1 分。）

看出来了吗？**不管对方怎么做，招供都不比沉默差**：对方沉默时多拿 2 分，对方招供时多拿 1 分。
可如果两个人都"理性"地招供，每轮只拿 1 分；而一直沉默，每轮各拿 3 分。
这就是囚徒困境：个体的最优，集体的灾难。

你要连续和 3 位对手各打 10 轮，每轮同时出招：
  c  合作（沉默）
  d  背叛（招供）
  hint  场外提示（知道对手什么路数，−20 分）
  q  退出

第 3 位对手策略未知，靠你自己在回合中摸清它。
三关满分各 100，按「你的得分 ÷ 该策略下理论最高分」折算。

运行：python3 2026-11-20_囚徒困境锦标赛.py
"""

import itertools

# (我的动作, 对手动作) -> (我得的分, 对手得的分)
PAYOFF = {
    ("C", "C"): (3, 3),
    ("C", "D"): (0, 5),
    ("D", "C"): (5, 0),
    ("D", "D"): (1, 1),
}
NAMES = {"C": "合作", "D": "背叛"}
ROUNDS = 10


# 每种对手：策略函数收「我此前出过的所有招」，返回它这一轮出什么。
OPPONENTS = [
    {
        "label": "对手 A · 老实人",
        "desc": "他相信人性，从来不知道「背叛」这个词怎么写。",
        "policy": lambda my: "C",
        "known": True,
        "hint": "他一直出合作，你每轮背叛都能拿 5 分，10 轮 50 分——这就是本关的天花板。",
    },
    {
        "label": "对手 B · 恶棍",
        "desc": "他认定每个人都会招供，所以抢先招供。",
        "policy": lambda my: "D",
        "known": True,
        "hint": "他永远背叛。你出合作得 0，出背叛得 1——这局天花板只有 10 分。",
    },
    {
        "label": "对手 C · 未知策略",
        "desc": "坐在你对面的人一言不发，看不出路数。",
        "policy": lambda my: "C" if not my else my[-1],
        "known": False,
        "hint": "这是一位「以牙还牙」的对手：第一轮合作，之后照抄你上一轮的动作。"
                "它抄不到你的未来，所以最后一轮的事情它管不着。",
    },
]


def simulate(policy, seq):
    """按我的出招序列跑完 10 轮，返回 (我的总分, 对手总分)。"""
    mine = 0
    theirs = 0
    history = []
    for act in seq:
        move = policy(history)
        a, b = PAYOFF[(act, move)]
        mine += a
        theirs += b
        history.append(act)
    return mine, theirs


def best_score(policy):
    """穷举 2^10 种出招序列，求该对手下的理论最高分。"""
    best = 0
    best_seq = None
    for seq in itertools.product("CD", repeat=ROUNDS):
        pts, _ = simulate(policy, seq)
        if pts > best:
            best, best_seq = pts, seq
    return best, best_seq


def parse_act(raw):
    low = raw.strip().lower()
    if low in ("c", "d"):
        return low.upper()
    if low in ("合作", "沉默", "合"):
        return "C"
    if low in ("背叛", "招供", "背"):
        return "D"
    raise ValueError("请输入 c（合作）或 d（背叛）")


def run_level(idx, opp):
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(OPPONENTS)} 关　{opp['label']}")
    print("=" * 62)
    print("  " + opp["desc"])
    print(f"  {ROUNDS} 轮，每轮你先出招，对手随后出招，然后结算。")

    best, best_seq = best_score(opp["policy"])
    penalty = 0
    my_pts = 0
    opp_pts = 0
    history = []

    for r in range(1, ROUNDS + 1):
        while True:
            try:
                raw = input(f"\n  第 {r}/{ROUNDS} 轮 · 你出（c 合作 / d 背叛 / hint / q）> ").strip()
            except EOFError:
                print("\n输入中断，提前结束。")
                return 0, None
            if not raw:
                continue
            low = raw.lower()
            if low in ("q", "quit"):
                return 0, None
            if low == "hint":
                penalty = 20
                print("  提示：" + opp["hint"])
                continue
            try:
                act = parse_act(raw)
                break
            except ValueError as msg:
                print(f"  {msg}")

        move = opp["policy"](history)
        a, b = PAYOFF[(act, move)]
        my_pts += a
        opp_pts += b
        history.append(act)
        print(f"  你{NAMES[act]}　对手{NAMES[move]}　→　本轮你得 {a} 分、他得 {b} 分"
              f"　｜　累计 {my_pts} : {opp_pts}")

    if penalty:
        print(f"  （用过提示，本关按 {max(0, 100 - penalty)} 分封顶）")
    raw_score = my_pts / best * 100 if best else 0
    score = round(min(raw_score, 100 - penalty))
    score = max(0, score)

    print(f"\n  本关你拿到 {my_pts} 分（对手 {opp_pts} 分）。")
    print(f"  这个对手的理论最高分是 {best} 分，你的达成率 {raw_score:.0f}%　→　本关 {score} 分。")
    if best == 10:
        print("  （他从不合作，所以你的天花板本来就只有 10 分——这局你应该是满分附近。）")
    return score, True


def play():
    print("=" * 62)
    print("      🤝 囚徒困境锦标赛")
    print("=" * 62)
    print("每轮同时出招：合作（沉默）或 背叛（招供）。")
    print("  (合作, 合作) → 各 3    (背叛, 合作) → 我 5 他 0")
    print("  (合作, 背叛) → 我 0 他 5   (背叛, 背叛) → 各 1")

    # 开局自检
    assert PAYOFF[("C", "C")] == (3, 3) and PAYOFF[("D", "C")] == (5, 0)
    assert PAYOFF[("C", "D")] == (0, 5) and PAYOFF[("D", "D")] == (1, 1)
    # 经典囚徒困境的收益序：诱惑 T=5 > 奖励 R=3 > 惩罚 P=1 > 吃亏 S=0
    T, R = PAYOFF[("D", "C")][0], PAYOFF[("C", "C")][0]
    P, S = PAYOFF[("D", "D")][0], PAYOFF[("C", "D")][0]
    assert T > R > P > S, f"收益序不对：T={T},R={R},P={P},S={S}"
    # 背叛在单轮上永远不吃亏：这正是困境的来源
    for mv in ("C", "D"):
        assert PAYOFF[("D", mv)][0] > PAYOFF[("C", mv)][0], f"单轮激励不成立：{mv}"
    # 三位对手的理论最高分必须符合预期
    expect_best = [50, 10, 32]
    for opp, eb in zip(OPPONENTS, expect_best):
        got, seq = best_score(opp["policy"])
        assert got == eb, f"{opp['label']} 最高分应为 {eb}，实得 {got}"
        assert simulate(opp["policy"], seq)[0] == got
    # 「以牙还牙」的状态机：第一轮合作，之后精确复制我上一轮
    tft = OPPONENTS[2]["policy"]
    for seq in itertools.product("CD", repeat=4):
        assert [tft(list(seq[:i])) for i in range(4)] == ["C"] + list(seq[:3]), f"TFT 复现错误：{seq}"
    # 对以牙还牙者：背叛一次只被报复一次（之后它又原谅你）→ 5 + 0 + 8×3 = 29
    assert simulate(tft, ("D",) + ("C",) * 9)[0] == 29
    # 一直背叛则每轮都在互坑：5 + 9×1 = 14
    assert simulate(tft, ("D",) * 10)[0] == 14
    # 对以牙还牙者的最优是「九轮合作 + 最后一轮背叛」：9×3 + 5 = 32
    assert simulate(tft, ("C",) * 9 + ("D",))[0] == 32
    print("  自检：收益序 T>R>P>S、单轮激励、三位对手的理论最高分（50/10/32）、以牙还牙状态机全部通过。")

    total = 0
    done = 0
    for i, opp in enumerate(OPPONENTS):
        sc, finished = run_level(i, opp)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(OPPONENTS)} 关完成，总分 {total}/{len(OPPONENTS) * 100}")
    if total >= 260:
        print("  🏆 你既抓住了「对老实人别太客气」的分寸，又治住了恶棍，还赢得了未知对手的长期合作。")
    elif total >= 150:
        print("  👍 关键一课：背叛单轮最多多拿 2 分，却会把对方推入互相背叛的低收益循环。")
    else:
        print("  🙂 回头看看：对「以牙还牙」者，一次背叛的账单是——本轮多拿 2 分，"
              "下一轮被报复成 0 分（少 3 分），净亏 1 分；若一路背叛，只剩 14 分（一直合作是 30 分）。")
    print("=" * 62)


if __name__ == "__main__":
    play()
