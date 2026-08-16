# -*- coding: utf-8 -*-
"""
demo5.py — 同 session 全链路求解验证

背景（F6）：demo2/3/4 横向数据证明 cf_clearance 的价值绑定会话上下文——
  原会话续航 13-16，新会话移植后 0-6（等于没带）。
  根因：bypass_solve 的提交用独立 cr.post（第三个上下文），CF 的
  「挑战通过 + 计数器归零」没有落在业务会话上。

改造：全程一个会话 A 完成「拿挑战页 → 下载 orchestrate → 提交 fo → 业务请求」。
  挑战页 body 直接来自 A 收到的 429 响应（不再由 fetch_material.py 独立抓取），
  提交用 A.post（A 的 cookie jar 自动接住 cf_clearance）。

流程：
  Phase 1  会话 A 串行触发 429，保留挑战页 body
  Phase 2  同 session 求解：落盘挑战页 -> A 下载 orchestrate JS -> A jar 取 __cf_bm
           -> Node run.js 求解 -> A.post 提交 -> A jar 验证 cf_clearance
  Phase 3  会话 A 续航测试（jar 自动带 clearance，不再显式传 cookie）
  Phase 4  新会话 B 对照（显式传 A 的 clearance，预期续航显著更短）

判定：A 续航明显大于 B -> 同 session 链路成立，bypass_solve 应改造成此形态。

用法：python demo5.py [--sn 143963534] [--gap 0.1] [--max-trigger 60]
                      [--verify-count 30] [--verify-gap 0.2]
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
    """单次请求。返回 (status, blocked, meta, content)。content 为响应体 bytes。"""
    h = {
        "User-Agent": UA_FF,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = session.get(TARGET.format(sn=sn), headers=h, timeout=timeout, cookies=cookies)
    except Exception:
        return 0, True, {}, b""
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
    return r.status_code, blocked, meta, r.content


def jar_get(session, name):
    """从 curl_cffi Session 的 cookie jar 取值（0.16 起 Cookies.get(name) 直接返回值）。"""
    return session.cookies.get(name)


def solve_same_session(session, challenge_body, outdir):
    """同 session 求解：挑战页落盘 -> session 下载 orchestrate -> Node 求解 -> session 提交。
    成功返回 (ck_dict, submit_url)；失败返回 (None, reason)。"""
    # 1. 落盘挑战页（session 自己收到的 429 响应体）
    page_path = os.path.join(outdir, "challenge-page.html")
    html = challenge_body.decode("utf-8", errors="replace")
    open(page_path, "w", encoding="utf-8").write(html)
    log(f"挑战页已落盘（{len(challenge_body)} bytes，来自会话 A 的 429 响应）")

    # 2. 解析 orchestrate URL + 用同一 session 下载
    m = re.search(r"\.src = '([^']*orchestrate[^']*)'", html)
    if not m:
        m = re.search(r'src = "([^"]*orchestrate[^"]*)"', html)
    if not m:
        return None, "orchestrate URL 解析失败"
    orch_rel = m.group(1)
    orch_path = os.path.join(outdir, "chl-page-orchestrate.js")
    orch_url = "https://www.psacard.com" + orch_rel
    r = session.get(orch_url, headers={"User-Agent": UA_FF,
                                       "Accept": "*/*",
                                       "Referer": TARGET.format(sn="x")})
    if r.status_code != 200:
        return None, f"orchestrate 下载失败 HTTP {r.status_code}"
    open(orch_path, "wb").write(r.content)
    log(f"orchestrate JS 已下载（{len(r.content)} bytes，会话 A 下载）")

    # 3. 会话 A jar 取 __cf_bm
    bm_val = jar_get(session, "__cf_bm")
    if not bm_val:
        return None, "__cf_bm 不在会话 A 的 jar 中"
    bm = f"__cf_bm={bm_val}"
    log(f"__cf_bm 取自会话 A jar（{bm_val[:20]}...）")

    # 4. Node 求解
    r = subprocess.run(
        [NODE, os.path.join(RUNTIME_DIR, "run.js"), page_path, orch_path, bm],
        capture_output=True, text=True, timeout=120)
    result = None
    for line in r.stdout.strip().splitlines():
        if line.strip().startswith("{"):
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                pass
    if not result or not result.get("submits"):
        return None, "Node 求解无 submits 输出"
    last = result["submits"][-1]
    url = last["url"]
    if url.startswith("/"):
        url = "https://www.psacard.com" + url

    # 5. 同一 session 提交（A 的 jar 自动带 __cf_bm 并接住 cf_clearance）
    ff_headers = {
        "User-Agent": UA_FF,
        "Accept": "*/*",
        "Content-Type": "text/plain",
    }
    r = session.post(url, data=last["fullBody"], headers=ff_headers, timeout=30)
    log(f"提交（会话 A.post）HTTP {r.status_code}")

    # 6. 从 A jar 验证 cf_clearance
    clearance = jar_get(session, "cf_clearance")
    if not clearance:
        return None, "提交后 jar 无 cf_clearance"
    bm_after = jar_get(session, "__cf_bm")
    ck = {"__cf_bm": bm_after, "cf_clearance": clearance}
    log(f"会话 A jar 已持有 cf_clearance（{clearance[:20]}...）", "ok")
    return ck, url


def main():
    parser = argparse.ArgumentParser(description="同 session 全链路求解验证")
    parser.add_argument("--sn", type=int, default=143963534, help="起始证书编号（须已知返回 200）")
    parser.add_argument("--gap", type=float, default=0.1, help="触发阶段请求间隔（秒）")
    parser.add_argument("--max-trigger", type=int, default=60, help="触发阶段最大请求数")
    parser.add_argument("--verify-count", type=int, default=30, help="续航测试请求数")
    parser.add_argument("--verify-gap", type=float, default=0.2, help="续航测试请求间隔（秒）")
    parser.add_argument("--post-solve-wait", type=float, default=5.0,
                        help="求解完成到续航开始的冷却秒数（与 demo2 对齐为 5，可扫参验证衰减窗口）")
    args = parser.parse_args()

    result = {"schema": "demo5-experiment.v1", "phases": {}}

    # Phase 1: 会话 A 串行请求直到触发 429，保留挑战页 body
    log(f"Phase 1: 会话 A 串行请求直到触发 429（间隔 {args.gap}s，上限 {args.max_trigger}）", "step")
    sa = cr.Session(impersonate=IMPERSONATE)
    sn_base = args.sn
    triggered = False
    last_ok_sn = args.sn
    challenge_body = b""
    challenge_sn = None
    for i in range(args.max_trigger):
        sn = sn_base + i * 3
        st, blocked, meta, content = fetch_page(sa, sn)
        if blocked:
            meta_s = "  ".join(f"{k}={v}" for k, v in meta.items() if v) or "（无诊断头）"
            log(f"[{i+1}/{args.max_trigger}] {sn}: {st} 触发挑战 | {meta_s}", "bad")
            triggered = True
            challenge_body = content
            challenge_sn = sn
            result["phases"]["trigger"] = {
                "requests_before": i, "sn": sn, "status": st, "meta": meta,
                "body_bytes": len(content)}
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

    # Phase 2: 同 session 求解
    log("Phase 2: 同 session 全链路求解（挑战页来自会话 A，提交走会话 A）", "step")
    epoch = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(MATERIAL_ROOT, f"demo5-{epoch}")
    os.makedirs(outdir, exist_ok=True)
    t0 = time.time()
    ck, reason = solve_same_session(sa, challenge_body, outdir)
    if not ck:
        log(f"同 session 求解失败：{reason}，实验结束", "bad")
        result["phases"]["solve"] = {"ok": False, "reason": reason}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    log(f"同 session 求解完成（{time.time()-t0:.0f}s）", "ok")
    result["phases"]["solve"] = {"ok": True, "elapsed_s": round(time.time() - t0, 1),
                                 "material_dir": os.path.basename(outdir)}

    # Phase 3: 会话 A 续航（jar 自动带 clearance，不再显式传 cookie）
    log(f"Phase 3: 会话 A 续航测试（{args.verify_count} 请求，jar 自动带 clearance，"
        f"先冷却 {args.post_solve_wait:.0f}s）", "step")
    time.sleep(args.post_solve_wait)
    a_passes = 0
    a_first_block = None
    for i in range(args.verify_count):
        sn = last_ok_sn + (i + 1) * 3
        st, blocked, meta, _ = fetch_page(sa, sn)
        if blocked:
            log(f"[{i+1}/{args.verify_count}] {sn}: {st} 被拦（A 续航 {a_passes} 请求）", "bad")
            a_first_block = {"at_request": i + 1, "sn": sn, "status": st}
            break
        a_passes += 1
        level = "ok" if st == 200 else "info"
        log(f"[{i+1}/{args.verify_count}] {sn}: {st}" + (" 通过" if st == 200 else " 未拦截"),
            level)
        time.sleep(args.verify_gap)
    result["phases"]["session_A_endurance"] = {
        "passes": a_passes, "first_block": a_first_block}

    # Phase 4: 新会话 B 对照（显式传 A 的 clearance）
    log(f"Phase 4: 新会话 B 对照（显式携带 A 的 clearance，{args.verify_count} 请求）", "step")
    sb = cr.Session(impersonate=IMPERSONATE)
    b_passes = 0
    b_first_block = None
    for i in range(args.verify_count):
        sn = last_ok_sn + (i + 1) * 3
        st, blocked, meta, _ = fetch_page(sb, sn, cookies=ck)
        if blocked:
            log(f"[{i+1}/{args.verify_count}] {sn}: {st} 被拦（B 续航 {b_passes} 请求）", "bad")
            b_first_block = {"at_request": i + 1, "sn": sn, "status": st}
            break
        b_passes += 1
        level = "ok" if st == 200 else "info"
        log(f"[{i+1}/{args.verify_count}] {sn}: {st}" + (" 通过" if st == 200 else " 未拦截"),
            level)
        time.sleep(args.verify_gap)
    result["phases"]["session_B_control"] = {
        "passes": b_passes, "first_block": b_first_block}

    # 判定
    print()
    log("实验判定：", "step")
    log(f"会话 A（同 session 链路）续航: {a_passes}  会话 B（跨 session 移植）续航: {b_passes}", "step")
    if a_passes >= 10 and a_passes >= b_passes * 2:
        verdict = "同 session 全链路有效：A 续航 >= 10 且 >= B 的 2 倍，bypass 改造方向证实"
        log(verdict, "ok")
    elif a_passes >= b_passes + 3:
        verdict = "同 session 链路有增益但不显著，需多轮重复确认"
        log(verdict, "info")
    elif a_passes <= 3 and b_passes <= 3:
        verdict = "双方续航都短：求解可能未被 CF 接受或计数残留，冷却后重跑"
        log(verdict, "bad")
    else:
        verdict = "结果未落入预期组合，人工复核"
        log(verdict, "bad")
    result["verdict"] = verdict
    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
