# -*- coding: utf-8 -*-
"""
ASCII 分形画廊 · 自相似之美
====================================================
分形是一类「放大之后还是自己」的图形。这里用纯字符在终端里画出三种经典分形：

  sierpinski  谢尔宾斯基三角 —— 用「杨辉三角取奇偶」画出来，每层由上一层的三角形一分为三
  mandelbrot  曼德勃罗集       —— 复平面上不断做 z = z² + c，逃逸快的点画成暗色
  tree        分形树           —— 每次分枝都长成两个更短的分枝，层层递归

玩法：
  1）画廊模式：随时输入名字和参数，看看分形长什么样；
        例：sierpinski 5    （谢尔宾斯基三角，5 层）
            mandelbrot 40   （曼德勃罗集，40 次迭代上限）
            tree 6          （分形树，6 层）
  2）参数推理：画廊里看够了，做 3 道推理题，考的是分形的「数量规律」。

命令：
  help    看说明
  q       退出

计分：每道推理题 100 分（答错 0 分），共 3 题。
运行：python3 2026-11-15_分形画廊.py
"""

import math

# ---------------------------------------------------------------- 谢尔宾斯基


def sierpinski(layers):
    """杨辉三角第 i 行、第 j 个数的奇偶，正好构成谢尔宾斯基三角。"""
    rows = 1 << layers
    lines = []
    for i in range(rows):
        c = 1
        buf = []
        for j in range(i + 1):
            buf.append("█" if c % 2 else " ")
            c = c * (i - j) // (j + 1)
        # 右侧补空格让整体居中
        pad = " " * (rows - i - 1)
        lines.append(pad + "".join(buf))
    return lines


def count_solid(lines):
    return sum(line.count("█") for line in lines)


# ---------------------------------------------------------------- 曼德勃罗集

RAMP = " .:-=+*#%@"


def mandelbrot(iters, width=70, height=26):
    lines = []
    for row in range(height):
        y = (row / (height - 1)) * 2.4 - 1.2      # 虚部，从 -1.2 到 1.2
        line = []
        for col in range(width):
            x = (col / (width - 1)) * 3.0 - 2.1   # 实部，从 -2.1 到 0.9
            zr, zi = 0.0, 0.0
            k = 0
            while k < iters and zr * zr + zi * zi <= 4.0:
                zr, zi = zr * zr - zi * zi + x, 2 * zr * zi + y
                k += 1
            line.append(RAMP[k % len(RAMP)] if k < iters else RAMP[-1])
        lines.append("".join(line))
    return lines


# ---------------------------------------------------------------- 分形树

GRID_W, GRID_H = 81, 26


