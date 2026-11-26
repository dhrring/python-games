#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRC 校验码实验室（终端交互小游戏）

【CRC 是什么】
发送方在信息位后面补上一段「校验码」，让整段数据（信息位 + 校验码）能被
给定的生成多项式整除。接收方收到后重新做一次除法，余数为 0 就认为传输没出错。
这里用的是最朴素的「二进制模 2 长除法」：异或代替减法，不产生借位。

【玩法】
共 5 关，每关两个小问（各 10 分，满分 100）：
  A. 给你信息位 M 和生成多项式 G（二进制），求校验码 R（余数）；
  B. 给你一段实际收到的数据（可能是干净的，也可能被改过一位），
     判断它能否通过校验（通过 / 失败）。

【命令】
  hint / h / 提示 / ?  ：思路提示（每题第一次用扣 10 分）
  q / quit / exit / 退出 ：退出
  直接回车            ：重看题目
  Ctrl+C / Ctrl+D     ：安全退出

【运行】
  python3 2026-11-26_CRC校验码实验室.py
  python3 2026-11-26_CRC校验码实验室.py --check   # 自检（不进入游戏）
"""

import sys

# msg=信息位，poly=生成多项式（二进制，最高位必为 1），flip=接收串故意翻转的位下标（None 表示没被改）
LEVELS = [
    {"msg": "1001", "poly": "1011", "flip": None},
    {"msg": "1011", "poly": "1101", "flip": 3},
    {"msg": "11011", "poly": "10011", "flip": None},
    {"msg": "1010110", "poly": "10011", "flip": 2},
    {"msg": "1011010", "poly": "1101", "flip": 0},
]

MAX_TRY = 3
WRONG_PENALTY = 3
HINT_PENALTY = 10
POINTS = 10

QUIT_WORDS = {"q", "quit", "exit", "退出"}
HINT_WORDS = {"hint", "h", "提示", "?"}
PASS_WORDS = {"通过", "y", "yes", "是", "1", "pass", "p", "对", "ok"}
FAIL_WORDS = {"失败", "n", "no", "否", "0", "fail", "f", "错", "不过"}


def crc_div(bits, poly):
    """二进制模 2 长除法，返回余数（长度 = len(poly)-1，左补 0）。"""
    b = list(bits)
    n = len(poly)
    for i in range(len(b) - n + 1):
        if b[i] == "1":
            for j in range(n):
                b[i + j] = "1" if b[i + j] != poly[j] else "0"
    w = n - 1
    return "".join(b[len(b) - w:]) if w else ""


def crc_register(bits, poly):
    """另一种实现：移位寄存器（逐位异或），用于交叉验证。"""
    w = len(poly) - 1
    if w == 0:
        return ""
    mask = (1 << w) - 1
    tap = int(poly[1:], 2)
    reg = 0
    for ch in bits:
        top = (reg >> (w - 1)) & 1          # 先记下即将被移出的最高位
        reg = ((reg << 1) | int(ch)) & mask  # 把新的一位塞进最低位
        if top:                              # 移出的是 1 就做一次异或“减法”
            reg ^= tap
    return format(reg, "0{}b".format(w))


def remainder(msg, poly):
    """M 后面补 (len(poly)-1) 个 0 再做除法，得到的余数就是校验码。"""
    return crc_div(msg + "0" * (len(poly) - 1), poly)


def transmitted(level):
    """接收端实际收到的比特串：信息位 + 校验码（按 flip 可能被改一位）。"""
    msg, poly = level["msg"], level["poly"]
    tx = msg + remainder(msg, poly)
    if level["flip"] is not None:
        i = level["flip"]
        tx = tx[:i] + ("1" if tx[i] == "0" else "0") + tx[i + 1:]
    return tx


def passes(bits, poly):
    """整段数据对多项式做除法，余数为全 0 即通过校验。"""
    return crc_div(bits, poly).count("1") == 0


def ask(prompt):
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def ask_text(prompt, attempts, hint_text):
    """返回 (输入, 剩余次数)；特殊值 "QUIT"/"EOF"/"HINT"/None（次数用尽）。"""
    tries = attempts
    while tries > 0:
        raw = ask("{}（余 {} 次）> ".format(prompt, tries))
        if raw is None:
            return "EOF", 0
        if raw in QUIT_WORDS:
            return "QUIT", 0
        if raw == "":
            continue
        if raw in HINT_WORDS:
            print(hint_text)
            return "HINT", tries
        return raw, tries - 1
    return None, 0


def play():
    print("=" * 52)
    print("      CRC 校验码实验室 · 5 关满分 100")
    print("=" * 52)
    print("规则：把信息位后面补 (G 长度-1) 个 0，与 G 做模 2 长除法，")
    print("      余数就是校验码；整段数据再除一次，余数为 0 则校验通过。")
    print("命令：hint 提示 ｜ q 退出 ｜ 回车 重看题目")
    print()

    total = 0
    for idx, lv in enumerate(LEVELS, 1):
        msg, poly = lv["msg"], lv["poly"]
        w = len(poly) - 1
        ans_r = remainder(msg, poly)
        tx = transmitted(lv)
        ans_pass = passes(tx, poly)
        used = [False, False]

        # 问 A：求校验码
        attempts = MAX_TRY
        got_a = False
        while not got_a:
            print(f"—— 第 {idx} 关 · A ——")
            print(f"信息位 M = {msg}    生成多项式 G = {poly}（{len(poly)} 位，生成 {w} 位校验码）")
            print(f"求校验码 R（{w} 位二进制）：")
            v, attempts = ask_text(
                "R = ?", attempts,
                "  提示：把 M 后面补 {} 个 0，从左往右看：只要当前最高位是 1，\n"
                "        就用这 {} 位与 G 按位异或（相当于长除法的减法），最后留下低 {} 位。".format(w, len(poly), w),
            )
            if v == "QUIT":
                print("\n已退出。")
                return
            if v == "EOF":
                print("输入已结束，游戏退出。")
                return
            if v is None:
                print(f"  ✗ 次数用完，本问记 0 分。正确答案：{ans_r}")
                break
            if v == "HINT":
                if not used[0]:
                    used[0] = True
                    print("  （提示已用，本问 -10 分）")
                continue
            cand = v.replace("0b", "").replace(" ", "")
            if cand.isdigit() and set(cand) <= {"0", "1"} and len(cand) == w:
                if cand == ans_r:
                    got_a = True
                    pts = max(0, POINTS - (HINT_PENALTY if used[0] else 0))
                    total += pts
                    print(f"  ✓ 正确！校验码 R = {ans_r}（本问 +{pts} 分）")
                else:
                    print(f"  ✗ 不对（你算的是 {cand}）。检查每一次异或有没有对齐。")
            elif cand.isdigit() and set(cand) <= {"0", "1"} and len(cand) < w:
                print(f"  ✗ 位数不够，应该是 {w} 位（前面的 0 也要写出来）。")
            else:
                print("  ✗ 请输入纯 0/1 的二进制串。")

        # 问 B：判断接收串能否通过校验
        attempts = MAX_TRY
        while got_a:
            print(f"—— 第 {idx} 关 · B ——")
            print(f"接收到的数据 = {tx}（共 {len(tx)} 位），生成多项式 G = {poly}")
            print("这段数据能通过 CRC 校验吗？（输入 通过 / 失败）")
            v, attempts = ask_text(
                "你的判断", attempts,
                "  提示：把整段数据（不用再补 0）直接与 G 做长除法，看最后 {} 位余数是否全为 0。".format(w),
            )
            if v == "QUIT":
                print("\n已退出。")
                return
            if v == "EOF":
                print("输入已结束，游戏退出。")
                return
            if v is None:
                print(f"  ✗ 次数用完，本问记 0 分。正确答案：{'通过' if ans_pass else '失败'}")
                break
            if v == "HINT":
                if not used[1]:
                    used[1] = True
                    print("  （提示已用，本问 -10 分）")
                continue
            if v in PASS_WORDS or v in FAIL_WORDS:
                guess_pass = v in PASS_WORDS
                if guess_pass == ans_pass:
                    pts = max(0, POINTS - (HINT_PENALTY if used[1] else 0))
                    total += pts
                    print(f"  ✓ 正确！（本问 +{pts} 分）余数为 {crc_div(tx, poly)}。")
                    break
                print("  ✗ 不对。再算一次余数，别凭感觉。")
            else:
                print("  ✗ 请输入「通过」或「失败」。")

        print(f"  本关：R = {ans_r}，接收串余数 = {crc_div(tx, poly)}，"
              f"结论 = {'通过' if ans_pass else '失败'}")
        print(f"  当前总分：{total}\n")

    print("=" * 52)
    print(f"最终得分：{total} / 100")
    if total >= 90:
        print("评级：S —— 长除法手算稳准狠，CRC 的门算是进去了。")
    elif total >= 70:
        print("评级：A —— 思路清楚，偶尔在异或对齐上会滑一下。")
    elif total >= 50:
        print("评级：B —— 会用，但建议拿纸笔把第 1 关重走一遍。")
    else:
        print("评级：C —— 记住口诀：左端是 1 就异或，是 0 就跳过，退一位继续。")
    print("=" * 52)


def check():
    ok = True

    # 1) 长除法 vs 移位寄存器（两种独立实现）逐关一致
    for idx, lv in enumerate(LEVELS, 1):
        msg, poly = lv["msg"], lv["poly"]
        w = len(poly) - 1
        a = remainder(msg, poly)
        b = crc_register(msg + "0" * w, poly)
        if a != b:
            ok = False
            print(f"✗ 第 {idx} 关两种实现不一致：{a} vs {b}")
        if poly[0] != "1" or poly[-1] != "1":
            ok = False
            print(f"✗ 第 {idx} 关多项式首/末位必须为 1：{poly}")
        if not set(poly) <= {"0", "1"}:
            ok = False
            print(f"✗ 第 {idx} 关多项式含非二进制字符")
        if len(a) != w:
            ok = False
            print(f"✗ 第 {idx} 关余数长度应为 {w}，实际 {len(a)}")
        print(f"  第{idx}关 M={msg} G={poly} → R={a}，接收串余数={crc_div(transmitted(lv), poly)}，"
              f"{'通过' if passes(transmitted(lv), poly) else '失败'}")

    # 2) 附加校验码后整体余数必须为 0（无翻转关卡）
    for idx, lv in enumerate(LEVELS, 1):
        if lv["flip"] is None:
            clean = lv["msg"] + remainder(lv["msg"], lv["poly"])
            if not passes(clean, lv["poly"]):
                ok = False
                print(f"✗ 第 {idx} 关干净接收串未通过校验")
        else:
            tx = transmitted(lv)
            if passes(tx, lv["poly"]):
                ok = False
                print(f"✗ 第 {idx} 关翻转 {lv['flip']} 位后仍被判通过（题目失效）")
            if tx == lv["msg"] + remainder(lv["msg"], lv["poly"]):
                ok = False
                print(f"✗ 第 {idx} 关翻转未真正改变接收串")

    # 3) 判定结果必须两种都有，避免全是同一答案
    kinds = {passes(transmitted(lv), lv["poly"]) for lv in LEVELS}
    if len(kinds) != 2:
        ok = False
        print("✗ 5 关的校验判定结果应同时包含「通过」和「失败」")

    # 4) 边界用例
    edge = [("1011", "1011"), ("1", "101"), ("0", "1011"), ("1111111", "11")]
    for msg, poly in edge:
        w = len(poly) - 1
        if w == 0:
            continue
        r = remainder(msg, poly)
        if len(r) != w or r != crc_register(msg + "0" * w, poly):
            ok = False
            print(f"✗ 边界用例失败：M={msg} G={poly}")
        if r.count("1") and not passes(msg + r, poly):
            ok = False
            print(f"✗ 边界用例附加后余数非 0：M={msg} G={poly}")

    # 5) 满分
    if 5 * 2 * POINTS != 100:
        ok = False
        print("✗ 满分不是 100")

    print("自检通过 ✅" if ok else "自检失败 ❌")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("--check", "-c", "check"):
        return check()
    try:
        play()
    except (BrokenPipeError, KeyboardInterrupt):
        try:
            sys.stdout.close()
        except Exception:
            pass
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
