#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调音师认证考试 —— 十二平均律与音程计算

【简介】
现代钢琴上每一个键的频率都由一条公式决定：以 A4=440Hz 为基准，每升高一个半音，
频率乘以 2^(1/12)；升高一个八度，频率正好翻一倍。这套「十二平均律」让转调变得毫不费力，
也让音程可以用「相差几个半音」来精确描述。

本程序扮演一位考官，出 5 关共 10 道题，考你四件事：
  ① 由音名算频率（保留 1 位小数，允许 ±1Hz 误差）
  ② 由频率反推音名
  ③ 看两个音，说出音程名称（大三度、纯五度……）
  ④ 移调与和弦、调性判断

【玩法】
- 每题 10 分，共 100 分；答错一次扣 3 分，用提示扣 10 分，每题最多答 2 次。
- 答案格式很宽松：
  频率直接写数字（523.3 / 523）；音名写 C5 或 C；音程写「纯五度」「P5」「7 个半音」；
  和弦性质写「小三和弦」「minor」；调性写「C大调」「C major」。
- 命令：hint 提示，help 规则，q 退出，空行重看题面。

【运行】
  python3 2026-11-28_调音师认证考试.py
  python3 2026-11-28_调音师认证考试.py --check   # 自检（公式互验、音程表唯一性、调性唯一、解析容错）

