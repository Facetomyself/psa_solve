#!/usr/bin/env python3
"""record_ruyijs.py — 回放对拍第 1 步：ruyijs 在线跑，录制离线回放材料。

录制内容：
  A. challenge-page HTML（引擎内 document.documentElement.outerHTML——服务器
     原文含 CSP/token，outerHTML 可能与原文有序列差，但 orchestrate 需要的
     _cf_chl_opt 与 script src 都在）
  B. orchestrate JS 文本（引擎内 XHR 同 URL 重取——script src 含 ray token，
     短窗口内稳定；若 404/304 退化则报错不产材料）
  C. atob/btoa I/O 全序列（expose sink，v5 同款）

对拍窗口：FO-3 之前（orchestrate 静态阶段）的调用——两侧吃同一 orchestrate
输入，程序路径同构，92B 选择子首段可字节级同位 diff。
产物：replay-materials/（gitignore 域）+ ruyijs-replay-atob.jsonl
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT_DIR = OUT_DIR / "replay-materials"
MAT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
CONTEXT_TIMEOUT = 400.0
MAX_TASKS = 100000
PUMP_WALL_S = 150.0

FINGERPRINT = {
    "navigator": {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
        "platform": "Win32",
        "language": "en-US",
        "languages": ["en-US", "en"],
    },
    "screen": {
        "width": 1920, "height": 1080, "availWidth": 1920,
        "availHeight": 1040, "colorDepth": 24,
    },
    "viewport": {"width": 1920, "height": 939, "devicePixelRatio": 1},
}

ATOBSRC = """(function () {
  var cur = globalThis.atob;
  if (cur && cur.__psaHooked) return cur;
  var orig = cur;
  var wrapper = function (input) {
    var s = String(input);
    var out = orig.call(globalThis, s);
    try { __psaSink('d', s, String(out)); } catch (e) {}
    return out;
  };
  wrapper.__psaHooked = true;
  return wrapper;
})()"""

BTOSRC = """(function () {
  var cur = globalThis.btoa;
  if (cur && cur.__psaHooked) return cur;
  var orig = cur;
  var wrapper = function (input) {
    var s = String(input);
    var out = orig.call(globalThis, s);
    try { __psaSink('e', s, String(out)); } catch (e) {}
    return out;
  };
  wrapper.__psaHooked = true;
  return wrapper;
})()"""


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import ruyijs

    pairs = []
    cert_ok = False

    def sink(direction, inp, outp):
        if len(pairs) < 20000:
            pairs.append((direction, str(inp), str(outp)))
        return True

    ctx = ruyijs.Context(timeout=CONTEXT_TIMEOUT, mode="debug")
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.expose(sink, "__psaSink")
        ctx.native("atob", ATOBSRC)
        ctx.native("btoa", BTOSRC)
        ctx.navigate(PAGE_URL)

        # ---- 泵前抓取：navigate 返回即抓（init script 已同步执行）----
        # 证据（v5 失败）：advance(10000) 冒进触发 document-swap 竞态
        # （createElement TypeError，已知 0.2.2 缺陷），文档换血后
        # _cf_chl_opt 随旧文档消失。navigate 返回时 init 已跑（_cf_chl_opt
        # 2427B），advance(3000) 后 orchestrate 追加至 18634B——抓取放
        # navigate 后、首次 advance 前，并随泵推进补抓增量。
        chl_opt = {}
        orch_url = None

        def snap_state():
            try:
                raw = ctx.eval("JSON.stringify(globalThis._cf_chl_opt || null)", to_py=True)
                if isinstance(raw, str) and raw != "null":
                    obj = json.loads(raw)
                    if isinstance(obj, dict):
                        chl_opt.update(obj)
            except Exception:
                pass
            try:
                for e in [e for e in ctx.net_log() if isinstance(e, dict)]:
                    u = str(e.get("url", ""))
                    if "/orchestrate/" in u and not orch_url:
                        return u
            except Exception:
                pass
            return orch_url

        orch_url = snap_state()
        try:
            ctx.advance(10000, max_tasks=MAX_TASKS)
        except Exception:
            pass
        orch_url = snap_state() or orch_url

        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        while time.monotonic() < deadline:
            try:
                ctx.native("atob", ATOBSRC)
                ctx.native("btoa", BTOSRC)
            except Exception:
                pass
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(ctx, fn)(**kw)
                except Exception:
                    pass
            try:
                ctx.advance(500, max_tasks=32000)
            except Exception:
                pass
            entries = [e for e in ctx.net_log() if isinstance(e, dict)]
            posts = [e for e in entries
                     if e.get("method") == "POST" and "/cdn-cgi/" in str(e.get("url", ""))]
            done = [e for e in posts if e.get("status") not in (None, 0)]
            gets = [e for e in entries if e.get("method") == "GET"
                    and "/cert/" in str(e.get("url", "")) and e.get("status") == 200]
            if gets:
                cert_ok = True
                last_progress = time.monotonic()
            if done:
                last_progress = time.monotonic()
            if not orch_url or len(chl_opt) < 5:
                orch_url = snap_state() or orch_url
            if cert_ok and len(done) >= 3:
                break
            if time.monotonic() - last_progress > 30.0:
                break
            time.sleep(0.25)

        # ---- 录制材料 ----
        # chl_opt / orch_url 已在泵前抓取（见上）。此处仅做 orchestrate JS
        # 同会话抓取与合成 init 页。
        from curl_cffi.requests import Session
        page_bytes = 0
        orch_len = 0
        try:
            ch = ctx.cookie_header(orch_url or PAGE_URL, source_url=PAGE_URL)
            cookie_hdr = ch.get("header", "") if isinstance(ch, dict) else str(ch or "")
        except Exception:
            cookie_hdr = ""
        if orch_url:
            try:
                with Session(impersonate="firefox") as s:
                    r2 = s.get(orch_url, headers={
                        "User-Agent": FINGERPRINT["navigator"]["userAgent"],
                        "Referer": PAGE_URL,
                        "Cookie": cookie_hdr,
                    }, timeout=30)
                if r2.status_code == 200 and len(r2.content) > 10000:
                    (MAT_DIR / "chl-page-orchestrate.js").write_bytes(r2.content)
                    orch_len = len(r2.content)
            except Exception:
                pass
        # 合成 init 页：run.js 提取第一个 <script> 内联体执行以设置 _cf_chl_opt
        if chl_opt:
            init_js = "window._cf_chl_opt = " + json.dumps(chl_opt, ensure_ascii=False) + ";"
            (MAT_DIR / "challenge-init.html").write_text(
                "<!doctype html><html><head><script>" + init_js + "</script></head><body></body></html>",
                encoding="utf-8")
            page_bytes = len(init_js)

        # net_log 概要（录制轮的请求清单，回放比对用）
        net = []
        for e in [e for e in ctx.net_log() if isinstance(e, dict)]:
            parts = urlsplit(str(e.get("url", "")))
            net.append({"m": e.get("method"), "p": parts.netloc + parts.path,
                        "s": e.get("status")})
        (MAT_DIR / "ruyijs-netlog.json").write_text(
            json.dumps(net, ensure_ascii=False, indent=1), encoding="utf-8")

    finally:
        try:
            ctx.close()
        except Exception:
            pass

    # atob I/O 序列落盘
    rows = []
    for i, (d, inp, out) in enumerate(pairs):
        rows.append({"n": i, "dir": d, "i": inp, "o": out})
    (OUT_DIR / "ruyijs-replay-atob.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    print(json.dumps({
        "certOk": cert_ok, "pairs": len(rows),
        "pageBytes": page_bytes, "orchBytes": orch_len,
        "netEvents": len(net),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
