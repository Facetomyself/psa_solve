#!/usr/bin/env python3
"""loop_scan.py — 扫描 orchestrate 里的 for 循环头（与 run.js CF_LOOPGUARD 同一算法）。

列出所有 for(...;true;/!0;) 循环的 id/偏移/init/inc，用于把全局 __lc 计数
映射回具体循环。用法：python -X utf8 loop_scan.py <orchestrate.js> [id...]
"""
import re
import sys

BS = chr(92)  # backslash


def scan(src):
    n = len(src)
    i = 0
    metas = []
    while i < n:
        idx = src.find("for", i)
        if idx < 0:
            break
        prev = src[idx - 1] if idx > 0 else ""
        after = src[idx + 3:idx + 40]
        if (prev.isalnum() or prev in "_$") or not re.match(r"^\s*\(", after or " "):
            i = idx + 3
            continue
        j = idx + 3
        while j < n and src[j].isspace():
            j += 1
        if src[j] != "(":
            i = idx + 3
            continue
        depth = 0
        k = j
        instr = None
        esc = False
        while k < n:
            ch = src[k]
            if instr:
                if esc:
                    esc = False
                elif ch == BS:
                    esc = True
                elif ch == instr:
                    instr = None
            else:
                if ch in "'\"`":
                    instr = ch
                elif ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0:
                        break
            k += 1
        if depth != 0:
            i = k + 1
            continue
        header = src[j + 1:k]
        parts = []
        cur = ""
        depth = 0
        instr = None
        esc = False
        for ch in header:
            if instr:
                cur += ch
                if esc:
                    esc = False
                elif ch == BS:
                    esc = True
                elif ch == instr:
                    instr = None
                continue
            if ch in "'\"`":
                instr = ch
                cur += ch
                continue
            if ch in "([{":
                depth += 1
            if ch in ")]}":
                depth -= 1
            if ch == ";" and depth == 0:
                parts.append(cur)
                cur = ""
                continue
            cur += ch
        parts.append(cur)
        if len(parts) == 3 and parts[1].strip() in ("true", "!0"):
            metas.append((len(metas), j, parts[0], parts[1], parts[2]))
        i = k + 1
    return metas, src


def main():
    path = sys.argv[1]
    src = open(path, "rb").read().decode("latin1")
    metas, _ = scan(src)
    want = {int(x) for x in sys.argv[2:]} if len(sys.argv) > 2 else None
    print("total", len(metas))
    for m in metas:
        mid, at, init, cond, inc = m
        if want is not None and mid not in want:
            continue
        print("#%d at %d cond=%s" % (mid, at, cond))
        print("  init=%r" % init[:200])
        print("  inc =%r" % inc[:120])


if __name__ == "__main__":
    main()
