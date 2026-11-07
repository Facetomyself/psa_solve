#!/usr/bin/env python3
"""diff_driver.py — ruyijs vs Node atob I/O 对拍 driver（2026-11-07）。

双跑同一目标（独立会话，FO 变体各自 fresh），各产 atob I/O 序列：
  A) ruyijs 侧：Context(debug) + native("atob") 包装 + expose Python sink
     （capture_atob_values.py v5 已验证：certOk 无扰动，1152 对）
  B) Node 侧：bridge_diag_driver 同协议（CF_CAPTURE_ONLY=1）+
     CF_ATOB_TRACE=1（lib/atob-trace.js 落盘 JSONL）

atob 是确定性 base64 解码——同输入必同输出，所以对拍信号是三个：
  1. 调用序列形状：调用数、输入尺寸序列的编辑距离/相关
  2. 同位输入分歧：序列第 n 对的输入 sha 不同 → 上游状态分歧
  3. 引擎语义分歧：ruyijs 抛(!name)而 Node 解码成功、或反向
变体同一性自证：两侧"大输入对"（FO-3 响应程序密文）尺寸独立比对——
同一变体则大输入尺寸相近（服务器同窗口下发的程序结构）。

产物：diagnostics/atob-diff-20261107/{ruyijs,bridge}-atob.jsonl + report.json
脱敏：报告只含尺寸/哈希/形状；原值落 gitignore 域 jsonl。
stdout：单行 JSON 摘要。
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NODE = r"D:\reverse_ENV\tools\node\node.exe"
RUNTIME_DIR = PROJECT / "runtime"
RUYIJS_PY = r"D:\reverse_ENV\temp\ruyijs-test-env\Scripts\python.exe"
TARGET = "https://www.psacard.com/cert/143963534/psa"
UA_FF = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"

FINGERPRINT = {
    "navigator": {
        "userAgent": UA_FF,
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


def sha16(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def shape(seq: list) -> dict:
    """序列形状：尺寸数组 + 每对输出哈希（不回显原值）。"""
    sizes = []
    ohash = []
    marks = []
    for item in seq:
        inp, _, out = item.partition("\u0001")
        sizes.append([len(inp), len(out)])
        ohash.append(sha16(out.encode("utf-8", "surrogatepass")))
        marks.append("!" if out.startswith("!") else "")
    return {"n": len(seq), "sizes": sizes, "ohash": ohash, "marks": marks}


# ---------------------------------------------------------------- A: ruyijs

def run_ruyijs() -> dict:
    os.environ["PYTHONIOENCODING"] = "utf-8"
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    sys.path.insert(0, r"D:\reverse_ENV\temp\ruyijs-test-env\Lib\site-packages")
    import ruyijs

    pairs = []
    cert_ok = False

    def sink(inp, outp):
        if len(pairs) < 20000:
            pairs.append(str(inp) + "\u0001" + str(outp))
        return True

    ctx = ruyijs.Context(timeout=400.0, mode="debug")
    try:
        ctx.configure_fingerprint(FINGERPRINT)
        ctx.configure_clock("system")
        ctx.expose(sink, "__psaSink")
        ctx.native("atob", ATOBSRC)
        ctx.navigate(TARGET)
        try:
            ctx.advance(10000, max_tasks=100000)
        except Exception:
            pass
        deadline = time.monotonic() + 150.0
        last_progress = time.monotonic()
        while time.monotonic() < deadline:
            try:
                ctx.native("atob", ATOBSRC)
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
    finally:
        try:
            ctx.close()
        except Exception:
            pass

    (OUT_DIR / "ruyijs-atob.jsonl").write_text(
        "\n".join(json.dumps({"n": i, "i": p.split("\u0001")[0],
                              "o": p.split("\u0001", 1)[1] if "\u0001" in p else "?"})
                  for i, p in enumerate(pairs)), encoding="utf-8")
    return {"certOk": cert_ok, "pairs": pairs}


# ---------------------------------------------------------------- B: Node bridge

async def run_node() -> dict:
    from curl_cffi.requests import AsyncSession

    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)

    trace_file = OUT_DIR / "bridge-atob.jsonl"
    if trace_file.exists():
        trace_file.unlink()
    env = dict(os.environ)
    env["CF_CAPTURE_ONLY"] = "1"
    env["CF_ATOB_TRACE"] = "1"
    env["CF_ATOB_TRACE_FILE"] = str(trace_file)
    env.pop("HTTP_PROXY", None); env.pop("HTTPS_PROXY", None)
    env.pop("http_proxy", None); env.pop("https_proxy", None)

    session = AsyncSession(impersonate="firefox")
    r = await session.get(TARGET, headers={"User-Agent": UA_FF}, timeout=15)
    if r.status_code not in (403, 429) or len(r.content) < 1000:
        return {"error": f"no challenge: {r.status_code}"}
    page_path = OUT_DIR / "challenge-page.html"
    page_path.write_bytes(r.content)

    html = r.content.decode("utf-8", errors="replace")
    import re
    m = re.search(r"\.src = '([^']*orchestrate[^']*)'", html) or \
        re.search(r'src = "([^"]*orchestrate[^"]*)"', html)
    if not m:
        return {"error": "orchestrate URL 解析失败"}
    orch_url = "https://www.psacard.com" + m.group(1)
    r2 = await session.get(orch_url, headers={"User-Agent": UA_FF, "Referer": TARGET}, timeout=30)
    if r2.status_code != 200:
        return {"error": f"orchestrate HTTP {r2.status_code}"}
    orch_path = OUT_DIR / "chl-page-orchestrate.js"
    orch_path.write_bytes(r2.content)
    bm = session.cookies.get("__cf_bm") or ""
    if not bm:
        return {"error": "__cf_bm 不在 jar 中"}

    proc = await asyncio.create_subprocess_exec(
        NODE, str(RUNTIME_DIR / "run.js"), str(page_path), str(orch_path), bm,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, env=env)

    async def pump_stderr() -> None:
        while True:
            line = await proc.stderr.readline()
            if not line:
                return

    stderr_task = asyncio.create_task(pump_stderr())
    result = None
    t0 = time.time()
    fo_rounds = []
    try:
        while time.time() - t0 < 150:
            try:
                raw = await asyncio.wait_for(proc.stdout.readline(), timeout=115)
            except asyncio.TimeoutError:
                break
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("{"):
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("type") == "runtime_request":
                url = msg["url"]
                if url.startswith("/"):
                    url = "https://www.psacard.com" + url
                method = msg.get("method", "GET").upper()
                headers = {k: v for k, v in msg.get("headers", {}).items()
                           if k.lower() not in ("cookie", "content-length", "host")}
                body = msg.get("body", "")
                try:
                    if method == "POST":
                        rr = await session.post(url, data=body, headers=headers, timeout=60)
                    else:
                        rr = await session.get(url, headers=headers, timeout=60)
                except Exception as e:
                    return {"error": f"send: {str(e)[:120]}"}
                parts = urlsplit(url)
                fo_rounds.append({"method": method, "path": parts.netloc + parts.path,
                                  "status": rr.status_code, "resp_len": len(rr.content)})
                envelope = {"type": "response", "request_id": msg["request_id"],
                            "status": rr.status_code,
                            "headers": {k.lower(): v for k, v in rr.headers.items()},
                            "set_cookies": [c.strip() for c in
                                            (rr.headers.get("set-cookie", "") or "").split(",")
                                            if "=" in c.strip()],
                            "body_b64": base64.b64encode(rr.content).decode("ascii")}
                proc.stdin.write((json.dumps(envelope, ensure_ascii=False) + "\n").encode("utf-8"))
                await proc.stdin.drain()
            elif msg.get("type") == "result" or ("ok" in msg and "elapsedMs" in msg):
                result = msg
                break
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=10)
        except Exception:
            proc.kill()
        stderr_task.cancel()
    try:
        await session.close()
    except Exception:
        pass
    return {"result": result, "foRounds": fo_rounds}


# ---------------------------------------------------------------- diff

def load_trace(path: Path) -> list:
    pairs = []
    if not path.exists():
        return pairs
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and not row.get("__summary") and "i" in row:
            pairs.append(str(row["i"]) + "\u0001" + str(row.get("o", "?")))
    return pairs


def compare(a: list, b: list) -> dict:
    sa, sb = shape(a), shape(b)
    report = {
        "ruyijsCalls": sa["n"], "nodeCalls": sb["n"],
        "ruyijsMarks": sum(1 for m in sa["marks"] if m),
        "nodeMarks": sum(1 for m in sb["marks"] if m),
    }
    # 大输入对（程序密文级 >100KB）：尺寸独立比对——变体同一性自证
    def big(seq):
        return [(len(p.split("\u0001")[0]), len(p.split("\u0001", 1)[1]))
                for p in seq if len(p.split("\u0001")[0]) > 100000]
    report["ruyijsBig"] = big(a)
    report["nodeBig"] = big(b)
    # 尺寸序列相关性（前 min(n) 对的输入尺寸逐位 diff 计数）
    k = min(sa["n"], sb["n"])
    if k:
        same_in = sum(1 for i in range(k)
                      if sa["sizes"][i][0] == sb["sizes"][i][0])
        same_out = sum(1 for i in range(k)
                       if sa["ohash"][i] == sb["ohash"][i])
        report["prefixPairs"] = k
        report["prefixSameInSize"] = same_in
        report["prefixSameOutHash"] = same_out
        report["firstInSizeMismatch"] = next(
            (i for i in range(k) if sa["sizes"][i][0] != sb["sizes"][i][0]), None)
        report["firstOutHashMismatch"] = next(
            (i for i in range(k) if sa["ohash"][i] != sb["ohash"][i]), None)
    # 引擎语义分歧样本：一侧 ! 一侧非 !
    semantic = []
    for i in range(k):
        ma, mb = sa["marks"][i], sb["marks"][i]
        if ma != mb:
            semantic.append({"n": i, "ruyijs": ma or "ok", "node": mb or "ok",
                             "inSize": [sa["sizes"][i][0], sb["sizes"][i][0]]})
            if len(semantic) >= 10:
                break
    report["semanticDivergence"] = semantic
    return report


async def main() -> int:
    epoch = datetime.now().strftime("%H%M%S")
    t0 = time.time()
    ruyijs_res = await asyncio.get_event_loop().run_in_executor(None, run_ruyijs)
    node_res = await run_node()
    a = ruyijs_res["pairs"]
    b = load_trace(OUT_DIR / "bridge-atob.jsonl")
    report = {
        "ts": epoch, "elapsedS": round(time.time() - t0, 1),
        "ruyijs": {"certOk": ruyijs_res.get("certOk"),
                   "foRounds": ruyijs_res.get("foRounds"),
                   "error": ruyijs_res.get("error")},
        "node": {"foRounds": node_res.get("foRounds"),
                 "hasClearance": bool((node_res.get("result") or {}).get("hasClearance")),
                 "error": node_res.get("error")},
        "diff": compare(a, b),
    }
    (OUT_DIR / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({
        "ruyijsCalls": report["diff"]["ruyijsCalls"],
        "nodeCalls": report["diff"]["nodeCalls"],
        "ruyijsBig": report["diff"]["ruyijsBig"],
        "nodeBig": report["diff"]["nodeBig"],
        "prefixPairs": report["diff"].get("prefixPairs"),
        "prefixSameInSize": report["diff"].get("prefixSameInSize"),
        "prefixSameOutHash": report["diff"].get("prefixSameOutHash"),
        "firstInSizeMismatch": report["diff"].get("firstInSizeMismatch"),
        "semanticDivergence": len(report["diff"].get("semanticDivergence", [])),
        "elapsedS": report["elapsedS"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
