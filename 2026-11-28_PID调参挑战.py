#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PID 调参挑战 —— 用三个旋钮把一条曲线驯服

【简介】
PID 是工业现场最常用的控制器：它根据「误差」算输出——比例看当前误差有多大，
积分看误差积累了多久，微分看误差变化得多快。调参就是给 Kp / Ki / Kd 找一组数，
让系统又快又稳地跟上目标值，既不慢吞吞，也不来回震荡。

本程序内置 5 个被控对象（一阶惯性、二阶振荡、带纯滞后、带输入扰动、执行器饱和），
每个对象在 t=1s 时给你一个阶跃目标 1.0。你要输入一组 PID 参数，
程序用数值仿真（RK4，步长 0.01s）跑 25 秒，算出三项指标并给分：

  稳态误差 |e| ≤ 允许值    …… 8 分
  超调量 ≤ 允许值           …… 6 分
  调节时间 ≤ 允许值         …… 6 分

一关满分 20，五关合计 100；每关最多试 6 组参数，取该关最好成绩。

【玩法】
- 输入三个数：Kp Ki Kd，用空格或逗号隔开，例如 `10 1 0` 或 `3,0.5,0.2`
- 参数范围 0~50，允许为 0（表示不用该项）。
- 每轮会打印 ASCII 阶跃响应曲线和三项指标，不合格可以继续调。
- 提示：hint（花 10 分看一眼参考参数方向），help 看规则，q 退出。

【命令】
  10 1 0     提交一组参数
  hint/h     花 10 分获取调参方向提示（同一关一次）
  help/?     再看一遍规则
  空行        重看本题目标与上一次曲线
  q/quit     退出

【运行】
  python3 2026-11-28_PID调参挑战.py
  python3 2026-11-28_PID调参挑战.py --check   # 自检（解析对照、可解性、步长收敛、积分必要性）

