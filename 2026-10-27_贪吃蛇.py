# -*- coding: utf-8 -*-
"""
贪吃蛇（Snake）
==============
终端版贪吃蛇：用 w/a/s/d 控制蛇移动，吃到食物 +1 分并增长，撞墙或撞自己则结束。
纯标准库实现，可直接运行：python3 2026-10-27_贪吃蛇.py
"""

import random
import os
import sys
import time

W, H = 20, 10


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def print_board(snake, food):
    board = [["." for _ in range(W)] for _ in range(H)]
    for x, y in snake:
        if 0 <= x < W and 0 <= y < H:
            board[y][x] = "#"
    fx, fy = food
    if 0 <= fx < W and 0 <= fy < H:
        board[fy][fx] = "@"
    print("+" + "-" * W + "+")
    for row in board:
        print("|" + "".join(row) + "|")
    print("+" + "-" * W + "+")


def main():
    print("=" * 40)
    print("        🐍 贪吃蛇 Snake")
    print("=" * 40)
    print("操作：w/a/s/d 控制方向，q 退出。食物 @，蛇 #。")
    snake = [(W // 2, H // 2)]
    dirs = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}
    dx, dy = 1, 0
    food = (random.randrange(W), random.randrange(H))
    score = 0
    time.sleep(1)

    while True:
        clear()
        print(f"得分：{score}  长度：{len(snake)}")
        print_board(snake, food)
        cmd = input("方向(w/a/s/d)：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("退出游戏。最终得分", score)
            break
        if cmd in dirs:
            dx, dy = dirs[cmd]

        head = (snake[0][0] + dx, snake[0][1] + dy)
        if not (0 <= head[0] < W and 0 <= head[1] < H):
            print(f"💥 撞墙了！得分 {score}，长度 {len(snake)}")
            break
        if head in snake:
            print(f"💥 咬到自己了！得分 {score}，长度 {len(snake)}")
            break

        snake.insert(0, head)
        if head == food:
            score += 1
            food = (random.randrange(W), random.randrange(H))
            # 避免食物出现在蛇身上
            while food in snake:
                food = (random.randrange(W), random.randrange(H))
        else:
            snake.pop()
        time.sleep(0.2)


if __name__ == "__main__":
    main()
