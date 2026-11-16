# -*- coding: utf-8 -*-
"""
弹道炮兵 · 抛体运动推演
====================================================
你有一门炮，出膛速度固定。目标在正前方某距离处，你还得考虑风。
任务是：给出一个发射角（0-90 度），让炮弹落在目标上。

背后的物理（这游戏不用猜，可以直接算）：
  水平：x(t) = (v0 cosθ) t + ½ a_wind t²
  竖直：y(t) = (v0 sinθ) t - ½ g t²        g = 9.8 m/s²
  落地时间（y=0）：t = 2 v0 sinθ / g
  于是射程 R(θ) = v0 cosθ · t + ½ a_wind t²

所以：
  · 角度太小 → 平飞但飞不远
  · 角度太大 → 飞得高但水平分量小、滞空时间长（逆风时被吹得更远或更近）
  · 同一个射程通常有「低伸」和「高抛」两个解

玩法：每关 3 发机会，输入角度（可以是小数，如 32.5）。
  第 1 发命中 = 100 分，第 2 发 = 70 分，第 3 发 = 40 分，全空 = 0 分。

命令：
  hint   本题提示（−30 分，告诉你最大射程与是否够得着）
  table  再看一次风速、目标距离等参数
  q      退出

运行：python3 2026-11-16_弹道炮兵.py
"""

import math

G = 9.8

LEVELS = [
    {"v0": 30.0, "dist": 45.0, "wind": 0.0, "tol": 1.0,
     "note": "无风，新手关。速度 30 m/s，目标 45 m。"},
    {"v0": 35.0, "dist": 70.0, "wind": -3.0, "tol": 1.0,
     "note": "逆风 3 m/s²：炮弹越飞越慢，需要更大的角度来补偿。"},
    {"v0": 40.0, "dist": 100.0, "wind": 2.0, "tol": 1.0,
     "note": "顺风 2 m/s²：风把炮弹往前推，角度要收一点，否则会过远。"},
]


def flight_time(v0, deg):
    return 2 * v0 * math.sin(math.radians(deg)) / G


def shots_range(v0, deg, wind):
    """解析求解射程：落地时炮弹水平走了多远。"""
    t = flight_time(v0, deg)
    x = v0 * math.cos(math.radians(deg)) * t + 0.5 * wind * t * t
    return t, x


def trajectory(v0, deg, wind, samples=24):
    """返回若干采样点 (x, y)，用于画一条简易轨迹。"""
    t_end = flight_time(v0, deg)
    pts = []
    for i in range(samples + 1):
        t = t_end * i / samples
        x = v0 * math.cos(math.radians(deg)) * t + 0.5 * wind * t * t
        y = v0 * math.sin(math.radians(deg)) * t - 0.5 * G * t * t
        pts.append((x, y))
    return pts


def plot(v0, deg, wind, dist, width=56, height=11):
    pts = trajectory(v0, deg, wind)
    xmax = max(max(p[0] for p in pts), dist)
    ymax = max(max(p[1] for p in pts), 1.0)
    grid = [[" "] * (width + 1) for _ in range(height + 1)]
    for x, y in pts:
        cx = int(round(x / xmax * width))
        cy = int(round((1 - y / ymax) * height))
        cx = max(0, min(width, cx))
        cy = max(0, min(height, cy))
        grid[cy][cx] = "*"
    tx = int(round(dist / xmax * width))
    grid[height][tx] = "◎"          # 目标位置
    lines = ["    +" + "-" * width + "+"]
    for row in grid:
        lines.append("    |" + "".join(row) + "|")
    lines.append("    +" + "-" * width + "+")
    lines.append(f"    0{' ' * (width // 2 - 2)}距离(m){' ' * (width // 2 - 4)}{int(xmax)}")
    return "\n".join(lines)


