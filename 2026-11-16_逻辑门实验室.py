# -*- coding: utf-8 -*-
"""
逻辑门实验室 · 用 NAND 造一切
====================================================
数字电路里最神奇的零件是「与非门」（NAND）：它实现 a·b 的反，
而理论上只靠 NAND 就能搭出所有逻辑功能。这个游戏就是让你亲手搭。

语法（写一行表达式，回车提交）：
  A, B, C        输入变量
  not(x)         非
  and(a, b)      与
  or(a, b)       或
  xor(a, b)      异或
  nand(a, b)     与非
  nor(a, b)      或非
可以嵌套，例如：nand(nand(A, B), nand(A, B))

每关给你：
  · 允许使用的门
  · 一张目标真值表（0/1 按输入组合从全 0 递增）
你要写出一个表达式，让它在所有输入组合上都等于目标输出。

计分：每关满分 100。门的个数不超过参考最优 = 100，
每多用 1 个门扣 10 分（最少 30 分）。用 ans 看参考答案 = 0 分。

命令：
  help    语法说明
  table   再看一次目标真值表
  ans     查看参考答案（本题 0 分）
  q       退出

运行：python3 2026-11-16_逻辑门实验室.py
"""

import itertools
import sys

sys.setrecursionlimit(2000)

GATE_ARITY = {
    "not": 1,
    "and": 2,
    "or": 2,
    "xor": 2,
    "nand": 2,
    "nor": 2,
}


# ---------------------------------------------------------------- 语法解析

def tokenize(text):
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch.isspace():
            i += 1
        elif ch.isalnum() or ch == "_":
            j = i
            while j < len(text) and (text[j].isalnum() or text[j] == "_"):
                j += 1
            out.append(("id", text[i:j]))
            i = j
        elif ch in "(),":
            out.append((ch, ch))
            i += 1
        else:
            raise SyntaxError(f"看不懂这个字符：{ch}")
    return out


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self, kind=None):
        tk = self.peek()
        if tk is None:
            raise SyntaxError("表达式还没写完")
        if kind and tk[0] != kind:
            raise SyntaxError(f"这里应该是 {kind}，实际是 {tk[1]}")
        self.pos += 1
        return tk

    def parse(self):
        node = self.expr()
        if self.peek() is not None:
            raise SyntaxError(f"多出来一块：{self.peek()[1]}")
        return node

    def expr(self):
        tk = self.take("id")
        name = tk[1]
        if self.peek() and self.peek()[0] == "(":
            self.take("(")
            args = [self.expr()]
            while self.peek() and self.peek()[0] == ",":
                self.take(",")
                args.append(self.expr())
            self.take(")")
            gname = name.lower()      # 门名大小写不敏感
            if gname not in GATE_ARITY:
                raise SyntaxError(f"没有这种门：{name}（可用：{'、'.join(GATE_ARITY)}）")
            if len(args) != GATE_ARITY[gname]:
                raise SyntaxError(f"{gname} 需要 {GATE_ARITY[gname]} 个输入，你给了 {len(args)} 个")
            return ("call", gname, args)
        return ("var", name)


def parse_text(text):
    return Parser(tokenize(text)).parse()


def gates_used(node):
    if node[0] == "var":
        return set()
    found = {node[1]}
    for arg in node[2]:
        found |= gates_used(arg)
    return found


def gate_count(node):
    if node[0] == "var":
        return 0
    return 1 + sum(gate_count(a) for a in node[2])


def eval_node(node, env):
    if node[0] == "var":
        name = node[1]
        if name not in env:
            raise SyntaxError(f"没有这个输入变量：{name}")
        return env[name]
    _, name, args = node
    if name not in GATE_ARITY:
        raise SyntaxError(f"没有这种门：{name}")
    if len(args) != GATE_ARITY[name]:
        raise SyntaxError(f"{name} 需要 {GATE_ARITY[name]} 个输入，你给了 {len(args)} 个")
    vals = [eval_node(a, env) for a in args]
    return apply_gate(name, vals)


def apply_gate(name, vals):
    if name == "not":
        return not vals[0]
    if name == "and":
        return vals[0] and vals[1]
    if name == "or":
        return vals[0] or vals[1]
    if name == "xor":
        return vals[0] != vals[1]
    if name == "nand":
        return not (vals[0] and vals[1])
    if name == "nor":
        return not (vals[0] or vals[1])
    raise ValueError(name)


# ---------------------------------------------------------------- 关卡

LEVELS = [
    {
        "inputs": ["A"],
        "allowed": ["nand"],
        "desc": "目标：非门（NOT A）。只给你一个与非门。",
        "optimal": 1,
        "ref": "nand(A, A)",
        "why": "把两个输入都接 A：A NAND A = NOT (A AND A) = NOT A。",
    },
    {
        "inputs": ["A", "B"],
        "allowed": ["nand"],
        "desc": "目标：与门（A AND B）。仍然只能用与非门。",
        "optimal": 3,
        "ref": "nand(nand(A, B), nand(A, B))",
        "why": "先 NAND 得到反值，再把结果接到一个与非门的两个输入上，反两次就回到 AND。",
    },
    {
        "inputs": ["A", "B"],
        "allowed": ["nand"],
        "desc": "目标：或门（A OR B）。还是只有与非门。",
        "optimal": 3,
        "ref": "nand(nand(A, A), nand(B, B))",
        "why": "德摩根律：A OR B = NOT(NOT A AND NOT B)，而每个 NOT 都是一个 NAND 门自己接自己。",
    },
    {
        "inputs": ["A", "B"],
        "allowed": ["nand"],
        "desc": "目标：异或门（A XOR B）——这是只靠 NAND 搭门里最经典的一道。",
        "optimal": 5,
        "ref": "nand(nand(A, nand(A, B)), nand(B, nand(A, B)))",
        "why": "记 N = nand(A,B)，则 nand(A,N) 与 nand(B,N) 再做一次 NAND 就是 A XOR B。"
               "注意表达式写法没法共享中间结果，所以 N 会算两次，共 5 个门。",
    },
    {
        "inputs": ["A", "B", "C"],
        "allowed": ["and", "or", "not"],
        "desc": "目标：三输入多数表决——A、B、C 中至少两个为 1 时输出 1。",
        "optimal": 5,
        "ref": "or(or(and(A, B), and(A, C)), and(B, C))",
        "why": "「至少两个为真」= 任意一对为真，也就是三组两两 AND 再全部 OR 起来。",
    },
]


