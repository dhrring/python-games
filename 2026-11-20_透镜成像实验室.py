# -*- coding: utf-8 -*-
"""
透镜成像实验室 · Thin Lens
====================================================
一块凸透镜，焦距 f。把物体放在距透镜 u 的地方，像会出现在距透镜 v 的地方：

    1/u + 1/v = 1/f　　　　→　　　v = u·f / (u - f)
    放大率 m = |v / u|　　（m > 1 放大，m = 1 等大，m < 1 缩小）

符号约定（本游戏用这一套）：
  · 实物在透镜左侧，u 取正值
  · 实像在右侧，v 取正值；虚像和物在同一侧，v 取**负值**
  · 当 u = f 时出射光平行，不成像

五种结局，全看你把物放在哪儿：
  u > 2f   → 倒立、缩小、实像
  u = 2f   → 倒立、等大、实像
  f < u < 2f → 倒立、放大、实像
  u = f    → 不成像（出射光平行，屏上永远模糊）
  u < f    → 正立、放大、虚像（放大镜就是这么用的）

玩法：每关给出 f 和 u，你先选像的性质（看下面的编号），再报像距 v（单位 cm，保留 1 位小数）。
  hint  变形公式与判断口诀（−10 分）
  q     退出
5 关，每关满分 20，答错一次扣 8 分（最低保 4 分），总分 100。

运行：python3 2026-11-20_透镜成像实验室.py
"""

KINDS = {
    1: "倒立缩小实像",
    2: "倒立等大实像",
    3: "倒立放大实像",
    4: "正立放大虚像",
    5: "不成像（出射光平行）",
}

LEVELS = [
    {"f": 10, "u": 30, "kind": 1, "note": "物体在 2 倍焦距以外（30 cm > 20 cm）。"},
    {"f": 10, "u": 20, "kind": 2, "note": "物体正好在 2 倍焦距处（20 cm = 2f）。"},
    {"f": 10, "u": 15, "kind": 3, "note": "物体在 f 与 2f 之间（10 < 15 < 20）。"},
    {"f": 10, "u": 6, "kind": 4, "note": "物体在焦点以内（6 cm < 10 cm），放大镜的用法。"},
    {"f": 8, "u": 8, "kind": 5, "note": "物体正好压在焦点上（8 cm = f）。这是一道陷阱题。"},
]


def image_distance(f, u):
    """薄透镜公式求像距；u == f 时返回 None（不成像）。"""
    if abs(u - f) < 1e-12:
        return None
    return u * f / (u - f)


def kind_of(f, u):
    """按物距判断像的性质。"""
    if abs(u - f) < 1e-12:
        return 5
    if u > 2 * f:
        return 1
    if abs(u - 2 * f) < 1e-12:
        return 2
    if u > f:
        return 3
    return 4


def hint_text():
    print("  公式：1/u + 1/v = 1/f，所以 v = u·f / (u - f)；放大率 m = |v/u|。")
    print("  口诀：一倍焦距分虚实（u > f 实像，u < f 虚像），")
    print("        二倍焦距分大小（u > 2f 缩小，u = 2f 等大，u < 2f 放大）。")
    print("  虚像的 v 要写成负数（像和物在透镜同一侧）。")


