# -*- coding: utf-8 -*-
"""
demo6.py — 生产级异步采集（capture-only bridge 求解 + 会话分离 + asyncio）

生产形态（F6 定稿）：
  干净 AsyncSession 采集（显式携带 clearance，404 跳过，间隔 --gap）
  -> 429 触发 -> 触发会话即用即弃：挑战页直接喂 capture-only bridge 异步求解
  -> 恢复等待（距触发 >= --recover-age）
  -> 新干净 AsyncSession + 显式 ck 继续采集
  全程 asyncio：请求、子进程 bridge、恢复等待均为异步。

吞吐约束（PSA 单 IP）：rate limit 计数器约 15 请求/窗口，触发后求解
~12s + 恢复等待，稳态吞吐由窗口长度决定；demo6 输出实测 QPS 与页/小时。

用法：python demo6.py [--count 60] [--gap 0.1] [--recover-age 30] [--max-solves 5]
"""
import argparse
import asyncio
import json
import os
import re
import time
from datetime import datetime

from curl_cffi.requests import AsyncSession

ROOT = r"D:\reverse_ENV\workspace\psa_solve"
RUNTIME_DIR = os.path.join(ROOT, "runtime")
MATERIAL_ROOT = os.path.join(ROOT, "challenge-material")
NODE = r"D:\reverse_ENV\tools\node\node.exe"
TARGET = "https://www.psacard.com/cert/{sn}/psa"
UA_FF = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0"
IMPERSONATE = "firefox"


