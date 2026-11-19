# -*- coding: utf-8 -*-
"""
天平称重 · 假币谜题
====================================================
一袋金币里混进了 1 枚假币：外观一模一样，重量偏了一点（重或轻）。
你有一台只能比较「左盘 vs 右盘」的天平（没有砝码，不会给出具体克数），
要在限定的次数内找出那枚假币。

关键不是运气，而是**三分法**：
  天平每次只有三种结果——左重、右重、平衡。
  一次称重最多把可能性切成 3 份，所以 3 次称重最多分辨 3³ = 27 种情况。
  于是：9 枚 → 一次能缩到 3 枚 → 再缩到 1 枚；27 枚正好 3 次搞定。

玩法：
  1 2 3 vs 4 5 6    把 1、2、3 号放左盘，4、5、6 号放右盘（两边必须一样多）
  guess 7           指认 7 号是假币
  coins             列出所有金币编号
  hint              提示本关该用几堆分法（−30 分）
  q                 退出
  每次称重的结果会直接告诉你：左重 / 右重 / 平衡。

运行：python3 2026-11-19_天平称重.py
"""

import math
import random

LEVELS = [
    {"coins": 9, "kind": "重", "tries": 3,
     "note": "9 枚金币，假币比真币**重**。3 次称重——分 3 堆，3-3-3 是天然答案。"},
    {"coins": 12, "kind": "重", "tries": 3,
     "note": "12 枚金币，假币偏**重**。3 次称重依然够（3³=27 ≥ 12）。"},
    {"coins": 25, "kind": "轻", "tries": 3,
     "note": "25 枚金币，假币比真币**轻**。3 次称重刚好够（27 ≥ 25），试试 9-9-7。"},
]


def weigh(left, right, fake, kind):
    """模拟天平：真币重 1，假币重 1.2（偏重）或 0.8（偏轻）。"""
    def total(side):
        s = 0.0
        for c in side:
            s += 0.8 if (c == fake and kind == "轻") else (1.2 if c == fake else 1.0)
        return s
    l, r = total(left), total(right)
    if abs(l - r) < 1e-9:
        return "平衡"
    return "左重" if l > r else "右重"


def parse_weighing(raw, n):
    low = raw.replace("VS", "vs").replace("vs", " vs ")
    if "vs" not in low:
        if "|" in raw:
            low = raw.replace("|", " vs ")
        elif ":" in raw:
            low = raw.replace(":", " vs ")
        else:
            raise ValueError("格式是：左盘号 vs 右盘号，例如 1 2 3 vs 4 5 6")
    a, b = low.split(" vs ", 1)
    def to_nums(s):
        toks = s.replace(",", " ").split()
        out = []
        for t in toks:
            if not t.isdigit():
                raise ValueError(f"金币编号必须是数字：{t}")
            out.append(int(t))
        return out
    left, right = to_nums(a), to_nums(b)
    if not left or not right:
        raise ValueError("两边都要放金币")
    if len(left) != len(right):
        raise ValueError(f"两边数量必须相同（现在左边 {len(left)} 枚，右边 {len(right)} 枚）")
    for c in left + right:
        if not (1 <= c <= n):
            raise ValueError(f"编号只能在 1 到 {n} 之间")
    if set(left) & set(right):
        raise ValueError("同一枚金币不能同时出现在两边")
    if len(set(left)) != len(left) or len(set(right)) != len(right):
        raise ValueError("同一枚金币不能重复放")
    return left, right


def ref_identify(n, fake, kind, max_tries):
    """参考策略（三分法）：返回 (用了多少次, 找到的编号)，用于自检可解性。"""
    cands = list(range(1, n + 1))
    for t in range(1, max_tries + 1):
        if len(cands) == 1:
            return t - 1, cands[0]
        k = math.ceil(len(cands) / 3)
        a, b = cands[:k], cands[k:2 * k]   # 两堆等长，第三堆可能略少
        res = weigh(a, b, fake, kind)
        if res == "平衡":
            cands = [c for c in cands if c not in a and c not in b]
        elif res == "左重":
            cands = a if kind == "重" else b
        else:
            cands = b if kind == "重" else a
    return max_tries, cands[0] if len(cands) == 1 else None


