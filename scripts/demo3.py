# -*- coding: utf-8 -*-
"""
demo3.py — cf_clearance 跨 session 复用验证实验

实验设计（求证官方文档的「(IP+UA+TLS) 绑定」模型）：
  Phase 1: 会话 A 串行请求直到触发 429（rate limit challenge）
  Phase 2: 调用求解链拿 cf_clearance（同 IP + 同 UA + 同 TLS 指纹）
  Phase 3: 全新会话 B 带 clearance 请求已知 200 的 sn
           全新会话 C 不带 clearance 请求同一 sn（对照）
  Phase 4: 会话 B 带 clearance 继续串行采集，测续航

判定：
  B 通过 且 C 被拦 -> clearance 跨 session 复用有效（IP+UA+TLS 绑定模型证实）
  B 被拦          -> 存在会话级额外绑定，模型需修正
  C 通过          -> 对照组未触发挑战（计数器已衰减），实验无效需重跑

用法：python demo3.py [--sn 143963534] [--gap 0.1] [--max-trigger 60] [--verify-count 30]
"""
import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime

from curl_cffi import requests as cr

ROOT = r"D:\reverse_ENV\workspace\psa_solve"
RUNTIME_DIR = os.path.join(ROOT, "runtime")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
MATERIAL_ROOT = os.path.join(ROOT, "challenge-material")
NODE = r"D:\reverse_ENV\tools\node\node.exe"
PYTHON = r"D:\reverse_ENV\.venv\Scripts\python.exe"
TARGET = "https://www.psacard.com/cert/{sn}/psa"
UA_FF = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0"
IMPERSONATE = "firefox"


