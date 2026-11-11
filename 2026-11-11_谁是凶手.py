# -*- coding: utf-8 -*-
"""
谁是凶手（线索推理断案）
==========================
3 桩案子，每桩都有若干嫌疑人和一叠线索。
你的任务是读完线索、指出真凶。
线索是逐条揭示的 —— 每看一条线索会扣 15 分，所以「看得越少、推得越准」得分越高。

游玩方法：
  clue / 线索     揭示下一条线索（扣分）
  all             一次性看完剩余线索（同样每条扣分，但省时间）
  1 / 2 / 3 / 4   指认对应编号的嫌疑人，指认即判定
  q               退出
  每案只有一次指认机会，指认错误即判该案失败。
运行：python3 2026-11-11_谁是凶手.py
"""

CASES = [
    {
        "title": "第一案 · 深夜书房",
        "story": (
            "推理小说作家老周被发现倒在自家书房里，已经没了气息。\n"
            "当晚到过他家的有 4 个人。警方初步判断：凶手就在这 4 人之中。"
        ),
        "suspects": ["管家老陈", "侄子周航", "出版社编辑林女士", "隔壁邻居吴先生"],
        "clues": [
            "死者右手攥着半张撕碎的信纸，只剩「下周三」三个字。",
            "侄子周航称自己晚上 8 点就走了，可大楼门禁记录显示他是 9 点 40 分才离开。",
            "管家老陈 9 点整送过一杯咖啡进去，当时死者还活着，杯子上的唇印与死者一致。",
            "编辑林女士当晚人在外地，有车票和酒店入住记录，且她与死者只有版权纠纷、无深仇。",
            "隔壁邻居吴先生 9 点 20 分听到书房里传出争吵声，他以为是作家在跟人谈事，没有报警。",
        ],
        "answer": 1,
        "explain": (
            "周航的说法与门禁记录直接矛盾：他说 8 点走，实际 9 点 40 分才走；\n"
            "  而 9 点整死者还活着、9 点 20 分有争吵声，说明 9 点之后死者还与人争执。\n"
            "  管家有送咖啡的时间证明他只是送东西；编辑人在外地；邻居只是听到声音。"
        ),
    },
    {
        "title": "第二案 · 图书馆失窃",
        "story": (
            "市图书馆闭架书库里一份清代手稿不见了。失窃时间锁定在傍晚 19:05 前后。\n"
            "当天有权限进入闭架区的只有 4 个人。"
        ),
        "suspects": ["管理员小赵", "研究生孙某", "退休教师钱老师", "清洁工李阿姨"],
        "clues": [
            "监控在 19:05 到 19:06 之间有一段盲区，正好一分钟。",
            "管理员小赵当天 19:00—19:30 在另一栋楼的自习室值班，有签到记录和同学作证。",
            "研究生孙某当天临时申请了「闭架书库」权限，理由是「进去整理旧书」，申请时间 18:50。",
            "手稿原本放置的格子里，留下了一枚不属于管理员的指纹，比对结果为孙某。",
            "清洁工李阿姨 19:10 才推着车进到这层楼，她说进门时架子已经开着、地上有一张借书卡复印件。",
        ],
        "answer": 1,
        "explain": (
            "孙某 18:50 临时申请闭架权限、19:05 盲区前后在场、格子里留下他的指纹，\n"
            "  三条线索指向同一人，形成闭环。管理员在别处签到、清洁工 19:10 才到、钱老师无异常。"
        ),
    },
    {
        "title": "第三案 · 雨夜肇事",
        "story": (
            "雨夜，一辆车撞倒骑电动车的人后逃逸。现场只留下几片车漆和一个模糊的轮胎印。\n"
            "4 位车主被叫来问话。"
        ),
        "suspects": ["车主王某（蓝色轿车）", "车主李某（深灰轿车）", "车主陈某（白色 SUV）", "车主赵某（黑色皮卡）"],
        "clues": [
            "现场提取到的漆片是深灰色，不是蓝色。",
            "王某的车当晚在 4S 店做保养，维修工单显示进店 19:20、出厂次日早晨。",
            "轮胎印宽度 205mm、扁平比 55、轮毂 16 寸 —— 与李某车型的原厂规格完全一致。",
            "陈某的车当晚 19:00 停在小区地库，地库摄像头连续拍到它没动过。",
            "赵某的车是皮卡，胎宽 265mm，与现场印痕明显不符；但他承认当晚路过该路段。",
            "李某说当晚一直在家，可手机基站记录显示 19:15—19:40 他在事故路段附近。",
        ],
        "answer": 1,
        "explain": (
            "漆片是深灰色（排除王某的蓝车）、胎印规格与李某车型完全吻合、\n"
            "  李某自称在家却有基站记录在事故路段 —— 三条独立证据同时指向李某。\n"
            "  陈某车辆有连续监控、赵某胎宽不符。"
        ),
    },
]