【小知识】
积分项消不掉「执行器饱和」，这叫积分饱和（windup），所以本程序在饱和时冻结积分；
微分项作用在被测量而不是误差上，可以避免目标跳变时的「微分冲击」。
"""

import math
import re
import sys

DT = 0.01
T_END = 25.0
STEP_T = 1.0
TF = 0.08          # 微分滤波时间常数
I_LIMIT = 20.0
MAX_TRIES = 6
HINT_COST = 10

LEVELS = [
    dict(name="一阶惯性环节", desc="G(s)=1/(s+1)，最温和的对象，先把稳态误差压下去。",
         A=[[-1.0]], B=[[1.0]], C=[[1.0]], u_max=10.0, delay=0.0, dist=None,
         ess_tol=0.020, os_lim=0.050, settle_lim=6.0, hint="只用一个旋钮也行：Kp 2~20 配 Ki 1~2；Kp 给大、Ki 更小也能压住误差。"),
    dict(name="二阶振荡环节", desc="G(s)=1/(s²+1.2s+1)，比例给大了会来回晃，需要微分来阻尼。",
         A=[[0.0, 1.0], [-1.0, -1.2]], B=[[0.0], [1.0]], C=[[1.0, 0.0]], u_max=10.0, delay=0.0, dist=None,
         ess_tol=0.020, os_lim=0.100, settle_lim=8.0, hint="Kp 2、Ki 1 是甜点区，Kd 给 0.5~2 就能把超调压到 10% 以下。"),
    dict(name="带纯滞后的对象", desc="G(s)=e^{-1.5s}/(s+1)，反馈总是迟到，比例太大就会震荡。",
         A=[[-1.0]], B=[[1.0]], C=[[1.0]], u_max=5.0, delay=1.5, dist=None,
         ess_tol=0.020, os_lim=0.040, settle_lim=10.0, hint="延迟对象要非常保守：Kp 降到 1 以下（甚至 0.5），Ki 0.1~0.3，再加一点微分。"),
    dict(name="带输入扰动的对象", desc="G(s)=1/(s+1)，t=8s 起混入 0.8 的输入扰动，只有积分能把它清除。",
         A=[[-1.0]], B=[[1.0]], C=[[1.0]], u_max=10.0, delay=0.0, dist=(8.0, 0.8),
         ess_tol=0.001, os_lim=0.050, settle_lim=8.0, hint="残差只能靠积分清零：Kp 10 附近、Ki 0.3 起步，跑满 25 秒就能收干净。"),
    dict(name="执行器饱和系统", desc="二阶对象但执行器只能输出 ±1.3，目标 1.0，给太猛会饱和卡住。",
         A=[[0.0, 1.0], [-1.0, -1.2]], B=[[0.0], [1.0]], C=[[1.0, 0.0]], u_max=1.3, delay=0.0, dist=None,
         ess_tol=0.030, os_lim=0.050, settle_lim=8.0, hint="Kp 控制在 1~5，配一点 Kd 抑制超调；饱和时硬顶只会更慢。"),
]


def _mat_vec(A, x):
    return [sum(A[i][j] * x[j] for j in range(len(x))) for i in range(len(A))]


def _clip(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def simulate(level, kp, ki, kd, dt=DT, t_end=T_END, record=False):
    """返回 (指标 dict, 采样曲线 list)。纯确定性，无随机。"""
    A, B, C = level["A"], level["B"], level["C"]
    nx = len(A)
    x = [0.0] * nx
    integ = 0.0
    d_filt = 0.0
    y_prev = 0.0
    hist = []          # 控制器输出历史，用于纯滞后
    delay_steps = int(round(level["delay"] / dt))
    u_max = level["u_max"]
    steps = int(round(t_end / dt))
    ys = []
    t_prev = 0.0
    es_acc = []
    for i in range(steps + 1):
        t = i * dt
        y = sum(C[0][j] * x[j] for j in range(nx))
        ys.append(y)
        target = 0.0 if t < STEP_T - 1e-9 else 1.0
        e = target - y
        if t >= STEP_T - 1e-9:
            es_acc.append((t, e))
        # 微分作用在测量值上，避免目标跳变的微分冲击
        dy = (y - y_prev) / dt if i > 0 else 0.0
        d_filt += dt / (TF + dt) * (-dy - d_filt)
        u_raw = kp * e + ki * integ + kd * d_filt
        u_sat = _clip(u_raw, -u_max, u_max)
        # 条件积分抗饱和：输出顶住上限且误差还想往上推时，冻结积分
        pushing = (u_raw > u_max and e > 0) or (u_raw < -u_max and e < 0)
        if not pushing:
            integ = _clip(integ + e * dt, -I_LIMIT, I_LIMIT)
        hist.append(u_sat)
        u_app = hist[-1 - delay_steps] if len(hist) > delay_steps else 0.0
        if level["dist"]:
            t0, amp = level["dist"]
            if t >= t0 - 1e-9:
                u_app += amp
        # RK4 推进状态
        def f(xx):
            g = _mat_vec(A, xx)
            for k in range(nx):
                g[k] += B[k][0] * u_app
            return g
        k1 = f(x)
        k2 = f([x[j] + 0.5 * dt * k1[j] for j in range(nx)])
        k3 = f([x[j] + 0.5 * dt * k2[j] for j in range(nx)])
        k4 = f([x[j] + dt * k3[j] for j in range(nx)])
        x = [x[j] + dt / 6.0 * (k1[j] + 2 * k2[j] + 2 * k3[j] + k4[j]) for j in range(nx)]
        y_prev = y
        t_prev = t
    # 指标
    post = [(t, y) for (t, y) in [(i * dt, ys[i]) for i in range(steps + 1)] if t >= STEP_T - 1e-9]
    if not post:
        return dict(ok=False, ess=99, overshoot=99, settle=99, maxy=0, diverged=True), ys
    maxy = max(y for _, y in post)
    overshoot = max(0.0, maxy - 1.0)
    band = 0.02
    last_out = STEP_T
    for t, y in post:
        if abs(y - 1.0) > band:
            last_out = t
    settle = last_out - STEP_T
    tail = [y for (t, y) in post if t >= post[-1][0] - 2.0]
    ess = sum(tail) / len(tail) - 1.0
    diverged = (not all(math.isfinite(y) for y in ys)) or max(abs(y) for y in ys) > 50.0
    maxu = max(abs(v) for v in hist) if hist else 0.0
    return dict(ok=not diverged, ess=abs(ess), overshoot=overshoot, settle=settle,
                maxy=maxy, diverged=diverged, maxu=maxu), ys


def score_of(level, met):
    if met["diverged"]:
        return 0, (False, False, False)
    e_ok = met["ess"] <= level["ess_tol"]
    o_ok = met["overshoot"] <= level["os_lim"] and met["maxy"] >= 0.9
    s_ok = met["settle"] <= level["settle_lim"]
    pts = (8 if e_ok else 0) + (6 if o_ok else 0) + (6 if s_ok else 0)
    return pts, (e_ok, o_ok, s_ok)


def chart(ys, t_end=T_END, dt=DT, width=56, height=11):
    """把阶跃响应画成 ASCII 图：目标线 '-'，曲线 '#'。"""
    step = max(1, len(ys) // width)
    vals = [ys[i] for i in range(0, len(ys), step)][:width]
    hi = max(1.25, max(vals) * 1.05)
    rows = []
    for row in range(height + 1):
        level_val = hi * (height - row) / height
        line = []
        for v in vals:
            if v >= level_val:
                line.append("#")
            elif abs(level_val - 1.0) < hi / height / 2:
                line.append("-")
            else:
                line.append(" ")
        rows.append("%6.2f|%s" % (level_val, "".join(line)))
    rows.append("      +" + "-" * len(vals))
    return "\n".join(rows)


def parse_params(text):
    s = text.strip().lower()
    s = re.sub(r"kp\s*[:=]", "", s)
    s = re.sub(r"ki\s*[:=]", "", s)
    s = re.sub(r"kd\s*[:=]", "", s)
    s = s.replace("，", ",").replace("、", ",").replace(";", ",").replace("；", ",")
    nums = re.findall(r"-?[0-9]+(?:\.[0-9]+)?", s)
    if len(nums) != 3:
        return None
    try:
        vals = [float(x) for x in nums]
    except ValueError:
        return None
    if any(v < 0 or v > 50 for v in vals):
        return None
    if len(set(s.replace(" ", "").split(","))) > 3:
        return None
    return tuple(vals)


def play_level(idx, level, input_fn, out):
    out("=" * 64)
    out("第 %d 关：%s —— %s" % (idx, level["name"], level["desc"]))
    out("合格线：稳态误差 ≤ %.3f，超调 ≤ %.0f％，调节时间 ≤ %.1fs" % (
        level["ess_tol"], level["os_lim"] * 100, level["settle_lim"]))
    out("执行器上限 ±%.2f%s%s" % (
        level["u_max"], ("，纯滞后 %.1fs" % level["delay"]) if level["delay"] else "",
        ("，t=%.0fs 起 %.1f 输入扰动" % level["dist"]) if level["dist"] else ""))
    out("输入三个参数（Kp Ki Kd，空格或逗号分隔）。")
    hint_used = False
    best_pts, best_desc = 0, "尚未提交"
    for attempt in range(1, MAX_TRIES + 1):
        out("--- 第 %d/%d 次尝试 ---" % (attempt, MAX_TRIES))
        while True:
            try:
                raw = input_fn("Kp Ki Kd > ")
            except EOFError:
                out("输入结束，本关按当前最好成绩（%d/20）结算。" % best_pts)
                return best_pts
            s = raw.strip()
            low = s.lower()
            if low in ("q", "quit", "exit", "退出"):
                raise KeyboardInterrupt
            if low in ("hint", "h", "提示") and not hint_used:
                hint_used = True
                out("提示（-10 分）：%s" % level["hint"])
                continue
            if low in ("help", "?", "帮助"):
                out("输入三个 0~50 的数，如 10 1 0；hint 求提示；q 退出。")
                continue
            if s == "":
                out("本关目标：%s" % level["hint"].replace(level["hint"], "见合格线，慢慢收敛即可。"))
                continue
            params = parse_params(s)
            if params is None:
                out("请给三个 0~50 之间的数，例如 `10 1 0`。")
                continue
            break
        kp, ki, kd = params
        met, ys = simulate(level, kp, ki, kd)
        pts, marks = score_of(level, met)
        if hint_used:
            pts = max(0, pts - HINT_COST)
        out(chart(ys))
        if met["diverged"]:
            out("结果：系统发散了（输出超出 50），这组参数不能用。")
        else:
            out("稳态误差 %.4f %s | 超调 %.1f％ %s | 调节时间 %.2fs %s" % (
                met["ess"], "✓" if marks[0] else "✗",
                met["overshoot"] * 100, "✓" if marks[1] else "✗",
                met["settle"], "✓" if marks[2] else "✗"))
        out("本次得分 %d/20%s" % (pts, "（含提示扣分）" if hint_used else ""))
        if pts > best_pts:
            best_pts, best_desc = pts, "Kp=%.2f Ki=%.2f Kd=%.2f" % (kp, ki, kd)
        if pts == 20:
            out("★ 全部指标达标，本关满分！")
            return 20
    out("本关结束：最好成绩 %d/20（%s）。" % (best_pts, best_desc))
    return best_pts


def main(input_fn=input, out=print):
    out(__doc__.split("【运行】")[0])
    total = 0
    for i, lv in enumerate(LEVELS, 1):
        total += play_level(i, lv, input_fn, out)
    out("=" * 64)
    out("总分：%d / 100" % total)
    if total >= 96:
        out("评级：首席调参师 —— 五个对象全部驯服。")
    elif total >= 70:
        out("评级：现场工程师 —— 大部分指标已经拿住。")
    elif total >= 40:
        out("评级：实习生 —— 先记住：误差靠积分，震荡靠微分。")
    else:
        out("评级：学徒 —— 从第 1 关慢慢来，曲线会听话的。")
    return total


def check():
    ok = True

    def say(cond, msg):
        nonlocal ok
        if cond:
            print("[PASS]", msg)
        else:
            ok = False
            print("[FAIL]", msg)

    # 1. 一阶 P 控制稳态误差解析式 e_ss = 1/(1+Kp)
    worst = 0.0
    for kp in (1.0, 5.0, 20.0, 40.0):
        met, _ = simulate(LEVELS[0], kp, 0.0, 0.0)
        worst = max(worst, abs(met["ess"] - 1.0 / (1.0 + kp)))
    say(worst < 0.004, "一阶对象纯比例的稳态误差与解析式 1/(1+Kp) 一致（最大偏差 %.4f）" % worst)

    # 2. 步长收敛：0.01 与 0.0025 的指标接近
    conv = True
    for lv in (LEVELS[0], LEVELS[1], LEVELS[4]):
        a, _ = simulate(lv, 8.0, 0.6, 0.4)
        b, _ = simulate(lv, 8.0, 0.6, 0.4, dt=0.0025)
        if abs(a["ess"] - b["ess"]) > 0.004 or abs(a["overshoot"] - b["overshoot"]) > 0.02 \
                or abs(a["settle"] - b["settle"]) > 0.3:
            conv = False
    say(conv, "步长 0.01→0.0025 时三项指标收敛（RK4 精度足够）")

    # 3. 可解性：网格搜索每关至少 1 组满分参数，且存在明显不合格的朴素参数
    grid = [(kp, ki, kd) for kp in (0, 0.5, 2, 10, 20, 50)
            for ki in (0, 0.1, 0.3, 1, 10, 20, 50)
            for kd in (0, 0.3, 0.5, 2)]
    for idx, lv in enumerate(LEVELS, 1):
        passing = []
        for kp, ki, kd in grid:
            met, _ = simulate(lv, kp, ki, kd)
            pts, _ = score_of(lv, met)
            if pts == 20:
                passing.append((kp, ki, kd))
        met0, _ = simulate(lv, 0.0, 0.0, 0.0)
        pts0, _ = score_of(lv, met0)
        say(len(passing) >= 1 and pts0 < 20,
            "第 %d 关可解：网格中 %d 组满分参数（如 %s）；(0,0,0) 得 %d 分" % (
                idx, len(passing), passing[0] if passing else "无", pts0))

    # 4. L4 必须靠积分：纯 PD 在扰动下留残差
    met, _ = simulate(LEVELS[3], 50.0, 0.0, 5.0)
    say(met["ess"] > LEVELS[3]["ess_tol"], "第 4 关纯 PD（Ki=0，Kp 顶到 50）残差 %.4f 仍超线 %.4f" % (
        met["ess"], LEVELS[3]["ess_tol"]))
    met2, _ = simulate(LEVELS[3], 20.0, 50.0, 0.5)
    say(met2["ess"] <= LEVELS[3]["ess_tol"] and met2["overshoot"] <= LEVELS[3]["os_lim"],
        "第 4 关给足积分（Kp=20 Ki=50 Kd=0.5）后残差 %.5f、超调 %.1f％ 达标" % (
            met2["ess"], met2["overshoot"] * 100))

    # 5. 饱和确实限制性能：L5 用 Kp=50 与 Kp=3 比较
    m50, _ = simulate(LEVELS[4], 50.0, 1.0, 2.0)
    m3, _ = simulate(LEVELS[4], 3.0, 0.6, 0.6)
    say(m50["maxu"] <= LEVELS[4]["u_max"] + 1e-9 and abs(m50["maxu"] - LEVELS[4]["u_max"]) < 1e-6
        and m3["maxu"] <= LEVELS[4]["u_max"] + 1e-9,
        "第 5 关控制量被饱和限制：大 Kp 顶到上限 %.2f，小 Kp 峰值 %.2f" % (
            m50["maxu"], m3["maxu"]))

    # 6. 解析器
    cases = [("10 1 0", (10.0, 1.0, 0.0)), ("3,0.5,0.2", (3.0, 0.5, 0.2)),
             ("Kp=5 Ki=0.5 Kd=1", (5.0, 0.5, 1.0)), (" 2、1、0 ", (2.0, 1.0, 0.0))]
    say(all(parse_params(t) == exp for t, exp in cases), "参数解析支持空格/逗号/顿号/Kp= 写法")
    say(parse_params("1 2") is None and parse_params("a b c") is None
        and parse_params("-1 0 0") is None and parse_params("60 0 0") is None,
        "个数不对、含字母、负数、超 50 都被拒绝")

    # 7. 确定性
    a, _ = simulate(LEVELS[1], 7.0, 0.8, 0.6)
    b, _ = simulate(LEVELS[1], 7.0, 0.8, 0.6)
    say(a == b, "同参数两次仿真指标完全一致（纯确定性）")

    # 8. 假 stdin 回归：直接输入满分组 → 每关 20 分；乱输不卡死
    first_pass = []
    for lv in LEVELS:
        found = None
        for kp, ki, kd in grid:
            met, _ = simulate(lv, kp, ki, kd)
            if score_of(lv, met)[0] == 20:
                found = "%g %g %g" % (kp, ki, kd)
                break
        first_pass.append(found or "9 1 1")
    buf = iter(first_pass)

    def fake_input(_p=""):
        try:
            return next(buf)
        except StopIteration:
            raise EOFError
    lines = []
    total = main(input_fn=fake_input, out=lines.append)
    say(total == 100, "输入五组满分组时总分 100（实际 %d）" % total)

    buf2 = iter(["abc", "60 0 0", "0 0 0", "0 0 0", "0 0 0", "0 0 0", "0 0 0"])

    def fake_input2(_p=""):
        try:
            return next(buf2)
        except StopIteration:
            raise EOFError
    lines2 = []
    try:
        t2 = main(input_fn=fake_input2, out=lines2.append)
        reg2 = t2 == 0
    except Exception:
        reg2 = False
    say(reg2, "乱输/零参数时总分为 0 且不崩溃")

    print()
    print("自检通过 ✅" if ok else "自检未通过 ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        if "--check" in sys.argv:
            sys.exit(check())
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n已退出。")
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
