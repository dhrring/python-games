"""
====================================================
 大圆航线 —— 地理与球面几何小游戏
====================================================

【游戏简介】
飞机飞的是"大圆航线"——地球表面上两点之间最短的路径。它不等于地图上
画出来的直线，因为在球面上，纬线越靠近两极越短。

本游戏共 5 关：每关给你两座城市的经纬度，你要算出它们之间的大圆距离
（单位：公里）。第 5 关会碰到跨半球、经度差超过 180° 的情况。

【公式（游戏里也会重复给出）】
把纬度 φ、经度差 Δλ 换算成弧度后：

  a = sin²(Δφ/2) + cos φ₁ · cos φ₂ · sin²(Δλ/2)
  d = 2R · arcsin(√a)          R = 6371 km

其中 Δφ = φ₂ − φ₁，Δλ = λ₂ − λ₁。

【游玩方法】
1. 运行：python 2026-11-22_大圆航线.py
2. 每关输入距离（整数公里即可，允许 1.5% 的误差，四舍五入的不影响判分）。
3. 输入 hint 或 h：看提示（-10 分，每关最低保留 4 分）。
4. 输入 q / quit / 退出：结束本局；直接回车：重看题目。
5. 每关 20 分，答错扣 8 分（不低于 4 分），满分 100。

【自检】
python 2026-11-22_大圆航线.py --check
会用两种独立公式（haversine 与球面余弦定理）互相校验，并核对答案。
"""

import math
import sys

R_EARTH = 6371.0

LEVELS = [
    dict(
        title="京沪直飞",
        a=("北京", 39.9042, 116.4074),
        b=("上海", 31.2304, 121.4737),
        answer=1067,
        hint="Δφ = 31.23 − 39.90 = −8.67°（先平方，正负无所谓）；"
             "Δλ = 5.07°。纬度不高、cos φ₁·cos φ₂ 约 0.75，两项都要老老实实算。",
        note="实际民航航线常报 1067 公里左右，这就是大圆距离。",
    ),
    dict(
        title="西北到华南",
        a=("乌鲁木齐", 43.8256, 87.6168),
        b=("广州", 23.1291, 113.2644),
        answer=3284,
        hint="Δφ ≈ −20.7°，Δλ ≈ 25.65°。这一关纬度跨度大，"
             "cos φ₁ 只有 0.72 左右，别漏乘。",
        note="斜跨整个中国，约 3300 公里，相当于北京飞新加坡的距离量级。",
    ),
    dict(
        title="高原到冰城",
        a=("拉萨", 29.6520, 91.1721),
        b=("哈尔滨", 45.8038, 126.5349),
        answer=3550,
        hint="Δλ ≈ 35.36°，这个角度够大，sin²(Δλ/2) 会接近 0.09，"
             "两项量级都比第一关更接近，加完再开方。",
        note="东西向的斜线，比同纬度纯东西飞要长。",
    ),
    dict(
        title="从热带到寒极",
        a=("三亚", 18.2528, 109.5119),
        b=("漠河", 52.9700, 122.5300),
        answer=4022,
        hint="纬度从 18° 直接跳到 53°，Δφ ≈ 34.72°，"
             "光这一项 sin²(Δφ/2) 就有约 0.089。",
        note="中国南北最远的两个点之一，4000 公里出头。",
    ),
    dict(
        title="跨半球：北京到纽约",
        a=("北京", 39.9042, 116.4074),
        b=("纽约", 40.7128, -74.0060),
        answer=10989,
        hint="Δλ = −74.006 − 116.407 = −190.41°，看似超过 180°，"
             "但 sin² 对 Δλ 的整周取劣弧等价，直接代入即可（sin(−95.2°) 一样）。"
             "两城纬度接近，cos φ₁·cos φ₂ ≈ 0.58，主要靠 Δλ 那一项。",
        note="地球另一面，最短路径其实从北极圈附近掠过，不是地图上横着画的那条线。",
    ),
]


# -----------------------------------------------------------
# 距离计算（check 模式用两种公式交叉验证）
# -----------------------------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_EARTH * math.asin(math.sqrt(min(1.0, a)))


