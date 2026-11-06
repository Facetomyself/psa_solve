#!/usr/bin/env python3
"""bridge_diag_driver.py — capture-only bridge 直连诊断 driver。

与 demo6 solve_bridge_async 同协议（429 触发 → Node runtime → envelope 回灌），
差异：
  - CF_CAPTURE_ONLY=1 + CF_DIAGNOSTICS=1
  - runtime 的 stdout/stderr 全量带前缀落盘（bridge 只认 JSON 行，这里全收）
  - envelope 与 runtime_request 时序全记录

产物：diagnostics/bridge-diag-<ts>/bridge-diag.jsonl（脱敏：URL query 剥离）
stdout：单行 JSON 摘要（无 URL/token 值）。
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

from curl_cffi.requests import AsyncSession

ROOT = Path(r"D:\reverse_ENV\workspace\psa_solve")
RUNTIME_DIR = ROOT / "runtime"
NODE = r"D:\reverse_ENV\tools\node\node.exe"
TARGET = "https://www.psacard.com/cert/143963534/psa"
UA_FF = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0"
IMPERSONATE = "firefox"

SN_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")


def redact_url(u: str) -> str:
    parts = urlsplit(u)
    return parts.netloc + parts.path


def classify(status: int, headers: dict, sc_raw: str) -> str:
    if "cf_clearance=" in sc_raw:
        return "FO_ACCEPTED"
    if "text/plain" in headers.get("content-type", ""):
        return "FO_CONTINUE"
    return "FO_REJECT_OR_DEGRADE"


async def main() -> int:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)

    epoch = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = ROOT / "diagnostics" / f"bridge-diag-{epoch}"
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "bridge-diag.jsonl"

    def emit(row: dict) -> None:
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    session = AsyncSession(impersonate=IMPERSONATE)
    r = await session.get(TARGET, headers={"User-Agent": UA_FF}, timeout=15)
    emit({"event": "trigger", "status": r.status_code, "len": len(r.content)})
    if r.status_code not in (403, 429) or len(r.content) < 1000:
        print(json.dumps({"ok": False, "reason": f"no challenge: {r.status_code} len={len(r.content)}"}))
        return 1
    (outdir / "challenge-page.html").write_bytes(r.content)

    html = r.content.decode("utf-8", errors="replace")
    m = re.search(r"\.src = '([^']*orchestrate[^']*)'", html) or re.search(r'src = "([^"]*orchestrate[^"]*)"', html)
    if not m:
        print(json.dumps({"ok": False, "reason": "orchestrate URL 解析失败"}))
        return 1
    orch_url = "https://www.psacard.com" + m.group(1)
    r2 = await session.get(orch_url, headers={"User-Agent": UA_FF, "Referer": TARGET}, timeout=30)
    emit({"event": "orchestrate", "status": r2.status_code, "len": len(r2.content)})
    if r2.status_code != 200:
        print(json.dumps({"ok": False, "reason": f"orchestrate HTTP {r2.status_code}"}))
        return 1
    orch_path = outdir / "chl-page-orchestrate.js"
    orch_path.write_bytes(r2.content)

    bm = session.cookies.get("__cf_bm") or ""
    if not bm:
        print(json.dumps({"ok": False, "reason": "__cf_bm 不在 jar 中"}))
        return 1

    env = dict(os.environ)
    env["CF_CAPTURE_ONLY"] = "1"
    env["CF_DIAGNOSTICS"] = "1"
    env.pop("HTTP_PROXY", None); env.pop("HTTPS_PROXY", None)
    env.pop("http_proxy", None); env.pop("https_proxy", None)

    proc = await asyncio.create_subprocess_exec(
        NODE, str(RUNTIME_DIR / "run.js"), str(outdir / "challenge-page.html"), str(orch_path), bm,
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, env=env)

    async def pump_stderr() -> None:
        while True:
            line = await proc.stderr.readline()
            if not line:
                return
            emit({"event": "runtime-stderr", "text": line.decode("utf-8", errors="replace")[:800]})

    stderr_task = asyncio.create_task(pump_stderr())

    result = None
    t0 = time.time()
    fo_rounds = []
    try:
        while time.time() - t0 < 150:
            try:
                raw = await asyncio.wait_for(proc.stdout.readline(), timeout=115)
            except asyncio.TimeoutError:
                emit({"event": "readline-timeout"})
                break
            if not raw:
                break
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("{"):
                emit({"event": "runtime-stdout", "text": line[:800]})
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                emit({"event": "runtime-stdout-badjson", "text": line[:400]})
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
                    emit({"event": "send-error", "error": str(e)[:200]})
                    break
                sc_raw = rr.headers.get("set-cookie", "") or ""
                klass = classify(rr.status_code, {k.lower(): v for k, v in rr.headers.items()}, sc_raw)
                sc_list = [c.strip() for c in sc_raw.split(",") if "=" in c.strip()]
                fo_rounds.append({"id": msg["request_id"], "method": method,
                                  "path": redact_url(url), "status": rr.status_code,
                                  "class": klass, "resp_len": len(rr.content)})
                emit({"event": "forwarded", "id": msg["request_id"], "method": method,
                      "path": redact_url(url), "status": rr.status_code,
                      "class": klass, "resp_len": len(rr.content)})
                # 无损搬运：base64 编码字节流，runtime 侧 decode 出 latin1 字符串。
                # 证据（2026-11-06）：utf-8/replace 解码对非 UTF-8 响应引入 U+FFFD，
                # 毁掉 VM opcode 字节流（ruyijs 走真实字节流无此问题）。
                import base64
                # 同步落盘请求体（Node FO 载荷 diff 用，私有目录）
                if body:
                    bdir = outdir / "fo-bodies"
                    bdir.mkdir(exist_ok=True)
                    (bdir / f"{msg['request_id']}-{len(str(body))}B.txt").write_text(
                        str(body), encoding="utf-8")
                envelope = {"type": "response", "request_id": msg["request_id"],
                            "status": rr.status_code,
                            "headers": {k.lower(): v for k, v in rr.headers.items()},
                            "set_cookies": sc_list,
                            "body_b64": base64.b64encode(rr.content).decode("ascii")}
                proc.stdin.write((json.dumps(envelope, ensure_ascii=False) + "\n").encode("utf-8"))
                await proc.stdin.drain()
            elif msg.get("type") == "result" or ("ok" in msg and "elapsedMs" in msg):
                result = msg
                emit({"event": "result", "result": msg})
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

    summary = {
        "ok": bool(result and result.get("hasClearance")),
        "hasResult": result is not None,
        "hasClearance": bool(result and result.get("hasClearance")),
        "requestCount": (result or {}).get("requestCount"),
        "errorCount": (result or {}).get("errorCount"),
        "missingGlobals": (result or {}).get("missingGlobals"),
        "missingHostProps": (result or {}).get("missingHostProps"),
        "foRounds": fo_rounds,
        "elapsedS": round(time.time() - t0, 1),
        "artifacts": str(outdir),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    try:
        await session.close()
    except Exception:
        pass
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
