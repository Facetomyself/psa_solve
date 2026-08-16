# -*- coding: utf-8 -*-
"""fo 载荷字段结构对比：Node 补环境 vs RuyiDOM 诊断层（分支缺失检查）。

载荷是分支执行的产物：$ 分隔字段数与各字段形态反映求解链走了哪些分支。
用法：python compare_payload.py <body1> <body2>
"""
import sys


def analyze(body):
    parts = body.split("$")
    return {
        "fields": len(parts),
        "lens": [len(p) for p in parts],
        "head": [p[:24] for p in parts[:12]],
    }


def main():
    if len(sys.argv) < 3:
        print("usage: python compare_payload.py <body1> <body2>")
        sys.exit(2)
    a, b = analyze(sys.argv[1]), analyze(sys.argv[2])
    print("body1:", a)
    print("body2:", b)
    if a["fields"] != b["fields"]:
        print(f"字段数不一致：{a['fields']} vs {b['fields']} —— 分支缺失嫌疑")
    else:
        print(f"字段数一致：{a['fields']}")
    # 长度分布对比
    if a["lens"] != b["lens"]:
        print("字段长度分布不同：")
        for i, (la, lb) in enumerate(zip(a["lens"], b["lens"])):
            if la != lb:
                print(f"  field[{i}]: {la} vs {lb}")


if __name__ == "__main__":
    main()
