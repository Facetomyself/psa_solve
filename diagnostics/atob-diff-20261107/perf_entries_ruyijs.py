#!/usr/bin/env python3
"""perf_entries_ruyijs.py — 取 ruyijs 引擎对配对材料的 performance.getEntries() 真值。

背景：Node 桥在 FO r1 响应驱动的嵌套字节码解释器里长跑不收敛（#17 ~110k op/秒）。
修复前是 vm-default 崩溃。两者共同点：FO 载荷的 performance 条目与引擎真值不一致
→ 键控流错位。本脚本在 ruyijs 离线回放同一对材料，直接 eval
performance.getEntries()，给出条目名/类型/时序真值，杨 Node 侧 __perfRecord 补条目。

产物：perf-entries-ruyijs.json（含 load_page 后立即 + 泵若干轮后的快照）
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT_DIR = OUT_DIR / "replay-materials"

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
MAX_TASKS = 100000

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

DUMP_JS = r"""
JSON.stringify((function () {
  function pack(e) {
    return {
      entryType: e.entryType,
      name: String(e.name),
      startTime: e.startTime,
      duration: e.duration,
      initiatorType: e.initiatorType,
      requestStart: e.requestStart,
      responseStart: e.responseStart,
      responseEnd: e.responseEnd,
      transferSize: e.transferSize,
      encodedBodySize: e.encodedBodySize,
      decodedBodySize: e.decodedBodySize,
      type: e.type,
    };
  }
  var all = performance.getEntries();
  var byType = {};
  try {
    byType = {
      navigation: performance.getEntriesByType('navigation').map(pack),
      resource: performance.getEntriesByType('resource').map(pack),
      mark: performance.getEntriesByType('mark').map(pack),
    };
  } catch (e) { byType = {error: String(e)}; }
  return {all: all.map(pack), byType: byType};
})())
"""


def dump(ctx, tag, out):
    try:
        raw = ctx.eval(DUMP_JS, to_py=True)
        out[tag] = json.loads(raw) if isinstance(raw, str) else raw
    except Exception as exc:  # noqa: BLE001
        out[tag] = {"error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import ruyijs

    page_html = (MAT_DIR / "pair-challenge-page.html").read_text(encoding="utf-8")
    orch_js = (MAT_DIR / "pair-orchestrate.js").read_bytes()
    orch_url = (MAT_DIR / "pair-orchestrate-url.txt").read_text(encoding="utf-8").strip()

    ctx = ruyijs.Context(timeout=120.0)
    out = {"material": {"orchUrl": orch_url, "pageBytes": len(page_html),
                        "orchBytes": len(orch_js)}}
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        orch_noq = orch_url.split("?", 1)[0]
        headers = [["content-type", "application/javascript"]]
        ctx.put_resource(orch_url, orch_js, status=200, headers=headers)
        ctx.put_resource(orch_noq, orch_js, status=200, headers=headers)
        ctx.load_page(PAGE_URL, page_html)
        dump(ctx, "afterLoadPage", out)
        try:
            ctx.advance(3000, max_tasks=MAX_TASKS)
        except Exception as exc:  # noqa: BLE001
            out["advance1Error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        dump(ctx, "afterAdvance3000", out)
        deadline = time.monotonic() + 15.0
        while time.monotonic() < deadline:
            try:
                ctx.checkpoint()
                ctx.drain_timers(max_tasks=8192)
                ctx.advance(500, max_tasks=32000)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(0.1)
        dump(ctx, "afterPump", out)
    except Exception as exc:  # noqa: BLE001
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            dump(ctx, "final", out)
        except Exception:  # noqa: BLE001
            pass

    (OUT_DIR / "perf-entries-ruyijs.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    # stdout 摘要
    summary = {}
    for tag in ("afterLoadPage", "afterAdvance3000", "afterPump", "final"):
        snap = out.get(tag) or {}
        if "error" in snap:
            summary[tag] = {"error": snap["error"]}
            continue
        by = snap.get("byType") or {}
        summary[tag] = {
            "total": len(snap.get("all") or []),
            "navigation": [e.get("name") for e in by.get("navigation") or []],
            "resources": [e.get("name") for e in by.get("resource") or []],
            "marks": [e.get("name") for e in by.get("mark") or []],
        }
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