def log(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    tag = {"info": " .. ", "ok": " OK ", "bad": " !! ", "step": ">>> "}[level]
    print(f"[{ts}] {tag}{msg}", flush=True)


def jar_get(session, name):
    """从 curl_cffi Session 的 cookie jar 取值。"""
    return session.cookies.get(name)


def classify_fo(status, headers, set_cookie_str):
    """fo 响应分类（对齐 5s v2 /fo 响应分类表）。headers key 已小写化。"""
    ct = headers.get("content-type", "")
    has_clearance = "cf_clearance=" in set_cookie_str
    if has_clearance:
        return "FO_ACCEPTED"
    if "text/plain" in ct:
        return "FO_CONTINUE"
    return "FO_REJECT_OR_DEGRADE"


async def fetch_page_async(asession, sn, cookies=None, timeout=10):
    """异步单页请求。返回 (status, blocked, meta, content)。
    timeout 默认 10s：挂起（CF silent drop）快速判定，不做 20s 空耗。"""
    h = {
        "User-Agent": UA_FF,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        r = await asession.get(TARGET.format(sn=sn), headers=h, timeout=timeout,
                                cookies=cookies)
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


async def solve_bridge_async(session, challenge_body, outdir):
    """异步 capture-only bridge 求解（触发会话即用即弃）。
    成功返回 (ck, fo_log)；失败返回 (None, reason)。"""
    # 1. 落盘挑战页（触发会话收到的 429 响应体）
    page_path = os.path.join(outdir, "challenge-page.html")
    html = challenge_body.decode("utf-8", errors="replace")
    open(page_path, "w", encoding="utf-8").write(html)

    # 2. 解析 orchestrate URL + 同会话异步下载
    m = re.search(r"\.src = '([^']*orchestrate[^']*)'", html)
    if not m:
        m = re.search(r'src = "([^"]*orchestrate[^"]*)"', html)
    if not m:
        return None, "orchestrate URL 解析失败"
    orch_rel = m.group(1)
    orch_path = os.path.join(outdir, "chl-page-orchestrate.js")
    orch_url = "https://www.psacard.com" + orch_rel
    r = await session.get(orch_url, headers={"User-Agent": UA_FF,
                                             "Accept": "*/*",
                                             "Referer": TARGET.format(sn="x")},
                          timeout=30)
    if r.status_code != 200:
        return None, f"orchestrate 下载失败 HTTP {r.status_code}"
    open(orch_path, "wb").write(r.content)

    # 3. jar 取 __cf_bm
    bm_val = jar_get(session, "__cf_bm")
    if not bm_val:
        return None, "__cf_bm 不在 jar 中"
    bm = f"__cf_bm={bm_val}"

    # 4. 异步子进程 capture-only bridge（Windows Proactor 仅支持 bytes 流）
    env = dict(os.environ)
    env["CF_CAPTURE_ONLY"] = "1"
    proc = await asyncio.create_subprocess_exec(
        NODE, os.path.join(RUNTIME_DIR, "run.js"), page_path, orch_path, bm,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        env=env)
    fo_log = []
    result = None
    deadline = time.time() + 120
    try:
        while time.time() < deadline:
            try:
                raw_line = await asyncio.wait_for(proc.stdout.readline(), timeout=30)
            except asyncio.TimeoutError:
                break
            if not raw_line:
                if proc.returncode is not None:
                    break
                continue
            line = raw_line.decode("utf-8", errors="replace").strip()
            if not line.startswith("{"):
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            mtype = msg.get("type")
            if mtype == "runtime_request":
                url = msg["url"]
                if url.startswith("/"):
                    url = "https://www.psacard.com" + url
                method = msg.get("method", "POST").upper()
                headers = {k: v for k, v in msg.get("headers", {}).items()
                           if k.lower() not in ("cookie", "content-length", "host")}
                body = msg.get("body", "")
                try:
                    if method == "POST":
                        r = await session.post(url, data=body, headers=headers,
                                               timeout=60)
                    else:
                        r = await session.get(url, headers=headers, timeout=60)
                except Exception as e:
                    log(f"fo {msg['request_id']} 发送异常: {e}", "bad")
                    return None, f"fo 发送异常: {e}"
                sc_raw = r.headers.get("set-cookie", "") or ""
                sc_list = [c.strip() for c in sc_raw.split(",") if "=" in c.strip()]
                klass = classify_fo(
                    r.status_code, {k.lower(): v for k, v in r.headers.items()},
                    sc_raw)
                fo_log.append({"request_id": msg["request_id"], "method": method,
                               "status": r.status_code, "class": klass,
                               "body_len": len(r.content)})
                log(f"fo {msg['request_id']} -> {r.status_code} [{klass}] "
                    f"({len(r.content)} bytes)")
                envelope = {
                    "type": "response",
                    "request_id": msg["request_id"],
                    "status": r.status_code,
                    "headers": {k.lower(): v for k, v in r.headers.items()},
                    "set_cookies": sc_list,
                    "body": r.content.decode("utf-8", errors="replace"),
                }
                proc.stdin.write(
                    (json.dumps(envelope, ensure_ascii=False) + "\n").encode("utf-8"))
                await proc.stdin.drain()
            elif mtype == "result":
                result = msg
                break
            elif msg.get("ok") is not None and "elapsedMs" in msg:
                result = msg
                break
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=10)
        except Exception:
            proc.kill()

    if not result or not result.get("hasClearance"):
        return None, f"bridge 未产出 clearance（fo {len(fo_log)} 轮）"

    # 5. jar 验证并收集干净 ck
    clearance = jar_get(session, "cf_clearance")
    if not clearance:
        return None, "bridge 后 jar 无 cf_clearance"
    bm_after = jar_get(session, "__cf_bm")
    ck = {"__cf_bm": bm_after, "cf_clearance": clearance}
    return ck, fo_log


async def main_async(args):
    stats = {}
    total = 0
    solves = 0
    streaks = []
    segment_passes = 0
    t_start = time.time()
    sn_cursor = args.sn
    ck = None
    asess = AsyncSession(impersonate=IMPERSONATE)  # 当前采集会话（干净）
    solve_durations = []

    log(f"生产采集启动：目标 {args.count} 请求，gap {args.gap}s，"
        f"恢复窗口 {args.recover_age}s，求解上限 {args.max_solves}", "step")

    while total < args.count and solves <= args.max_solves:
        st, blocked, meta, content = await fetch_page_async(
            asess, sn_cursor, cookies=ck, timeout=args.request_timeout)
        total += 1
        stats[st] = stats.get(st, 0) + 1
        sn = sn_cursor
        sn_cursor += 3

        if blocked:
            streaks.append(segment_passes)
            segment_passes = 0
            meta_s = "  ".join(f"{k}={v}" for k, v in meta.items() if v) or "（无诊断头）"
            log(f"[{total}/{args.count}] {sn}: {st} 被拦（本段 {streaks[-1]} 通过）| {meta_s}", "bad")
            if len(content) < 1000:
                # 连接级异常（挂起/断开）：立即重建会话重试一次，仍异常才冷却
                log("连接级异常（无挑战页），重建会话立即重试", "bad")
                asess = AsyncSession(impersonate=IMPERSONATE)
                st2, blocked2, meta2, content2 = await fetch_page_async(
                    asess, sn, cookies=ck, timeout=args.request_timeout)
                total += 1
                stats[st2] = stats.get(st2, 0) + 1
                if not blocked2:
                    segment_passes += 1
                    log(f"[{total}/{args.count}] {sn}: {st2} 通过（重试恢复）", "ok")
                    await asyncio.sleep(args.skip_gap if st2 == 404 else args.gap)
                    continue
                if blocked2 and len(content2) >= 1000:
                    # 重试撞上挑战页：转入下方求解流程（不重复统计段）
                    log(f"重试 {sn}: {st2} 挑战页，转入求解", "bad")
                    content, meta, st = content2, meta2, st2
                else:
                    log(f"重试仍连接异常，冷却 {args.abort_cooldown:.0f}s", "bad")
                    await asyncio.sleep(args.abort_cooldown)
                    asess = AsyncSession(impersonate=IMPERSONATE)
                    continue
            # 求解：触发会话即用即弃（bridge 会污染其 jar，采集中止不用它）
            if solves >= args.max_solves:
                break
            t_trig = time.time()
            epoch = datetime.now().strftime("%Y%m%d-%H%M%S")
            outdir = os.path.join(MATERIAL_ROOT, f"demo6-{epoch}-{solves}")
            os.makedirs(outdir, exist_ok=True)
            log("429 挑战 -> capture-only bridge 异步求解", "step")
            ck_new, reason = await solve_bridge_async(asess, content, outdir)
            solve_durations.append(time.time() - t_trig)
            if not ck_new:
                log(f"求解失败：{reason}，冷却 60s", "bad")
                await asyncio.sleep(60)
                asess = AsyncSession(impersonate=IMPERSONATE)
                continue
            solves += 1
            ck = ck_new
            log(f"求解成功（{solve_durations[-1]:.0f}s，"
                f"fo {len(reason)} 轮），clearance 已收集", "ok")
            wait = max(5.0, args.recover_age - (time.time() - t_trig))
            log(f"恢复等待 {wait:.0f}s（距触发将达 {args.recover_age}s）")
            await asyncio.sleep(wait)
            asess = AsyncSession(impersonate=IMPERSONATE)  # 新干净会话
            continue

        segment_passes += 1
        if st == 404:
            # 404 也带微间隔：无间隔连发 micro-burst 会诱发连接级惩罚
            log(f"[{total}/{args.count}] {sn}: 404 跳过，直接下一个", "info")
            await asyncio.sleep(args.skip_gap)
            continue
        log(f"[{total}/{args.count}] {sn}: {st} 通过", "ok")
        await asyncio.sleep(args.gap)

    # 统计
    elapsed = time.time() - t_start
    if segment_passes:
        streaks.append(segment_passes)
    print()
    log("运行结束，统计：", "step")
    log(f"总请求: {total}  状态分布: {stats}")
    ok_count = stats.get(200, 0)
    not_found = stats.get(404, 0)
    blocked_total = stats.get(403, 0) + stats.get(429, 0) + stats.get(0, 0)
    log(f"有效请求: {ok_count + not_found}（200×{ok_count} + 404×{not_found}）")
    log(f"被拦: {blocked_total}  求解次数: {solves}")
    if streaks:
        log(f"段通过数（两次被拦之间）: {streaks}  平均 {sum(streaks)/len(streaks):.1f}")
    if solve_durations:
        log(f"求解耗时: {solve_durations}  平均 {sum(solve_durations)/len(solve_durations):.1f}s")
    valid = ok_count + not_found
    if valid > 0 and elapsed > 0:
        qps = valid / elapsed
        per_hour = qps * 3600
        log(f"实测吞吐: {qps:.2f} 请求/秒 = {per_hour:.0f} 页/小时"
            f"（含求解与恢复开销，总耗时 {elapsed:.0f}s）", "step")
    log("demo6 完成")


def main():
    parser = argparse.ArgumentParser(description="生产级异步采集（bridge 求解 + 会话分离）")
    parser.add_argument("--count", type=int, default=60, help="目标请求总数")
    parser.add_argument("--gap", type=float, default=0.1, help="采集请求间隔（秒）")
    parser.add_argument("--skip-gap", type=float, default=0.15,
                        help="404 快速跳过间隔（秒，防 micro-burst 诱发连接惩罚）")
    parser.add_argument("--request-timeout", type=float, default=10.0,
                        help="单请求超时（秒，挂起快速判定）")
    parser.add_argument("--recover-age", type=float, default=30.0,
                        help="求解后恢复等待的距触发最短秒数")
    parser.add_argument("--abort-cooldown", type=float, default=45.0,
                        help="连接异常重试失败后的冷却秒数")
    parser.add_argument("--max-solves", type=int, default=5, help="求解次数上限")
    parser.add_argument("--sn", type=int, default=143963534, help="起始证书编号")
    args = parser.parse_args()

    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\ninterrupted")


if __name__ == "__main__":
    main()
