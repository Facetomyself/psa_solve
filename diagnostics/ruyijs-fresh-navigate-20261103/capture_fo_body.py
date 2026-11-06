#!/usr/bin/env python3
"""capture_fo_body.py — 捕获 ruyijs FO POST 请求体做 Node 侧字段级 diff。

与 run2_022 同链路，但提前在 certOk 即停，net_log 原始 requestBody 落盘到
诊断目录（私有，gitignore 域）。stdout 只报计数与哈希前缀，不回显载荷。
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
OUT_DIR = PROJECT / "diagnostics" / "ruyijs-fresh-navigate-20261103"
BODY_DIR = OUT_DIR / "fo-bodies"
BODY_DIR.mkdir(parents=True, exist_ok=True)

CONTEXT_TIMEOUT = 400.0
MAX_TASKS = 100000
PUMP_WALL_S = 120.0

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


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import ruyijs

    ctx = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    captured = []
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.navigate(PAGE_URL)
        try:
            ctx.advance(10000, max_tasks=MAX_TASKS)
        except Exception:
            pass
        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        seen = 0
        while time.monotonic() < deadline:
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(ctx, fn)(**kw)
                except Exception:
                    pass
            try:
                ctx.advance(500, max_tasks=32000)
            except Exception:
                pass
            raw = ctx.net_log()
            entries = [e for e in raw if isinstance(e, dict)]
            posts = [e for e in entries
                     if e.get("method") == "POST" and "/cdn-cgi/" in str(e.get("url", ""))]
            if len(entries) != seen:
                seen = len(entries)
                last_progress = time.monotonic()
            if len(posts) >= 2 and not any(e.get("status") == 0 for e in posts[:2]):
                # FO r1 与后续轮都已回来，够 diff 用，提前收
                break
            if time.monotonic() - last_progress > 25.0:
                break
            time.sleep(0.25)
        raw = ctx.net_log()
        for e in raw:
            if not isinstance(e, dict) or e.get("method") != "POST":
                continue
            url = str(e.get("url", ""))
            if "/cdn-cgi/" not in url:
                continue
            body = e.get("requestBody")
            if body is None:
                continue
            data = body.encode("utf-8", "surrogatepass") if isinstance(body, str) else bytes(body)
            digest = hashlib.sha256(data).hexdigest()[:16]
            path = BODY_DIR / f"fo-post-{len(captured)}-{digest}.txt"
            path.write_bytes(data)
            captured.append({
                "idx": len(captured),
                "status": e.get("status"),
                "bodyBytes": len(data),
                "sha16": digest,
                "file": path.name,
                "head4": data[:4].decode("latin1", "replace"),
            })
    finally:
        try:
            ctx.close()
        except Exception:
            pass
    print(json.dumps({"count": len(captured), "captures": captured[:6]}, ensure_ascii=False, indent=1))
    return 0 if captured else 1


if __name__ == "__main__":
    sys.exit(main())