def solve_angles(level, step=0.05):
    """扫描所有角度，找出能把炮弹落在目标容差内的角度，按误差从小到大排序。"""
    hits = []
    for i in range(1, 1800):
        deg = i * step
        if deg >= 90:
            break
        _t, x = shots_range(level["v0"], deg, level["wind"])
        err = abs(x - level["dist"])
        if err <= level["tol"]:
            hits.append((deg, x, err))
    hits.sort(key=lambda h: h[2])
    return hits


def max_range(level):
    best = (0, 0)
    for i in range(1, 1800):
        deg = i * 0.05
        if deg >= 90:
            break
        _t, x = shots_range(level["v0"], deg, level["wind"])
        if x > best[1]:
            best = (deg, x)
    return best


def run_level(idx, level):
    v0, dist, wind, tol = level["v0"], level["dist"], level["wind"], level["tol"]
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + level["note"])
    print(f"  出膛速度 {v0} m/s　目标距离 {dist} m　水平风加速度 {wind:+.1f} m/s²　容差 ±{tol} m")

    score = 100
    for attempt in range(1, 4):
        try:
            raw = input(f"\n  第 {attempt} 发，角度（0-90）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "hint":
            if score > 30:
                score = 30
            d_max, r_max = max_range(level)
            state = "够得着" if r_max >= dist else "够不着，参数设计有问题"
            print(f"  提示：本关最大射程约 {r_max:.1f} m（角度 {d_max:.1f}°），目标 {dist} m，{state}。"
                  f"（本题上限 {score} 分）")
            continue
        if low == "table":
            print(f"  v0={v0} m/s，目标={dist} m，风={wind:+.1f} m/s²，容差=±{tol} m")
            continue
        try:
            deg = float(raw)
        except ValueError:
            print("  请输入一个数字角度，例如 32.5")
            continue
        if not (0 < deg < 90):
            print("  角度要在 0 到 90 度之间。")
            continue

        t, x = shots_range(v0, deg, wind)
        err = x - dist
        print(plot(v0, deg, wind, dist))
        print(f"  滞空 {t:.2f} s，落点 {x:.1f} m（目标 {dist} m）")
        if abs(err) <= tol:
            pts = {1: 100, 2: 70, 3: 40}[attempt]
            final = min(score, pts)
            print(f"  ✅ 命中！偏差 {abs(err):.2f} m，在容差内。本关 {final} 分。")
            return final, True

        if err > 0:
            print(f"  ❌ 打远了 {abs(err):.1f} m —— 角度收小一点。")
        else:
            print(f"  ❌ 打近了 {abs(err):.1f} m —— 角度加大一点。")
        if attempt == 3:
            sols = solve_angles(level)
            if sols:
                print("  本关可命中的角度有：" +
                      "、".join(f"{a:.1f}°" for a, _x, _e in sols[:6]) +
                      ("…" if len(sols) > 6 else ""))
            else:
                print("  本关没有可命中角度（关卡数据需调整）。")
        score = min(score, {1: 100, 2: 70, 3: 40}[min(attempt + 1, 3)])
    return 0, True


def play():
    print("=" * 62)
    print("      🎯 弹道炮兵 · 抛体运动推演")
    print("=" * 62)
    print("输入发射角，把炮弹打到目标上。每关 3 发，越早命中分越高。")

    # 开局自检：每关必须存在命中角度，否则关卡不可解
    for i, lv in enumerate(LEVELS, 1):
        hits = solve_angles(lv)
        assert hits, f"第 {i} 关无解，请调整参数"

    total = 0
    done = 0
    for i, lv in enumerate(LEVELS):
        sc, ok = run_level(i, lv)
        total += sc
        if ok is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 250:
        print("  🏆 你已经会用「射程 = v0 cosθ · t + ½a t²」来反推角度了。")
    elif total >= 100:
        print("  👍 抓住了规律：角度越小越平、射程先增后减，45° 附近最远。")
    else:
        print("  🙂 诀窍：先看最大射程，再按「打近了加角度、打远了减角度」微调。")
    print("=" * 62)


if __name__ == "__main__":
    play()