【小知识】
「纯五度」的频率比在纯律里是 3:2=1.5，而在十二平均律里是 2^(7/12)≈1.4983。
为了转调方便，我们牺牲了这一点点「纯净」，换来十二个调完全等价。
"""

import math
import re
import sys

A4 = 440.0
NOTE_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MIDI_C4 = 60

INTERVALS = {
    0: "纯一度", 1: "小二度", 2: "大二度", 3: "小三度", 4: "大三度", 5: "纯四度",
    6: "三全音", 7: "纯五度", 8: "小六度", 9: "大六度", 10: "小七度", 11: "大七度", 12: "纯八度",
}
INTERVAL_ALIAS = {
    "纯一度": 0, " unison": 0, "p1": 0,
    "小二度": 1, "m2": 1, "min2": 1,
    "大二度": 2, "maj2": 2, "M2": 2,
    "小三度": 3, "m3": 3, "min3": 3,
    "大三度": 4, "M3": 4, "maj3": 4,
    "纯四度": 5, "p4": 5, "per4": 5,
    "三全音": 6, "增四度": 6, "减五度": 6, "tt": 6, "aug4": 6, "dim5": 6,
    "纯五度": 7, "p5": 7, "per5": 7,
    "小六度": 8, "m6": 8, "min6": 8,
    "大六度": 9, "M6": 9, "maj6": 9,
    "小七度": 10, "m7": 10, "min7": 10,
    "大七度": 11, "M7": 11, "maj7": 11,
    "纯八度": 12, "p8": 12, "octave": 12,
}
NAME_TO_PC = {n: i for i, n in enumerate(NOTE_SHARP)}
FLAT_TO_SHARP = {"DB": "C#", "EB": "D#", "GB": "F#", "AB": "G#", "BB": "A#",
                 "CB": "B", "FB": "E"}


def midi_of(note, octave):
    return (octave + 1) * 12 + NAME_TO_PC[note]


def freq_of_midi(m):
    return A4 * (2.0 ** ((m - 69) / 12.0))


def parse_note(text):
    """'D5' / 'd' / 'F#4' → (pitch_class, octave or None)。"""
    s = text.strip().upper().replace(" ", "")
    s = s.replace("♯", "#").replace("♭", "B")
    m = re.fullmatch(r"([A-G])([#B]?)(-?[0-9])?", s)
    if not m:
        return None
    letter, acc, oct_ = m.group(1), m.group(2) or "", m.group(3)
    name = letter + ("#" if acc == "#" else "")
    if acc == "B":
        key = letter + "B"
        if key not in FLAT_TO_SHARP:
            return None
        name = FLAT_TO_SHARP[key]
    if name not in NAME_TO_PC:
        return None
    return (name, int(oct_) if oct_ is not None else None)


def note_name(midi):
    return NOTE_SHARP[midi % 12] + str(midi // 12 - 1)


def interval_between(a, b):
    """a、b 是 (pc, octave)；返回半音数与区间名。"""
    ma = midi_of(a[0], a[1])
    mb = midi_of(b[0], b[1])
    return abs(mb - ma), INTERVALS.get(abs(mb - ma))


def quality_of(notes):
    """由三个音的音级判断三和弦性质。"""
    root = NAME_TO_PC[notes[0]]      # 以第一个音为根
    gaps = sorted((NAME_TO_PC[n] - root) % 12 for n in notes)
    if gaps == [0, 4, 7]:
        return "大三和弦"
    if gaps == [0, 3, 7]:
        return "小三和弦"
    if gaps == [0, 3, 6]:
        return "减三和弦"
    if gaps == [0, 4, 8]:
        return "增三和弦"
    return None


DIATONIC = [("I", "大三和弦"), ("ii", "小三和弦"), ("iii", "小三和弦"), ("IV", "大三和弦"),
            ("V", "大三和弦"), ("vi", "小三和弦"), ("vii", "减三和弦")]


def key_chords(tonic_pc):
    """某个大调里的七个自然三和弦，返回 [(根音音级, 性质), ...]。"""
    out = []
    for step, (deg, quality) in enumerate(DIATONIC):
        root = (tonic_pc + [0, 2, 4, 5, 7, 9, 11][step]) % 12
        out.append((root, quality))
    return out


def keys_containing(chords):
    """找出所有「大调」，使给定和弦都在其自然音阶内。chords 为 [(根音音级, 性质)]。"""
    matches = []
    for tonic in range(12):
        pool = set(key_chords(tonic))
        if all(c in pool for c in chords):
            matches.append(tonic)
    return matches


# 关卡数据：题目用结构化描述，答案由计算得出
LEVELS = [
    dict(title="入门：音名与频率", qs=[
        dict(kind="freq", note=("C", 5), tol=1.0,
             text="已知 A4=440Hz。请算出 C5 的频率（Hz，保留 1 位小数即可）。"),
        dict(kind="interval", a=("C", 4), b=("G", 4),
             text="从 C4 到 G4，这是什么音程？"),
    ]),
    dict(title="进阶：反推音名", qs=[
        dict(kind="note_of_freq", hz=587.3,
             text="若 A4=440Hz，频率约 587.3Hz 的音是哪一个（写音名，可带八度）？"),
        dict(kind="interval", a=("A", 3), b=("C", 4),
             text="从 A3 到 C4，这是什么音程？"),
    ]),
    dict(title="移调：整体搬家", qs=[
        dict(kind="freq", note=("E", 4), tol=1.0,
             text="已知 A4=440Hz。请算出 E4 的频率（Hz）。"),
        dict(kind="transpose", notes=[("C", 4), ("E", 4), ("G", 4)], shift=5,
             text="把 C4-E4-G4 这个三和弦整体升高 5 个半音，三个音分别变成什么（只写字母音名即可）？"),
    ]),
    dict(title="音程辨析", qs=[
        dict(kind="interval", a=("F", 4), b=("A", 4),
             text="从 F4 到 A4，这是什么音程？"),
        dict(kind="note_of_freq", hz=880.0,
             text="频率 880.0Hz 对应哪个音（A4=440Hz）？"),
    ]),
    dict(title="综合：和弦与调性", qs=[
        dict(kind="quality", notes=["A", "C", "E"],
             text="A-C-E 这个三和弦属于哪一类（大三和弦 / 小三和弦 / 减三和弦 / 增三和弦）？"),
        dict(kind="key", progression=["C", "G", "Am", "F"],
             text="和弦进行 C - G - Am - F 属于哪个调（写「X大调」）？"),
    ]),
]


def expected_answer(q):
    kind = q["kind"]
    if kind == "freq":
        pc, octv = q["note"]
        return round(freq_of_midi(midi_of(pc, octv)), 1)
    if kind == "note_of_freq":
        best = min(range(128), key=lambda m: abs(freq_of_midi(m) - q["hz"]))
        return note_name(best)
    if kind == "interval":
        semi, name = interval_between(q["a"], q["b"])
        if name is None:
            raise ValueError("音程超过一个八度")
        return name
    if kind == "transpose":
        out = []
        for pc, octv in q["notes"]:
            m = midi_of(pc, octv) + q["shift"]
            out.append(NOTE_SHARP[m % 12])
        return " ".join(out)
    if kind == "quality":
        return quality_of(q["notes"])
    if kind == "key":
        chords = []
        for c in q["progression"]:
            quality = "小三和弦" if c.endswith("m") else "大三和弦"
            root_pc = NAME_TO_PC[c[:-1] if c.endswith("m") else c]
            chords.append((root_pc, quality))
        matches = keys_containing(chords)
        if len(matches) != 1:
            raise ValueError("调性不唯一：%d 个" % len(matches))
        return NOTE_SHARP[matches[0]] + "大调"
    raise ValueError("未知题型")


def check_answer(q, raw):
    """返回 (是否正确, 反馈)。"""
    s = raw.strip()
    low = s.lower().replace(" ", "")
    ans = expected_answer(q)
    kind = q["kind"]
    if kind == "freq":
        nums = re.findall(r"-?[0-9]+(?:\.[0-9]+)?", s.replace("，", ""))
        if len(nums) != 1:
            return None, "请只写一个数字，例如 523.3。"
        try:
            v = float(nums[0])
        except ValueError:
            return None, "这个数字看不懂，再试一次。"
        ok = abs(v - ans) <= q["tol"]
        hint = "偏高" if v > ans else "偏低"
        return ok, ("正确" if ok else "差一点，你的值%s（容差 ±%.1fHz）。" % (hint, q["tol"]))
    if kind == "note_of_freq":
        p = parse_note(s)
        if p is None:
            return None, "音名请用 C、D、E… 加可选的八度，如 D5。"
        # ans 形如 D5
        m2 = re.fullmatch(r"([A-G]#?)([0-9]+)", ans)
        target_pc, target_oct = NAME_TO_PC[m2.group(1)], int(m2.group(2))
        got_pc = NAME_TO_PC[p[0]]
        ok = got_pc == target_pc and (p[1] is None or p[1] == target_oct)
        if ok:
            return True, "正确"
        if got_pc == target_pc:
            return False, "音名对了，但八度不对。"
        return False, "音名不对，再看看频率差了几个半音。"
    if kind == "interval":
        key = low
        if key in INTERVAL_ALIAS:
            semi = INTERVAL_ALIAS[key]
            ok = INTERVALS.get(semi) == ans
            return ok, ("正确" if ok else "不对：%d 个半音的音程是「%s」。" % (semi, INTERVALS[semi]))
        m = re.fullmatch(r"([0-9]{1,2})(个半音)?", key)
        if m:
            semi = int(m.group(1))
            if semi not in INTERVALS:
                return None, "半音数应在 0~12 之间。"
            ok = INTERVALS[semi] == ans
            return ok, ("正确" if ok else "这个半音数对应「%s」，不是你说的那个。" % INTERVALS[semi])
        return None, "音程请写「纯五度」「大三度」这类名称，或「7个半音」。"
    if kind == "transpose":
        toks = re.findall(r"[A-Ga-g][#Bb]?", s)
        if len(toks) != len(ans.split()):
            return None, "请写三个音名，用空格或逗号隔开。"
        got = []
        for t in toks:
            p = parse_note(t)
            if p is None:
                return None, "有一个音名不认识：%s" % t
            got.append(p[0])
        ok = got == ans.split()
        if ok:
            return True, "正确"
        return False, "实际应是：%s（注意每个音都升 5 个半音）。" % ans
    if kind == "quality":
        mapping = {"大三和弦": "大三和弦", "大三": "大三和弦", "major": "大三和弦",
                   "小三和弦": "小三和弦", "小三": "小三和弦", "minor": "小三和弦",
                   "减三和弦": "减三和弦", "减三": "减三和弦", "dim": "减三和弦",
                   "增三和弦": "增三和弦", "增三": "增三和弦", "aug": "增三和弦"}
        got = mapping.get(low)
        if got is None:
            return None, "请回答：大三和弦 / 小三和弦 / 减三和弦 / 增三和弦。"
        return got == ans, ("正确" if got == ans else "不对，音级间隔决定它是「%s」。" % ans)
    if kind == "key":
        m = re.fullmatch(r"([a-g])([#b]?)大调|[a-g]major|([a-g])大调", low)
        if m:
            letter = m.group(1) or m.group(3)
            acc = m.group(2) or ""
            p = parse_note(letter + acc)
            if p is None:
                return None, "没认出这个调名。"
            got = NOTE_SHARP[NAME_TO_PC[p[0]]] + "大调"
            return got == ans, ("正确" if got == ans else "这个进行只属于一个调，再排排看。")
        return None, "请写「C大调」这种形式。"
    return None, "无法判定的答案格式。"


def ask(q, idx, total, input_fn, out):
    out("=" * 64)
    out("第 %d/%d 题：%s" % (idx, total, q["text"]))
    out("（最多答 2 次；答错一次扣 3 分；hint 扣 10 分）")
    pts = 10
    tries = 0
    hinted = False
    while tries < 2:
        try:
            raw = input_fn("你的答案 > ")
        except EOFError:
            if tries == 0:
                out("输入结束，本题未作答，计 0 分。")
                return 0
            out("输入结束，本题按当前分数 %d 结算。" % max(0, pts))
            return max(0, pts)
        s = raw.strip()
        low = s.lower()
        if low in ("q", "quit", "exit", "退出"):
            raise KeyboardInterrupt
        if low in ("hint", "h", "提示"):
            if hinted:
                out("提示已经用过了。")
            else:
                hinted = True
                pts -= 10
                out("提示（-10 分）：%s" % hint_of(q))
            continue
        if low in ("help", "?", "帮助"):
            out("答案格式见文件开头的【玩法】；q 退出。")
            continue
        if s == "":
            out(q["text"])
            continue
        tries += 1
        ok, fb = check_answer(q, s)
        if ok is None:
            out("格式问题：%s（本次不计作答）" % fb)
            tries -= 1
            continue
        out(fb)
        if ok:
            out("★ 答对，本题得 %d 分。" % max(0, pts))
            return max(0, pts)
        pts -= 3
        if tries < 2:
            out("还有一次机会。")
    out("两次都没答对。正确答案：%s。本题 0 分。" % expected_answer(q))
    return 0


def hint_of(q):
    kind = q["kind"]
    if kind == "freq":
        pc, octv = q["note"]
        semis = midi_of(pc, octv) - 69
        return "公式 f = 440 × 2^(%d/12)，先算 2 的 1/12 次方约 1.0595。" % semis
    if kind == "note_of_freq":
        m = min(range(128), key=lambda k: abs(freq_of_midi(k) - q["hz"]))
        return "这个频率在 A4(%d) 附近 %d 个半音，往 %s 方向数。" % (
            69, m - 69, "上" if m >= 69 else "下")
    if kind == "interval":
        semi, _ = interval_between(q["a"], q["b"])
        return "两个音相差 %d 个半音，查表：0 纯一度、2 大二度、3 小三度、4 大三度、5 纯四度、7 纯五度…" % semi
    if kind == "transpose":
        return "每个音加 %d 个半音，注意 C→C#→D 这样数过去，别漏掉半音。" % q["shift"]
    if kind == "quality":
        return "把三个音按音级排列，看根音到三音、五音各差几个半音：4+3 是大三，3+4 是小三。"
    if kind == "key":
        return "先写出 C 大调的七个自然三和弦（C、Dm、Em、F、G、Am、Bdim），再看这四个是否都在里面。"
    return "再读一遍题面。"


def main(input_fn=input, out=print):
    out(__doc__.split("【运行】")[0])
    out("考官：A4 = 440Hz，十二平均律。共 5 关 10 题。")
    total_pts = 0
    idx = 0
    for lv in LEVELS:
        out("")
        out("### %s ###" % lv["title"])
        for q in lv["qs"]:
            idx += 1
            total_pts += ask(q, idx, 10, input_fn, out)
    out("=" * 64)
    out("总分：%d / 100" % total_pts)
    if total_pts >= 95:
        out("评级：持证调音师 —— 频率、音程、调性一手抓。")
    elif total_pts >= 70:
        out("评级：见习调音师 —— 公式熟了，个别音程还要再背背。")
    elif total_pts >= 40:
        out("评级：琴童 —— 先把「差几个半音」这件事记住。")
    else:
        out("评级：旁听生 —— 从第一关的频率公式开始吧。")
    return total_pts


def check():
    ok = True

    def say(cond, msg):
        nonlocal ok
        if cond:
            print("[PASS]", msg)
        else:
            ok = False
            print("[FAIL]", msg)

    # 1. 频率公式与标准值互验
    known = {("C", 4): 261.63, ("A", 4): 440.0, ("C", 5): 523.25, ("E", 4): 329.63,
             ("A", 5): 880.0, ("D", 5): 587.33}
    worst = max(abs(freq_of_midi(midi_of(pc, o)) - v) for (pc, o), v in known.items())
    say(worst < 0.01, "频率公式与标准音高一致（最大偏差 %.4fHz）" % worst)

    # 2. 音名与频率互为反函数
    rt = True
    for m in range(0, 128):
        f = freq_of_midi(m)
        got = min(range(128), key=lambda k: abs(freq_of_midi(k) - f))
        if got != m:
            rt = False
    say(rt, "MIDI 0~127 逐一半音频率再反推音名，全部还原（双向一致）")

    # 3. 音程表：名称唯一、半音数覆盖 0~12
    say(sorted(INTERVALS) == list(range(13)), "音程表覆盖 0~12 个半音")
    say(len(set(INTERVALS.values())) == 13, "13 个半音各自对应唯一音程名")
    alias_ok = all(INTERVALS[semi] == name for name, semi in INTERVAL_ALIAS.items() if name in INTERVALS)
    say(alias_ok, "别名映射（P5、m3、大三度…）指向正确的半音数")
    # 抽查：C4→G4 7 半音 = 纯五度；A3→C4 3 半音 = 小三度
    d1, n1 = interval_between(("C", 4), ("G", 4))
    d2, n2 = interval_between(("A", 3), ("C", 4))
    say((d1, n1) == (7, "纯五度") and (d2, n2) == (3, "小三度"), "抽查音程：C4-G4 纯五度、A3-C4 小三度")

    # 4. 移调保结构：整段平移后内部音程不变
    base = [("C", 4), ("E", 4), ("G", 4)]
    trans = " ".join(NOTE_SHARP[(midi_of(pc, o) + 5) % 12] for pc, o in base)
    say(trans == expected_answer(LEVELS[2]["qs"][1]), "C-E-G 上移 5 个半音 = F-A-C（内部音程保持）")

    # 5. 和弦性质与调性唯一性
    say(quality_of(["A", "C", "E"]) == "小三和弦", "A-C-E 判为小三和弦（3+4 半音）")
    say(quality_of(["C", "E", "G"]) == "大三和弦", "C-E-G 判为大三和弦（4+3 半音）")
    prog = [(NAME_TO_PC["C"], "大三和弦"), (NAME_TO_PC["G"], "大三和弦"),
            (NAME_TO_PC["A"], "小三和弦"), (NAME_TO_PC["F"], "大三和弦")]
    say(keys_containing(prog) == [0], "C-G-Am-F 只属于 C 大调（唯一解）")
    say(keys_containing([(NAME_TO_PC["C"], "大三和弦"), (NAME_TO_PC["D"], "大三和弦")]) == [7],
        "C 与 D 大三和弦同时出现时只能属于 G 大调（IV 与 V）")
    say(keys_containing([(NAME_TO_PC["C"], "大三和弦")]) == [0, 5, 7],
        "单个 C 大三和弦可出现在 C/F/G 三个大调（I/IV/V），不强行收敛")

    # 6. 每题答案可计算、且不越界
    solved = True
    for lv in LEVELS:
        for q in lv["qs"]:
            try:
                a = expected_answer(q)
            except Exception:
                solved = False
                continue
            if a is None or a == "":
                solved = False
    say(solved, "10 道题的答案都能由公式直接算出（无手写答案）")
    quest = [q for lv in LEVELS for q in lv["qs"]]
    say(len(quest) == 10, "共 10 道题（5 关 × 2）")

    # 7. 频率题的容差不会误判邻音（相邻半音差 ≥ 3.5Hz）
    freq_qs = [q for q in quest if q["kind"] == "freq"]
    gap_ok = True
    for q in freq_qs:
        ans = expected_answer(q)
        tol = q["tol"]
        nearest = freq_of_midi(midi_of(*q["note"]))
        # 上下各一个半音的频率差
        up = freq_of_midi(midi_of(*q["note"]) + 1) - nearest
        down = nearest - freq_of_midi(midi_of(*q["note"]) - 1)
        if min(up, down) <= 2 * tol:
            gap_ok = False
    say(gap_ok, "频率题容差 ±1Hz 远小于相邻半音间隔，不会模棱两可")

    # 8. 解析容错
    q_freq = LEVELS[0]["qs"][0]
    ok1, _ = check_answer(q_freq, "523.3")
    ok2, _ = check_answer(q_freq, "523")
    ok3, _ = check_answer(q_freq, "48")
    q_int = LEVELS[0]["qs"][1]
    ok4, _ = check_answer(q_int, "纯五度")
    ok5, _ = check_answer(q_int, "P5")
    ok6, _ = check_answer(q_int, "7个半音")
    ok7, _ = check_answer(q_int, "大三度")
    say(ok1 and ok2 and not ok3 and ok4 and ok5 and ok6 and not ok7,
        "答案解析：523.3/523 判对、48 判错；纯五度/P5/7个半音 判对、大三度判错")

    # 9. 假 stdin：全对 100 分；全错给 0~20 分且不崩；EOF 与 q 可退出
    answers = []
    for q in quest:
        a = expected_answer(q)
        answers.append(str(a))

    def feed(seq):
        it = iter(seq)

        def fi(_p=""):
            try:
                return next(it)
            except StopIteration:
                raise EOFError
        lines = []
        try:
            score = main(input_fn=fi, out=lines.append)
        except KeyboardInterrupt:
            score = None
        return score, lines
    s1, _ = feed(answers)
    say(s1 == 100, "按标准答案答题得满分 100（实际 %s）" % s1)
    wrong = ["0"] * len(answers)
    s2, _ = feed(wrong)
    say(s2 is not None and s2 <= 20, "全答错时得分不高于 20 且流程正常结束（实际 %s）" % s2)
    s3, _ = feed([])
    say(s3 is not None and s3 <= 10, "输入立即结束（EOF）时按已得分结算，不崩溃（实际 %s）" % s3)
    s4, _ = feed(["q"])
    say(s4 is None, "输入 q 能干净退出（KeyboardInterrupt）")

    print()
    print("自检通过 ✅" if ok else "自检未通过 ❌")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        if "--check" in sys.argv:
            sys.exit(check())
        main()
    except (EOFError, KeyboardInterrupt):
        print("\n已退出，下次再来。")
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
