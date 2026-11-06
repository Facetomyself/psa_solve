#!/usr/bin/env python3
"""fresh-navigate long-pump on ruyijs inner 0.2.2: let the live challenge finish.

Historical rj_20261102211143_61a75afb (0.1.3, 12s pump) reached FO POST x3 all 200
with payloads escalating to 84KB — the chain was working but the pump ended early.
This run: same live entry, 180s pump, 0.2.2 fingerprint schema (viewport group),
per-round document state eval, and a second navigate() to test clearance readback.

Stdout: one JSON object. No URL, cookie, or token values.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
TOOLS = Path(r"D:\reverse_ENV\tools\web-reverse")
PAGE_URL = "https://www.psacard.com/cert/67417377/psa"
CASE_ID = "psa-cf-5s-shield-20260815"

CONTEXT_TIMEOUT = 400.0
ADVANCE_MS = 10000
MAX_TASKS = 100000  # inner 0.2.2 hard cap: 1..100000
PUMP_WALL_S = 180.0
EVAL_EVERY_S = 15.0
CERT_FILE_SN = "67417377"

OUT_DIR = PROJECT / "diagnostics" / "ruyijs-fresh-navigate-20261103"
BOUNDARY_PATH = OUT_DIR / "boundary-022-longpump.json"

sys.path.insert(0, str(TOOLS))
from run_ruyijs import _redact_net_events  # noqa: E402

FINGERPRINT = {
    "navigator": {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
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
    "viewport": {
        "width": 1920,
        "height": 939,
        "devicePixelRatio": 1,
    },
}

EVAL_STATE = (
    "(function(){"
    "return JSON.stringify({"
    "forms:document.getElementsByTagName('form').length,"
    "inputs:document.getElementsByTagName('input').length,"
    "scripts:document.getElementsByTagName('script').length,"
    "iframes:document.getElementsByTagName('iframe').length,"
    "titleLen:(document.title||'').length,"
    "host:(location.hostname||'').indexOf('psacard')>=0?'page-host':'other',"
    "hasOpt:!!(window._cf_chl_opt&&typeof window._cf_chl_opt==='object'),"
    "cookiePairs:(document.cookie||'').length?document.cookie.split(';').filter(Boolean).length:0,"
    "rs:String(document.readyState||''),"
    "sn:(document.body&&document.body.innerText?document.body.innerText.indexOf('%SN%')>=0:false)"
    "})})()"
).replace("%SN%", CERT_FILE_SN)

BANNED_MARKERS = ("cf_clearance=", "cf-turnstile-response=", "__cf_bm=", "cUPMDTk", "cf-chl-out")


def classify(events: list) -> dict:
    fo, cert_get, cert_post, cert_2xx = [], [], [], []
    for item in events:
        if not isinstance(item, dict):
            continue
        prefix = item.get("pathPrefix")
        row = {"method": item.get("method"), "status": item.get("status"), "body": item.get("requestBodyBytes")}
        if item.get("method") == "POST" and isinstance(prefix, str) and prefix.startswith("/cdn-cgi/"):
            fo.append(row)
        if isinstance(prefix, str) and prefix.startswith("/cert/"):
            if item.get("method") == "POST":
                cert_post.append(row)
            else:
                cert_get.append(row)
                if isinstance(item.get("status"), int) and 200 <= item["status"] < 300:
                    cert_2xx.append(row)
    return {
        "foPosts": fo,
        "certGets": cert_get,
        "certPosts": cert_post,
        "certOk": bool(cert_2xx),
        "certOkStatuses": [r["status"] for r in cert_2xx],
    }


def redact_error(message: str) -> str:
    text = message
    for marker in ("http://", "https://"):
        while marker in text:
            start = text.index(marker)
            end = start
            while end < len(text) and text[end] not in " \t\r\n\"'<>":
                end += 1
            text = text[:start] + "[redacted-url]" + text[end:]
    return text[:800]


def assert_no_leak(payload: dict) -> None:
    encoded = json.dumps(payload, ensure_ascii=False).lower()
    for banned in BANNED_MARKERS:
        if banned.lower() in encoded:
            raise SystemExit(f"leak: {banned}")
    if "http://" in encoded or "https://" in encoded:
        raise SystemExit("leak: url")


def parse_state(raw) -> dict:
    if isinstance(raw, str) and raw.startswith("{"):
        try:
            return json.loads(raw)
        except Exception:
            return {}
    if isinstance(raw, dict):
        return raw
    return {}


def pump(context, deadline: float, seen_events: int) -> tuple[list, list, float]:
    """Pump until cert 2xx seen, quiet, or wall deadline. Returns (net, states, quiet_s)."""
    net: list = []
    states: list = []
    last_progress = time.monotonic()
    next_eval = 0.0
    while time.monotonic() < deadline:
        for fn in ("checkpoint", "drain_timers"):
            try:
                getattr(context, fn)(max_tasks=8192) if fn == "drain_timers" else getattr(context, fn)()
            except Exception:
                pass
        try:
            context.advance(500, max_tasks=32000)
        except Exception:
            pass
        raw = context.net_log() if callable(getattr(context, "net_log", None)) else []
        net = _redact_net_events(raw if isinstance(raw, list) else [])
        if len(net) != seen_events:
            seen_events = len(net)
            last_progress = time.monotonic()
        verdict = classify(net)
        now = time.monotonic()
        if now >= next_eval:
            next_eval = now + EVAL_EVERY_S
            try:
                st = parse_state(context.eval(EVAL_STATE))
                st["t"] = round(now, 1)
                st["netCount"] = seen_events
                states.append(st)
            except Exception:
                pass
        if verdict["certOk"]:
            break
        if now - last_progress > 25.0:
            break
        time.sleep(0.25)
    return net, states, round(time.monotonic() - last_progress, 1)


def one_launch() -> dict:
    import ruyijs  # noqa: E402

    started = datetime.now(timezone.utc)
    error = None
    adv_errors: list = []
    state = {}
    states: list = []
    net: list = []
    second_cert_status = None
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["PYTHONIOENCODING"] = "utf-8"

    context = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    try:
        context.configure_fingerprint(FINGERPRINT)
        context.configure_clock("system")
        context.navigate(PAGE_URL)
        try:
            context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
        except Exception as exc:
            # 0.2.2 document-swap races throw out of advance; the context may survive.
            adv_errors.append(redact_error(f"{type(exc).__name__}: {exc}"))
        deadline = time.monotonic() + PUMP_WALL_S
        net, states, quiet_s = pump(context, deadline, 0)
        verdict = classify(net)
        try:
            state = parse_state(context.eval(EVAL_STATE))
        except Exception:
            pass
        # Readback: second navigate in the SAME context reuses the cookie jar.
        if not verdict["certOk"]:
            try:
                context.navigate(PAGE_URL)
                context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
            except Exception as exc:
                adv_errors.append("second:" + redact_error(f"{type(exc).__name__}: {exc}"))
            deadline2 = time.monotonic() + 30.0
            net2, _, _ = pump(context, deadline2, len(net))
            net = net2 if len(net2) >= len(net) else net + net2
            verdict = classify(net)
            if verdict["certGets"]:
                second_cert_status = verdict["certGets"][-1]["status"]
            try:
                state = parse_state(context.eval(EVAL_STATE))
            except Exception:
                pass
        else:
            if verdict["certGets"]:
                second_cert_status = verdict["certGets"][-1]["status"]
    except Exception as exc:
        error = {"kind": "execution_error", "message": redact_error(f"{type(exc).__name__}: {exc}")}
    finally:
        try:
            context.close()
        except Exception as exc:
            if error is None:
                error = {"kind": "cleanup_error", "message": redact_error(f"{type(exc).__name__}: {exc}")}
    finished = datetime.now(timezone.utc)
    verdict = classify(net)
    ok = error is None
    result = {
        "ok": ok,
        "engine": "ruyijs-inner-0.2.2",
        "entry": "fresh-navigate-longpump",
        "pumpWallS": PUMP_WALL_S,
        "foPostCount": len(verdict["foPosts"]),
        "foPostStatuses": [r["status"] for r in verdict["foPosts"]],
        "foPostBodies": [r["body"] for r in verdict["foPosts"]],
        "certOk": verdict["certOk"],
        "certOkStatuses": verdict["certOkStatuses"],
        "certGetStatuses": [r["status"] for r in verdict["certGets"]],
        "certPostStatuses": [r["status"] for r in verdict["certPosts"]],
        "secondCertStatus": second_cert_status,
        "finalState": state,
        "stateTimeline": states,
        "netEventCount": len(net),
        "netEvents": net,
        "wallS": round((finished - started).total_seconds(), 1),
    }
    if error is not None:
        result["error"] = error
    if adv_errors:
        result["advanceErrors"] = adv_errors[:6]
    assert_no_leak(result)
    return result


def main() -> int:
    result = one_launch()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BOUNDARY_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {k: v for k, v in result.items() if k not in ("netEvents", "stateTimeline")}
    summary["stateTimelineTail"] = result["stateTimeline"][-4:]
    summary["boundary"] = str(BOUNDARY_PATH)
    assert_no_leak(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    return 0 if result["certOk"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
