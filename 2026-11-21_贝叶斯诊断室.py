"""
====================================================
 贝叶斯诊断室 —— 概率推理小游戏
====================================================

【中文说明】
医院检验科给你一份检测报告：某项检测阳性。问题是——你真的患病的概率有多少？
很多人会把「灵敏度 90%」直接当成「我 90% 得病了」，这叫基础率谬误（base rate fallacy）。
真实答案由贝叶斯公式决定：

                          P(病)·灵敏度
            P(病|阳) = ──────────────────────────────────────
                          P(病)·灵敏度 + (1−P(病))·(1−特异度)

也就是说，当疾病本身很罕见时，即使检测很准，阳性里也有大量是假阳性。

【游玩方法】
  · 直接运行：python 2026-11-21_贝叶斯诊断室.py
  · 共 5 关，每关 20 分，满分 100。
  · 根据题干给的患病率、灵敏度、特异度，输入你的答案（百分数，例如 8.3）。
  · 也可以直接输入小数（如 0.083），程序会自动换算成百分比。
  · 命令：hint 看解题提示（−10 分）｜ q 退出
  · 答错一次 −8 分，每关保底 4 分。

【知识点】
  贝叶斯公式、灵敏度（真阳性率）、特异度（真阴性率）、阳性预测值、基础率谬误。
====================================================
"""

TOL = 0.6          # 允许的百分比误差（百分点）
PER_LEVEL = 20     # 每关满分
WRONG_COST = 8
HINT_COST = 10
FLOOR = 4

# kind="posterior"：已知患病率/灵敏度/特异度，求阳性预测值（百分数）
# kind="prevalence"：已知灵敏度/特异度与目标阳性预测值，反求所需患病率（百分数）
LEVELS = [
    {
        "kind": "posterior",
        "prevalence": 0.01, "sens": 0.90, "spec": 0.90,
        "story": "某罕见病在人群中患病率 1%。检测灵敏度 90%、特异度 90%。你检测阳性，真正患病的概率是多少？",
    },
    {
        "kind": "posterior",
        "prevalence": 0.05, "sens": 0.95, "spec": 0.90,
        "story": "患病率 5%。检测灵敏度 95%、特异度 90%。阳性者的真实患病概率是多少？",
    },
    {
        "kind": "posterior",
        "prevalence": 0.02, "sens": 0.99, "spec": 0.95,
        "story": "患病率 2%，但检测很准：灵敏度 99%、特异度 95%。阳性者中真正患病的比例是多少？",
    },
    {
        "kind": "posterior",
        "prevalence": 0.30, "sens": 0.80, "spec": 0.70,
        "story": "这次是高危人群筛查：患病率 30%，灵敏度 80%、特异度只有 70%。阳性者患病概率是多少？",
    },
    {
        "kind": "prevalence",
        "target": 0.50, "sens": 0.90, "spec": 0.90,
        "story": "检测灵敏度 90%、特异度 90%。要让「阳性者中有一半真的患病」，人群患病率至少要达到多少？",
    },
]


def posterior(prevalence, sens, spec):
    """阳性预测值：P(病|阳)。"""
    hit = prevalence * sens
    false_alarm = (1 - prevalence) * (1 - spec)
    return hit / (hit + false_alarm)


def prevalence_for(target, sens, spec):
    """反解：使阳性预测值等于 target 所需的最低患病率。"""
    return target * (1 - spec) / (sens * (1 - target) + target * (1 - spec))


def expected_percent(level):
    if level["kind"] == "posterior":
        return posterior(level["prevalence"], level["sens"], level["spec"]) * 100
    return prevalence_for(level["target"], level["sens"], level["spec"]) * 100


def fmt_pct(x):
    return f"{x:.1f}%"


def parse_answer(text):
    """把用户输入解析成百分数；0~1 的小数按概率换算成百分数。"""
    raw = text.strip().replace("%", "").replace("％", "")
    val = float(raw)
    if 0 < val <= 1:
        val *= 100
    return val


def show_level(idx, level):
    print()
    print("─" * 48)
    print(f"【第 {idx + 1} 关 / {len(LEVELS)}】")
    if level["kind"] == "posterior":
        print(f"患病率 {level['prevalence'] * 100:g}%｜灵敏度 {level['sens'] * 100:g}%"
              f"｜特异度 {level['spec'] * 100:g}%")
        print(f"问：阳性者真正患病的概率 = ?（填百分数）")
    else:
        print(f"灵敏度 {level['sens'] * 100:g}%｜特异度 {level['spec'] * 100:g}%"
              f"｜目标阳性预测值 {level['target'] * 100:g}%")
        print(f"问：人群患病率至少要达到多少，阳性预测值才够 {level['target'] * 100:g}%？"
              f"（填百分数）")
    print(level["story"])


def show_hint(level):
    print("  💡 提示：")
    print("     先算「真阳性」和「假阳性」各有多少：")
    print("       真阳性 = 患病率 × 灵敏度　假阳性 = (1−患病率) × (1−特异度)")
    print("     阳性预测值 = 真阳性 ÷ (真阳性 + 假阳性)。")
    if level["kind"] == "prevalence":
        print("     反问题把公式倒过来解：设患病率为 p，令")
        print("       p·灵敏度 ÷ [p·灵敏度 + (1−p)·(1−特异度)] = 目标值，解出 p。")
        print("     答案会是一个整数百分比。")


def play():
    print(__doc__.split("【中文说明】")[0].strip())
    print("输入答案（百分数）开始；输入 hint 看提示，q 退出。")
    total = 0.0
    for idx, level in enumerate(LEVELS):
        show_level(idx, level)
        target = expected_percent(level)
        penalty = 0
        hinted = False
        while True:
            try:
                cmd = input("  你的答案 > ").strip()
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
            try:
                ans = parse_answer(cmd)
            except ValueError:
                print("  请输入数字（例如 8.3），或 hint / q。")
                continue

            if abs(ans - target) <= TOL:
                score = max(FLOOR, PER_LEVEL - penalty)
                total += score
                print(f"  ✅ 正确！标准答案 {fmt_pct(target)}，本关得 {score} 分。")
                if level["kind"] == "prevalence":
                    print(f"     （患病率低于 {fmt_pct(target)} 时，阳性里的人多数是假阳性。）")
                else:
                    p, s, c = level["prevalence"], level["sens"], level["spec"]
                    print(f"     （真阳性 {p * s * 100:.2f}% 人群，假阳性 "
                          f"{(1 - p) * (1 - c) * 100:.2f}% 人群。）")
                break
            penalty += WRONG_COST
            gap = "偏小" if ans < target else "偏大"
            print(f"  ❌ 不对，你给的数{gap}。再算算真阳性与假阳性的比例。")

    print()
    print("═" * 48)
    print(f"结算：{len(LEVELS)}/{len(LEVELS)} 关完成，总分 {min(100, int(total))}/100")
    if total >= 90:
        print("评级：贝叶斯高手 —— 你已经能识破基础率谬误了。")
    elif total >= 60:
        print("评级：入门医师 —— 公式记住了，反问题再练练。")
    else:
        print("评级：实习生 —— 建议重玩一遍，重点体会「罕见病 + 高准确率」的陷阱。")
    print("═" * 48)


if __name__ == "__main__":
    play()