def law_of_cosines(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return R_EARTH * math.acos(max(-1.0, min(1.0, c)))


def tolerance(answer):
    return max(6.0, 0.015 * answer)


def run_check():
    print("大圆距离自检（haversine vs 球面余弦定理，并核对内置答案）\n")
    ok = True
    for i, lv in enumerate(LEVELS, 1):
        _, la1, lo1 = lv["a"]
        _, la2, lo2 = lv["b"]
        d1 = haversine(la1, lo1, la2, lo2)
        d2 = law_of_cosines(la1, lo1, la2, lo2)
        diff = abs(d1 - d2)
        in_range = abs(d1 - lv["answer"]) <= tolerance(lv["answer"])
        good = diff < 1.0 and in_range
        ok &= good
        print(f"[{'OK' if good else 'FAIL'}] 第 {i} 关 {lv['a'][0]}→{lv['b'][0]}："
              f"haversine {d1:.2f} km，余弦定理 {d2:.2f} km，两法差 {diff:.3f} km；"
              f"内置答案 {lv['answer']}（容差 ±{tolerance(lv['answer']):.1f} km）"
              f"{'符合' if in_range else '不符合'}")
    print("\n自检结果：", "全部通过" if ok else "存在不一致")
    return 0 if ok else 1


# -----------------------------------------------------------
# 游戏流程
# -----------------------------------------------------------
def parse_number(text):
    """从用户输入里抠出一个数字（允许 1067、1067km、1,067 之类）。"""
    cleaned = text.replace(",", "").replace("，", "").replace(" ", "")
    for unit in ("公里", "千米", "km", "KM", "Km"):
        cleaned = cleaned.replace(unit, "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def show_level(lv, idx):
    _, la1, lo1 = lv["a"]
    _, la2, lo2 = lv["b"]
    print("\n" + "=" * 52)
    print(f"第 {idx} 关 · {lv['title']}（{idx}/{len(LEVELS)}，20 分）")
    print("=" * 52)
    print(f"  A：{lv['a'][0]}　北纬 {la1:.4f}°，东经 {lo1:.4f}°")
    sign = "西经" if la2 < 0 else "东经"
    print(f"  B：{lv['b'][0]}　北纬 {la2:.4f}°，{sign} {abs(lo2):.4f}°")
    print("\n求：A、B 之间的大圆距离（公里，取整数）")
    print("公式：d = 2·6371·arcsin( √( sin²(Δφ/2) + cosφ₁·cosφ₂·sin²(Δλ/2) ) )")
    print("（h = 提示（-10 分）；q = 退出；回车 = 重看题目）")


def play():
    print("=" * 52)
    print(" 大圆航线 —— 地理与球面几何小游戏")
    print("=" * 52)
    print("5 关，每关 20 分，共 100 分。允许 1.5% 的计算误差。")
    print("命令：hint/h 提示（-10 分）｜q/quit/退出 结束｜回车 重看｜Ctrl+C 退出\n")

    score, hints = 0, 0
    for idx, lv in enumerate(LEVELS, 1):
        level_score, hint_used = 20, False
        show_level(lv, idx)
        while True:
            try:
                raw = input("\n你的答案（公里）> ")
            except (EOFError, KeyboardInterrupt):
                print("\n\n已退出，当前累计得分 {} 分。".format(score))
                return
            cmd = raw.strip()
            if not cmd:
                show_level(lv, idx)
                continue
            low = cmd.lower()
            if low in ("q", "quit", "exit", "退出"):
                print("\n已退出，当前累计得分 {} 分。".format(score))
                return
            if low in ("h", "hint", "提示", "?"):
                if not hint_used:
                    hint_used = True
                    hints += 1
                    level_score = max(4, level_score - 10)
                print(f"\n[提示] {lv['hint']}")
                print(f"（本关当前 {level_score} 分）")
                continue

            val = parse_number(cmd)
            if val is None:
                print("没看懂这个数字，输入一个公里数，或 h 要提示。")
                continue

            target = lv["answer"]
            if abs(val - target) <= tolerance(target):
                print(f"\n✅ 距离约 {target} 公里，你的答案 {val:g} km 在容差内。")
                print(f"   {lv['note']}")
                score += level_score
                print(f"本关得分 {level_score}，累计 {score}")
                break
            level_score = max(4, level_score - 8)
            off = (val - target) / target * 100
            tip = "偏高" if off > 0 else "偏低"
            print(f"\n❌ 差了约 {abs(off):.1f}%，你的结果{tip}。"
                  f"（本关当前 {level_score} 分）")
            print("检查一下：度数有没有换成弧度？cos φ 有没有乘上？")

    print("\n" + "=" * 52)
    print(f"全部通关！总分 {score}/100（用过 {hints} 次提示）")
    if score >= 95:
        print("评级：球面几何之神 —— 公式用得像计算器一样稳。")
    elif score >= 80:
        print("评级：航线规划师 —— 弧度换算和三角函数都很熟。")
    elif score >= 60:
        print("评级：见习导航员 —— 思路对，留意度数/弧度混用。")
    else:
        print("评级：纸上谈兵 —— 建议先把 Δφ、Δλ 单独写出来再代公式。")
    print("=" * 52)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(run_check())
    play()
