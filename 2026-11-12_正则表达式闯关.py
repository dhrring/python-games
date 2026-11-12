# -*- coding: utf-8 -*-
"""
正则表达式闯关（8 关 · 用一条正则同时说服「该匹配的」和「不该匹配的」）
=====================================================================
每一关给你两批样本：
  ✅ 必须匹配（yes）   ❌ 必须拒绝（no）
你要写出唯一一条正则，用 Python 的 re.fullmatch 去跑这批样本，
全部答对才算过关。程序会逐条告诉你哪条错了、错在哪。

玩法：
  直接输入正则表达式回车提交（不要加引号、不要写 /.../ 这种斜杠包裹）。
  输入 hint  看本题提示（扣 30 分）
  输入 show  重新打印本关样本
  输入 skip  跳过本关（本题得 0 分）
  输入 q     退出
评分：每题基准 100 分；看提示扣 30；每错一次扣 10；最低保底 20 分。

运行：python3 2026-11-12_正则表达式闯关.py
"""

import re

LEVELS = [
    {
        "title": "第 1 关 · 四位年份",
        "task": "匹配一个四位数（年份），不能多也不能少。",
        "yes": ["1999", "2024", "0850"],
        "no": ["19", "20245", "abc", "19a9"],
        "hint": r"恰好四位数字：\d 重复 4 次。别忘了 fullmatch 要求整串匹配。",
        "solution": r"\d{4}",
    },
    {
        "title": "第 2 关 · 纯小写单词",
        "task": "匹配只由小写英文字母组成的单词，长度至少 2。",
        "yes": ["hello", "ab", "python"],
        "no": ["Hello", "hello1", "a", "hello world"],
        "hint": r"小写字母集合是 a-z，量词用 {2,}。",
        "solution": r"[a-z]{2,}",
    },
    {
        "title": "第 3 关 · 中国大陆手机号",
        "task": "匹配 11 位手机号：必须以 1 开头，后面 10 位都是数字。",
        "yes": ["13800138000", "19912345678"],
        "no": ["23800138000", "1380013800", "138001380001", "1380013800a"],
        "hint": r"先写死开头的 1，再接 10 个数字：1\d{10}。",
        "solution": r"1\d{10}",
    },
    {
        "title": "第 4 关 · 简易邮箱",
        "task": "匹配形如 用户名@域名.后缀 的邮箱：用户名和域名只含字母数字，后缀只能是 com 或 cn。",
        "yes": ["hori@qq.com", "a1@abc.cn"],
        "no": ["hori@qq", "hori@qq.net", "@qq.com", "hori@.com"],
        "hint": r"用户名部分 [A-Za-z0-9]+，@ 要转义吗？不用，@ 不是元字符。后缀用 (com|cn)。",
        "solution": r"[A-Za-z0-9]+@[A-Za-z0-9]+\.(com|cn)",
    },
    {
        "title": "第 5 关 · 标准日期格式",
        "task": "匹配 YYYY-MM-DD 格式：4 位年、横线、2 位月、横线、2 位日（只校验格式，不校验大小月）。",
        "yes": ["2024-01-05", "1999-12-31"],
        "no": ["2024-1-5", "2024/01/05", "24-01-05", "2024-01-05x"],
        "hint": r"三段数字，用 - 连接，月份和日期都恰好 2 位。横线是普通字符，不需要转义。",
        "solution": r"\d{4}-\d{2}-\d{2}",
    },
    {
        "title": "第 6 关 · 连续重复字符",
        "task": "匹配「同一个字符连续出现 2 次以上」的字符串（整串都是这个字符），例如 aaa、zzzz。",
        "yes": ["aa", "zzzz", "000"],
        "no": ["ab", "a1", "a"],
        "hint": r"反向引用：先用 (...) 捕获一个字符，再用 \1 引用它，量词 + 表示至少再来一次。",
        "solution": r"([a-z0-9])\1+",
    },
    {
        "title": "第 7 关 · 首字母大写的单词",
        "task": "匹配「一个大写字母开头 + 若干小写字母」的单词，至少 2 个字符。",
        "yes": ["Hello", "Ab", "Python"],
        "no": ["hello", "H", "Hello1", "HELLO"],
        "hint": r"大写字母 [A-Z]，后面跟 1 个以上小写字母。",
        "solution": r"[A-Z][a-z]+",
    },
    {
        "title": "第 8 关 · 纯汉字",
        "task": "匹配只由汉字组成的字符串（不含标点、数字、字母），长度至少 1。",
        "yes": ["汉字", "正则表达式"],
        "no": ["abc", "汉字1", "汉 字"],
        "hint": r"汉字在 Unicode 里大致落在 \u4e00-\u9fa5，用字符范围 [\u4e00-\u9fa5]+。",
        "solution": r"[\u4e00-\u9fa5]+",
    },
]


