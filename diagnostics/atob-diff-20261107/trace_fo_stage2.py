#!/usr/bin/env python3
"""trace_fo_stage2.py — 同字节 FO trace 对齐：ruyijs 吃 Node 同会话的 FO 响应字节。

前置（阶段 1 实测）：同一份材料下 ruyijs 生成的 FO r1 URL 与 Node 抓到的
268 字符 URL 逐字节相同（ray/cITime 来自页面材料），因此可以在 load_page
之前用 put_resource 精确预注册 Node 的 FO 响应，让引擎走与 Node 完全相同的
输入字节，不联网。

同时 orchestrate 使用 make_instrumented.js 生成的插桩版（插桩算法原样复制自
runtime/run.js）：Node probe 侧是 applied x1/loopcounters=42，本侧同算法同字节
必然同 id。pump 期间用 ctx.eval 读 globalThis.__lc / __hotp，与 Node 侧
inspector 采样逐 id 对照，回答：ruyijs 正常解码时同一组循环的调用量是否有限，
Node 的热循环（如 id 7/10 的 5 指令状态机）在 ruyijs 侧是否也热。

产物（gitignore 域 online-probe-*）：stage2.json / samples.jsonl / atob.jsonl
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
DIAG = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT = Path(sys.argv[1]) if len(sys.argv) > 1 else (DIAG / "online-probe-new")
OUT = Path(os.environ.get("TRACE_OUT") or (DIAG / "online-probe-ruyijs-fo" / "stage2"))
OUT.mkdir(parents=True, exist_ok=True)
# 逐 opcode 落盘的循环 id（逗号分隔）；空串 = 只做循环计数
OP_IDS = os.environ.get("TRACE_OP_IDS", "").strip()

PAGE_URL = "https://www.psacard.com/cert/143963534/psa"
BASE = "https://www.psacard.com"
NODE = r"D:\reverse_ENV\tools\node\node.exe"
MAKE_INST = DIAG / "make_instrumented.js"
PUMP_WALL_S = float(os.environ.get("TRACE_WALL_S", "60"))
SAMPLE_EVERY = float(os.environ.get("TRACE_SAMPLE_S", "0.2"))
MAX_SAMPLES = int(os.environ.get("TRACE_MAX_SAMPLES", "600"))
MAX_SMALL_ATOBS = 20000

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

# 与 replay_ruyijs.py 相同语义；大输入（>20000）只回传长度，避免 RPC 巨帧。
ATOBSRC = """(function () {
  var cur = globalThis.atob;
  if (cur && cur.__psaHooked) return cur;
  var orig = cur;
  var wrapper = function (input) {
    var s = String(input);
    var out = orig.call(globalThis, s);
    try {
      if (s.length > 20000) __psaSink('D', String(s.length), String(out.length));
      else __psaSink('d', s, String(out));
    } catch (e) {}
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

LC_EXPR = "JSON.stringify([globalThis.__lc||null,globalThis.__hotp||null])"


def slim(entry, cap=800):
    row = {}
    for key, value in entry.items():
        if isinstance(value, str) and len(value) > cap:
            value = value[:cap] + "…(%d)" % len(entry[key])
        row[key] = value
    return row


def ensure_instrumented(orch_bytes: bytes) -> Path:
    tag = re.sub(r"[^0-9A-Za-z_]+", "_", OP_IDS) or "plain"
    inst = OUT / ("orchestrate.instrumented.%s.js" % tag)
    meta = Path(str(inst) + ".meta.json")
    if inst.is_file() and meta.is_file():
        return inst
    src = OUT / ("orchestrate.plain.%s.js" % tag)
    src.write_bytes(orch_bytes)
    env = dict(os.environ)
    env["CF_HOT_SNAPSHOT"] = "1"
    env["CF_OP_TRACE"] = OP_IDS
    import subprocess
    proc = subprocess.run(
        [NODE, str(MAKE_INST), str(src), str(inst), "5000000"],
        capture_output=True, text=True, env=env, timeout=120)
    if proc.returncode != 0:
        raise RuntimeError("make_instrumented failed: " + (proc.stderr or "")[-800:])
    return inst


def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"

    import ruyijs

    html = (MAT / "403-page.html").read_text(encoding="utf-8")
    orch = (MAT / "orchestrate.js").read_bytes()
    fo_meta = json.loads((MAT / "fo-dump" / "fo-resp-1.json").read_text(encoding="utf-8"))
    fo_body = (MAT / "fo-dump" / "fo-resp-1-200.bin").read_bytes()
    node_fo_url = BASE + fo_meta["url"]

    match = re.search(r"""src\s*=\s*["']([^"']*orchestrate[^"']*)""", html)
    src = match.group(1) if match else ""
    orch_url = src if src.startswith("http") else BASE + src
    orch_noq = orch_url.split("?", 1)[0]

    inst_path = ensure_instrumented(orch)
    inst_bytes = inst_path.read_bytes()
    inst_meta = json.loads(Path(str(inst_path) + ".meta.json").read_text(encoding="utf-8"))

    fo_headers = []
    for name in ("date", "content-type", "content-length", "connection",
                 "cf-chl-gen", "timing-allow-origin", "server", "cf-ray", "alt-svc"):
        value = fo_meta.get("headers", {}).get(name)
        if isinstance(value, str):
            fo_headers.append([name, value])
    for cookie in fo_meta.get("headers", {}).get("set-cookie", []) or []:
        fo_headers.append(["set-cookie", cookie])

    small_atob, big_atob = [], []
    samples = []
    net_seen = {}
    net_rows = []
    state = {"fo_matched": None, "fo_status": None}

    def sink(direction, inp, outp):
        if direction == "D":
            if len(big_atob) < 200:
                big_atob.append({"in": int(inp), "out": int(outp)})
        elif len(small_atob) < MAX_SMALL_ATOBS:
            small_atob.append({"dir": str(direction), "i": str(inp), "o": str(outp)})
        return True

    t0 = time.monotonic()
    log = {
        "mat": str(MAT), "orch_url": orch_url,
        "instr": {"meta": inst_meta, "bytes": len(inst_bytes), "plain": len(orch)},
        "node_fo_url": node_fo_url, "fo_body_len": len(fo_body),
        "fo_body_sha256": hashlib.sha256(fo_body).hexdigest(),
        "fo_headers": [[k, v[:80]] for k, v in fo_headers],
        "fo_entries": [], "advance_errors": [], "eval_errors": [],
    }
    ctx = ruyijs.Context(timeout=60.0)
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        headers = [["content-type", "application/javascript"]]
        ctx.expose(sink, "__psaSink")
        ctx.native("atob", ATOBSRC)
        ctx.native("btoa", BTOSRC)
        # 预注册插桩版 orchestrate（精确 + 去 query 双写）
        ctx.put_resource(orch_url, inst_bytes, status=200, headers=headers)
        ctx.put_resource(orch_noq, inst_bytes, status=200, headers=headers)
        # 预注册 Node 同会话 FO r1 响应（精确 URL；阶段 1 已证 URL 同字节）
        ctx.put_resource(node_fo_url, fo_body, status=200, headers=fo_headers)
        log["load_page"] = ctx.load_page(PAGE_URL, html)
        log["load_page_s"] = round(time.monotonic() - t0, 2)

        deadline = time.monotonic() + PUMP_WALL_S
        next_sample = 0.0
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
                if entry_id in net_seen:
                    continue
                net_seen[entry_id] = True
                net_rows.append(slim(entry))
                url = str(entry.get("url", ""))
                if "/fo/" in url:
                    log["fo_entries"].append(slim(entry, 2000))
                    if state["fo_matched"] is None:
                        state["fo_matched"] = bool(entry.get("matched"))
                        state["fo_status"] = entry.get("status")
                        log["first_fo_at_s"] = round(time.monotonic() - t0, 2)
            now = time.monotonic() - t0
            if now >= next_sample and len(samples) < MAX_SAMPLES:
                next_sample = now + SAMPLE_EVERY
                try:
                    value = ctx.eval(LC_EXPR, to_py=True)
                    parsed = json.loads(value) if isinstance(value, str) else None
                    if parsed is not None:
                        samples.append({"t": round(now, 2),
                                        "lc": parsed[0], "hotp": parsed[1]})
                except Exception as exc:
                    msg = "%s: %s" % (type(exc).__name__, str(exc)[:120])
                    if len(log["eval_errors"]) < 10:
                        log["eval_errors"].append(msg)
                    if ctx.closed:
                        log["eval_closed"] = True
                        break
            time.sleep(0.05)
    except Exception as exc:
        log["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    finally:
        try:
            raw = ctx.net_log()
            if isinstance(raw, list):
                for entry in raw:
                    if isinstance(entry, dict) and entry.get("id") not in net_seen:
                        net_seen[entry.get("id")] = True
                        net_rows.append(slim(entry))
        except Exception:
            pass
        op_trace = {}
        if OP_IDS:
            for lid in [part.strip() for part in OP_IDS.split(",") if part.strip()]:
                expr = "JSON.stringify(globalThis.__op%s||null)" % lid
                try:
                    value = ctx.eval(expr, to_py=True)
                    if isinstance(value, list):
                        seq = value
                    elif isinstance(value, str):
                        seq = json.loads(value)
                    else:
                        seq = None
                    if isinstance(seq, list):
                        (OUT / ("op-%s.json" % lid)).write_text(
                            json.dumps(seq), encoding="utf-8")
                        op_trace[lid] = {
                            "count": len(seq),
                            "distinct": len({json.dumps(x) for x in seq}),
                            "head": seq[:30], "tail": seq[-30:],
                        }
                    else:
                        op_trace[lid] = {"missing": True}
                except Exception as exc:
                    log.setdefault("op_errors", []).append(
                        "%s: %s" % (type(exc).__name__, str(exc)[:160]))
        log["op_trace"] = op_trace
        try:
            ctx.close()
        except Exception:
            pass

    log["elapsed_s"] = round(time.monotonic() - t0, 2)
    log["fo_matched"] = state["fo_matched"]
    log["fo_status"] = state["fo_status"]
    log["net"] = net_rows
    log["net_count"] = len(net_rows)
    log["samples_count"] = len(samples)
    log["atob_small"], log["atob_big"] = len(small_atob), len(big_atob)
    log["atob_big_list"] = big_atob
    # 热循环摘要：最后采样里偏移最大的几个 id + 全程最大增量
    if samples:
        last = samples[-1]["lc"] or []
        log["lc_last"] = last
        first = samples[0]["lc"] or []
        log["lc_delta_top"] = sorted(
            ({"id": i, "delta": int(b) - int(a)}
             for i, (a, b) in enumerate(zip(first, last)) if isinstance(a, int) and isinstance(b, int)),
            key=lambda row: row["delta"], reverse=True)[:12]
        hots = [s["hotp"] for s in samples if s.get("hotp")]
        log["hotp_samples"] = hots[-12:]
        log["hotp_distinct"] = len({json.dumps(h) for h in hots})

    (OUT / "stage2.json").write_text(
        json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "samples.jsonl").write_text(
        "\n".join(json.dumps(s, ensure_ascii=False) for s in samples), encoding="utf-8")
    (OUT / "atob.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in small_atob), encoding="utf-8")
    print(json.dumps({
        "ok": "error" not in log,
        "error": log.get("error"),
        "load_page_s": log.get("load_page_s"),
        "elapsed_s": log["elapsed_s"],
        "fo_matched": log["fo_matched"], "fo_status": log["fo_status"],
        "net": log["net_count"],
        "samples": log["samples_count"],
        "atob_small": log["atob_small"], "atob_big": len(big_atob),
        "lc_delta_top": log.get("lc_delta_top", [])[:6],
        "hotp_last": (log.get("hotp_samples") or [None])[-1],
        "op_trace": {k: {kk: vv for kk, vv in v.items() if kk != "head" and kk != "tail"}
                     for k, v in log.get("op_trace", {}).items()},
        "eval_errors": len(log["eval_errors"]),
        "out": str(OUT / "stage2.json"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
