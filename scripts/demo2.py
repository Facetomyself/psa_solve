# -*- coding: utf-8 -*-
"""
demo2.py — 持续采集 + 风控自愈验证 Demo

不断请求（Firefox TLS 指纹，短间隔）；遇到 403/429/挑战页立即调用求解代码
（抓材料 + vanilla Node 求解 + Firefox 指纹提交）获取 cf_clearance，然后继续请求。

用法：python demo2.py [--count 200] [--gap 0.15] [--recover-gap 0.4]
"""
import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
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


# 会话复用（keep-alive）——真短间隔高频请求；每次新建连接会有 ~1-2s TLS 握手开销
# curl_cffi Session 非线程安全，改为线程本地：每个 worker 线程独立 session
_tls = threading.local()
_state_lock = threading.Lock()   # 保护共享统计与诊断头
_solve_lock = threading.Lock()   # 求解互斥：同一时刻只有一个线程调用求解代码
_last_meta = {}  # 最近一次被拦响应的诊断头（server / cf-ray / retry-after）


def collect_page(sn, cookies=None, timeout=20):
    """采集请求（始终 Firefox 指纹，连接复用）。返回 (status, blocked)。"""
    if getattr(_tls, "session", None) is None:
        _tls.session = cr.Session(impersonate=IMPERSONATE)
    h = {
        "User-Agent": UA_FF,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = _tls.session.get(TARGET.format(sn=sn), headers=h, timeout=timeout, cookies=cookies)
    except Exception:
        _tls.session = cr.Session(impersonate=IMPERSONATE)  # 断连后重建会话
        with _state_lock:
            _last_meta.clear()  # 连接异常无响应头，清空避免显示上一次 429 的陈旧诊断
        return 0, True
    title_m = re.search(rb"<title>([^<]*)</title>", r.content[:3000])
    title = title_m.group(1).decode("utf-8", "replace").strip() if title_m else ""
    blocked = r.status_code in (403, 429) or "Just a moment" in title
    if blocked:
        with _state_lock:
            _last_meta.clear()
            _last_meta.update({
                "server": r.headers.get("server", ""),
                "cf-ray": r.headers.get("cf-ray", ""),
                "cf-mitigated": r.headers.get("cf-mitigated", ""),
                "retry-after": r.headers.get("retry-after", ""),
                "content-length": r.headers.get("content-length", ""),
            })
    return r.status_code, blocked


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


class SharedState:
    """并发 worker 共享状态。所有可变字段经 lock 访问。"""

    def __init__(self):
        self.lock = threading.Lock()
        self.ck = None          # 当前 clearance cookie dict
        self.ck_ts = 0.0        # clearance 更新时间（新鲜度判断用）
        self.last_solve_ts = 0.0  # 上次求解发起时间（失败冷却用）
        self.recover_done = threading.Event()  # 求解/恢复完成信号；初始 set
        self.recover_done.set()
        self.stats = {}         # status -> 次数
        self.bypass_count = 0
        self.streak = 0
        self.streaks = []       # 两次被拦之间通过的请求数
        self.consecutive_blocked = 0


FRESH_WINDOW = 60.0  # clearance 视为新鲜的最长秒数；超过则被拦时重新求解


def do_one(sn, idx, total, args, state):
    """单次请求 + 风控处置（worker 线程入口）。返回状态码。"""
    # 全局暂停：并发模式下若求解/恢复进行中，发新请求前先等恢复完成，
    # 避免求解期间继续请求触发 429 烧信誉
    if args.workers > 1 and not args.no_solve:
        state.recover_done.wait()
    with state.lock:
        ck = state.ck
    st, blocked = collect_page(sn, cookies=ck)
    with state.lock:
        state.stats[st] = state.stats.get(st, 0) + 1

    if blocked:
        with state.lock:
            if state.streak:
                state.streaks.append(state.streak)
                state.streak = 0
            state.consecutive_blocked += 1
            consecutive = state.consecutive_blocked
        meta = "  ".join(f"{k}={v}" for k, v in _last_meta.items() if v) or "（无诊断头）"
        log(f"[{idx+1}/{total}] {sn}: {st} 被拦（连续 {consecutive} 次）| {meta}", "bad")
        if args.no_solve:
            # 对照实验：只等待不求解
            log(f"no-solve 对照：等待 {args.passive_wait:.0f}s（模拟求解耗时，不求解）", "step")
            time.sleep(args.passive_wait)
            with state.lock:
                state.consecutive_blocked = 0
            return st
        # 求解协调：全局暂停所有 worker → 求解一次 → 生效后统一放行
        with _solve_lock:
            with state.lock:
                ck_fresh = state.ck is not None and (time.time() - state.ck_ts) < FRESH_WINDOW
                solve_cooldown = (time.time() - state.last_solve_ts) < FRESH_WINDOW
            if ck_fresh:
                # 其他线程刚求解完且 clearance 已生效：直接继续，无需再等待
                log("复用新鲜 clearance，直接继续", "info")
            elif solve_cooldown:
                # 刚求解失败过：冷却期内不再重试求解，短暂等待后继续
                log("求解冷却中，等待 5s 后继续", "info")
                time.sleep(5)
            else:
                # 承担求解：暂停全部 worker → 求解 → 等生效 → 放行
                state.recover_done.clear()
                log("调用求解代码获取 cf_clearance ...（其他 worker 暂停等待）", "step")
                t0 = time.time()
                with state.lock:
                    state.last_solve_ts = time.time()
                new_ck = bypass_solve()
                if new_ck:
                    with state.lock:
                        state.bypass_count += 1
                        state.ck = new_ck
                        state.ck_ts = time.time()
                    log(f"求解成功（{time.time()-t0:.0f}s），clearance 已更新", "ok")
                else:
                    log("求解失败，冷却 60s 后才会重试", "bad")
                log("等待 clearance 生效（5s）...")
                time.sleep(5)
                with state.lock:
                    state.consecutive_blocked = 0
                state.recover_done.set()
                log("恢复完成，全部 worker 放行", "step")
        return st

    with state.lock:
        state.consecutive_blocked = 0
        state.streak += 1
        ck = state.ck
    if st == 404:
        # 无效编号：不求解、不等间隔，立即请求下一个 sn
        log(f"[{idx+1}/{total}] {sn}: 404 跳过，直接下一个", "info")
        return st
    log(f"[{idx+1}/{total}] {sn}: {st} 通过", "ok")
    gap = args.recover_gap if ck else args.gap
    time.sleep(gap)
    return st


def main():
    parser = argparse.ArgumentParser(description="持续采集 + 风控自愈验证")
    parser.add_argument("--count", type=int, default=200, help="总请求数")
    parser.add_argument("--gap", type=float, default=0.15, help="请求间隔（秒）")
    parser.add_argument("--recover-gap", type=float, default=0.4, help="恢复后间隔（秒）")
    parser.add_argument("--workers", type=int, default=1,
                        help="并发 worker 数（每线程独立 session；>1 时 QPS 成倍提升，更易触发 403）")
    parser.add_argument("--no-solve", action="store_true",
                        help="对照实验：被拦后只等待不求解（验证限速窗口是否自然恢复）")
    parser.add_argument("--passive-wait", type=float, default=18.0,
                        help="no-solve 模式下被拦后的等待秒数（模拟求解耗时）")
    args = parser.parse_args()

    state = SharedState()
    sn_base = 143963534
    mode = f"{args.workers} 并发" if args.workers > 1 else "串行"
    log(f"持续采集启动：{args.count} 请求，{mode}，间隔 {args.gap}s，"
        f"{'no-solve 对照' if args.no_solve else '遇到风控即时求解'}", "step")

    if args.workers <= 1:
        for i in range(args.count):
            sn = sn_base + i * 3
            do_one(sn, i, args.count, args, state)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(do_one, sn_base + i * 3, i, args.count, args, state)
                       for i in range(args.count)]
            for f in futures:
                f.result()

    print()
    log("运行结束，统计：", "step")
    log(f"总请求: {args.count}  状态分布: {state.stats}")
    ok_count = state.stats.get(200, 0)
    not_found = state.stats.get(404, 0)
    blocked_total = state.stats.get(403, 0) + state.stats.get(429, 0) + state.stats.get(0, 0)
    log(f"有效请求: {ok_count + not_found}（200×{ok_count} + 404×{not_found}）")
    log(f"被拦: {blocked_total}  求解次数: {state.bypass_count}")
    if state.streak:
        state.streaks.append(state.streak)
    if state.streaks:
        avg = sum(state.streaks) / len(state.streaks)
        log(f"恢复后坚持请求数（两次被拦之间）: {state.streaks}  平均 {avg:.1f}", "step")
        log(f"该值对比求解组 vs no-solve 组：求解有效则明显更大")
    valid = ok_count + not_found
    if valid > 0:
        log(f"有效页面成功率: {ok_count/valid:.0%}（200/{valid}）",
            "ok" if ok_count / valid > 0.8 else "bad")
    log("demo2 完成")


if __name__ == "__main__":
    main()
