# -*- coding: utf-8 -*-
"""
密室寻宝（Text Adventure）
============================
经典文字冒险小游戏。你身处一座地牢，用方向命令在房间间移动，
找到钥匙后进入宝藏室，带回宝藏即为胜利。纯标准库实现。
运行：python3 2026-11-04_密室寻宝.py

命令说明：
  北 / 南 / 东 / 西   —— 移动方向
  拿                 —— 拾取当前房间的物品
  开                 —— 打开当前房间的门/宝箱
  帮助 / 查          —— 显示命令帮助
  退出 / q           —— 结束游戏
"""

import time

ROOMS = {
    "大厅": {"北": "走廊", "东": "储藏室", "物品": [], "描述": "昏暗的大厅，四周有火把的余烬。"},
    "走廊": {"南": "大厅", "东": "书房", "物品": [], "描述": "一条长长的走廊，墙上挂着褪色的画像。"},
    "书房": {"西": "走廊", "物品": ["钥匙"], "描述": "堆满旧书的书房，书桌抽屉里似乎有东西。"},
    "储藏室": {"西": "大厅", "北": "地下室", "物品": [], "描述": "塞满杂物的储藏室，木桶散发霉味。"},
    "地下室": {"南": "储藏室", "物品": [], "描述": "阴暗的地下室，角落里有一扇沉重的铁门。"},
}

TREASURE_ROOM = "宝藏室"


def main():
    print("=" * 46)
    print("        🏰 密室寻宝 Text Adventure")
    print("=" * 46)
    print("身处地牢，移动探索，找到钥匙开启宝藏室。")
    print("方向命令：北/南/东/西；动作：拿/开；帮助/查；退出。\n")

    room = "大厅"
    inventory = []
    has_key = False
    steps = 0
    treasure_found = False

    while True:
        # 宝藏室单独处理，不进入 ROOMS 查询
        if room == TREASURE_ROOM:
            print("\n你来到【宝藏室】。宝箱在角落闪着金光。")
            cmd = input("> ").strip().replace(" ", "")
            if cmd == "开":
                print("🎉 你打开了宝箱，找到了稀世宝藏！")
                print(f"\n🏆 通关！你共走了 {steps} 步，带回了宝藏。")
                return
            if cmd in ("退出", "q", "quit", "exit"):
                print(f"你带着钥匙离开了，共走了 {steps} 步。")
                return
            print("输入「开」打开宝箱。")
            continue

        desc = ROOMS[room]["描述"]
        items = ROOMS[room]["物品"]
        print(f"\n你在【{room}】。{desc}")
        if room == "地下室" and not treasure_found:
            print("地下室深处有一扇铁门，似乎需要一把钥匙。")
        if items:
            print("这里有一件物品：" + "、".join(items))
        if inventory:
            print("你的背包：" + "、".join(inventory))

        cmd = input("> ").strip()
        cmd = cmd.replace(" ", "")
        if cmd in ("退出", "q", "quit", "exit"):
            print(f"你离开了地牢，共走了 {steps} 步。")
            return

        if cmd in ("帮助", "帮助", "查", "help"):
            print("北/南/东/西 移动 · 拿 拾取物品 · 开 开门/宝箱 · 退出 结束")
            continue

        if cmd in ROOMS[room]:
            room = ROOMS[room][cmd]
            steps += 1
            continue

        if cmd == "拿":
            if items:
                item = items.pop(0)
                inventory.append(item)
                print(f"你拾取了【{item}】。")
                if item == "钥匙":
                    has_key = True
                    print("🔑 拿到钥匙了！")
            else:
                print("这里没有可拿的东西。")
            continue

        if cmd == "开":
            if room == "地下室" and not treasure_found:
                if has_key:
                    print("你用钥匙打开了铁门，走进【宝藏室】！")
                    room = TREASURE_ROOM
                    treasure_found = True
                else:
                    print("铁门锁着，需要钥匙才能打开。")
            else:
                print("这里没有可以打开的东西。")
            continue

        if cmd == "北" and room == "储藏室" and not has_key:
            # 通往地下室的门口
            pass
        print(f"无法「{cmd}」，试试：北/南/东/西、拿、开、帮助。")


if __name__ == "__main__":
    main()
