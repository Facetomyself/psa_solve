#!/usr/bin/env python3
"""capture_atob_values.py — ruyijs 引擎内 atob hook v5（expose Python sink）。

证据链（v1-v4）：
- v3 归因 1086/1086 'ruyijs:native:10'：挑战调用确实经过 wrapper（hook 生效）
- v3/v4 drain 失败：eval realm 与 native 求值 realm 因 document 换血错位，
  eval 读不到 wrapper 状态（globalThis 属性跨 realm 不可见）
- expose() Python 回调在页面 realm 与 eval 均可调用（expose_probe 实测），
  返回值进 JS——引擎→Python 直通道，realm 无关
v5：atob wrapper 内 try{ __psaSink(in,out) }catch——值直落 Python 列表，
无 drain。sink 异常被吞，求解不受扰动。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "ruyijs-api-log-20261107"
LOG_DIR = OUT_DIR / "api-log"
BODY_DIR = OUT_DIR / "fo-bodies"
VAL_DIR = OUT_DIR / "atob-values"
VAL_DIR.mkdir(parents=True, exist_ok=True)

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
CONTEXT_TIMEOUT = 400.0
MAX_TASKS = 100000
PUMP_WALL_S = 150.0
SINK_LIMIT = 20000  # 帧上限：溢出后只计数不再传值

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
    try { __psaSink(s, String(out)); } catch (e) {}
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
    overflow = [0]

    def sink(inp, outp):
        if len(pairs) < SINK_LIMIT:
            pairs.append(str(inp) + "\u0001" + str(outp))
        else:
            overflow[0] += 1
        return True

    cert_ok = False
    ctx = ruyijs.Context(timeout=CONTEXT_TIMEOUT, mode="debug")
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.expose(sink, "__psaSink")
        try:
            ctx.native("atob", ATOBSRC)
        except Exception:
            pass
        ctx.navigate(PAGE_URL)
        try:
            ctx.advance(10000, max_tasks=MAX_TASKS)
        except Exception:
            pass
        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        while time.monotonic() < deadline:
            try:
                ctx.native("atob", ATOBSRC)  # 幂等（__psaHooked 守卫）
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
            if cert_ok and len(done) >= 3:
                break
            if time.monotonic() - last_progress > 30.0:
                break
            time.sleep(0.25)
        manifest = []
        for i, pair in enumerate(pairs):
            data = pair.encode("utf-8", "surrogatepass")
            digest = hashlib.sha256(data).hexdigest()[:16]
            (VAL_DIR / f"atob-{i:04d}-{digest}.txt").write_bytes(data)
            manifest.append({"i": i, "bytes": len(data), "sha16": digest})
        try:
            log = ctx._request("api_log", action="get")
        except Exception:
            log = []
        if isinstance(log, list):
            (LOG_DIR / "atob-run-sequence.json").write_text(
                json.dumps(log, ensure_ascii=False), encoding="utf-8")
        bodies = []
        for e in [e for e in ctx.net_log() if isinstance(e, dict)]:
            if e.get("method") != "POST" or "/cdn-cgi/" not in str(e.get("url", "")):
                continue
            body = e.get("requestBody")
            if body is None:
                continue
            data = body.encode("utf-8", "surrogatepass") if isinstance(body, str) else bytes(body)
            digest = hashlib.sha256(data).hexdigest()[:16]
            (BODY_DIR / f"atob-run-fo-{len(bodies)}-{digest}.txt").write_bytes(data)
            bodies.append({"idx": len(bodies), "status": e.get("status"),
                           "bytes": len(data), "sha16": digest})
        print(json.dumps({
            "certOk": cert_ok, "atobCalls": len(manifest), "overflow": overflow[0],
            "foBodies": len(bodies),
            "apiLogRecords": len(log) if isinstance(log, list) else 0,
        }, ensure_ascii=False))
    finally:
        try:
            ctx.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
