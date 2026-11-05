# -*- coding: utf-8 -*-
"""
文字打怪RPG（Text RPG Battle）
================================
纯文字的回合制角色扮演战斗。你是一名勇者，依次迎战 3 名怪物，
最后挑战 BOSS 巨龙，全部战胜即通关。
每回合可选择：攻击、闪避、回复。纯标准库实现。
运行：python3 2026-11-05_文字打怪RPG.py
"""

import random

ACTIONS = {
    "1": "攻击", "攻": "攻击", "attack": "攻击",
    "2": "闪避", "闪": "闪避", "dodge": "闪避",
    "3": "回复", "回": "回复", "heal": "回复",
}

MONSTERS = [
    ("史莱姆", 8, 3),   # 名字, 生命, 攻击
    ("野狼", 12, 5),
    ("骷髅兵", 16, 6),
]
BOSS = ("巨龙", 35, 9)


def player_turn(player_hp):
    """玩家行动，返回 (伤害, 新HP, 是否闪避)。"""
    while True:
        choice = input("行动（1 攻击 / 2 闪避 / 3 回复）：").strip().lower()
        if choice in ("q", "quit", "退出"):
            return None, player_hp, False
        if choice not in ACTIONS:
            print("无效，输入 1/2/3。")
            continue
        act = ACTIONS[choice]
        if act == "攻击":
            dmg = random.randint(6, 11)
            print(f"⚔️ 你挥剑攻击，造成 {dmg} 点伤害！")
            return dmg, player_hp, False
        if act == "回复":
            heal = random.randint(5, 8)
            player_hp = min(30, player_hp + heal)
            print(f"💊 你包扎伤口，回复 {heal} 点生命（当前 {player_hp}/30）。")
            return 0, player_hp, False
        if act == "闪避":
            print("🛡️ 你摆出防御姿态，准备闪避攻击。")
            return 0, player_hp, True


def main():
    print("=" * 46)
    print("        🐉 文字打怪RPG Text RPG Battle")
    print("=" * 46)
    print("你是勇者（生命 30）。打败 3 只怪物和 BOSS 巨龙即可通关。")
    print("行动：1 攻击 / 2 闪避（伤害减半）/ 3 回复。输入 q 退出。\n")

    player_hp = 30
    wave = 0
    battles = MONSTERS + [BOSS]

    for mh_name, mh_hp, mh_atk in battles:
        m_hp = mh_hp
        wave += 1
        tag = "BOSS" if mh_name == "巨龙" else "怪物"
        print(f"\n—— 第 {wave} 战：遭遇【{mh_name}】！生命 {m_hp}，攻击 {mh_atk} ——")
        while m_hp > 0 and player_hp > 0:
            print(f"\n你的生命 {player_hp}/30，{mh_name} 生命 {m_hp}。")
            dmg, player_hp, dodging = player_turn(player_hp)
            if dmg is None:  # 玩家退出
                print("你逃走了。")
                return
            if dmg >= m_hp:
                m_hp = 0
                print(f"🎉 你击败了【{mh_name}】！")
                break
            m_hp -= dmg
            # 怪物反击（玩家闪避当回合伤害减半）
            if m_hp <= 0:
                print(f"🎉 你击败了【{mh_name}】！")
                break
            if dodging:
                m_hit = max(0, mh_atk // 2 - random.randint(0, 2))
            else:
                m_hit = max(0, mh_atk - random.randint(0, 2))
            player_hp -= m_hit
            if player_hp <= 0:
                print(f"💀 {mh_name} 击倒了你，你生命归零……")
            else:
                print(f"{mh_name} 攻击你，造成 {m_hit} 点伤害（剩余生命 {player_hp}）。")

        if player_hp <= 0:
            print("\n❌ 你倒下了，勇者之路到此为止。")
            return

    print(f"\n🏆 你战胜了所有怪物和 BOSS 巨龙，成为真正的勇者！")
    print(f"   最终剩余生命：{player_hp}/30")


if __name__ == "__main__":
    main()
