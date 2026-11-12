# -*- coding: utf-8 -*-
"""
拍卖行风云（英式增价拍卖 · 5 件拍品 · 3 位 AI 对手）
=====================================================
你是刚入行的拍卖师兼买家，带着 1200 元预算进拍场。
每件拍品都有「真实市价」，但你看不到它——只能拿到鉴定师给的一个估价区间。
你的对手是三位老手：他们各自对拍品有不同的心理上限，会一路跟你顶价。

赢的方式不是「买到最多」，而是「买得比市价便宜」：
  单件利润 = 真实市价 − 成交价
买到手却比市价贵，就是亏；最后按总利润评级。

玩法：
  轮到你就输入：
    y          按最低加价幅度加价
    y 500      直接把价格叫到 500 元（必须高于最低加价，且不超过你的预算）
    n          放弃这件拍品
    q          退出拍场
  每件的起拍价、真实市价、AI 的心理价都是每次运行随机生成的，重玩不重样。
运行：python3 2026-11-12_拍卖行风云.py
"""

import random

ITEMS = [
    {"name": "青花缠枝莲纹瓷瓶", "low": 260, "high": 620},
    {"name": "1950 年代手动上链机械表", "low": 340, "high": 780},
    {"name": "民国手绘城市地图", "low": 200, "high": 520},
    {"name": "老式双反胶片相机", "low": 180, "high": 460},
    {"name": "黄花梨木雕摆件", "low": 420, "high": 900},
]

AI_NAMES = ["戴礼帽的老陈", "举牌很快的小周", "只看品相的王姐"]
PLAYER_CASH = 1200
AI_CASH = 1400


def money(x):
    return f"{x:.0f} 元"


def next_step(price):
    """最低加价幅度：当前价的 10%，取整到 10，最低 20。"""
    return max(20, int(round(price * 0.1 / 10)) * 10)


class Bidder:
    def __init__(self, name, cash, max_bid, aggressive, is_player=False):
        self.name = name
        self.cash = cash
        self.max_bid = min(max_bid, cash)
        self.aggressive = aggressive
        self.is_player = is_player
        self.active = True
        self.spent = 0

    def can_bid(self, target):
        return target <= min(self.max_bid, self.cash - self.spent)


def play_item(item, player):
    market = random.randint(item["low"], item["high"])
    start = max(50, int(round(market * 0.45 / 10)) * 10)

    # 鉴定区间：包住真实市价，但有一定宽度
    est_low = max(50, int(market * 0.78 / 10) * 10)
    est_high = int(market * 1.14 / 10) * 10

    ais = []
    for name in AI_NAMES:
        coef = random.uniform(0.72, 1.16)
        ais.append(Bidder(name, AI_CASH, int(market * coef), random.uniform(0.7, 0.95)))

    print("\n" + "=" * 62)
    print(f"  拍品：{item['name']}")
    print(f"  鉴定师估价：{money(est_low)} ~ {money(est_high)}（真实市价在区间内，但不告诉你具体数）")
    print(f"  起拍价：{money(start)}｜最低加价 {money(next_step(start))}")
    print(f"  你的预算：{money(PLAYER_CASH - player.spent)}")

    price = start
    leader = None
    order = [player] + ais
    round_no = 0

    while True:
        round_no += 1
        bids = 0
        for b in order:
            if not b.active:
                continue
            if leader is b:
                continue
            if leader is not None and not b.can_bid(price + next_step(price)):
                if not b.is_player:
                    b.active = False
                    print(f"  · {b.name} 摇头退出了。")
                continue

            if b.is_player:
                print("\n  " + "-" * 56)
                print(f"  当前价 {money(price)}" + (f"（领先：{leader.name}）" if leader else "（还没人出价）"))
                print(f"  你的预算 {money(PLAYER_CASH - player.spent)}｜最低加价 {money(next_step(price))}")
                try:
                    raw = input("  加价？(y / y 金额 / n 放弃 / q 退出)：").strip().lower()
                except EOFError:
                    return market, None, True
                if raw in ("q", "quit", "exit"):
                    return market, None, True
                if raw in ("n", "no"):
                    b.active = False
                    print("  · 你放弃这件拍品。")
                    continue
                parts = raw.split()
                target = price + next_step(price)
                if len(parts) >= 2:
                    if not parts[1].isdigit():
                        print("  金额要写纯数字，例如：y 500")
                        continue
                    target = int(parts[1])
                    if target < price + next_step(price):
                        print(f"  出价必须不低于 {money(price + next_step(price))}。")
                        continue
                    if target > PLAYER_CASH - player.spent:
                        print("  超出你的预算了。")
                        continue
                elif raw not in ("y", "yes"):
                    print("  输入看不懂，请用 y / y 金额 / n / q。")
                    continue
                price = target
                leader = b
                bids += 1
                print(f"  → 你叫到 {money(price)}")
            else:
                minimum = price + next_step(price)
                jump = random.choice([0, 1, 1, 2])  # 偶尔跳价，制造压力
                target = minimum + jump * next_step(minimum)
                if not b.can_bid(target):
                    b.active = False
                    print(f"  · {b.name} 摇头退出了。")
                    continue
                # 越接近心理上限越犹豫
                ratio = target / max(1, b.max_bid)
                p = b.aggressive * (1.0 - 0.6 * max(0.0, ratio - 0.6))
                if random.random() < p:
                    price = target
                    leader = b
                    bids += 1
                    print(f"  → {b.name} 叫到 {money(price)}")
                # 不加价不代表退出，下一轮还会再考虑

        alive = [b for b in order if b.active]
        if bids == 0:
            break
        if len(alive) <= 1 and leader is not None:
            break

    if leader is None:
        print("\n  🔨 流拍：没人出价，这件拍品收回。")
        return market, None, False

    if leader.is_player:
        player.spent += price
        profit = market - price
        print(f"\n  🔨 成交！你以 {money(price)} 拍下「{item['name']}」。")
        print(f"     真实市价 {money(market)}，单件利润 {'+' if profit >= 0 else ''}{money(profit)}")
        return market, profit, False
    else:
        print(f"\n  🔨 成交！{leader.name} 以 {money(price)} 拍下，你出局。")
        print(f"     真实市价 {money(market)}（如果你当时能出到这个价，利润 {money(market - price)}）")
        return market, None, False


