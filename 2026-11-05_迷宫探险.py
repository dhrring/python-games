# -*- coding: utf-8 -*-
"""
迷宫探险（Maze Escape）
========================
程序随机生成一座迷宫，你从左上角起点（P）出发，
用方向命令在迷宫中穿行，走到右下角出口（E）即为胜利。
迷宫每次运行都不同。纯标准库实现。
运行：python3 2026-11-05_迷宫探险.py

方向命令：
  w / 上 / 北   向上
  s / 下 / 南   向下
  a / 左 / 西   向左
  d / 右 / 东   向右
  q / 退出      结束游戏
"""

import random


def generate_maze(size):
    """用递归回溯（深度优先）生成 size x size 迷宫，返回二维网格：0 路，1 墙。"""
    grid = [[1] * size for _ in range(size)]
    stack = [(1, 1)]
    grid[1][1] = 0
    while stack:
        r, c = stack[-1]
        moves = []
        for dr, dc in ((0, 2), (0, -2), (2, 0), (-2, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 1:
                moves.append((nr, nc, dr, dc))
        if not moves:
            stack.pop()
            continue
        nr, nc, dr, dc = random.choice(moves)
        grid[nr][nc] = 0
        grid[r + dr // 2][c + dc // 2] = 0
        stack.append((nr, nc))
    return grid


DIRS = {
    "w": (-1, 0), "上": (-1, 0), "北": (-1, 0),
    "s": (1, 0), "下": (1, 0), "南": (1, 0),
    "a": (0, -1), "左": (0, -1), "西": (0, -1),
    "d": (0, 1), "右": (0, 1), "东": (0, 1),
}


def show(grid, r, c, end_r, end_c):
    for rr in range(len(grid)):
        row = ""
        for cc in range(len(grid)):
            if (rr, cc) == (r, c):
                row += "P "
            elif (rr, cc) == (end_r, end_c):
                row += "E "
            else:
                row += "# " if grid[rr][cc] else "  "
        print(row)


def main():
    size = 13
    print("=" * 46)
    print("        🧭 迷宫探险 Maze Escape")
    print("=" * 46)
    print(f"随机生成 {size}x{size} 迷宫，从 P 走到 E。方向：w/s/a/d（或中文 上/下/左/右）。")

    grid = generate_maze(size)
    r, c = 1, 1
    end_r, end_c = size - 2, size - 2
    grid[end_r][end_c] = 0
    steps = 0

    print("\n迷宫如下（P=你，E=出口）：")
    show(grid, r, c, end_r, end_c)

    while (r, c) != (end_r, end_c):
        cmd = input(f"\n[步数 {steps}] 方向：").strip().lower()
        if cmd in ("q", "quit", "exit", "退出"):
            print(f"你退出了迷宫，走了 {steps} 步。")
            return
        if cmd not in DIRS:
            print("无效命令，用 w/s/a/d 或 上/下/左/右。")
            continue
        dr, dc = DIRS[cmd]
        nr, nc = r + dr, c + dc
        if not (0 <= nr < size and 0 <= nc < size) or grid[nr][nc] == 1:
            print("撞墙了！换个方向。")
            continue
        r, c = nr, nc
        steps += 1
        show(grid, r, c, end_r, end_c)

    print(f"\n🏆 成功走出迷宫！共走了 {steps} 步。")


if __name__ == "__main__":
    main()
