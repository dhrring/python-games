# -*- coding: utf-8 -*-
"""
小吃摊大亨（7 天经营模拟）
==========================
你盘下了一个小吃摊，手里 200 元本金，要连续经营 7 天，看能赚多少。

每天的流程：
  1. 看今日天气 → 天气会明显影响客流（晴天 1.0、下雨 0.65、周末集市 1.4）
  2. 决定进货量（每份食材成本 3 元，当天卖不完会报废，成本打水漂）
  3. 决定单价（越低卖得越多，但低于成本就必亏；定太高没人买）
  4. 系统按「需求模型」计算客流，销量 = min(进货量, 需求)

需求模型（游戏内真实生效，不是随便写的）：
    需求 ≈ 基础客流 × 天气系数 × (8 / 单价)^1.5  +  ±15% 随机波动
也就是说，单价 8 元是"心理价位"，每提高 1 元客流会按 1.5 次方衰减。
这个模型下存在一个利润最优价，你能找到吗？

游玩方法：
  每天按提示输入 进货量 和 单价（回车确认），全部 7 天结束后给出结算单。
  输入 q 可随时退出。
运行：python3 2026-11-11_小吃摊大亨.py
"""

import random

START_CASH = 200
COST_PER_UNIT = 3.0
REF_PRICE = 8.0
DAYS = 7
MAX_STOCK_PER_DAY = 80

WEATHERS = [
    ("晴天", 1.00, "客流正常"),
    ("下雨", 0.65, "路上没人，客流明显减少"),
    ("周末集市", 1.40, "人多热闹，客流大涨"),
    ("工作日中午", 0.90, "只有上班族路过"),
    ("节假日", 1.20, "游客比平时多"),
]


def base_demand():
    return random.randint(22, 40)


def demand_model(base, weather_mult, price):
    """单价越高需求越低；指数 1.5 让高价衰减很快。"""
    if price <= 0:
        return 0
    d = base * weather_mult * (REF_PRICE / price) ** 1.5
    # ±15% 随机波动
    noise = random.uniform(0.85, 1.15)
    return max(0, int(round(d * noise)))


def ask_int(prompt, lo, hi):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        try:
            v = int(raw)
        except ValueError:
            print(f"  请输入 {lo}~{hi} 的整数。")
            continue
        if not lo <= v <= hi:
            print(f"  请输入 {lo}~{hi} 的整数。")
            continue
        return v


def ask_price(prompt, cash_left, min_price):
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        try:
            v = round(float(raw), 1)
        except ValueError:
            print("  请输入一个数字，例如 7 或 7.5。")
            continue
        if v < min_price:
            print(f"  单价不能低于成本价 {min_price:.1f} 元，否则每卖一份都亏钱。")
            continue
        if v > 60:
            print("  单价不建议超过 60 元（基本没人买），请重新输入。")
            continue
        return v


def main():
    print("=" * 56)
    print("      🍢 小吃摊大亨 7 天经营")
    print("=" * 56)
    print(f"本金 {START_CASH} 元｜食材成本 {COST_PER_UNIT:.0f} 元/份｜心理价位约 {REF_PRICE:.0f} 元/份")
    print("提示：定价太低赚不到钱，太高卖不出去；进货太多当天会报废。")

    cash = START_CASH
    total_revenue = 0.0
    total_cost = 0.0
    total_sold = 0
    total_waste = 0
    record = []

    for day in range(1, DAYS + 1):
        weather_name, w_mult, w_tip = random.choice(WEATHERS)
        base = base_demand()
        print("\n" + "-" * 56)
        print(f"【第 {day} 天】天气：{weather_name}（系数 {w_mult}，{w_tip}）")
        print(f"  当前资金：{cash:.1f} 元｜基础客流 {base} 人，受天气影响后约 {round(base * w_mult)} 人")

        max_affordable = int(cash // COST_PER_UNIT)
        cap = min(MAX_STOCK_PER_DAY, max_affordable)
        if cap <= 0:
            print("  资金不足，进不了货了，今天只能空手回家。")
            record.append((day, weather_name, 0, 0.0, 0, 0, 0.0))
            continue

        stock = ask_int(f"  进货几份？（0~{cap}，每份 {COST_PER_UNIT:.0f} 元）：", 0, cap)
        if stock is None:
            print("\n你收摊不干了。")
            break

        price = ask_price("  单价定多少元？（可带小数，如 7.5）：", cash - stock * COST_PER_UNIT, COST_PER_UNIT)
        if price is None:
            print("\n你收摊不干了。")
            break

        cost = stock * COST_PER_UNIT
        demand = demand_model(base, w_mult, price)
        sold = min(stock, demand)
        revenue = sold * price
        waste = stock - sold
        cash += revenue - cost

        total_revenue += revenue
        total_cost += cost
        total_sold += sold
        total_waste += waste
        record.append((day, weather_name, stock, price, demand, sold, revenue - cost))

        print(f"  ➜ 客流需求 {demand} 人，卖出 {sold} 份，收入 {revenue:.1f} 元")
        print(f"  ➜ 进货成本 {cost:.1f} 元，报废 {waste} 份")
        print(f"  ➜ 今日净{'利润' if revenue - cost >= 0 else '亏损'}：{revenue - cost:+.1f} 元｜结余 {cash:.1f} 元")

    print("\n" + "=" * 56)
    print("  经营结算单")
    print("=" * 56)
    print(f"  {'天':<4}{'天气':<10}{'进货':>4}{'单价':>7}{'需求':>5}{'实卖':>5}{'净利':>9}")
    for day, w, stock, price, demand, sold, profit in record:
        print(f"  {day:<4}{w:<10}{stock:>4}{price:>7.1f}{demand:>5}{sold:>5}{profit:>+9.1f}")
    profit_total = cash - START_CASH
    print("-" * 56)
    print(f"  总销量 {total_sold} 份｜总进货成本 {total_cost:.1f} 元｜总报废 {total_waste} 份")
    print(f"  期末资金 {cash:.1f} 元｜净利润 {profit_total:+.1f} 元")
    if profit_total >= 900:
        print("  🏆 摊王！7 天几乎每天都在高客流日吃满，定价与进货都踩得很准。")
    elif profit_total >= 550:
        print("  👍 优秀，已经摸到最优价格的边了。")
    elif profit_total >= 250:
        print("  🙂 稳稳盈利，但还有空间：注意下雨天少进货。")
    elif profit_total >= 0:
        print("  🙂 没赔，但还有空间：试试把单价压在 7~10 元区间，注意别进货过量。")
    else:
        print("  😅 亏了。复盘一下：进货是不是超过客流太多？单价是不是定得太离谱？")
    print("  参考结论：这个需求模型下，单价约 9 元时单位客流利润最高，进货量贴近预测客流最不容易报废。")
    print("=" * 56)


if __name__ == "__main__":
    main()