def log(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    tag = {"info": " .. ", "ok": " OK ", "bad": " !! ", "step": ">>> "}[level]
    print(f"[{ts}] {tag}{msg}", flush=True)


def fetch_page(session, sn, cookies=None, timeout=20):
    """单次请求。返回 (status, blocked, meta)。meta 为被拦时的诊断头。"""
    h = {
        "User-Agent": UA_FF,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = session.get(TARGET.format(sn=sn), headers=h, timeout=timeout, cookies=cookies)
    except Exception:
        return 0, True, {}
    title_m = re.search(rb"<title>([^<]*)</title>", r.content[:3000])
    title = title_m.group(1).decode("utf-8", "replace").strip() if title_m else ""
    blocked = r.status_code in (403, 429) or "Just a moment" in title
    meta = {}
    if blocked:
        meta = {
            "server": r.headers.get("server", ""),
            "cf-ray": r.headers.get("cf-ray", ""),
            "cf-mitigated": r.headers.get("cf-mitigated", ""),
            "retry-after": r.headers.get("retry-after", ""),
            "content-length": r.headers.get("content-length", ""),
        }
    return r.status_code, blocked, meta


def bypass_solve():
    """风控后求解：抓材料 + Node 求解载荷 + Firefox 指纹提交 -> cookie dict。"""
    r = subprocess.run([PYTHON, os.path.join(SCRIPTS_DIR, "fetch_material.py")],
                       capture_output=True, text=True, timeout=90)
    epochs = [d for d in os.listdir(MATERIAL_ROOT)
              if os.path.isfile(os.path.join(MATERIAL_ROOT, d, "manifest.json"))]
    epoch = sorted(epochs)[-1]
    m = json.load(open(os.path.join(MATERIAL_ROOT, epoch, "manifest.json"), encoding="utf-8"))
    bm = m["cfBm"][0].split(";")[0]

    r = subprocess.run(
        [NODE, os.path.join(RUNTIME_DIR, "run.js"),
         os.path.join(MATERIAL_ROOT, epoch, "challenge-page.html"),
         os.path.join(MATERIAL_ROOT, epoch, "chl-page-orchestrate.js"), bm],
        capture_output=True, text=True, timeout=120)
    result = None
    for line in r.stdout.strip().splitlines():
        if line.strip().startswith("{"):
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                pass
    if not result or not result.get("submits"):
        return None
    last = result["submits"][-1]
    url = last["url"]
    if url.startswith("/"):
        url = "https://www.psacard.com" + url

    ff_headers = {
        "User-Agent": UA_FF,
        "Accept": "*/*",
        "Content-Type": "text/plain",
    }
    ck = {"__cf_bm": bm.split("=", 1)[1]}
    r = cr.post(url, data=last["fullBody"], headers=ff_headers, cookies=ck,
                impersonate=IMPERSONATE, timeout=30)
    clearance = ""
    for part in (r.headers.get("set-cookie", "") or "").split(","):
        part = part.strip()
        if part.startswith("cf_clearance="):
            clearance = part.split(";")[0]
        if part.startswith("__cf_bm="):
            ck["__cf_bm"] = part.split(";")[0].split("=", 1)[1]
    if not clearance:
        return None
    ck["cf_clearance"] = clearance.split("=", 1)[1]
    return ck


def main():
    parser = argparse.ArgumentParser(description="cf_clearance 跨 session 复用验证实验")
    parser.add_argument("--sn", type=int, default=143963534, help="验证用证书编号（须已知返回 200）")
    parser.add_argument("--gap", type=float, default=0.1, help="触发阶段请求间隔（秒）")
    parser.add_argument("--max-trigger", type=int, default=60, help="触发阶段最大请求数")
    parser.add_argument("--control-probes", type=int, default=5, help="Phase 3 对照组 C 连续请求数")
    parser.add_argument("--verify-count", type=int, default=30, help="Phase 4 续航请求数")
    parser.add_argument("--verify-gap", type=float, default=0.2, help="Phase 4 续航请求间隔（秒）")
    args = parser.parse_args()

    result = {"schema": "demo3-experiment.v1", "phases": {}}

    # Phase 0: 基线确认目标 sn 当前状态（带挑战状态则提醒）
    log("Phase 0: 基线——全新会话请求验证目标（预期 200）", "step")
    s0 = cr.Session(impersonate=IMPERSONATE)
    st0, blk0, meta0 = fetch_page(s0, args.sn)
    log(f"基线 {args.sn}: {st0}" + (" 被拦（IP 当前带挑战状态，建议稍后重跑）" if blk0 else ""),
        "ok" if st0 == 200 else "bad")
    result["phases"]["baseline"] = {"sn": args.sn, "status": st0, "blocked": blk0}
    if st0 == 200:
        last_ok_sn = args.sn
    else:
        log("基线不是 200，Phase 3 对照结果解释需留意", "bad")
        last_ok_sn = args.sn

    # Phase 1: 会话 A 串行请求直到触发 429
    log(f"Phase 1: 会话 A 串行请求直到触发 429（间隔 {args.gap}s，上限 {args.max_trigger}）", "step")
    sa = cr.Session(impersonate=IMPERSONATE)
    sn_base = args.sn
    triggered = False
    for i in range(args.max_trigger):
        sn = sn_base + i * 3
        st, blocked, meta = fetch_page(sa, sn)
        if blocked:
            meta_s = "  ".join(f"{k}={v}" for k, v in meta.items() if v) or "（无诊断头）"
            log(f"[{i+1}/{args.max_trigger}] {sn}: {st} 触发挑战 | {meta_s}", "bad")
            triggered = True
            result["phases"]["trigger"] = {
                "requests_before": i, "sn": sn, "status": st, "meta": meta}
            break
        log(f"[{i+1}/{args.max_trigger}] {sn}: {st} 通过", "ok")
        if st == 200:
            last_ok_sn = sn
        time.sleep(args.gap)
    if not triggered:
        log(f"未触发挑战（{args.max_trigger} 次请求内），实验提前结束", "bad")
        result["phases"]["trigger"] = {"triggered": False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    # Phase 2: 求解
    log("Phase 2: 调用求解链获取 cf_clearance", "step")
    t0 = time.time()
    ck = bypass_solve()
    if not ck:
        log("求解失败，实验结束", "bad")
        result["phases"]["solve"] = {"ok": False}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    log(f"求解成功（{time.time()-t0:.0f}s）", "ok")
    result["phases"]["solve"] = {"ok": True, "elapsed_s": round(time.time() - t0, 1)}

    # Phase 3: 跨 session 验证。
    # 顺序关键：先对照组 C（裸新会话连续打，量化挑战状态残留），再实验组 B（带 clearance）。
    log("Phase 3: 全新会话跨 session 验证（先对照 C，后实验 B）", "step")
    time.sleep(2)  # clearance 生效微等待

    sc = cr.Session(impersonate=IMPERSONATE)  # 全新会话 C（对照，无 clearance）
    c_passes = 0
    c_first = None
    for i in range(args.control_probes):
        sn = last_ok_sn + i * 3
        st_c, blk_c, meta_c = fetch_page(sc, sn)
        if c_first is None:
            c_first = {"sn": sn, "status": st_c, "blocked": blk_c}
        if blk_c:
            meta_s = "  ".join(f"{k}={v}" for k, v in meta_c.items() if v) or "（无诊断头）"
            log(f"会话 C 裸请求 [{i+1}/{args.control_probes}] {sn}: {st_c} 被拦 | {meta_s}", "bad")
            break
        c_passes += 1
        log(f"会话 C 裸请求 [{i+1}/{args.control_probes}] {sn}: {st_c} 通过", "info")
        time.sleep(0.2)
    result["phases"]["control_C"] = {
        "passes": c_passes, "first": c_first}

    sb = cr.Session(impersonate=IMPERSONATE)  # 全新会话 B（实验，带 clearance）
    st_b, blk_b, meta_b = fetch_page(sb, last_ok_sn, cookies=ck)
    log(f"会话 B（全新，带 clearance）-> {last_ok_sn}: {st_b}",
        "ok" if st_b == 200 else "bad")
    result["phases"]["with_clearance_B"] = {
        "sn": last_ok_sn, "status": st_b, "blocked": blk_b}

    # Phase 4: 会话 B 带 clearance 续航测试
    log(f"Phase 4: 会话 B 带 clearance 续航测试（{args.verify_count} 请求）", "step")
    stats = {}
    for i in range(args.verify_count):
        sn = last_ok_sn + (i + 1) * 3
        st, blocked, meta = fetch_page(sb, sn, cookies=ck)
        stats[st] = stats.get(st, 0) + 1
        if blocked:
            log(f"[{i+1}/{args.verify_count}] {sn}: {st} 被拦（续航 {i} 请求）", "bad")
            break
        level = "ok" if st == 200 else "info"
        log(f"[{i+1}/{args.verify_count}] {sn}: {st}" + (" 通过" if st == 200 else " 未拦截"),
            level)
        time.sleep(args.verify_gap)
    result["phases"]["endurance"] = {"stats": stats}

    # 判定矩阵：
    #   有效前提 = 对照组 C 第一个请求就被拦（挑战状态仍在）
    #   有效 + B 通过   -> clearance 跨 session 复用有效
    #   有效 + B 被拦   -> 会话级额外绑定
    #   C 通过 >= 3 个  -> 挑战状态已衰减，实验无效
    print()
    log("实验判定：", "step")
    c_blocked_first = (c_first is not None) and c_first["blocked"]
    if c_passes >= 3:
        verdict = f"对照组 C 连过 {c_passes} 个（挑战状态已衰减），实验无效需冷却后重跑"
        log(verdict, "bad")
    elif st_b == 200 and c_blocked_first:
        verdict = "clearance 跨 session 复用有效（IP+UA+TLS 绑定模型证实）"
        log(verdict, "ok")
    elif st_b != 200 and c_blocked_first:
        verdict = "clearance 跨 session 复用失败（存在会话级额外绑定，模型需修正）"
        log(verdict, "bad")
    else:
        verdict = f"混合结果（C 首个 {c_first}，B {st_b}），人工复核"
        log(verdict, "bad")
    result["verdict"] = verdict
    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