def run_level(idx, level):
    n = level["coins"]
    kind = level["kind"]
    tries = level["tries"]
    fake = random.randint(1, n)

    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关 · {n} 枚金币（假币偏{kind}）")
    print("=" * 62)
    print("  " + level["note"])
    print(f"  你最多有 {tries} 次称重机会。金币编号 1 到 {n}。")

    used = 0
    penalty = 0
    while True:
        if used >= tries:
            print(f"\n  ⏳ 称重机会用完了（{tries} 次）。")
            try:
                raw = input("  最后指认一枚（guess 编号），或 q 放弃 > ").strip()
            except EOFError:
                print("\n输入中断。")
                return 0, None
            low = raw.lower()
            if low in ("q", "quit"):
                print(f"  本关没找到，假币其实是 {fake} 号。")
                return 0, True
            if low.startswith("guess"):
                ans = raw.split()[-1]
                if ans.isdigit() and int(ans) == fake:
                    print(f"  ✅ 就是 {fake} 号！不过超了次数，本关 {max(20, 60 - penalty)} 分。")
                    return max(20, 60 - penalty), True
                print(f"  ❌ 不是它。假币其实是 {fake} 号。本关 20 分。")
                return 20, True
            print("  请输入 guess 编号。")
            continue

        try:
            raw = input(f"\n  第 {used + 1}/{tries} 次 · 怎么称？> ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, None
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return 0, None
        if low == "coins":
            print("  金币编号：" + " ".join(str(c) for c in range(1, n + 1)))
            continue
        if low == "hint":
            penalty = 30
            print("  提示：把候选金币尽量**三等分**，称其中两堆。"
                  "天平只有三种结果，一次称重最多把可能性缩成三分之一。")
            continue

        if low.startswith("guess"):
            parts = raw.split()
            if len(parts) != 2 or not parts[1].isdigit():
                print("  用法：guess 7")
                continue
            g = int(parts[1])
            if not (1 <= g <= n):
                print(f"  编号只能在 1 到 {n} 之间。")
                continue
            if g == fake:
                score = max(20, 100 - penalty - max(0, used - 1) * 10)
                print(f"  ✅ 找对了！{g} 号就是那枚偏{kind}的假币。用了 {used} 次称重，本关 {score} 分。")
                return score, True
            print(f"  ❌ {g} 号是真币。再想想（还可以继续称重）。")
            penalty += 10
            continue

        try:
            left, right = parse_weighing(raw, n)
        except ValueError as msg:
            print(f"  {msg}")
            continue

        res = weigh(left, right, fake, kind)
        used += 1
        print(f"  ⚖ 左盘 {left}　右盘 {right}　→　【{res}】")
        if res == "平衡":
            print("     说明假币不在这两堆里。")
        else:
            print(f"     说明假币在这两堆里（偏{kind}的那一边藏着它）。")


def play():
    print("=" * 62)
    print("      ⚖ 天平称重 · 假币谜题")
    print("=" * 62)
    print("一台只能比较左右轻重的天平，找出那一枚重量不对的金币。")

    # 开局自检：三分法参考策略必须对所有可能的假币位置都在限定次数内定位
    for i, lv in enumerate(LEVELS, 1):
        n, kind, tries = lv["coins"], lv["kind"], lv["tries"]
        assert 3 ** tries >= n, f"第 {i} 关信息量不足：3^{tries}={3 ** tries} < {n}"
        for fake in range(1, n + 1):
            t, found = ref_identify(n, fake, kind, tries)
            assert found == fake and t <= tries, f"第 {i} 关假币 {fake} 号参考策略失败（{t} 次, 得到 {found}）"
        # 称重函数自检：平衡 / 左重 / 右重 三种结果都要能出现且方向正确
        assert weigh([1, 2], [3, 4], 5, "重") == "平衡"
        assert weigh([1, 2], [3, 4], 1, "重") == "左重"
        assert weigh([1, 2], [3, 4], 3, "重") == "右重"
        assert weigh([1, 2], [3, 4], 1, "轻") == "右重"

    total = done = 0
    for i, lv in enumerate(LEVELS):
        sc, finished = run_level(i, lv)
        total += sc
        if finished is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关完成，总分 {total}/{len(LEVELS) * 100}")
    if total >= 250:
        print("  🏆 三分法已经刻进你的直觉里了：每次把候选砍到三分之一。")
    elif total >= 100:
        print("  👍 记住「3 次称重最多分辨 27 种情况」这条信息量上限。")
    else:
        print("  🙂 先数候选，再三等分；两边数量一定要相同。")
    print("=" * 62)


if __name__ == "__main__":
    play()
