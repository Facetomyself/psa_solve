#!/usr/bin/env python3
"""solve_ruyijs.py — ruyijs inner 0.2.2 自含 PSA Cloudflare 挑战求解器。

流程（对照 diagnostics/ruyijs-fresh-navigate-20261103/run2_022.py 已验证链）：
  1. ruyijs Context（UA 与生产会话对齐）navigate cert URL -> 403 挑战页
  2. 泵到挑战自转完成（FO 轮 + clearance + document 切换）
  3. readback：GET cert -> 200 且正文含 SN
  4. export_cookies -> cf_clearance/__cf_bm 交给生产 curl_cffi 会话
  5. 同 UA curl_cffi 验证 clearance（不落日志、不打印值）

demo6 集成：solve_challenge(ua) -> {"ok", "cookies", "wallS", "foRounds"}。
cookie 值只经内存/返回值传递；日志与 stdout 只出现计数与状态。
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

TOOLS = Path(r"D:\reverse_ENV\tools\web-reverse")
PAGE_URL = "https://www.psacard.com/cert/{sn}/psa"
CERT_SN = "87356241"  # 求解触发用 SN（采集范围内任一）

sys.path.insert(0, str(TOOLS))

FINGERPRINT_TMPL = {
    "navigator": {
        "userAgent": "{ua}",
        "platform": "Win32",
        "language": "en-US",
        "languages": ["en-US", "en"],
    },
    "screen": {
        "width": 1920,
        "height": 1080,
        "availWidth": 1920,
        "availHeight": 1040,
        "colorDepth": 24,
    },
    "viewport": {"width": 1920, "height": 939, "devicePixelRatio": 1},
}

CONTEXT_TIMEOUT = 400.0
ADVANCE_MS = 10000
MAX_TASKS = 100000
PUMP_WALL_S = 180.0
ADVANCE_QUIET_S = 25.0


def _strip_proxy_env() -> None:
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)


def _classify(events: list, sn: str) -> dict:
    fo, cert_get, cert_post = [], [], []
    for item in events:
        if not isinstance(item, dict):
            continue
        prefix = item.get("pathPrefix")
        row = {"status": item.get("status"), "body": item.get("requestBodyBytes")}
        if item.get("method") == "POST" and isinstance(prefix, str) and prefix.startswith("/cdn-cgi/"):
            fo.append(row)
        elif isinstance(prefix, str) and prefix.startswith("/cert/"):
            (cert_post if item.get("method") == "POST" else cert_get).append(row)
    return {
        "foPosts": fo,
        "certGets": cert_get,
        "certPosts": cert_post,
        "certOk": any(isinstance(r["status"], int) and 200 <= r["status"] < 300 for r in cert_get),
    }


# 计数器改写模式（OV2 已验证：服务端不校验 4 计时值，模板化 MZ 全链收敛
# clearance——见 diagnostics/atob-diff-20261107/static-payload-verify/
# online-verify/ov2/notes.md）。默认模板值 = OV2 s8 验证值；可用
# --counters-template <json> 覆盖（{"vA":..,"vB":..,"vC":..,"vD":..}）。
COUNTERS_REWRITE_ENV = "PSA_COUNTERS_REWRITE"
COUNTERS_TEMPLATE_ENV = "PSA_COUNTERS_TEMPLATE"

DEFAULT_COUNTERS = {"vA": 20, "vB": 800, "vC": 800, "vD": 1500}


def _load_counters_template() -> dict:
    """模板值：内置默认 + 可选 JSON 文件覆盖（env 指路径）。"""
    tpl = dict(DEFAULT_COUNTERS)
    path = os.environ.get(COUNTERS_TEMPLATE_ENV, "")
    if path:
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if isinstance(data, dict):
                for k in ("vA", "vB", "vC", "vD"):
                    if isinstance(data.get(k), (int, float)):
                        tpl[k] = data[k]
        except Exception:
            pass  # 覆盖文件坏 → 静默用内置默认（改写值语义已证安全）
    return tpl


def _fetch_material(url: str, ua: str) -> dict:
    """curl_cffi 非 impersonate 抓 403 页 + orchestrate（fetch_material/OV 范式）。
    返回 {html, orch_bytes, orch_url, error}。失败 error 非 None。"""
    from curl_cffi import requests as cr

    out = {"html": "", "orch_bytes": b"", "orch_url": "", "error": None}
    try:
        r1 = cr.get(url, headers={"User-Agent": ua, "Accept": "*/*"},
                    timeout=30, allow_redirects=False)
        html = r1.content.decode("utf-8", errors="replace")
        if r1.status_code != 403:
            out["error"] = f"page HTTP {r1.status_code} (expect 403)"
            return out
        m = re.search(r"""src\s*=\s*["']([^"']*orchestrate[^"']*)""", html)
        if not m:
            out["error"] = "orchestrate src not found in 403 page"
            return out
        src = m.group(1)
        orch_url = src if src.startswith("http") else "https://www.psacard.com" + src
        r2 = cr.get(orch_url, headers={"User-Agent": ua, "Referer": url},
                    timeout=30)
        if r2.status_code != 200 or len(r2.content) < 10000:
            out["error"] = f"orchestrate HTTP {r2.status_code}/{len(r2.content)}B"
            return out
        out.update(html=html, orch_bytes=r2.content, orch_url=orch_url)
    except Exception as exc:
        out["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    return out


def solve_challenge(ua: str, sn: str = CERT_SN, verbose: bool = False,
                    counters_rewrite: bool = False) -> dict:
    """ruyijs 自含求解。返回 cookies dict（值仅内存传递）+ 元数据，不含 cookie 值的日志。

    counters_rewrite=True：预抓材料 → 探针内联改写 4 计数器（template_probe）→
    load_page+put_resource 跑（OV2 混合跑同款）；定位失败或链不收敛 → 原生
    navigate 模式完整重跑。summary 带 mode 字段：
      native / templated / templated-fallback。"""
    import ruyijs
    from run_ruyijs import _redact_net_events

    _strip_proxy_env()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    url = PAGE_URL.format(sn=sn)
    fingerprint = {g: dict(v) for g, v in FINGERPRINT_TMPL.items()}
    fingerprint["navigator"]["userAgent"] = ua

    if counters_rewrite:
        result = _solve_templated(ruyijs, _redact_net_events, url, ua, fingerprint, sn)
        if result is not None:
            return result
        # 降级：改写跑失败 → 落到原生 navigate 模式（结果 mode 标记）

    started = time.monotonic()
    context = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    error = None
    net: list = []
    cookies: dict = {}
    try:
        context.configure_fingerprint(fingerprint)
        context.configure_clock("system")
        context.navigate(url)
        try:
            context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
        except Exception:
            pass  # 0.2.2 document-swap 竞态：炸一批 task，context 存活
        deadline = time.monotonic() + PUMP_WALL_S
        last_progress = time.monotonic()
        seen = 0
        while time.monotonic() < deadline:
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(context, fn)(**kw)
                except Exception:
                    pass
            try:
                context.advance(500, max_tasks=32000)
            except Exception:
                pass
            raw = context.net_log() if callable(getattr(context, "net_log", None)) else []
            net = _redact_net_events(raw if isinstance(raw, list) else [])
            if len(net) != seen:
                seen = len(net)
                last_progress = time.monotonic()
            verdict = _classify(net, sn)
            if verdict["certOk"]:
                break
            if time.monotonic() - last_progress > ADVANCE_QUIET_S:
                break
            time.sleep(0.25)
        verdict = _classify(net, sn)
        raw_cookies = context.export_cookies() if callable(getattr(context, "export_cookies", None)) else None
        if isinstance(raw_cookies, str):
            for pair in raw_cookies.split(";"):
                if "=" in pair:
                    k, _, v = pair.strip().partition("=")
                    cookies[k.strip()] = v
        elif isinstance(raw_cookies, dict):
            cookies = {str(k): str(v) for k, v in raw_cookies.items()}
        elif isinstance(raw_cookies, list):
            for row in raw_cookies:
                if isinstance(row, dict) and row.get("name"):
                    cookies[str(row["name"])] = str(row.get("value", ""))
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"[:500]
    finally:
        try:
            context.close()
        except Exception:
            pass

    wall = round(time.monotonic() - started, 1)
    verdict = _classify(net, sn)
    return {
        "ok": bool(cookies.get("cf_clearance")) and verdict["certOk"] and error is None,
        "cookies": cookies,
        "wallS": wall,
        "foRounds": len(verdict["foPosts"]),
        "foStatuses": [r["status"] for r in verdict["foPosts"]],
        "certOk": verdict["certOk"],
        "certGetStatuses": [r["status"] for r in verdict["certGets"]],
        "cookieNames": sorted(cookies.keys()),
        "error": error,
        "mode": "templated-fallback" if counters_rewrite else "native",
    }


def _solve_templated(ruyijs, redact, url: str, ua: str, fingerprint: dict, sn: str) -> dict | None:
    """改写模式求解（OV2 混合跑生产化）。失败返回 None（调用方降级原生）。

    流程：curl_cffi 预抓材料（403+orchestrate）→ template_probe 生成探针
    （定位失败即放弃）→ Context: put_resource(探针版 orchestrate) + __psaSink
    + __tpl 模板 → load_page(403 html) → 泵到 clearance。
    """
    import time as _t

    started = _t.monotonic()
    # -I 隔离模式下脚本目录不进 sys.path，模板探针同目录需要显式加入
    here = str(Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        from template_probe import build_probe, TemplateProbeError
    except Exception as exc:
        sys.stderr.write("counters-rewrite: template_probe import failed: %s\n"
                         % (str(exc)[:200]))
        return None

    mat = _fetch_material(url, ua)
    if mat["error"]:
        sys.stderr.write("counters-rewrite: material fetch failed: %s\n" % mat["error"])
        return None
    try:
        probe_bytes, probe_meta = build_probe(mat["orch_bytes"], _load_counters_template())
    except TemplateProbeError as exc:
        sys.stderr.write("counters-rewrite: probe locate failed: %s\n" % (str(exc)[:200]))
        return None

    error = None
    net: list = []
    cookies: dict = {}
    tpl_seen = 0
    tpl_pre = tpl_post = None
    context = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    try:
        context.configure_fingerprint(fingerprint)
        context.configure_clock("system")

        def sink(direction, inp, outp):
            nonlocal tpl_seen, tpl_pre, tpl_post
            if direction == "TP":
                tpl_pre, tpl_post = str(inp), str(outp)
            elif direction == "TS":
                try:
                    tpl_seen = max(tpl_seen, int(inp))
                except Exception:
                    pass
            return True

        context.expose(sink, "__psaSink")
        context.eval("globalThis.__tpl=JSON.parse(%s)"
                     % json.dumps(json.dumps({
                         "kA": "", "vA": probe_meta["template"]["vA"],
                         "kB": "", "vB": probe_meta["template"]["vB"],
                         "kC": "", "vC": probe_meta["template"]["vC"],
                         "kD": "", "vD": probe_meta["template"]["vD"]})))
        headers = [["content-type", "application/javascript"]]
        context.put_resource(mat["orch_url"], probe_bytes, status=200, headers=headers)
        context.put_resource(mat["orch_url"].split("?", 1)[0], probe_bytes,
                             status=200, headers=headers)
        context.load_page(url, mat["html"])
        try:
            context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
        except Exception:
            pass  # 0.2.2 document-swap 竞态：炸一批 task，context 存活
        deadline = _t.monotonic() + PUMP_WALL_S
        last_progress = _t.monotonic()
        seen = 0
        while _t.monotonic() < deadline:
            for fn, kw in (("checkpoint", {}), ("drain_timers", {"max_tasks": 8192})):
                try:
                    getattr(context, fn)(**kw)
                except Exception:
                    pass
            try:
                context.advance(500, max_tasks=32000)
            except Exception:
                pass
            raw = context.net_log() if callable(getattr(context, "net_log", None)) else []
            net = redact(raw if isinstance(raw, list) else [])
            if len(net) != seen:
                seen = len(net)
                last_progress = _t.monotonic()
            verdict = _classify(net, sn)
            if verdict["certOk"]:
                break
            if _t.monotonic() - last_progress > ADVANCE_QUIET_S:
                break
            time.sleep(0.25)
        verdict = _classify(net, sn)
        raw_cookies = context.export_cookies() if callable(getattr(context, "export_cookies", None)) else None
        if isinstance(raw_cookies, str):
            for pair in raw_cookies.split(";"):
                if "=" in pair:
                    k, _, v = pair.strip().partition("=")
                    cookies[k.strip()] = v
        elif isinstance(raw_cookies, dict):
            cookies = {str(k): str(v) for k, v in raw_cookies.items()}
        elif isinstance(raw_cookies, list):
            for row in raw_cookies:
                if isinstance(row, dict) and row.get("name"):
                    cookies[str(row["name"])] = str(row.get("value", ""))
    except Exception as exc:
        error = "%s: %s" % (type(exc).__name__, str(exc)[:500])
    finally:
        try:
            context.close()
        except Exception:
            pass

    wall = round(_t.monotonic() - started, 1)
    verdict = _classify(net, sn)
    ok = bool(cookies.get("cf_clearance")) and verdict["certOk"] and error is None
    if not ok:
        sys.stderr.write("counters-rewrite: chain not converged "
                         "(certOk=%s clearance=%s error=%s tplSeen=%s)\n"
                         % (verdict["certOk"], bool(cookies.get("cf_clearance")),
                            error, tpl_seen))
        return None  # 调用方降级原生
    return {
        "ok": True,
        "cookies": cookies,
        "wallS": wall,
        "foRounds": len(verdict["foPosts"]),
        "foStatuses": [r["status"] for r in verdict["foPosts"]],
        "certOk": verdict["certOk"],
        "certGetStatuses": [r["status"] for r in verdict["certGets"]],
        "cookieNames": sorted(cookies.keys()),
        "error": None,
        "mode": "templated",
        "rewrite": {"tplSeen": tpl_seen,
                    "pre": tpl_pre, "post": tpl_post,
                    "probeSha16": probe_meta["probe_sha16"],
                    "v0Name": probe_meta["v0_name"]},
    }


def validate_clearance(cookies: dict, ua: str, sn: str = CERT_SN) -> dict:
    """生产 curl_cffi 同 UA 验证 clearance。返回 {ok, status, challenge}，不落 cookie 值。"""
    from curl_cffi.requests import Session

    session = Session(impersonate="firefox")
    try:
        r = session.get(PAGE_URL.format(sn=sn), headers={"User-Agent": ua}, cookies=cookies, timeout=15)
        title = b"Just a moment" in r.content[:3000]
        return {"ok": r.status_code == 200 and not title, "status": r.status_code, "challenge": title}
    finally:
        session.close()


def main() -> int:
    # 子进程模式（demo6 集成入口）：--out <file> 把 cookie JSON 落盘后自删由调用方负责
    out_path = None
    counters_rewrite = False
    args = sys.argv[1:]
    if "--out" in args:
        i = args.index("--out")
        out_path = args[i + 1]
        args = args[:i] + args[i + 2:]
    if "--counters-rewrite" in args:
        i = args.index("--counters-rewrite")
        val = args[i + 1] if i + 1 < len(args) and not args[i + 1].startswith("--") else "on"
        counters_rewrite = val not in ("off", "0", "false")
        drop = args[i:i + 2] if (i + 1 < len(args) and not args[i + 1].startswith("--")) else args[i:i + 1]
        args = args[:i] + args[i + len(drop):]
    # 模板覆盖文件也可经 env 传（demo6 子进程 env 透传）
    if os.environ.get(COUNTERS_REWRITE_ENV, "").lower() in ("1", "on", "true"):
        counters_rewrite = True
    ua = args[0] if args else "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0"
    result = solve_challenge(ua, counters_rewrite=counters_rewrite)
    if out_path is not None:
        Path(out_path).write_text(json.dumps(result["cookies"], ensure_ascii=False), encoding="utf-8")
    summary = {k: v for k, v in result.items() if k != "cookies"}
    summary["hasCfClearance"] = bool(result["cookies"].get("cf_clearance"))
    summary["hasCfBm"] = bool(result["cookies"].get("__cf_bm"))
    if result["ok"] and out_path is None:
        v = validate_clearance(result["cookies"], ua)
        summary["crossEngineValidation"] = v
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
