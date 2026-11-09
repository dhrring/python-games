# -*- coding: utf-8 -*-
"""
推箱子（Sokoban）
=================
仓库工人要把所有箱子推到目标点上。你只能「推」箱子，不能拉；
一次只能推动一个箱子，箱子后面必须是空地或目标点。
纯标准库实现。

符号说明：
  #  墙
  .  目标点
  $  箱子
  *  箱子已在目标点上
  @  你
  +  你站在目标点上
  (空格) 空地

游玩方法：
  输入 w / a / s / d 向 上 / 左 / 下 / 右 移动（回车确认），
  输入 u 撤销一步，r 重玩本关，q 退出。
  全部箱子推到目标点即过关，共 4 关。
运行：python3 2026-11-09_推箱子.py
"""

WALL = "#"
GOAL = "."
BOX = "$"
PLAYER = "@"

LEVELS = [
    ("热身", [
        "#######",
        "#     #",
        "# .$@ #",
        "#     #",
        "#######",
    ]),
    ("绕行", [
        "#########",
        "#       #",
        "#  $ .  #",
        "#   @   #",
        "#       #",
        "#########",
    ]),
    ("双箱", [
        "##########",
        "#        #",
        "#  $  .  #",
        "#        #",
        "#  $  .  #",
        "#   @    #",
        "##########",
    ]),
    ("错层", [
        "##########",
        "#        #",
        "#  $  .  #",
        "#        #",
        "#     $  #",
        "#  @  .  #",
        "##########",
    ]),
]


def parse(lines):
    walls, goals, boxes = set(), set(), set()
    player = None
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == WALL:
                walls.add((r, c))
            elif ch == GOAL:
                goals.add((r, c))
            elif ch == BOX:
                boxes.add((r, c))
            elif ch == PLAYER:
                player = (r, c)
            elif ch == "*":
                boxes.add((r, c))
                goals.add((r, c))
            elif ch == "+":
                player = (r, c)
                goals.add((r, c))
    return walls, goals, boxes, player


def inside(walls, r, c, rows, cols):
    return 0 <= r < rows and 0 <= c < cols and (r, c) not in walls


def render(walls, goals, boxes, player):
    rows = max(r for r, _ in walls) + 1
    cols = max(c for _, c in walls) + 1
    out = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            p = (r, c)
            if p in walls:
                line += WALL
            elif p == player and p in goals:
                line += "+"
            elif p == player:
                line += PLAYER
            elif p in boxes and p in goals:
                line += "*"
            elif p in boxes:
                line += BOX
            elif p in goals:
                line += GOAL
            else:
                line += " "
        out.append(line)
    return "\n".join(out)


def try_move(walls, boxes, player, dr, dc):
    """返回 (新玩家位置, 新箱子集合, 是否真的移动了)。"""
    nr, nc = player[0] + dr, player[1] + dc
    if (nr, nc) in walls:
        return player, boxes, False
    if (nr, nc) in boxes:
        br, bc = nr + dr, nc + dc
        if (br, bc) in walls or (br, bc) in boxes:
            return player, boxes, False
        new_boxes = set(boxes)
        new_boxes.discard((nr, nc))
        new_boxes.add((br, bc))
        return (nr, nc), new_boxes, True
    return (nr, nc), boxes, True


def play_level(name, lines, idx):
    walls, goals, boxes, player = parse(lines)
    history = []
    print(f"\n第 {idx + 1} 关：{name}（箱子 {len(boxes)} 个 / 目标 {len(goals)} 个）")
    while True:
        print("\n" + render(walls, goals, boxes, player))
        if boxes == goals and boxes:
            print(f"\n✅ 第 {idx + 1} 关「{name}」过关！")
            return True
        raw = input("w/a/s/d 移动，u 撤销，r 重来，q 退出：").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None
        if raw == "u":
            if history:
                player, boxes = history.pop()
                print("已撤销一步。")
            else:
                print("没有可撤销的步骤。")
            continue
        if raw == "r":
            walls, goals, boxes, player = parse(lines)
            history = []
            print("已重置本关。")
            continue
        dmap = {"w": (-1, 0), "a": (0, -1), "s": (1, 0), "d": (0, 1)}
        if raw not in dmap:
            print("请输入 w / a / s / d 之一。")
            continue
        dr, dc = dmap[raw]
        np, nb, moved = try_move(walls, boxes, player, dr, dc)
        if not moved:
            print("那边过不去（墙或者箱子后面被挡住）。")
            continue
        history.append((player, set(boxes)))
        player, boxes = np, nb


def main():
    print("=" * 46)
    print("        📦 推箱子 Sokoban")
    print("=" * 46)
    print("把 $ 推到 . 上，只能推不能拉，箱子后面要有空位。")

    passed = 0
    for i, (name, lines) in enumerate(LEVELS):
        r = play_level(name, lines, i)
        if r is None:
            print("你已退出。")
            break
        if r:
            passed += 1
    print("\n" + "=" * 46)
    print(f"        通关：{passed}/{len(LEVELS)} 关")
    if passed == len(LEVELS):
        print("        🏆 全部通关，空间推理很到位！")
    print("=" * 46)


if __name__ == "__main__":
    main()
