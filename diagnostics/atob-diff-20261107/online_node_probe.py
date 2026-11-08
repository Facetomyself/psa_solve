#!/usr/bin/env python3
"""online_node_probe.py — 修复后 Node runtime 端到端在线探测。

流程：curl_cffi(firefox) 抓 403 页 + 配套 orchestrate（同会话、同 ray），
Node run.js 非 capture 模式吃这对材料并真实发 FO POST，观察：
  - FO 请求是否被 CF 接受（200 且响应进入下一阶段解码）
  - 解码是否崩溃（stderr 的 vm-default/TypeError 位点）
  - 是否产出 clearance（页面 200 正文 / cookie）
对照基线（11-07 早）：FO r1 被接受但响应驱动下一阶段 VM 程序解码崩溃
（opcode 206 / F4=131 位点轮换）。performance 修复后行为变化为 FO r1
onreadystatechange 内同步挂死（CF_WATCHDOG 定位）。

挂死诊断：node 以 --inspect 启动，挂死窗口里 Debugger.pause 抓调用栈
（V8 中断可打断同步循环），帧落 inspector-paused.json。
产物：online-probe/（gitignore 域），stdout 单行 JSON 摘要。
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
# 产物目录可被 PROBE_OUT 覆盖：并发探测必须用独立目录，否则 node-stdout.txt
# 的文件句柄互相占用/覆盖（2026-11-07 教训：两次探测互毁结论）。
OUT = Path(os.environ.get("PROBE_OUT")
           or str(PROJECT / "diagnostics" / "atob-diff-20261107" / "online-probe"))
OUT.mkdir(parents=True, exist_ok=True)

NODE = r"D:\reverse_ENV\tools\node\node.exe"
PAGE = "https://www.psacard.com/cert/143963534/psa"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"

# inspector 端口可覆盖：同机并发探测各用各的端口。
INSPECT_PORT = int(os.environ.get("PROBE_INSPECT_PORT", "9333"))

LC_EXPR = "JSON.stringify((globalThis.__lc||[]).map(x=>x||0))"


def compute_hot(lc_json, orch_path):
    """从 __lc 计数找出最热循环 id，解析其函数名/指令表/指针变量。

    loop_scan 与 run.js CF_LOOPGUARD 对 `for(...;true;/!0;)` 用同一扫描算法，
    id 顺序一致；材料（未插桩）与执行版（插桩）的变量名相同。返回 dict 或 None。
    """
    try:
        lc = json.loads(lc_json or "[]")
    except Exception:  # noqa: BLE001
        return None
    best_id, best = -1, -1
    for idx, val in enumerate(lc or []):
        if isinstance(val, (int, float)) and val > best:
            best, best_id = val, idx
    if best_id < 0 or best < 100000:
        return None
    try:
        import loop_scan
        src = open(orch_path, "rb").read().decode("latin1")
        metas, _ = loop_scan.scan(src)
        if best_id >= len(metas):
            return None
        mid, at, init, cond, inc = metas[best_id]
        head = src[max(0, at - 5000):at]
        fns = re.findall(r"function\s+([A-Za-z_$][\w$]*)\s*\(", head)
        fn = fns[-1] if fns else ""
        body = src[at:at + 3000]
        # 指令指针不一定是裸标识符（本族变体常见 `switch(TABLE[PTR[1]++])`，
        # 指针是成员表达式 nJ[1]）。table 用非贪婪匹配到最后一个 `[...++]`。
        m = re.search(
            r"switch\s*\(\s*(.+?)\[\s*([A-Za-z_$][\w$]*(?:\[[^\[\]]*\])?)\s*\+\+\s*\]\s*\)",
            body)
        table = m.group(1).strip() if m else ""
        ptr = m.group(2) if m else ""
        return {"id": best_id, "count": best, "fn": fn, "table": table,
                "ptr": ptr, "at": at}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)[:200], "id": best_id, "count": best}
PAUSE_AFTER_S = float(os.environ.get("PROBE_PAUSE_AFTER", "15"))
TOTAL_TIMEOUT_S = float(os.environ.get("PROBE_TOTAL", "60"))


def inspector_pause(port: int, out_path: Path, samples: int = 5,
                    orch_path=None) -> dict:
    """Attach via inspector, pause N times, dump call frames; save script sources."""
    try:
        targets = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json/list", timeout=5).read().decode())
        ws_url = targets[0]["webSocketDebuggerUrl"]
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "stage": "target", "error": str(exc)[:200]}

    import websocket
    ws = websocket.create_connection(ws_url, timeout=20)
    state = {"id": 0}

    def rpc(method, params=None, timeout=20):
        """Send request, drain events until matching response. Returns (result, events)."""
        state["id"] += 1
        rid = state["id"]
        ws.send(json.dumps({"id": rid, "method": method, "params": params or {}}))
        events = []
        deadline = time.time() + timeout
        while time.time() < deadline:
            ws.settimeout(max(0.5, deadline - time.time()))
            msg = json.loads(ws.recv())
            if msg.get("id") == rid:
                if "error" in msg:
                    return None, events
                return msg.get("result", {}), events
            if "method" in msg:
                events.append(msg)
        return None, events

    def pause_once(timeout=20):
        """Send Debugger.pause and wait for the paused event."""
        state["id"] += 1
        ws.send(json.dumps({"id": state["id"], "method": "Debugger.pause", "params": {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            ws.settimeout(max(0.5, deadline - time.time()))
            msg = json.loads(ws.recv())
            if msg.get("method") == "Debugger.paused":
                return msg["params"]
        return None

    def frames_of(paused, tag):
        out = []
        for fr in paused.get("callFrames", []):
            out.append({
                "sample": tag,
                "fn": fr.get("functionName") or "(anonymous)",
                "url": fr.get("url", ""),
                "line": fr.get("location", {}).get("lineNumber"),
                "col": fr.get("location", {}).get("columnNumber"),
                "scriptId": fr.get("location", {}).get("scriptId"),
            })
        return out

    try:
        rpc("Debugger.enable")
        data = {"ok": True, "samples": []}
        first_paused = None
        all_frames = []
        hot = None
        for i in range(samples):
            paused = pause_once()
            if not paused:
                data["error"] = f"no paused event at sample {i}"
                break
            if first_paused is None:
                first_paused = paused
            all_frames.extend(frames_of(paused, i))
            # 每帧局部作用域全量导出（不依赖变体名）：热循环此刻的指令指针
            # yA / 状态数组 yH / 程序表长度等都在 local scope 里。两次采样对比
            # 同一函数帧的变量变化即可判定“推进中”还是“原地死循环”。
            locals_dump = []
            for fr in paused.get("callFrames", [])[:8]:
                entry = {"fn": fr.get("functionName") or "(anonymous)", "scopes": []}
                for sc in (fr.get("scopeChain") or [])[:3]:
                    obj = (sc.get("object") or {})
                    oid = obj.get("objectId")
                    if not oid:
                        continue
                    try:
                        pres, _ = rpc("Runtime.getProperties",
                                      {"objectId": oid, "ownProperties": True})
                    except Exception:  # noqa: BLE001
                        continue
                    props = []
                    for pr in (pres or {}).get("result", [])[:120]:
                        val = pr.get("value") or {}
                        t = val.get("type")
                        if t in ("string", "number", "boolean"):
                            v = str(val.get("value"))[:100]
                        elif t in ("object", "function"):
                            v = (val.get("className") or t or "") + ":" + \
                                str(val.get("description", ""))[:60]
                        else:
                            v = val.get("description", "")
                        props.append({"name": pr.get("name"), "type": t, "value": v})
                    entry["scopes"].append({"type": sc.get("type"), "props": props})
                locals_dump.append(entry)
            # 在 run 帧上读循环计数器/程序计数器（CF_LOOPGUARD 注入的 __lg1 +
            # 该变体的 VM 程序数组 RN/pc RF；材料 pinned 时表达式有效）
            evals = {}
            for fr in paused.get("callFrames", [])[:10]:
                if fr.get("functionName") != "run":
                    continue
                for expr in ("__lg1",
                             "Date.now()",
                             LC_EXPR,
                             "JSON.stringify(globalThis.__hotp||null)",
                             "Object.keys(globalThis).filter(function(k){return k.indexOf('__op')===0;}).join(',')",
                             "JSON.stringify(Object.keys(globalThis).filter(function(k){return k.indexOf('_0x')===0;}).slice(0,3).map(function(k){return [k,globalThis[k]];}))",
                             "typeof RN==='object'&&RN?RN.length:-1",
                             "typeof RF==='number'?String(RF):null",
                             "typeof RN==='object'&&RN&&typeof RF==='number'?String(RN[RF]):null",
                             "this&&typeof this==='object'?Object.keys(this).join(','):null"):
                    try:
                        res, _ = rpc("Debugger.evaluateOnCallFrame", {
                            "callFrameId": fr["callFrameId"],
                            "expression": expr, "returnByValue": True,
                            "silent": True})
                        r = (res or {}).get("result", {})
                        evals[expr] = r.get("value", r.get("description"))
                    except Exception as exc:  # noqa: BLE001
                        evals[expr] = "ERR:" + str(exc)[:60]
                break
            # 第一次采样确定最热循环，后续采样在其帧上读指令指针/指令表长度：
            # 指针递增且表长有限 → 有限推进；指针不动/回绕 → 原地死循环。
            if i == 0 and orch_path is not None:
                hot = compute_hot(evals.get(LC_EXPR), orch_path)
                data["hot"] = hot
            hot_vals = {}
            if hot and hot.get("ptr"):
                exprs = [hot["ptr"]]
                if hot.get("table"):
                    exprs.append(hot["table"] + ".length")
                target = hot.get("fn") or ""
                frames_try = [fr for fr in paused.get("callFrames", [])[:10]
                              if fr.get("functionName") == target]
                frames_try += [fr for fr in paused.get("callFrames", [])[:6]
                               if fr.get("functionName") != target]
                for fr in frames_try:
                    got = {}
                    for expr in exprs:
                        try:
                            hres, _ = rpc("Debugger.evaluateOnCallFrame", {
                                "callFrameId": fr["callFrameId"],
                                "expression": expr, "returnByValue": True,
                                "silent": True})
                            if hres and hres.get("exceptionDetails"):
                                continue
                            hr = (hres or {}).get("result", {})
                            if hr.get("type") == "undefined" or hr.get("subtype") == "error":
                                continue
                            got[expr] = hr.get("value", hr.get("description"))
                        except Exception:  # noqa: BLE001
                            continue
                    if got:
                        hot_vals = {"fn": fr.get("functionName") or "(anonymous)",
                                    "vals": got}
                        break
            # 逐 opcode 序列：读取所有 __op<id>（run.js CF_OP_TRACE=* 限长记录）。
            # 不依赖热循环是否存在——变体轮换时失败点可能不在 for(true) 计数循环里
            # （2026-11-07 实测：某变体挂死在 Lpb 流处理，__lc 最大仅 62）。
            if i > 0 and "op_all" not in data:
                key_expr = next((k for k in evals if "indexOf('__op')" in k), None)
                key_str = str(evals.get(key_expr) or "") if key_expr else ""
                op_all = {}
                frames_run = [fr for fr in paused.get("callFrames", [])[:10]
                              if fr.get("functionName") == "run"]
                for key in [k.strip() for k in key_str.split(",") if k.strip()]:
                    if key == "__opTmp" or not key.startswith("__op") or not key[4:].isdigit():
                        continue
                    expr = "JSON.stringify(globalThis.%s||null)" % key
                    for fr in frames_run:
                        try:
                            ores, _ = rpc("Debugger.evaluateOnCallFrame", {
                                "callFrameId": fr["callFrameId"],
                                "expression": expr, "returnByValue": True,
                                "silent": True})
                            orr = (ores or {}).get("result", {})
                            if orr.get("type") == "string" and orr.get("value") is not None:
                                op_all[key] = orr["value"]
                            else:
                                op_all[key] = {"value": orr.get("value",
                                                               orr.get("description"))}
                        except Exception as exc:  # noqa: BLE001
                            op_all[key] = {"error": str(exc)[:100]}
                        break
                if op_all:
                    data["op_all"] = op_all
            data["samples"].append({"i": i, "evals": evals, "locals": locals_dump,
                                    "hot": hot_vals})
            if i < samples - 1:
                rpc("Debugger.resume")
                time.sleep(1.0)
        data["frames"] = all_frames
        data["reason"] = first_paused.get("reason") if first_paused else None

        # 各 distinct 脚本源码（动态 eval 的 VM 程序、orchestrate 都在内）
        script_dir = out_path.parent / "scripts"
        script_dir.mkdir(exist_ok=True)
        script_info = []
        seen = set()
        for f in all_frames:
            sid = f["scriptId"]
            if not sid or sid in seen:
                continue
            seen.add(sid)
            if len(seen) > 12:
                break
            res, _ = rpc("Debugger.getScriptSource", {"scriptId": sid})
            src = (res or {}).get("scriptSource", "")
            if src:
                p = script_dir / f"script-{sid}.js"
                p.write_text(src, encoding="utf-8", errors="replace")
                script_info.append({"scriptId": sid, "len": len(src),
                                    "path": str(p.relative_to(OUT))})
        data["scripts"] = script_info

        # 每帧局部作用域变量（找循环计数器/程序计数器）——仅首个 pause 的 orchestrate 帧
        top_scope = None
        try:
            frames0 = first_paused.get("callFrames", [])
            for fr in frames0[:6]:
                url = fr.get("url", "")
                if url and "orchestrate" not in url:
                    continue
                scopes = fr.get("scopeChain", [])
                if not scopes:
                    continue
                res, _ = rpc("Runtime.getProperties",
                             {"objectId": scopes[0]["object"]["objectId"],
                              "ownProperties": True})
                props = []
                for pr in (res or {}).get("result", [])[:120]:
                    val = pr.get("value") or {}
                    props.append({
                        "name": pr.get("name"),
                        "type": val.get("type"),
                        "value": str(val.get("value"))[:80]
                        if val.get("type") in ("string", "number", "boolean")
                        else None,
                    })
                top_scope = {"fn": fr.get("functionName"), "props": props}
                break
        except Exception as exc:  # noqa: BLE001
            top_scope = {"error": str(exc)[:200]}
        data["topScope"] = top_scope

        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                            encoding="utf-8")
        # 采样结束必须 resume：否则 V8 保持在暂停态，进程静默挂起（2026-11-07
        # 教训：900s“长跑不结束”实为暂停态假象）。resume 后再 disable 调试器。
        try:
            rpc("Debugger.resume")
            rpc("Debugger.disable")
        except Exception:  # noqa: BLE001
            pass
        tops = [f"{f['fn']}@{f['col']}" for f in all_frames if f["sample"] == 0][:6]
        return {"ok": True, "sampleCount": len({f['sample'] for f in all_frames}),
                "topSamples": tops, "scripts": script_info, "topScope": top_scope}
    finally:
        try:
            ws.close()
        except Exception:  # noqa: BLE001
            pass


def main() -> int:
    reuse = "--reuse" in sys.argv
    page_path = OUT / "403-page.html"
    orch_path = OUT / "orchestrate.js"
    cookies_path = OUT / "cookies.txt"  # gitignore 域：会话 cookie 原值

    page_status = -1
    page_bytes = 0
    orch_status = -1
    orch_bytes = 0
    if reuse and page_path.exists() and orch_path.exists() and cookies_path.exists():
        html = page_path.read_bytes()
        orch = orch_path.read_bytes()
        cookies = cookies_path.read_text(encoding="utf-8").strip()
        page_bytes = len(html)
        orch_bytes = len(orch)
    else:
        for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                    "ALL_PROXY", "all_proxy"):
            os.environ.pop(key, None)
        from curl_cffi.requests import Session

        with Session(impersonate="firefox") as s:
            r1 = s.get(PAGE, headers={"User-Agent": UA}, timeout=30)
            html = r1.content
            m = re.search(rb"a\.src = '([^']+)'", html)
            if not m:
                print(json.dumps({"ok": False, "reason": "no orchestrate src in 403 page",
                                  "status": r1.status_code}))
                return 1
            orch_url = "https://www.psacard.com" + m.group(1).decode()
            r2 = s.get(orch_url, headers={"User-Agent": UA, "Referer": PAGE}, timeout=30)
            cookies = "; ".join(f"{c.name}={c.value}" for c in s.cookies.jar)
            page_status = r1.status_code
            orch_status = r2.status_code
            page_bytes = len(html)
            orch_bytes = len(r2.content)

        page_path.write_bytes(html)
        orch_path.write_bytes(r2.content)
        cookies_path.write_text(cookies, encoding="utf-8")

    env = dict(os.environ)
    env.pop("CF_CAPTURE_ONLY", None)
    env.pop("CF_ATOB_TRACE", None)
    env["CF_DIAGNOSTICS"] = "1"
    # 干净计时模式：不开看门狗/循环计数（避免诊断插桩 deopt 热函数影响耗时）
    quiet = os.environ.get("PROBE_QUIET") == "1"
    # FO 轮间有 ~5s 定时器（PoW/Ot 回调）；默认 3s 静默早退会把轮间等待误判为完成
    env["CF_STABLE_MS"] = "12000"
    if not quiet:
        # 看门狗：定时器/XHR 回调 enter/exit 打点（fd2 同步写），定位同步挂死位点
        env["CF_WATCHDOG"] = "1"
        # VM 程序执行循环迭代上限：命中抛错（栈里能看挂死回调链）
        env["CF_LOOPGUARD"] = "5000000"
    # FO 请求/响应原始字节落盘（离线回放与真值对比；gitignore 域）
    env["CF_DUMP_FO_DIR"] = str(OUT / "fo-dump")

    stdout_path = OUT / "node-stdout.txt"
    stderr_path = OUT / "node-stderr.txt"
    for p in (OUT / "node-stdout-timeout.txt", OUT / "node-stderr-timeout.txt",
              OUT / "inspector-paused.json"):
        if p.exists():
            p.unlink()

    t0 = time.time()
    inspect_args = [] if quiet else [f"--inspect=127.0.0.1:{INSPECT_PORT}"]
    with open(stdout_path, "wb") as so, open(stderr_path, "wb") as se:
        proc = subprocess.Popen(
            [NODE] + inspect_args + [str(PROJECT / "runtime" / "run.js"),
             str(page_path), str(orch_path), cookies],
            stdout=so, stderr=se, env=env)
        pause_info = None
        try:
            pause_at = t0 + PAUSE_AFTER_S
            while time.time() < t0 + TOTAL_TIMEOUT_S:
                if proc.poll() is not None:
                    break
                if pause_info is None and time.time() >= pause_at and not quiet:
                    pause_info = inspector_pause(
                        INSPECT_PORT, OUT / "inspector-paused.json",
                        samples=int(os.environ.get("PROBE_SAMPLES", "5")),
                        orch_path=orch_path)
                time.sleep(0.2)
        finally:
            killed = False
            if proc.poll() is None:
                proc.kill()
                killed = True
            proc.wait(timeout=10)

    elapsed = round(time.time() - t0, 1)
    stdout = stdout_path.read_bytes().decode("utf-8", errors="replace")
    stderr = stderr_path.read_bytes().decode("utf-8", errors="replace")
    # 超时路径也保留一份带后缀副本，兼容旧排查习惯
    if killed:
        (OUT / "node-stdout-timeout.txt").write_bytes(stdout.encode("utf-8"))
        (OUT / "node-stderr-timeout.txt").write_bytes(stderr.encode("utf-8"))

    result = None
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if "ok" in obj and ("submits" in obj or "elapsedMs" in obj):
                result = obj

    diag = {
        "ok": True,
        "elapsedS": elapsed,
        "killed": killed,
        "exitCode": proc.returncode,
        "pageStatus": page_status,
        "pageBytes": page_bytes,
        "orchStatus": orch_status,
        "orchBytes": orch_bytes,
        "pause": pause_info,
        "stderrHead": stderr.splitlines()[-6:],
    }
    if result is None:
        diag["ok"] = False
        diag["reason"] = "no result json"
        print(json.dumps(diag, ensure_ascii=False))
        return 1

    subs = result.get("submits") or []
    resp = result.get("responses") or []
    errs = result.get("errors") or []
    vm_default = [ln for ln in stderr.splitlines() if "vm-default" in ln]
    resp_detail = []
    for x in resp:
        u = str(x.get("url", ""))
        kind = ("fo" if "/fo/" in u else "orchestrate" if "orchestrate" in u
                else "cert" if "/cert/" in u else "other")
        resp_detail.append({
            "kind": kind, "status": x.get("status"),
            "bodyLen": x.get("bodyLength"),
            "head": str(x.get("bodyHead", ""))[:60],
            "error": x.get("error"),
        })
    diag.update({
        "submits": len(subs),
        "submitPaths": [str(x.get("url", ""))[:80] for x in subs[:4]],
        "submitBodies": [x.get("bodyLen") for x in subs[:4]],
        "respCount": len(resp),
        "respDetail": resp_detail,
        "clearance": bool(result.get("clearance")),
        "cfClearance": bool((result.get("pageState") or {}).get("cfClearance")),
        "errors": [str(e)[:120] for e in errs[:5]],
        "vmDefaultLines": len(vm_default),
        "vmDefaultSample": vm_default[:2],
    })
    print(json.dumps(diag, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
