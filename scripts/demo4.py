# -*- coding: utf-8 -*-
"""
demo4.py — cf_clearance 有效性 AB 交替实验（消除时间漂移）

背景：demo3 两次实验中「求解后新会话续航」与「纯等待」无显著差异，
     且出现「带 clearance 的会话比裸会话更早被拦」的反常结果。
     推断：rate limit 计数器按 IP 级累积，求解链的 counter reset 未生效。

设计：触发 429 后，两个全新会话在同一时间段内严格交替请求：
     会话 B（带 cf_clearance）与 会话 C（裸）交替打同一 sn 序列。
     时间因素被交替消除；若 clearance 对计数有豁免，被拦的应集中在 C 的请求上。

判定：
  429 几乎只出现在 C 的请求 -> clearance 有效（豁免 rate limit 计数）
  429 在 B/C 请求上随机分布    -> clearance 对该站 rate limit 无效（counter reset 未生效）

用法：python demo4.py [--sn 143963534] [--gap 0.1] [--max-trigger 60] [--rounds 15]
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
    """单次请求。返回 (status, blocked, meta)。"""
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
    parser = argparse.ArgumentParser(description="cf_clearance 有效性 AB 交替实验")
    parser.add_argument("--sn", type=int, default=143963534, help="起始证书编号（须已知返回 200）")
    parser.add_argument("--gap", type=float, default=0.1, help="触发阶段请求间隔（秒）")
    parser.add_argument("--max-trigger", type=int, default=60, help="触发阶段最大请求数")
    parser.add_argument("--rounds", type=int, default=15, help="交替轮数（每轮 B 一个 + C 一个）")
    parser.add_argument("--alternate-gap", type=float, default=0.3,
                        help="交替阶段请求间隔（秒，两会话共用）")
    args = parser.parse_args()

    result = {"schema": "demo4-experiment.v1", "phases": {}}

    # Phase 1: 会话 A 串行请求直到触发 429
    log(f"Phase 1: 会话 A 串行请求直到触发 429（间隔 {args.gap}s，上限 {args.max_trigger}）", "step")
    sa = cr.Session(impersonate=IMPERSONATE)
    sn_base = args.sn
    triggered = False
    last_ok_sn = args.sn
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

    # Phase 3: AB 交替。B（带 clearance）与 C（裸）严格交替请求同一 sn 序列。
    log(f"Phase 3: AB 交替验证（{args.rounds} 轮，B 带 clearance / C 裸）", "step")
    time.sleep(2)
    sb = cr.Session(impersonate=IMPERSONATE)
    sc = cr.Session(impersonate=IMPERSONATE)
    events = []  # [(round, side, sn, status, blocked)]
    b_blocked_after = None   # B 被拦前的通过数
    c_blocked_after = None
    b_passes = c_passes = 0
    for rnd in range(args.rounds):
        for side, sess, cookies, label in (
                ("B", sb, ck, "带 clearance"), ("C", sc, None, "裸")):
            sn = last_ok_sn + (rnd * 2 + (1 if side == "C" else 0) + 1) * 3
            st, blocked, meta = fetch_page(sess, sn, cookies=cookies)
            events.append({"round": rnd + 1, "side": side, "sn": sn,
                           "status": st, "blocked": blocked})
            if blocked:
                log(f"R{rnd+1} {side}({label}) {sn}: {st} 被拦", "bad")
                if side == "B" and b_blocked_after is None:
                    b_blocked_after = b_passes
                if side == "C" and c_blocked_after is None:
                    c_blocked_after = c_passes
                time.sleep(args.alternate_gap)
                continue
            if side == "B":
                b_passes += 1
            else:
                c_passes += 1
            log(f"R{rnd+1} {side}({label}) {sn}: {st} 通过", "ok")
            time.sleep(args.alternate_gap)
        # 双方都至少被拦一次后可提前结束（信息已足够）
        if b_blocked_after is not None and c_blocked_after is not None:
            log(f"双方均已至少被拦一次（B 拦前通过 {b_blocked_after}，C 拦前通过 {c_blocked_after}），提前结束", "step")
            break
    result["phases"]["alternate"] = {
        "events": events,
        "b_passes": b_passes, "b_blocked_after": b_blocked_after,
        "c_passes": c_passes, "c_blocked_after": c_blocked_after,
    }

    # 判定
    print()
    log("实验判定：", "step")
    # 统计被拦事件在 B/C 上的分布
    b_blocks = sum(1 for e in events if e["blocked"] and e["side"] == "B")
    c_blocks = sum(1 for e in events if e["blocked"] and e["side"] == "C")
    log(f"被拦分布：B（带 clearance）{b_blocks} 次 / C（裸）{c_blocks} 次", "step")
    if c_blocks > 0 and b_blocks == 0:
        verdict = "429 全部落在裸会话 C 上：clearance 有效（豁免 rate limit 计数）"
        log(verdict, "ok")
    elif b_blocks > 0 and c_blocks > 0:
        verdict = "429 在 B/C 上均有分布：clearance 对该站 rate limit 计数无豁免（counter reset 未生效）"
        log(verdict, "bad")
    elif c_blocks == 0 and b_blocks == 0:
        verdict = "交替阶段未触发 429（计数已充分衰减），实验无效需冷却后重跑"
        log(verdict, "bad")
    else:
        verdict = "结果未落入预期组合，人工复核"
        log(verdict, "bad")
    result["verdict"] = verdict
    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