def tree(depth):
    """从底部中央向上生长的一棵树，每层分成左右两枝，长度按 0.68 缩短。"""
    grid = [[" "] * GRID_W for _ in range(GRID_H)]
    tips = [0]

    def draw(x, y, angle, length, level):
        if length < 1.4 or level <= 0:
            tips[0] += 1
            if 0 <= x < GRID_W and 0 <= y < GRID_H:
                grid[int(y)][int(x)] = "*"
            return
        steps = int(length)
        for _ in range(steps):
            x += math.sin(angle)
            y -= math.cos(angle)
            ix, iy = int(x), int(y)
            if 0 <= ix < GRID_W and 0 <= iy < GRID_H:
                dx = math.sin(angle)
                grid[iy][ix] = "|" if abs(dx) < 0.2 else ("/" if dx < 0 else "\\")
        left = angle - math.radians(38)
        right = angle + math.radians(38)
        draw(x, y, left, length * 0.68, level - 1)
        draw(x, y, right, length * 0.68, level - 1)

    draw(GRID_W // 2, GRID_H - 1, 0.0, GRID_H - 2, depth)
    return ["".join(row).rstrip() for row in grid], tips[0]


# ---------------------------------------------------------------- 推理题

QUIZ = [
    {
        "q": "谢尔宾斯基三角画到第 5 层（共 2^5 = 32 行）时，实心方块「█」一共有多少个？",
        "options": {"A": "81", "B": "162", "C": "243", "D": "512"},
        "answer": "C",
        "why": "每多一层，实心数量变成原来的 3 倍：第 n 层是 3^n，第 5 层 = 3^5 = 243。",
    },
    {
        "q": "分形树递归到第 6 层，末梢（每个分枝的起点/叶尖）一共有多少个？",
        "options": {"A": "12", "B": "36", "C": "64", "D": "128"},
        "answer": "C",
        "why": "每次分叉都由一枝变两枝，末梢数量是 2^n，第 6 层 = 64。",
    },
    {
        "q": "曼德勃罗集的 ASCII 图，上下两半是否对称？对称轴是哪一条？",
        "options": {"A": "对称，关于水平中线（复平面的实轴）",
                    "B": "对称，关于竖直中线（复平面的虚轴）",
                    "C": "完全不对称",
                    "D": "对称，关于对角线"},
        "answer": "A",
        "why": "z²+c 的迭代只涉及实数四则运算，把 c 取共轭（虚部变号）结果照样共轭，所以图形关于实轴（水平中线）镜像对称。",
    },
]


def gallery_cmd(text):
    parts = text.split()
    if not parts:
        return True
    name = parts[0].lower()
    arg = None
    if len(parts) > 1:
        try:
            arg = int(parts[1])
        except ValueError:
            print("  参数要写整数，例如 sierpinski 5。")
            return True
    try:
        if name == "sierpinski":
            layers = arg if arg else 4
            layers = max(1, min(layers, 6))
            lines = sierpinski(layers)
            print(f"\n  谢尔宾斯基三角 · 第 {layers} 层（实心 {count_solid(lines)} 个，正好 3^{layers}）\n")
            for line in lines:
                print("   " + line)
        elif name == "mandelbrot":
            iters = arg if arg else 40
            iters = max(10, min(iters, 120))
            lines = mandelbrot(iters)
            print(f"\n  曼德勃罗集 · 迭代上限 {iters}\n")
            for line in lines:
                print("   " + line)
        elif name == "tree":
            depth = arg if arg else 5
            depth = max(1, min(depth, 8))
            lines, tips = tree(depth)
            print(f"\n  分形树 · {depth} 层（末梢 {tips} 个，正好 2^{depth}）\n")
            for line in lines:
                if line:
                    print("   " + line)
        else:
            print("  没有这个分形。可选：sierpinski / mandelbrot / tree")
    except Exception as exc:      # 参数极端时不至于崩掉整局
        print(f"  渲染失败：{exc}")
    return True


def play():
    print("=" * 62)
    print("      🌀 ASCII 分形画廊 · 自相似之美")
    print("=" * 62)
    print("随时输入「sierpinski 5」「mandelbrot 40」「tree 6」渲染分形，输入 quiz 开始做题。")
    print("输入 help 看说明，q 退出。")
    gallery_cmd("sierpinski 3")

    total = 0
    while True:
        try:
            raw = input("\n  > ").strip()
        except EOFError:
            print("\n输入中断，提前结束。")
            return
        if not raw:
            continue
        low = raw.lower()
        if low in ("q", "quit", "exit"):
            print("  再见。")
            return
        if low == "help":
            print("""  命令：
    sierpinski N   谢尔宾斯基三角，N 层（1-6）
    mandelbrot N   曼德勃罗集，迭代上限 N（10-120）
    tree N         分形树，N 层（1-8）
    quiz           开始 3 道推理题
    q              退出""")
            continue
        if low == "quiz":
            total += run_quiz()
            break
        gallery_cmd(raw)

    print("\n" + "=" * 62)
    print(f"  结算：总分 {total}/300")
    if total >= 200:
        print("  🏆 你抓住了分形的数量规律：三分、二分、对称。")
    elif total >= 100:
        print("  👍 有感觉了，记住 3^n 和 2^n 这两个增长方式。")
    else:
        print("  🙂 关键就一句：分形每深入一层，元素数量按固定倍数增长。")
    print("=" * 62)


def run_quiz():
    score = 0
    for i, item in enumerate(QUIZ, 1):
        print("\n" + "-" * 62)
        print(f"  第 {i} 题：{item['q']}")
        for k, v in item["options"].items():
            print(f"    {k}. {v}")
        while True:
            try:
                ans = input("  选（A/B/C/D）：").strip().upper()
            except EOFError:
                print("\n输入中断，提前结算。")
                return score
            if ans in item["options"]:
                break
            print("  请输入 A、B、C 或 D。")
        if ans == item["answer"]:
            print("  ✅ 正确！" + item["why"])
            score += 100
        else:
            print(f"  ❌ 正确答案是 {item['answer']}。" + item["why"])
    return score


if __name__ == "__main__":
    play()
