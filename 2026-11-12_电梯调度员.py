# -*- coding: utf-8 -*-
"""
电梯调度员（30 回合 · 一栋 8 层楼 · 一部电梯）
=================================================
你是这栋楼的电梯调度员。每回合你只能给电梯一条指令：
    u  上行一层        d  下行一层        s  停靠（开门上下客）
电梯最多装 10 人；乘客等太久会不耐烦，直接走楼梯（算你失职）。

得分：每送 1 位乘客到目的地 +10 分，每流失 1 位乘客 −15 分。
30 回合后结算，看你把这栋楼调度得怎么样。

玩法要点：
  乘客不挑方向——电梯到了就上，所以「顺路」比「专程」重要。
  空跑一层也是要花一回合的，别为了一个乘客把整栋楼的人都放跑。
运行：python3 2026-11-12_电梯调度员.py
"""

import random

FLOORS = 8
CAPACITY = 10
TURNS = 30
PATIENCE = 12  # 等超过这么多回合就流失


class Passenger:
    _id = 0

    def __init__(self, src, dst):
        Passenger._id += 1
        self.sid = Passenger._id
        self.src = src
        self.dst = dst
        self.wait = 0

    def label(self):
        return f"{self.sid}号({self.src}→{self.dst})"


def draw(floor, inside, waiting):
    print()
    for f in range(FLOORS, 0, -1):
        mark = "🚪" if f == floor else "  "
        bar = "#" if f == floor else "."
        w = waiting.get(f, [])
        w_txt = f"  等 {len(w)} 人：" + "、".join(f"{p.dst}↑" if p.dst > f else f"{p.dst}↓" for p in w) if w else ""
        print(f"  {f:>2} 层 │{bar}{mark}{w_txt}")
    print("  ————┴——" + "-" * 40)
    if inside:
        print("  轿内（" + str(len(inside)) + "/" + str(CAPACITY) + "）：" +
              "、".join(f"{p.dst}层" for p in inside))
    else:
        print(f"  轿内：空（0/{CAPACITY}）")


def main():
    print("=" * 62)
    print("      🛗 电梯调度员")
    print("=" * 62)
    print(f"目标：{TURNS} 回合内尽可能多送人，少流失人。")
    print(f"规则：电梯容量 {CAPACITY} 人；乘客等待超过 {PATIENCE} 回合会自己走楼梯（每次 −15 分）。")
    print("指令：u=上行一层 / d=下行一层 / s=停靠开门 / q=退出")

    floor = 1
    inside = []
    waiting = {}
    delivered = 0
    lost = 0
    turn = 0

    while turn < TURNS:
        turn += 1
        print("\n" + "=" * 62)
        print(f"  第 {turn}/{TURNS} 回合｜电梯在 {floor} 层｜已送达 {delivered} 人｜流失 {lost} 人")
        draw(floor, inside, waiting)

        cmd = ""
        while cmd not in ("u", "d", "s"):
            try:
                cmd = input("  指令（u 上 / d 下 / s 停靠 / q 退出）：").strip().lower()
            except EOFError:
                print("\n输入中断，提前结束。")
                turn = TURNS + 1
                break
            if cmd in ("q", "quit", "exit"):
                print("\n你提前下班了。")
                turn = TURNS + 1
                break
            if cmd not in ("u", "d", "s"):
                print("  只能输入 u / d / s。")
        if turn > TURNS:
            break

        if cmd == "u":
            if floor < FLOORS:
                floor += 1
                print(f"  ↑ 上行到 {floor} 层")
            else:
                print("  ⌛ 已经在顶层，上行无效（浪费了一回合）")
        elif cmd == "d":
            if floor > 1:
                floor -= 1
                print(f"  ↓ 下行到 {floor} 层")
            else:
                print("  ⌛ 已经在一层，下行无效（浪费了一回合）")
        else:
            # 停靠：先下人，再上人
            dropped = [p for p in inside if p.dst == floor]
            inside = [p for p in inside if p.dst != floor]
            if dropped:
                delivered += len(dropped)
                print(f"  🔔 开门：{len(dropped)} 人到站下车（{', '.join(p.label() for p in dropped)}）")
                print(f"     送达累计 {delivered} 人")
            else:
                print("  🔔 开门：没人下车")

            board = waiting.get(floor, [])
            room = CAPACITY - len(inside)
            taken = board[:room]
            waiting[floor] = board[room:]
            if not waiting[floor]:
                waiting.pop(floor)
            inside.extend(taken)
            if taken:
                print(f"  🚶 {len(taken)} 人上车：{', '.join(p.label() for p in taken)}")
            elif board:
                print(f"  🧍 轿厢满了，{len(board)} 人没挤上")

        # 时间推进：所有等待者 +1，超时流失
        gone = []
        for f in list(waiting):
            keep = []
            for p in waiting[f]:
                p.wait += 1
                if p.wait >= PATIENCE:
                    gone.append(p)
                else:
                    keep.append(p)
            if keep:
                waiting[f] = keep
            else:
                waiting.pop(f)
        if gone:
            lost += len(gone)
            print(f"  😤 放弃等待走了：{', '.join(p.label() for p in gone)}（−{15 * len(gone)} 分）")

        # 新乘客到达
        rate = 0.38 + 0.016 * turn
        if random.random() < rate:
            n = 1 + (1 if random.random() < 0.35 else 0)
            for _ in range(n):
                src = random.randint(1, FLOORS)
                dst = random.randint(1, FLOORS)
                while dst == src:
                    dst = random.randint(1, FLOORS)
                waiting.setdefault(src, []).append(Passenger(src, dst))
                print(f"  🆕 {src} 层来了一位要去 {dst} 层的乘客")

    score = delivered * 10 - lost * 15
    rate = delivered / max(1, delivered + lost)
    print("\n" + "=" * 62)
    print("  交班结算")
    print("=" * 62)
    print(f"  送达 {delivered} 人（+{delivered * 10} 分）")
    print(f"  流失 {lost} 人（−{lost * 15} 分）")
    print(f"  最终得分：{score}｜送达率 {rate * 100:.0f}%")
    if rate >= 0.75:
        print("  🏆 金牌调度员：这栋楼的人几乎没等过你。")
    elif rate >= 0.55:
        print("  👍 优秀，只是偶尔空跑。")
    elif rate >= 0.35:
        print("  🙂 及格，回头看看哪些楼层被你冷落了。")
    else:
        print("  😅 乘客开始贴投诉信了。")
    print("  参考结论：别为了一个人横穿整栋楼——顺路接人、顺路送人，单位回合的送达率才最高。")
    print("=" * 62)


if __name__ == "__main__":
    main()
