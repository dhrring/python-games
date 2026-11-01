# -*- coding: utf-8 -*-
"""
Simon 记忆游戏（Simon Says）
============================
电脑随机亮出一串方向（上/下/左/右），你按顺序复述。
每轮加长一个，记住并复述对即过关，错则结束。纯标准库实现。
运行：python3 2026-11-01_记忆游戏.py
"""

import random
import time

DIRS = ["上", "下", "左", "右"]
TIPS = ["👆", "👇", "👈", "👉"]


def main():
    print("=" * 42)
    print("        🧠 Simon 记忆游戏")
    print("=" * 42)
    print("电脑逐轮亮出一串方向，你按顺序输入中文方向。")
    print("例：序列为上上左下  →  输入: 上 上 左 下（空格分隔）")
    print("输入 'q' 退出。")
    input("按回车开始……")

    seq = []
    level = 0
    while True:
        seq.append(random.randrange(4))
        level += 1
        # 展示序列
        print(f"\n—— 第 {level} 关 ——")
        time.sleep(0.5)
        shown = " ".join(DIRS[i] for i in seq)
        print(f"请记: {shown}")
        time.sleep(1.2 + level * 0.25)
        print("\033[2A\033[K", end="")  # 尝试清掉提示行（终端支持才有效）
        ans = input("复述：").strip()
        if ans.lower() in ("q", "quit", "exit"):
            print(f"\n退出游戏。你闯到了第 {level - 1} 关。")
            return
        parts = [p for p in ans.split() if p]
        ok = len(parts) == len(seq) and all(
            DIRS[seq[k]] == parts[k] for k in range(len(seq))
        )
        if not ok:
            print(f"❌ 错误。正确序列: {shown}")
            print(f"你闯到了第 {level - 1} 关。")
            return
        print(f"✅ 第 {level} 关通过！")
        time.sleep(0.8)


if __name__ == "__main__":
    main()
