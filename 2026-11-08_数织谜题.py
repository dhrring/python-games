# -*- coding: utf-8 -*-
"""
数织谜题（Nonogram 5×5）
========================
每一行、每一列左侧（或下方）给出的数字，表示该行/该列中「连续黑格」的段长度，
多段之间至少隔一个空格。按提示把整幅 5×5 图案涂出来即可通关。

符号：· 未定，■ 涂黑，× 标记为空
纯标准库实现。

游玩方法：
  输入「行 列」切换该格状态（· → ■ → × → ·），例如 3 2；
  输入 c 检查答案；输入 h 看当前提示；输入 q 退出。
  共 5 关，逐关挑战。
运行：python3 2026-11-08_数织谜题.py
"""

SIZE = 5

LEVELS = [
    ("心形", [
        ".#.#.",
        "#####",
        "#####",
        ".###.",
        ".....",
    ]),
    ("大叉", [
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
    ]),
    ("十字", [
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
    ]),
    ("字母 T", [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ]),
    ("阶梯", [
        "#....",
        "##...",
        "###..",
        "####.",
        "#####",
    ]),
]

UNKNOWN, FILLED, CROSS = 0, 1, 2
SYM = {UNKNOWN: "·", FILLED: "■", CROSS: "×"}


def runs(seq):
    """把 0/1 序列转成连续段长度列表；全空返回 [0]。"""
    out, cnt = [], 0
    for v in seq:
        if v:
            cnt += 1
        elif cnt:
            out.append(cnt)
            cnt = 0
    if cnt:
        out.append(cnt)
    return out if out else [0]


def hints(pattern):
    rows = [[1 if ch == "#" else 0 for ch in line] for line in pattern]
    row_hints = [runs(r) for r in rows]
    col_hints = [runs([rows[r][c] for r in range(SIZE)]) for c in range(SIZE)]
    return row_hints, col_hints


def fmt(h):
    return ",".join(str(x) for x in h)


def show(grid, row_hints, col_hints, name, idx):
    print(f"\n第 {idx + 1} 关：{name}")
    print("列提示：")
    for c in range(SIZE):
        print(f"  第 {c + 1} 列 → [{fmt(col_hints[c])}]")
    print("棋盘（左侧为行提示）：")
    for r in range(SIZE):
        line = " ".join(SYM[grid[r][c]] for c in range(SIZE))
        print(f"  [{fmt(row_hints[r]):>7}]  {line}   ← 第 {r + 1} 行")
    print("  列号：" + " ".join(str(c + 1) for c in range(SIZE)))


def check(grid, row_hints, col_hints):
    ok = True
    for r in range(SIZE):
        if runs([1 if grid[r][c] == FILLED else 0 for c in range(SIZE)]) != row_hints[r]:
            ok = False
    for c in range(SIZE):
        if runs([1 if grid[r][c] == FILLED else 0 for r in range(SIZE)]) != col_hints[c]:
            ok = False
    return ok


def play_level(name, pattern, idx):
    row_hints, col_hints = hints(pattern)
    grid = [[UNKNOWN] * SIZE for _ in range(SIZE)]
    while True:
        show(grid, row_hints, col_hints, name, idx)
        raw = input("输入「行 列」切换格子 / c 检查 / q 退出：").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        if raw in ("c", "check"):
            if check(grid, row_hints, col_hints):
                print(f"✅ 第 {idx + 1} 关「{name}」完成！")
                return True
            print("❌ 还有行列提示没满足，再检查一下。")
            continue
        parts = raw.replace("，", " ").replace(",", " ").split()
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            print("格式：行 列（都是 1~5），例如 3 2。")
            continue
        r, c = int(parts[0]) - 1, int(parts[1]) - 1
        if not (0 <= r < SIZE and 0 <= c < SIZE):
            print("行列都必须在 1~5 之间。")
            continue
        grid[r][c] = (grid[r][c] + 1) % 3
        print(f"({r + 1},{c + 1}) 现在是 {SYM[grid[r][c]]}")


def main():
    print("=" * 48)
    print("        🧩 数织谜题 Nonogram 5×5")
    print("=" * 48)
    print("提示数字表示「连续黑格的段长度」，多段之间至少空一格。")
    print("用「行 列」涂格：· 未定 → ■ 涂黑 → × 标记为空 → ·，全部行列为 c 检查。")

    passed = 0
    for i, (name, pattern) in enumerate(LEVELS):
        r = play_level(name, pattern, i)
        if r is None:
            print("你已退出。")
            break
        if r:
            passed += 1

    print("\n" + "=" * 48)
    print(f"        通关：{passed}/{len(LEVELS)} 关")
    if passed == len(LEVELS):
        print("        🏆 全通关！逻辑与耐心都很强。")
    print("=" * 48)


if __name__ == "__main__":
    main()
