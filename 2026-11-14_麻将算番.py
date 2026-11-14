# -*- coding: utf-8 -*-
"""
麻将算番小课堂（7 手牌 · 判断「和没和」+ 算番）
====================================================
给你一手 14 张牌，你要回答两件事：
  1）这手牌到底和不和？
  2）如果和了，按下面的简化番表，它是几番？

简化番表（本游戏专用，只算这几项）：
  平胡（四顺子 + 一对将）      1 番（只有在没有其他番时才算）
  碰碰胡（四刻子 + 一对将）    2 番
  七对                         4 番
  十三幺                       13 番
  大三元（中、发、白 各三张）  +8 番，可与碰碰胡叠加
  清一色（全是一门的牌，无字牌） +6 番
  混一色（一门牌 + 字牌）       +2 番

输入格式：
  不和                → 认为这手牌没和
  5                   → 认为和了，且是 5 番
  hint                → 显示这手牌和不和（本题 −30 分）
  table               → 再看一次番表
  q                   → 退出

计分：每题 100 分，答对得满分，答错 0 分。
运行：python3 2026-11-14_麻将算番.py
"""

from collections import Counter

SUITS = "万条饼"
ZI = "东南西北中发白"

HANDS = [
    ("123万456万789万123条55条", "标准牌型，两门花色，只有顺子"),
    ("111万333万555万777条99条", "四组刻子加一对将"),
    ("123条234条567条789条88条", "整手牌只有条子"),
    ("11万22万33条44条55饼66饼东东", "七种牌各一对"),
    ("1万9万1条9条1饼9饼东南西北中发白中", "老牌型：十三幺"),
    ("中中中发发发白白白111万55条", "字牌三巨头各三张，全刻子"),
    ("123万456万789万123条5条9饼", "看起来挺整齐，其实……"),
]


def parse(hand):
    tiles = []
    buf = ""
    for ch in hand:
        if ch.isdigit():
            buf += ch
        elif ch in SUITS:
            for d in buf:
                tiles.append((ch, int(d)))
            buf = ""
        elif ch in ZI:
            tiles.append(("字", ZI.index(ch) + 1))
            buf = ""
    if buf:
        raise ValueError("数字后面缺少花色")
    return tiles


def render(tiles):
    groups = {}
    order = []
    for s, n in sorted(tiles, key=lambda t: (["万", "条", "饼", "字"].index(t[0]), t[1])):
        if s not in groups:
            groups[s] = []
            order.append(s)
        groups[s].append(str(n) if s != "字" else ZI[n - 1])
    parts = []
    for s in order:
        body = "".join(groups[s])
        parts.append(body + (s if s != "字" else ""))
    return " ".join(parts)


def can_melds(cnt):
    """剩余牌能否全部拆成刻子/顺子（计数为 0 的牌视为已用完）。"""
    alive = [t for t, v in cnt.items() if v > 0]
    if not alive:
        return True
    tile = min(alive)
    if cnt[tile] >= 3:
        cnt[tile] -= 3
        if can_melds(cnt):
            cnt[tile] += 3
            return True
        cnt[tile] += 3
    suit, num = tile
    if suit != "字" and num <= 7:
        seq = [(suit, num), (suit, num + 1), (suit, num + 2)]
        if all(cnt[t] >= 1 for t in seq):
            for t in seq:
                cnt[t] -= 1
            if can_melds(cnt):
                for t in seq:
                    cnt[t] += 1
                return True
            for t in seq:
                cnt[t] += 1
    return False


def is_standard(cnt):
    for pair in list(cnt):
        if cnt[pair] >= 2:
            cnt[pair] -= 2
            ok = can_melds(cnt)
            cnt[pair] += 2
            if ok:
                return True
    return False


