#!/usr/bin/env python3
"""replay_fo_ruyijs.py — 用 online-probe 抓到的 FO 响应字节做 ruyijs 离线回放 oracle。

材料（全部来自同一次 Node 在线会话）：
  online-probe/403-page.html
  online-probe/orchestrate.js
  online-probe/fo-dump/fo-resp-1.json   （URL/状态/响应头）
  online-probe/fo-dump/fo-resp-1-200.bin（229968B 加密下一阶段程序）

流程：ruyijs 离线 load_page + put_resource(orchestrate) + put_resource(FO URL → 响应字节)，
泵循环观察 FO POST 后引擎是否快速解码并继续发后续请求（FO r2 / eb）。同时用
expose sink 捕获 atob 输入/输出（值级真值），定位 Node 侧长解码的分歧点。

产物（gitignore 域）：ruyijs-fo-atob.jsonl、ruyijs-fo-netlog.json、stdout JSON 摘要。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
PROBE_DIR = OUT_DIR / "online-probe"

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
MAX_TASKS = 100000
PUMP_WALL_S = float(os.environ.get("FO_REPLAY_WALL", "120"))

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

    page_html = (PROBE_DIR / "403-page.html").read_text(encoding="utf-8")
    orch_js = (PROBE_DIR / "orchestrate.js").read_bytes()

    # FO 响应材料
    fo_meta = None
    fo_body = b""
    for cand in sorted((PROBE_DIR / "fo-dump").glob("fo-resp-*.json")):
        meta = json.loads(cand.read_text(encoding="utf-8"))
        if meta.get("status") != 200:
            continue
        bin_cand = cand.with_name(cand.stem + "-200.bin")
        if bin_cand.exists():
            fo_meta = meta
            fo_body = bin_cand.read_bytes()
            break
    if not fo_meta or not fo_body:
        print(json.dumps({"ok": False, "reason": "no FO 200 dump in online-probe/fo-dump"}))
        return 1

    fo_path = str(fo_meta.get("url", ""))
    fo_url = fo_path if fo_path.startswith("http") else "https://www.psacard.com" + fo_path
    hdrs = []
    for k, v in (fo_meta.get("headers") or {}).items():
        if isinstance(v, list):
            for item in v:
                hdrs.append([str(k), str(item)])
        else:
            hdrs.append([str(k), str(v)])

    atob_events = []
    sink_errors = 0

    def sink(direction, inp, outp):
        nonlocal sink_errors
        try:
            if len(atob_events) < 20000:
                atob_events.append([str(direction), len(inp), len(outp)])
        except Exception:
            sink_errors += 1
        return True

    ctx = ruyijs.Context(timeout=180.0)
    net = []
    error = None
    t0 = time.monotonic()
    fo_first_at = None
    post_fo_requests = []
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.expose(sink, "__psaSink")
        ctx.native("atob", ATOBSRC)
        ctx.native("btoa", BTOSRC)

        # orchestrate URL：从页面 loader 脚本提取（与 Node 同源）
        import re
        m = re.search(r"a\.src\s*=\s*'([^']+)'", page_html)
        orch_url = "https://www.psacard.com" + m.group(1) if m else ""
        if orch_url:
            ctx.put_resource(orch_url, orch_js, status=200,
                             headers=[["content-type", "application/javascript"]])
            ctx.put_resource(orch_url.split("?", 1)[0], orch_js, status=200,
                             headers=[["content-type", "application/javascript"]])
        ctx.put_resource(fo_url, fo_body, status=200, headers=hdrs)
        ctx.put_resource(fo_url.split("?", 1)[0], fo_body, status=200, headers=hdrs)

        ctx.load_page(PAGE_URL, page_html)
        try:
            ctx.advance(3000, max_tasks=MAX_TASKS)
        except Exception as exc:  # noqa: BLE001
            error = "advance1: %s: %s" % (type(exc).__name__, str(exc)[:200])

        deadline = time.monotonic() + PUMP_WALL_S
        seen = 0
        last_progress = time.monotonic()
        while time.monotonic() < deadline:
            try:
                ctx.native("atob", ATOBSRC)
                ctx.native("btoa", BTOSRC)
            except Exception:  # noqa: BLE001
                pass
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(ctx, fn)(**kw)
                except Exception:  # noqa: BLE001
                    pass
            try:
                ctx.advance(500, max_tasks=32000)
            except Exception:  # noqa: BLE001
                pass
            try:
                raw = ctx.net_log()
                entries = [e for e in raw if isinstance(e, dict)]
            except Exception:  # noqa: BLE001
                entries = []
            if len(entries) != seen:
                seen = len(entries)
                last_progress = time.monotonic()
            posts = [e for e in entries if e.get("method") == "POST"]
            if posts and fo_first_at is None:
                fo_first_at = round(time.monotonic() - t0, 2)
            if len(posts) >= 2 and len(post_fo_requests) == 0:
                post_fo_requests = [
                    {"url": str(e.get("url", ""))[:100],
                     "bodyLen": len(str(e.get("requestBody") or e.get("body") or "")),
                     "status": e.get("status")}
                    for e in posts[1:4]
                ]
                break
            if time.monotonic() - last_progress > 30.0:
                break
            time.sleep(0.1)

        try:
            raw = ctx.net_log()
            net = [e for e in raw if isinstance(e, dict)]
        except Exception:  # noqa: BLE001
            net = []
    except Exception as exc:  # noqa: BLE001
        error = "%s: %s" % (type(exc).__name__, str(exc)[:300])

    elapsed = round(time.monotonic() - t0, 1)
    (OUT_DIR / "ruyijs-fo-atob.jsonl").write_text(
        "\n".join(json.dumps(e) for e in atob_events), encoding="utf-8")
    (OUT_DIR / "ruyijs-fo-netlog.json").write_text(
        json.dumps(net[-80:], ensure_ascii=False, indent=1), encoding="utf-8")

    big = sorted(atob_events, key=lambda x: -x[1])[:5]
    print(json.dumps({
        "ok": True,
        "elapsedS": elapsed,
        "foUrlMatched": bool(fo_url),
        "foBodyBytes": len(fo_body),
        "foFirstPostAtS": fo_first_at,
        "postFoRequests": post_fo_requests,
        "netEvents": len(net),
        "atobCalls": len(atob_events),
        "topAtob": big,
        "error": error,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
