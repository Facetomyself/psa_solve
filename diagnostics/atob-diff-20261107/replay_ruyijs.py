#!/usr/bin/env python3
"""replay_ruyijs.py — 消变体对拍第 1 步（v2）：ruyijs 离线吃配对材料。

背景（2026-11-07 首轮回放反转）：curl_cffi 事后抓的 orchestrate 与录制会话执行的
是不同加密变体（27488B 常量同位 20.3% 字节差），两侧"同一份材料"前提失效。
本脚本改为：配对抓取（同 curl_cffi 会话拿 403 页 + orchestrate JS）后，ruyijs
不联网——load_page(403 页 HTML) + put_resource(orchestrate URL → 该 JS)，
引擎对 orchestrate script src 的 GET 由预置资源命中，执行与 Node 回放完全
相同的字节。atob/btoa 值经 expose sink 全量落盘。

对拍窗口：orchestrate 静态执行段（aa/a0 解密器流），FO POST 前终止。
产物：ruyijs-pair-atob.jsonl + ruyijs-pair-netlog.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT_DIR = OUT_DIR / "replay-materials"

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
MAX_TASKS = 100000
PUMP_WALL_S = 60.0

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

    page_html = (MAT_DIR / "pair-challenge-page.html").read_text(encoding="utf-8")
    orch_js = (MAT_DIR / "pair-orchestrate.js").read_bytes()
    orch_url = (MAT_DIR / "pair-orchestrate-url.txt").read_text(encoding="utf-8").strip()

    pairs = []
    pair_ts = []
    fo_seen = []
    apilog = []  # {p,t,d,n} 中 p 为 atob/btoa 的条目（debug 模式行号归因）

    def drain_apilog():
        try:
            batch = ctx._request("api_log", action="get")
        except Exception:
            return
        if not isinstance(batch, list):
            return
        for e in batch:
            if isinstance(e, dict) and e.get("p") in ("atob", "btoa"):
                apilog.append(e)

    def sink(direction, inp, outp):
        if len(pairs) < 20000:
            pairs.append((str(direction), str(inp), str(outp)))
            pair_ts.append(time.monotonic())
        return True

    ctx = ruyijs.Context(timeout=120.0, mode="debug")
    net = []
    error = None
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.expose(sink, "__psaSink")
        # 预置 orchestrate 响应（去 query 的精确 URL + 带 query 双写，保匹配）
        orch_noq = orch_url.split("?", 1)[0]
        headers = [["content-type", "application/javascript"]]
        ctx.put_resource(orch_url, orch_js, status=200, headers=headers)
        ctx.put_resource(orch_noq, orch_js, status=200, headers=headers)
        # 其余静态请求回空体（挑战平台 API JS 等——本窗口不依赖其内容）
        ctx.native("atob", ATOBSRC)
        ctx.native("btoa", BTOSRC)

        ctx.load_page(PAGE_URL, page_html)
        try:
            ctx.advance(3000, max_tasks=MAX_TASKS)
        except Exception as exc:
            error = "advance1: %s: %s" % (type(exc).__name__, str(exc)[:200])

        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        last_count = len(pairs)
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
            drain_apilog()
            try:
                raw = ctx.net_log()
                entries = [e for e in raw if isinstance(e, dict)] if isinstance(raw, list) else []
            except Exception:
                entries = []
            fo = [e for e in entries
                  if e.get("method") == "POST" and "/cdn-cgi/" in str(e.get("url", ""))]
            if fo:
                if not fo_seen:
                    # 首次 FO 发出时刻：用时间戳与 pair_ts 对齐，精确到调用级
                    fo_seen.append(str(fo[-1].get("url", ""))[:120])
                    t_fo = time.monotonic()
                    first_after = next((k for k, t in enumerate(pair_ts) if t > t_fo), -1)
                    net.append({"event": "first_fo",
                                "at_pairs": len(pairs),
                                "first_pair_after": first_after})
                last_progress = time.monotonic()
            if len(pairs) != last_count:
                last_count = len(pairs)
                last_progress = time.monotonic()
            if len(fo_seen) >= 1 and time.monotonic() - last_progress > 8.0:
                break  # FO 已开始，静态解码窗口结束
            if time.monotonic() - last_progress > 20.0:
                break
            time.sleep(0.2)
    except Exception as exc:
        error = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            drain_apilog()
        except Exception:
            pass
        try:
            raw = ctx.net_log()
            for e in ([x for x in raw if isinstance(x, dict)] if isinstance(raw, list) else []):
                row = {}
                for k, v in e.items():
                    if isinstance(v, str) and len(v) > 160:
                        v = v[:160]
                    row[k] = v
                net.append(row)
        except Exception:
            pass
        try:
            ctx.close()
        except Exception:
            pass

    rows = [{"n": i, "dir": d, "i": x, "o": y} for i, (d, x, y) in enumerate(pairs)]
    (OUT_DIR / "ruyijs-pair-atob.jsonl").write_text(
        "\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    (OUT_DIR / "ruyijs-pair-netlog.json").write_text(
        json.dumps(net, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT_DIR / "ruyijs-pair-apilog.jsonl").write_text(
        "\n".join(json.dumps(r) for r in apilog), encoding="utf-8")

    # 快速自检：atob 输入来自 pair JS 的比例
    orch_text = orch_js.decode("utf-8", errors="replace")
    dec = [r for r in rows if r["dir"] == "d"]
    if dec:
        hit = sum(1 for r in dec[:50] if ("`" + r["i"] + "`") in orch_text)
    else:
        hit = 0
    print(json.dumps({
        "ok": error is None, "error": error, "pairs": len(rows),
        "foPosts": len(fo_seen), "netEvents": len(net),
        "first50-in-pairJS": hit,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