def run_level(idx, lv):
    f, u = lv["f"], lv["u"]
    v = image_distance(f, u)

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关　f = {f} cm，u = {u} cm")
    print("=" * 62)
    print("  " + lv["note"])
    print("  像的性质编号：")
    for k, name in KINDS.items():
        print(f"    {k}. {name}")

    score = 20
    # 第一步：判断像的性质
    while True:
        try:
            raw = input("\n  ① 像的性质（输入编号 1~5 / hint / q）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return 0, None
        if low == "hint":
            score = max(4, score - 10)
            hint_text()
            print(f"  （本关上限 {score} 分）")
            continue
        if not raw.isdigit() or not (1 <= int(raw) <= 5):
            print("  请输入 1 到 5 之间的编号。")
            continue
        pick = int(raw)
        if pick == lv["kind"]:
            print(f"  ✅ {KINDS[pick]}，判断正确。")
            break
        score = max(4, score - 8)
        print(f"  ❌ 不对。用口诀想一想：u = {u} cm 与 f = {f} cm、2f = {2 * f} cm 比，谁大谁小？"
              f"（本关上限 {score} 分）")

    # 第二步：报像距（不成像的关卡跳过）
    if lv["kind"] == 5:
        print(f"  像距：出射光平行，像在无穷远 —— 本关 {score} 分。")
        return score, True

    while True:
        try:
            raw = input("  ② 像距 v = ?（cm，保留 1 位小数，虚像写负数）> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return score, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "hint":
            score = max(4, score - 10)
            hint_text()
            print(f"  （本关上限 {score} 分）")
            continue
        try:
            got = float(raw)
        except ValueError:
            print("  请输入一个数字，例如 15.0 或 -15.0。")
            continue

        if abs(got - v) <= 0.15:
            m = abs(v / u)
            print(f"  ✅ 正确！v = {v:.1f} cm，放大率 m = |v/u| = {m:.2f}"
                  + ("（m < 1，缩小）" if m < 1 - 1e-9 else "（m = 1，等大）" if abs(m - 1) < 1e-9 else "（m > 1，放大）"))
            if v < 0:
                print("     负号表示像和物在透镜同一侧 —— 这是虚像，光屏接不到，眼睛能看到。")
            print(f"  本关 {score} 分。")
            return score, True

        score = max(4, score - 8)
        print(f"  ❌ {got:.1f} 不对。代公式：v = u·f/(u-f) = {u}×{f}/({u}-{f}) = {u * f}/{u - f}。"
              f"（本关上限 {score} 分）")


def play():
    print("=" * 62)
    print("      🔍 透镜成像实验室 · Thin Lens")
    print("=" * 62)
    print("一块凸透镜，物距 u、焦距 f，推出像距 v 和像的性质。")

    # 开局自检：公式、像距、性质、放大率四者必须自洽
    for lv in LEVELS:
        f, u = lv["f"], lv["u"]
        assert kind_of(f, u) == lv["kind"], f"性质判断错：f={f},u={u}"
        v = image_distance(f, u)
        if v is None:
            assert lv["kind"] == 5, "只有 u = f 才允许不成像"
            continue
        assert lv["kind"] != 5
        assert abs(1 / u + 1 / v - 1 / f) < 1e-9, f"成像公式不成立：f={f},u={u},v={v}"
        m = abs(v / u)
        if lv["kind"] == 1:
            assert v > 0 and m < 1, f"应为缩小实像，实得 v={v:.2f}, m={m:.2f}"
        elif lv["kind"] == 2:
            assert v > 0 and abs(m - 1) < 1e-9, f"应为等大实像，实得 m={m:.2f}"
        elif lv["kind"] == 3:
            assert v > 0 and m > 1, f"应为放大实像，实得 v={v:.2f}, m={m:.2f}"
        elif lv["kind"] == 4:
            assert v < 0 and m > 1, f"应为放大虚像，实得 v={v:.2f}, m={m:.2f}"
    kinds_used = {lv["kind"] for lv in LEVELS}
    assert kinds_used == {1, 2, 3, 4, 5}, f"五关没有覆盖全部五种结局：{kinds_used}"
    print("  自检：五关的 1/u+1/v=1/f 全部成立，五种结局各出现一次，虚像符号为负。")

    total = 0
    done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 20}")
    if total >= 90:
        print("  🏆 一倍焦距分虚实、二倍焦距分大小 —— 你已经把薄透镜公式用顺手了。")
    elif total >= 55:
        print("  👍 记住 v = u·f/(u-f)，以及虚像必须写负号。")
    else:
        print("  🙂 先固定 f=10，把 u 从 40 慢慢减到 5，看看像距怎么变、什么时候翻成虚像。")
    print("=" * 62)


if __name__ == "__main__":
    play()
