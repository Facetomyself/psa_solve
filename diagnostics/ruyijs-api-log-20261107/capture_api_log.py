#!/usr/bin/env python3
"""capture_api_log.py — ruyijs debug 模式下全求解过程的宿主面访问序列捕获。

目的：拿引擎内 ground truth（挑战各阶段读了哪些宿主成员、什么顺序），作为
Node 桥补环境的规格来源（spec-driven，替代 crash-driven 打地鼠）。
机制：Context(mode="debug") 启用引擎 ApiMonitor（源码确认：只记录不改行为，
不装任何页面属性）；泵循环内按 FO 轮分段 drain（action="clear"）。
产物：api-log/ 目录（gitignore 域，本地事实）——分段序列 + FO body 哈希对齐。
stdout：仅计数与哈希，不回显载荷与访问明细。
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
OUT_DIR = PROJECT / "diagnostics" / "ruyijs-api-log-20261107"
LOG_DIR = OUT_DIR / "api-log"
BODY_DIR = OUT_DIR / "fo-bodies"
LOG_DIR.mkdir(parents=True, exist_ok=True)
BODY_DIR.mkdir(parents=True, exist_ok=True)

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


def redact(u: str) -> str:
    parts = urlsplit(str(u))
    return parts.netloc + parts.path


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import ruyijs

    ctx = ruyijs.Context(timeout=CONTEXT_TIMEOUT, mode="debug")
    segments = []          # 每个 FO 轮一段：[{p,t,d,n}, ...]
    net_summary = []       # 每条网络事件：{method, path, status}
    buffer = []            # 当前段
    fo_seen = 0
    cert_ok = False
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
        while time.monotonic() < deadline:
            # drain 本轮新增访问（peek 拿走 + clear 清空）
            try:
                batch = ctx._request("api_log", action="get")
                if isinstance(batch, list):
                    buffer.extend(batch)
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
            try:
                batch = ctx._request("api_log", action="get")
                if isinstance(batch, list):
                    buffer.extend(batch)
            except Exception:
                pass
            entries = [e for e in ctx.net_log() if isinstance(e, dict)]
            posts = [e for e in entries
                     if e.get("method") == "POST" and "/cdn-cgi/" in str(e.get("url", ""))]
            # 新 FO 轮完成（有响应）→ 切段
            done_posts = [e for e in posts if e.get("status") not in (None, 0)]
            if len(done_posts) > fo_seen:
                fo_seen = len(done_posts)
                path = LOG_DIR / f"segment-fo{fo_seen}.json"
                path.write_text(json.dumps(buffer, ensure_ascii=False), encoding="utf-8")
                segments.append({"fo": fo_seen, "records": len(buffer), "file": path.name})
                buffer = []
                last_progress = time.monotonic()
            if len(entries) != len(net_summary):
                for e in entries[len(net_summary):]:
                    net_summary.append({"method": e.get("method"),
                                        "path": redact(e.get("url", "")),
                                        "status": e.get("status")})
                last_progress = time.monotonic()
            # cert readback（求解成功的读出口）
            gets = [e for e in entries if e.get("method") == "GET"
                    and "/cert/" in str(e.get("url", "")) and e.get("status") == 200]
            if gets and not cert_ok:
                cert_ok = True
            if cert_ok and len(done_posts) >= 3:
                break
            if time.monotonic() - last_progress > 30.0:
                break
            time.sleep(0.25)
        # 残段收尾
        if buffer:
            path = LOG_DIR / f"segment-final-{len(segments) + 1}.json"
            path.write_text(json.dumps(buffer, ensure_ascii=False), encoding="utf-8")
            segments.append({"fo": "final", "records": len(buffer), "file": path.name})
        # FO body 落盘（与既有 capture_fo_body.py 同规则）
        bodies = []
        for e in [e for e in ctx.net_log() if isinstance(e, dict)]:
            if e.get("method") != "POST" or "/cdn-cgi/" not in str(e.get("url", "")):
                continue
            body = e.get("requestBody")
            if body is None:
                continue
            data = body.encode("utf-8", "surrogatepass") if isinstance(body, str) else bytes(body)
            digest = hashlib.sha256(data).hexdigest()[:16]
            (BODY_DIR / f"fo-post-{len(bodies)}-{digest}.txt").write_bytes(data)
            bodies.append({"idx": len(bodies), "status": e.get("status"),
                           "bytes": len(data), "sha16": digest})
        # 访问序列总体形状（只报成员名计数，不报值）
        all_recs = []
        for seg in segments:
            all_recs.extend(json.loads((LOG_DIR / seg["file"]).read_text(encoding="utf-8")))
        members = {}
        for r in all_recs:
            if isinstance(r, dict) and isinstance(r.get("p"), str):
                members[r["p"]] = members.get(r["p"], 0) + 1
        top = sorted(members.items(), key=lambda kv: -kv[1])[:30]
        (OUT_DIR / "summary.json").write_text(json.dumps({
            "certOk": cert_ok,
            "segments": segments,
            "netEvents": net_summary,
            "foBodies": bodies,
            "totalRecords": len(all_recs),
            "distinctMembers": len(members),
            "topMembers": top,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({
            "certOk": cert_ok, "segments": len(segments),
            "totalRecords": len(all_recs),
            "distinctMembers": len(members),
            "netEvents": len(net_summary),
            "foBodies": len(bodies),
        }, ensure_ascii=False))
    finally:
        try:
            ctx.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