def truth_table(inputs, fn):
    rows = []
    for combo in itertools.product([False, True], repeat=len(inputs)):
        env = dict(zip(inputs, combo))
        rows.append((combo, fn(env)))
    return rows


def make_fn(node):
    return lambda env: eval_node(node, env)


TARGET_TABLES = {
    # 输出序列按输入组合从全 0 递增排列：000,001,010,...
    0: "10",          # NOT A
    1: "0001",        # A AND B
    2: "0111",        # A OR B
    3: "0110",        # A XOR B
    4: "00010111",    # 多数表决（ABC）
}


def level_target(level):
    return TARGET_TABLES[LEVELS.index(level)]


def show_truth(level, expected):
    inp = level["inputs"]
    print(f"\n  目标真值表（{', '.join(inp)} → 输出）：")
    print("  " + "  ".join(inp) + "  | 输出")
    print("  " + "-" * (len(inp) * 3 + 5))
    for i, combo in enumerate(itertools.product([0, 1], repeat=len(inp))):
        print("  " + "  ".join(str(c) for c in combo) + f"  |  {expected[i]}")
    print(f"  （连起来写就是 {expected}）")


def run_level(idx):
    level = LEVELS[idx]
    expected = level_target(level)
    print("\n" + "=" * 62)
    print(f"  第 {idx + 1} 关 / 共 {len(LEVELS)} 关")
    print("=" * 62)
    print("  " + level["desc"])
    print("  可用门：" + "、".join(level["allowed"]))
    show_truth(level, expected)

    score = 100
    tries = 0
    while True:
        try:
            raw = input("\n  表达式 > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return 0, False
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit"):
            return score, None
        if low == "help":
            print("  语法：变量 A/B/C，门用函数写法，如 and(A, B)、not(x)、nand(A, B)，可嵌套。")
            continue
        if low == "table":
            show_truth(level, expected)
            continue
        if low == "ans":
            if score > 0:
                score = 0
            print(f"  参考答案：{level['ref']}")
            print(f"  原理：{level['why']}")
            continue

        try:
            node = parse_text(raw)
        except SyntaxError as exc:
            print(f"  ⚠ 语法问题：{exc}")
            continue

        used = gates_used(node)
        bad = [g for g in used if g not in level["allowed"]]
        if bad:
            print(f"  ⚠ 本关不能使用这些门：{'、'.join(bad)}")
            continue

        try:
            rows = truth_table(level["inputs"], make_fn(node))
        except SyntaxError as exc:
            print(f"  ⚠ 求值失败：{exc}")
            continue

        got = "".join("1" if v else "0" for _, v in rows)
        if got == expected:
            gates = gate_count(node)
            base = 100 - max(0, gates - level["optimal"]) * 10
            final = max(30, base)
            if score == 0:
                final = 0
            print(f"  ✅ 真值表完全匹配！用了 {gates} 个门，参考最优 {level['optimal']} 个。本关 {final} 分。")
            if gates > level["optimal"]:
                print(f"  （还能再省 {gates - level['optimal']} 个门，比如：{level['ref']}）")
            return final, True

        print(f"  ❌ 不匹配：你得到 {got}，目标 {expected}")
        # 指出第一处不一致，方便调试
        for i, (combo, v) in enumerate(rows):
            if ("1" if v else "0") != expected[i]:
                print(f"     在第一处不符：{', '.join(f'{n}={int(c)}' for n, c in zip(level['inputs'], combo))} "
                      f"时你输出 {int(v)}，应为 {expected[i]}")
                break
        tries += 1
        if tries == 2 and score > 30:
            score = 70
            print("  （已经错两次，本关最高 70 分；可以输入 ans 看参考答案，但会归零）")
        continue


def play():
    print("=" * 62)
    print("      🔌 逻辑门实验室 · 用 NAND 造一切")
    print("=" * 62)
    print("写一个逻辑表达式，让它的真值表与目标完全一致。输入 help 看语法。")
    total = 0
    done = 0
    for i in range(len(LEVELS)):
        sc, ok = run_level(i)
        total += sc
        if ok is None:
            break
        done += 1

    print("\n" + "=" * 62)
    print(f"  结算：{done}/{len(LEVELS)} 关通过，总分 {total}/{len(LEVELS) * 100}")
    if total >= 450:
        print("  🏆 德摩根律 + 双重否定，你已经能徒手搭门电路了。")
    elif total >= 250:
        print("  👍 记住这两条：反两次回到原值；NOT A AND NOT B = NOT(A OR B)。")
    else:
        print("  🙂 起手式：nand(x, x) 就是非门，其他全靠它组合。")
    print("=" * 62)


if __name__ == "__main__":
    play()