def play_case(case, no):
    suspects = case["suspects"]
    print("\n" + "=" * 56)
    print(f"  {case['title']}")
    print("=" * 56)
    print(case["story"])
    print("\n  嫌疑人：")
    for i, s in enumerate(suspects, 1):
        print(f"    {i}. {s}")
    print("  已揭示线索：0 /", len(case["clues"]))

    revealed = 0
    while True:
        raw = input("\n  操作（clue=看下一条线索 / 数字=指认 / q=退出）：").strip().lower()
        if raw in ("q", "quit", "exit"):
            return None, 0

        if raw in ("clue", "线索", "c"):
            if revealed >= len(case["clues"]):
                print("  线索已经全部看完了。")
                continue
            print(f"  线索 {revealed + 1}：{case['clues'][revealed]}")
            revealed += 1
            print(f"  （已看 {revealed}/{len(case['clues'])} 条，每看一条扣 15 分）")
            continue

        if raw in ("all", "全部"):
            while revealed < len(case["clues"]):
                print(f"  线索 {revealed + 1}：{case['clues'][revealed]}")
                revealed += 1
            print(f"  （已看全部 {revealed} 条线索）")
            continue

        if raw.isdigit():
            idx = int(raw) - 1
            if not 0 <= idx < len(suspects):
                print(f"  请输入 1~{len(suspects)} 的编号。")
                continue
            if idx == case["answer"]:
                score = max(10, 100 - 15 * revealed)
                print(f"\n  ✅ 破案！真凶是 {suspects[idx]}")
                print(f"  推理链：{case['explain']}")
                print(f"  本案得分 {score}（用了 {revealed} 条线索）")
                return True, score
            else:
                print(f"\n  ❌ 错了。你指认的是 {suspects[idx]}，真正的凶手是 {suspects[case['answer']]}。")
                print(f"  真相：{case['explain']}")
                return False, 0

        print("  无法识别，请输入 clue / all / 数字 / q。")


def main():
    print("=" * 56)
    print("      🕵️ 谁是凶手 · 线索推理")
    print("=" * 56)
    print(f"共 {len(CASES)} 桩案子。每看一条线索扣 15 分，一次指认定胜负。")
    print("诀窍：先只读关键线索，用「谁说谎」「哪个物证对得上」做交叉检验。")

    total = 0
    solved = 0
    for no, case in enumerate(CASES, 1):
        ok, score = play_case(case, no)
        if ok is None:
            print("\n你已退出。")
            print(f"当前得分：{total}")
            return
        total += score
        if ok:
            solved += 1

    print("\n" + "=" * 56)
    print(f"  破案 {solved}/{len(CASES)} 桩，总得分 {total}")
    if solved == len(CASES):
        print("  🏆 全破！你的证据链思维很扎实。")
    elif solved == 2:
        print("  👍 不错，注意「陈述与记录矛盾」往往就是突破口。")
    else:
        print("  🙂 下次先看物证类线索（指纹、记录、规格），它们最难说谎。")
    print("=" * 56)


if __name__ == "__main__":
    main()
