#!/usr/bin/env python3
"""replay_node.py — 回放对拍第 2 步：Node 离线吃 ruyijs 录制的材料。

输入：replay-materials/{challenge-page.html, chl-page-orchestrate.js}
     （record_ruyijs.py 产出；两侧同一 orchestrate 输入 → 同程序路径）
驱动：CF_CAPTURE_ONLY=1 + CF_ATOB_TRACE=1 跑 run.js；
     对 runtime_request 回放 envelope——orchestrate/静态 GET 用录制文件自身
     （challenge-platform GET 回 200 空体即可，非解码链路），FO POST 回
     200 + 合成 base64（结构近似：同尺寸量级，让链路推进到下一阶段即可——
     对拍窗口是 FO-3 之前的 orchestrate 静态阶段）。
产物：bridge-replay-atob.jsonl
对拍：与 ruyijs-replay-atob.jsonl 的前缀段做字节级同位 diff。
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import time
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT_DIR = PROJECT / "diagnostics" / "atob-diff-20261107"
MAT_DIR = OUT_DIR / "replay-materials"

NODE = r"D:\reverse_ENV\tools\node\node.exe"
RUNTIME_DIR = PROJECT / "runtime"

UA_FF = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"


def synth_body(n: int) -> str:
    """合成 n 字节量级的 base64 文本（结构近似，不重复原值）。"""
    block = base64.b64encode(b"REPLAY" * (n // 6 + 1)).decode("ascii")
    return block[:n]


TURNSTILE_JS_B64 = None  # 运行时若录制有 api.js 则回放；无则合成


async def main() -> int:
    # pair 模式（2026-11-07 消变体）：吃配对抓取的 403 页 + orchestrate JS，
    # ruyijs 侧 replay_ruyijs.py 用 put_resource 吃同一字节，两侧同材料。
    pair_page = MAT_DIR / "pair-challenge-page.html"
    pair_orch = MAT_DIR / "pair-orchestrate.js"
    if pair_page.exists() and pair_orch.exists():
        page_path = pair_page
    else:
        page_path = MAT_DIR / "challenge-init.html"
        if not page_path.exists():
            page_path = MAT_DIR / "challenge-page.html"
    orch_path = pair_orch if pair_orch.exists() else MAT_DIR / "chl-page-orchestrate.js"
    if not page_path.exists() or not orch_path.exists():
        print(json.dumps({"ok": False, "reason": "replay materials missing"}))
        return 1
    trace_file = OUT_DIR / "bridge-pair-atob.jsonl"
    if trace_file.exists():
        trace_file.unlink()
    env = dict(os.environ)
    env["CF_CAPTURE_ONLY"] = "1"
    env["CF_ATOB_TRACE"] = "1"
    env["CF_ATOB_TRACE_FILE"] = str(trace_file)
    env["CF_DIAGNOSTICS"] = "1"
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        env.pop(key, None)

    orch_body = orch_path.read_text(encoding="utf-8")
    orch_b64 = base64.b64encode(orch_body.encode("utf-8")).decode("ascii")

    proc = await asyncio.create_subprocess_exec(
        NODE, str(RUNTIME_DIR / "run.js"), str(page_path), str(orch_path), "",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, env=env)

    stderr_tail = []

    async def pump_stderr() -> None:
        while True:
            line = await proc.stderr.readline()
            if not line:
                return
            stderr_tail.append(line.decode("utf-8", errors="replace")[:400])

    stderr_task = asyncio.create_task(pump_stderr())
    result = None
    t0 = time.time()
    served = 0
    try:
        while time.time() - t0 < 150:
            try:
                raw = await asyncio.wait_for(proc.stdout.readline(), timeout=60)
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
            if msg.get("type") != "runtime_request":
                if msg.get("type") == "result" or ("ok" in msg and "elapsedMs" in msg):
                    result = msg
                    break
                continue
            url = str(msg.get("url", ""))
            method = str(msg.get("method", "GET")).upper()
            # 回放 envelope：orchestrate 自身回录制字节；其余一律 200 空体。
            # 空体对齐 ruyijs 离线侧（load_page + 无预置资源 → 默认 200 空响应），
            # 消除 FO/静态响应内容这个旁变量（2026-11-07 第三轮：synth REPLAY
            # 2369B 导致 Node 在 FO-1 后走不同 VM 分支，与 ruyijs 不可比）。
            if "/orchestrate/" in url and method == "GET":
                body_bytes, b64 = len(orch_body), orch_b64
                status = 200
                ctype = "application/javascript"
            else:
                status = 200
                body_bytes = 0
                b64 = ""
                ctype = "text/plain"
            envelope = {"type": "response", "request_id": msg["request_id"],
                        "status": status,
                        "headers": {"content-type": ctype,
                                    "content-length": str(body_bytes)},
                        "set_cookies": [],
                        "body_b64": b64}
            proc.stdin.write((json.dumps(envelope) + "\n").encode("utf-8"))
            await proc.stdin.drain()
            served += 1
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
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
