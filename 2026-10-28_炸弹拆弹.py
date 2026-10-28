# -*- coding: utf-8 -*-
"""
炸弹拆弹（Bomb Defusal）
========================
推理+运气小游戏：炸弹有若干根引线，其中一根是"爆破线"。
你依次选线剪断，选到安全线则提示"还剩X根"，选到爆破线则爆炸。
也可以使用"拆弹钳"工具查询线索减少风险。纯标准库实现。
运行：python3 2026-10-28_炸弹拆弹.py
"""

import random

LIVES = 3
PLIERS = 2  # 拆弹钳次数


def main():
    print("=" * 40)
    print("        💣 炸弹拆弹 Bomb Defusal")
    print("=" * 40)
    print("炸弹有若干引线，其中一根是爆破线。依次选线剪断。")
    print("你有拆弹钳可用：用钳子可安全排除一根线（不耗命）。")
    print("q 退出，p 使用拆弹钳。")

    wires = 8
    bomb_wire = random.randint(1, wires)
    pliers = PLIERS

    while wires > 1:
        print(f"\n当前剩余引线 {wires} 根，拆弹钳剩余 {pliers} 次")
        for i in range(1, wires + 1):
            print(f"  线{i}", end="  ")
        print()
        cmd = input(f"选择剪断的线号(1~{wires})，或 p 用钳子，q 退出：").strip().lower()
        if cmd in ("q", "quit", "exit"):
            print("你放弃了拆弹。炸弹倒计时停止……")
            return
        if cmd == "p":
            if pliers <= 0:
                print("拆弹钳用完了！")
                continue
            pliers -= 1
            # 用钳子排除一根安全线
            safe = [i for i in range(1, wires + 1) if i != bomb_wire]
            remove = random.choice(safe)
            if remove < bomb_wire:
                bomb_wire -= 1  # 重新编号
            wires -= 1
            print(f"🔧 钳子安全排除了线{remove}（不是爆破线）。")
            continue
        if not cmd.isdigit():
            print("请输入线号。")
            continue
        n = int(cmd)
        if not (1 <= n <= wires):
            print(f"请输入1~{wires}之间的线号。")
            continue
        if n == bomb_wire:
            print("💥 轰！你剪到了爆破线，炸弹爆炸了！")
            return
        # 剪到安全线，重新编号
        if n < bomb_wire:
            bomb_wire -= 1
        wires -= 1
        print(f"✅ 剪断线{n}，安全！还剩 {wires} 根。")

    print(f"🎉 只剩一根安全线，炸弹成功拆除！拆弹钳还剩 {pliers} 次。")


if __name__ == "__main__":
    main()