def main():
    print("=" * 62)
    print("      🔨 拍卖行风云")
    print("=" * 62)
    print("五件拍品，三个对手，1200 元预算。目标：总利润最大化，而不是抢到最多。")
    print("记住：拍到手的每一件，都要拿真实市价去减成交价才知道赚没赚。")

    player = Bidder("你", PLAYER_CASH, PLAYER_CASH, 1.0, is_player=True)
    total_profit = 0
    won = 0
    results = []

    for item in ITEMS:
        market, profit, quit_now = play_item(item, player)
        if quit_now:
            print("\n你离开了拍场。")
            break
        results.append((item["name"], market, profit))
        if profit is not None:
            total_profit += profit
            won += 1

    print("\n" + "=" * 62)
    print("  拍卖结算单")
    print("=" * 62)
    print("  拍品                          真实市价   你的结果")
    for name, market, profit in results:
        print(f"  {name:<24}  {money(market):>8}   " +
              ("未拍到" if profit is None else f"{'+' if profit >= 0 else ''}{money(profit)}"))
    print("-" * 62)
    print(f"  拍下 {won} 件｜总利润 {'+' if total_profit >= 0 else ''}{money(total_profit)}"
          f"｜剩余现金 {money(PLAYER_CASH - player.spent)}")

    if won == 0:
        print("  🪑 空手而归：一件都没拍下，预算一分没动。")
        print("  下次至少在一件你判断「明显低于估价中段」的拍品上举一次牌。")
    elif total_profit >= 700:
        print("  🏆 金牌拍卖师：几乎每件都买在市价之下。")
    elif total_profit >= 300:
        print("  👍 眼光不错，只有个别拍品追高了。")
    elif total_profit >= 60:
        print("  🙂 小赚，注意别在别人明显在顶价的时候还跟。")
    elif total_profit > 0:
        print("  🙂 勉强没亏，但资金效率不高。")
    elif total_profit == 0:
        print("  🙂 打平收场：买到的东西刚好值回成交价。")
    else:
        print("  😅 亏了。教训：出价超过鉴定区间的中段就该收手。")
    print("  参考结论：英式拍卖的最优策略是「出到你自己的估值上限就停止」，")
    print("  超过估值继续跟，长期一定是亏的。")
    print("=" * 62)


if __name__ == "__main__":
    main()