def is_seven_pairs(cnt):
    return sum(v // 2 for v in cnt.values()) == 7 and all(v % 2 == 0 for v in cnt.values())


def is_thirteen_orphans(cnt):
    need = set()
    for suit in ("万", "条", "饼"):
        need.add((suit, 1))
        need.add((suit, 9))
    for i in range(1, 8):
        need.add(("字", i))
    if set(cnt) != need or len(cnt) != 13:
        return False
    return sum(cnt.values()) == 14 and max(cnt.values()) == 2


def is_pung(cnt):
    """碰碰胡：所有牌都是刻子，只留一对将（计数为 3 或 2，且恰好一个 2）。"""
    vals = list(cnt.values())
    return sum(vals) == 14 and vals.count(2) == 1 and all(v in (2, 3) for v in vals)


def analyze(tiles):
    """返回 (牌型名称, 番数)；不和返回 (None, 0)。"""
    cnt = Counter(tiles)
    if len(tiles) != 14:
        return None, 0
    if is_thirteen_orphans(cnt):
        return "十三幺", 13
    if is_seven_pairs(cnt):
        fp = 4 + (6 if all(s != "字" for s, _ in tiles) and len({s for s, _ in tiles}) == 1 else 0)
        if len({s for s, _ in tiles} - {"字"}) == 1 and "字" in {s for s, _ in tiles}:
            fp += 2
        return "七对", fp
    if not is_standard(cnt):
        return None, 0

    fan = 0
    suits = {s for s, _ in tiles}
    if "字" not in suits and len(suits) == 1:
        fan += 6
    elif "字" in suits and len(suits - {"字"}) == 1:
        fan += 2
    big_three = all(cnt.get(("字", i), 0) >= 3 for i in (5, 6, 7))
    if big_three:
        fan += 8
    if is_pung(cnt):
        fan += 2
        name = "碰碰胡"
    else:
        name = "平胡"
        if fan == 0:
            fan = 1
    return name, fan


def show_table():
    print("""
  番表（简化版）
    平胡 1 番（无其他番时才算）      碰碰胡 2 番
    七对 4 番                        十三幺 13 番
    大三元 +8 番                     清一色 +6 番
    混一色 +2 番
""")


def play():
    print("=" * 62)
    print("      🀄 麻将算番小课堂")
    print("=" * 62)
    print("七手牌，每手回答「和不和」以及「几番」。输入 table 看番表，hint 看答案（−30）。")
    total = 0
    right = 0

    for idx, (hand, _desc) in enumerate(HANDS, 1):
        tiles = parse(hand)
        kind, fan = analyze(tiles)
        score = 100
        print("\n" + "-" * 62)
        print(f"  第 {idx} 手：{render(tiles)}")
        print("  这手牌和不和？和的话是几番？（输入番数，或输入 不和）")

        while True:
            try:
                raw = input("  > ").strip()
            except EOFError:
                print("\n输入中断，提前结算。")
                return report(total, right)
            low = raw.lower()
            if low in ("q", "quit"):
                return report(total, right)
            if low == "table":
                show_table()
                continue
            if low == "hint":
                if score >= 30:
                    score -= 30
                print(f"  提示：{'这手牌和了' if kind else '这手牌没和'}（本题剩 {score} 分）")
                continue

            if raw in ("不和", "没和", "否", "no"):
                answer = 0
            elif raw.isdigit():
                answer = int(raw)
            else:
                print("  输入「不和」或者一个番数（数字），也可以输入 hint。")
                continue

            expect = fan if kind else 0
            if answer == expect:
                print(f"  ✅ 正确！{'不和' if expect == 0 else f'{kind}，{expect} 番'}。")
                total += score
                right += 1
            else:
                print(f"  ❌ 不对。正确结果：{'不和' if not kind else f'{kind}，{expect} 番'}。")
                if kind and answer == 0:
                    print("  （这手牌其实是和的，只是你判定为不和。）")
                elif not kind and answer > 0:
                    print("  （这手牌凑不出四面子一将，也没有七对/十三幺。）")
            break

    return report(total, right)


def report(total, right):
    print("\n" + "=" * 62)
    print(f"  结算：{right}/{len(HANDS)} 手正确，总分 {total}/{len(HANDS) * 100}")
    if total >= 600:
        print("  🏆 可以上桌算番了。")
    elif total >= 300:
        print("  👍 牌型认得清，再练练番数叠加。")
    else:
        print("  🙂 建议先记三种结构：四面子一将、七对、十三幺。")
    print("=" * 62)
    return total


if __name__ == "__main__":
    play()
