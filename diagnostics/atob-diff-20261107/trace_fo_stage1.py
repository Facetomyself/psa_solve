#!/usr/bin/env python3
"""trace_fo_stage1.py — 同字节 FO trace 阶段 1：探 ruyijs 在 Node 同会话材料上生成的 FO URL。

背景：online-probe-* 目录是一份完整同会话三元组（403 页 + orchestrate JS +
FO r1 响应字节）。Node 在这份材料上 FO r1 后陷入 DD/vA 重试忙循环；ruyijs 在
同目标在线全链秒级完成。要对齐两侧，先回答：ruyijs 用同一份材料生成的 FO 请求
URL 是否与 Node 抓到的一致（若一致即可在阶段 2 预注册 Node 的 FO 响应字节）。

本阶段不注入 FO 响应，只观察：
- load_page 是否命中 put_resource 的 orchestrate；
- ruyijs 生成的 FO POST URL（绝对化）与 Node 的 fo-resp-1.json.url 对比；
- net_log 条目（method/url/status/matched）与推进错误。

产物：<TRACE_OUT>/stage1.json（FO URL/请求含会话签名，放 online-probe-* 忽略域）
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
DIAG = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT = Path(sys.argv[1]) if len(sys.argv) > 1 else (DIAG / "online-probe-new")
OUT = Path(os.environ.get("TRACE_OUT") or (DIAG / "online-probe-ruyijs-fo" / "stage1"))
OUT.mkdir(parents=True, exist_ok=True)

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
BASE = "https://www.psacard.com"
MAX_TASKS = 100000
PUMP_WALL_S = float(os.environ.get("TRACE_WALL_S", "90"))
SETTLE_S = float(os.environ.get("TRACE_SETTLE_S", "5"))

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


def slim(entry, url_cap=900):
    row = {}
    for key, value in entry.items():
        if isinstance(value, str) and len(value) > url_cap:
            value = value[:url_cap] + "…(%d)" % len(entry[key])
        row[key] = value
    return row


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"

    import ruyijs

    html = (MAT / "403-page.html").read_text(encoding="utf-8")
    orch = (MAT / "orchestrate.js").read_bytes()
    fo_meta = json.loads((MAT / "fo-dump" / "fo-resp-1.json").read_text(encoding="utf-8"))
    node_fo_url = BASE + fo_meta["url"]

    match = re.search(r"""src\s*=\s*["']([^"']*orchestrate[^"']*)""", html)
    src = match.group(1) if match else ""
    orch_url = src if src.startswith("http") else BASE + src
    orch_noq = orch_url.split("?", 1)[0]

    log = {
        "mat": str(MAT), "orch_url": orch_url, "node_fo_url": node_fo_url,
        "node_fo_len": len(fo_meta.get("url", "")),
        "fo_entries": [], "advance_errors": [], "net": [],
    }
    seen = {}
    fo_first_at = None
    t0 = time.monotonic()
    ctx = ruyijs.Context(timeout=120.0)
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        headers = [["content-type", "application/javascript"]]
        ctx.put_resource(orch_url, orch, status=200, headers=headers)
        ctx.put_resource(orch_noq, orch, status=200, headers=headers)
        log["load_page"] = ctx.load_page(PAGE_URL, html)
        log["load_page_s"] = round(time.monotonic() - t0, 2)

        deadline = time.monotonic() + PUMP_WALL_S
        while time.monotonic() < deadline:
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(ctx, fn)(**kw)
                except Exception:
                    pass
            try:
                ctx.advance(500, max_tasks=32000)
            except Exception as exc:
                msg = "%s: %s" % (type(exc).__name__, str(exc)[:160])
                if len(log["advance_errors"]) < 40 and msg not in log["advance_errors"]:
                    log["advance_errors"].append(msg)
            try:
                entries = ctx.net_log()
            except Exception:
                entries = []
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                entry_id = entry.get("id")
                if entry_id in seen:
                    continue
                seen[entry_id] = True
                url = str(entry.get("url", ""))
                if "/fo/" in url or url.rstrip("/").endswith("/fo"):
                    if fo_first_at is None:
                        fo_first_at = time.monotonic()
                        log["first_fo_at_s"] = round(fo_first_at - t0, 2)
                    log["fo_entries"].append(slim(entry, 2000))
            if fo_first_at is not None and time.monotonic() - fo_first_at > SETTLE_S:
                break
            time.sleep(0.1)
    except Exception as exc:
        log["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            raw = ctx.net_log()
            if isinstance(raw, list):
                log["net"] = [slim(e) for e in raw if isinstance(e, dict)]
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass

    log["elapsed_s"] = round(time.monotonic() - t0, 2)
    log["net_count"] = len(log["net"])
    matched = sum(1 for e in log["net"] if e.get("matched"))
    log["net_matched"] = matched
    # FO URL 对比（去掉同源前缀，逐段找第一个不同字符）
    if log["fo_entries"]:
        ruyi_url = BASE + str(log["fo_entries"][0].get("url", ""))
        log["ruyijs_fo_url"] = ruyi_url
        same = ruyi_url == node_fo_url
        log["fo_url_same_as_node"] = same
        if not same:
            prefix = 0
            for a, b in zip(ruyi_url, node_fo_url):
                if a != b:
                    break
                prefix += 1
            log["fo_url_first_diff"] = prefix
            log["fo_url_ruyijs_tail"] = ruyi_url[prefix:prefix + 160]
            log["fo_url_node_tail"] = node_fo_url[prefix:prefix + 160]

    (OUT / "stage1.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "ok": "error" not in log,
        "error": log.get("error"),
        "load_page_s": log.get("load_page_s"),
        "elapsed_s": log["elapsed_s"],
        "net": log["net_count"], "matched": matched,
        "fo_entries": len(log["fo_entries"]),
        "fo_url_same": log.get("fo_url_same_as_node"),
        "fo_first_diff": log.get("fo_url_first_diff"),
        "out": str(OUT / "stage1.json"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