def check(pattern, level):
    """返回 (是否通过, 失败明细列表)。"""
    try:
        compiled = re.compile(pattern)
    except re.error as e:
        return False, [f"正则语法错误：{e}"]
    fails = []
    for s in level["yes"]:
        if compiled.fullmatch(s) is None:
            fails.append(f"  ✗ 「{s}」应该匹配，但没匹配上")
    for s in level["no"]:
        if compiled.fullmatch(s) is not None:
            fails.append(f"  ✗ 「{s}」不该匹配，却被匹配了")
    return (not fails), fails


def show_samples(level):
    print("  ✅ 必须匹配：", "  ".join(f"「{s}」" for s in level["yes"]))
    print("  ❌ 必须拒绝：", "  ".join(f"「{s}」" for s in level["no"]))


def main():
    print("=" * 62)
    print("        🧩 正则表达式闯关")
    print("=" * 62)
    print("提示：每关只要一条正则就能同时搞定「该匹配」和「不该匹配」两批样本。")
    print("      可能要先想清楚边界，而不是急着写。")

    total = 0
    passed_levels = 0
    for idx, level in enumerate(LEVELS):
        score = 100
        print("\n" + "=" * 62)
        print(f"  {level['title']}：{level['task']}")
        show_samples(level)

        while True:
            raw = input("\n  输入正则（hint=提示 / show=样本 / skip=跳过 / q=退出）：").strip()
            if raw.lower() in ("q", "quit", "exit"):
                print(f"\n你已退出。本次总分 {total} 分，通过 {passed_levels}/{len(LEVELS)} 关。")
                return
            if raw.lower() == "show":
                show_samples(level)
                continue
            if raw.lower() == "skip":
                print(f"  已跳过本关（本题 0 分）。参考答案：{level['solution']}")
                break
            if raw.lower() == "hint":
                score = max(20, score - 30)
                print(f"  💡 {level['hint']}")
                continue
            if not raw:
                print("  正则为空，请重新输入。")
                continue
            if len(raw) > 200:
                print("  正则太长了，精简一下（最多 200 字符）。")
                continue

            ok, fails = check(raw, level)
            if ok:
                total += score
                passed_levels += 1
                print(f"  ✅ 全对！本题得 {score} 分，累计 {total} 分。")
                break
            score = max(20, score - 10)
            print(f"  ❌ 有 {len(fails)} 处不符（本题当前价值 {score} 分）：")
            for f in fails:
                print(f)

    print("\n" + "=" * 62)
    print(f"  通关 {passed_levels}/{len(LEVELS)} 关，总分 {total} 分")
    if passed_levels == len(LEVELS) and total >= 700:
        print("  🏆 正则大师！你已经掌握了字符类、量词、分组和反向引用。")
    elif passed_levels == len(LEVELS):
        print("  👍 八关全通，只是提示用得有点多。")
    else:
        print("  🙂 下次可以试试不看提示通关。")
    print("  参考：反向引用 \\1 和字符范围 [\\u4e00-\\u9fa5] 是这两类题的常用解法。")
    print("=" * 62)


if __name__ == "__main__":
    main()
