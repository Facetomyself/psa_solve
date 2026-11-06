#!/usr/bin/env python3
"""solve_ruyijs.py — ruyijs inner 0.2.2 自含 PSA Cloudflare 挑战求解器。

流程（对照 diagnostics/ruyijs-fresh-navigate-20261103/run2_022.py 已验证链）：
  1. ruyijs Context（UA 与生产会话对齐）navigate cert URL -> 403 挑战页
  2. 泵到挑战自转完成（FO 轮 + clearance + document 切换）
  3. readback：GET cert -> 200 且正文含 SN
  4. export_cookies -> cf_clearance/__cf_bm 交给生产 curl_cffi 会话
  5. 同 UA curl_cffi 验证 clearance（不落日志、不打印值）

demo6 集成：solve_challenge(ua) -> {"ok", "cookies", "wallS", "foRounds"}。
cookie 值只经内存/返回值传递；日志与 stdout 只出现计数与状态。
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

TOOLS = Path(r"D:\reverse_ENV\tools\web-reverse")
PAGE_URL = "https://www.psacard.com/cert/{sn}/psa"
CERT_SN = "87356241"  # 求解触发用 SN（采集范围内任一）

sys.path.insert(0, str(TOOLS))

FINGERPRINT_TMPL = {
    "navigator": {
        "userAgent": "{ua}",
        "platform": "Win32",
        "language": "en-US",
        "languages": ["en-US", "en"],
    },
    "screen": {
        "width": 1920,
        "height": 1080,
        "availWidth": 1920,
        "availHeight": 1040,
        "colorDepth": 24,
    },
    "viewport": {"width": 1920, "height": 939, "devicePixelRatio": 1},
}

CONTEXT_TIMEOUT = 400.0
ADVANCE_MS = 10000
MAX_TASKS = 100000
PUMP_WALL_S = 180.0
ADVANCE_QUIET_S = 25.0


def _strip_proxy_env() -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)


def _classify(events: list, sn: str) -> dict:
    fo, cert_get, cert_post = [], [], []
    for item in events:
        if not isinstance(item, dict):
            continue
        prefix = item.get("pathPrefix")
        row = {"status": item.get("status"), "body": item.get("requestBodyBytes")}
        if item.get("method") == "POST" and isinstance(prefix, str) and prefix.startswith("/cdn-cgi/"):
            fo.append(row)
        elif isinstance(prefix, str) and prefix.startswith("/cert/"):
            (cert_post if item.get("method") == "POST" else cert_get).append(row)
    return {
        "foPosts": fo,
        "certGets": cert_get,
        "certPosts": cert_post,
        "certOk": any(isinstance(r["status"], int) and 200 <= r["status"] < 300 for r in cert_get),
    }


def solve_challenge(ua: str, sn: str = CERT_SN, verbose: bool = False) -> dict:
    """ruyijs 自含求解。返回 cookies dict（值仅内存传递）+ 元数据，不含 cookie 值的日志。"""
    import ruyijs
    from run_ruyijs import _redact_net_events

    _strip_proxy_env()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    url = PAGE_URL.format(sn=sn)
    fingerprint = {g: dict(v) for g, v in FINGERPRINT_TMPL.items()}
    fingerprint["navigator"]["userAgent"] = ua

    started = time.monotonic()
    context = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    error = None
    net: list = []
    cookies: dict = {}
    try:
        context.configure_fingerprint(fingerprint)
        context.configure_clock("system")
        context.navigate(url)
        try:
            context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
        except Exception:
            pass  # 0.2.2 document-swap 竞态：炸一批 task，context 存活
        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        seen = 0
        while time.monotonic() < deadline:
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(context, fn)(**kw)
                except Exception:
                    pass
            try:
                context.advance(500, max_tasks=32000)
            except Exception:
                pass
            raw = context.net_log() if callable(getattr(context, "net_log", None)) else []
            net = _redact_net_events(raw if isinstance(raw, list) else [])
            if len(net) != seen:
                seen = len(net)
                last_progress = time.monotonic()
            verdict = _classify(net, sn)
            if verdict["certOk"]:
                break
            if time.monotonic() - last_progress > ADVANCE_QUIET_S:
                break
            time.sleep(0.25)
        verdict = _classify(net, sn)
        raw_cookies = context.export_cookies() if callable(getattr(context, "export_cookies", None)) else None
        if isinstance(raw_cookies, str):
            for pair in raw_cookies.split(";"):
                if "=" in pair:
                    k, _, v = pair.strip().partition("=")
                    cookies[k.strip()] = v
        elif isinstance(raw_cookies, dict):
            cookies = {str(k): str(v) for k, v in raw_cookies.items()}
        elif isinstance(raw_cookies, list):
            for row in raw_cookies:
                if isinstance(row, dict) and row.get("name"):
                    cookies[str(row["name"])] = str(row.get("value", ""))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"[:500]
    finally:
        try:
            context.close()
        except Exception:
            pass

    wall = round(time.monotonic() - started, 1)
    verdict = _classify(net, sn)
    return {
        "ok": bool(cookies.get("cf_clearance")) and verdict["certOk"] and error is None,
        "cookies": cookies,
        "wallS": wall,
        "foRounds": len(verdict["foPosts"]),
        "foStatuses": [r["status"] for r in verdict["foPosts"]],
        "certOk": verdict["certOk"],
        "certGetStatuses": [r["status"] for r in verdict["certGets"]],
        "cookieNames": sorted(cookies.keys()),
        "error": error,
    }


def validate_clearance(cookies: dict, ua: str, sn: str = CERT_SN) -> dict:
    """生产 curl_cffi 同 UA 验证 clearance。返回 {ok, status, challenge}，不落 cookie 值。"""
    from curl_cffi.requests import Session

    session = Session(impersonate="firefox")
    try:
        r = session.get(PAGE_URL.format(sn=sn), headers={"User-Agent": ua}, cookies=cookies, timeout=15)
        title = b"Just a moment" in r.content[:3000]
        return {"ok": r.status_code == 200 and not title, "status": r.status_code, "challenge": title}
    finally:
        session.close()


def main() -> int:
    # 子进程模式（demo6 集成入口）：--out <file> 把 cookie JSON 落盘后自删由调用方负责
    out_path = None
    args = sys.argv[1:]
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    ua = args[0] if args else "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"
    result = solve_challenge(ua)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(result["cookies"], ensure_ascii=False), encoding="utf-8")
    summary = {k: v for k, v in result.items() if k != "cookies"}
    summary["hasCfClearance"] = bool(result["cookies"].get("cf_clearance"))
    summary["hasCfBm"] = bool(result["cookies"].get("__cf_bm"))
    if result["ok"] and out_path is None:
        v = validate_clearance(result["cookies"], ua)
        summary["crossEngineValidation"] = v
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
