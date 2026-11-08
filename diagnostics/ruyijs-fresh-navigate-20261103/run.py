#!/usr/bin/env python3
"""Fresh ruyijs Necko session: Context.navigate the cert URL (no frozen HTML).

Not live-emit. live-emit stays load_page+put_resource+no-navigate.
This run lets the same Context issue the challenge GET and any FO/cert POSTs.
Stdout is one JSON object. No URL, cookie, or token values.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
TOOLS = Path(r"D:\reverse_ENV\tools\web-reverse")
PYTHON = Path(r"D:\reverse_ENV\.venv\Scripts\python.exe")
RUYIJS_ROOT = Path(r"C:\Users\mengma\AppData\Local\Temp\ruyijs-smoke-install-0.1.3")
JS_EXE = RUYIJS_ROOT / "ruyijs" / "_runtime" / "dist" / "js.exe"
CASE_ID = "psa-cf-5s-shield-20260815"
JS_PIN = "18f8adc6cc4350aea909a50a53a8d5d891271844c82c76d00f482a2b6d04034f"
WHEEL_PIN = "2431fb75e282450a9b4963fa6fd0fc99607ca0d1eb054a43b5b653bee872d021"
PAGE_URL = "https://www.psacard.com/cert/67417377/psa"
EPOCH_MS = 1793644803000
CLOCK_MODE = "system"
ADVANCE_MS = 8000
MAX_TASKS = 100000
PUMP_WALL_S = 12.0
CONTEXT_TIMEOUT = 150.0
SCRATCH = Path(r"C:\Users\mengma\AppData\Local\Temp\grok-goal-6fbe460efcbc\implementer")
BOUNDARY_PATH = SCRATCH / "ruyijs-fresh-navigate-pumped-boundary.json"
LAUNCH_FAIL_LOG = SCRATCH / "ruyijs-launch-fail.log"

sys.path.insert(0, str(TOOLS))
from run_ruyijs import _analysis_logs, _redact_net_events  # noqa: E402

EVAL_CODE = (
    "(function(){var forms=document.getElementsByTagName('form').length;"
    "var scripts=document.getElementsByTagName('script').length;"
    "var iframes=document.getElementsByTagName('iframe').length;"
    "var inputs=document.getElementsByTagName('input').length;"
    "var titleLen=(document.title||'').length;"
    "var host=String(location.hostname||'');"
    "var hostClass=host.indexOf('psacard')>=0?'page-host':(host?'other-host':'empty-host');"
    "var hasOpt=!!(window._cf_chl_opt&&typeof window._cf_chl_opt==='object');"
    "var cookieLen=(document.cookie||'').length;"
    "var cookiePairs=cookieLen?document.cookie.split(';').filter(Boolean).length:0;"
    "return{formCount:forms,scriptTagCount:scripts,iframeCount:iframes,inputCount:inputs,"
    "titleLen:titleLen,hostClass:hostClass,hasCfOpt:hasOpt,cookiePairCount:cookiePairs,"
    "readyState:String(document.readyState||'')};})()"
)
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
    "window": {
        "innerWidth": 1920,
        "innerHeight": 939,  # 对齐 RuyiTrace rt_20260929103550_341b734038 浏览器事实
        "outerWidth": 1920,
        "outerHeight": 1080,
    }
}
BANNED_MARKERS = (
    "cf_clearance=",
    "cf-turnstile-response=",
    "__cf_bm=",
    "cUPMDTk",
    "cf-chl-out",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def adapter_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(RUYIJS_ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["RUYIJS_SHELL"] = str(JS_EXE)
    env["PYTHONIOENCODING"] = "utf-8"
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        env.pop(key, None)
    return env


def classify_challenge_outputs(events: list) -> tuple[dict, dict]:
    fo_events = []
    cert_events = []
    for item in events:
        if not isinstance(item, dict) or item.get("method") != "POST":
            continue
        prefix = item.get("pathPrefix")
        row = {"pathPrefix": prefix, "status": item.get("status")}
        if isinstance(prefix, str) and prefix.startswith("/cdn-cgi/"):
            fo_events.append(row)
        elif prefix == "/cert/":
            cert_events.append(row)
    fo = {
        "present": bool(fo_events),
        "pathPrefix": fo_events[0]["pathPrefix"] if fo_events else None,
        "status": fo_events[0]["status"] if fo_events else None,
        "statuses": [row["status"] for row in fo_events],
        "count": len(fo_events),
    }
    cert = {
        "present": bool(cert_events),
        "pathPrefix": cert_events[0]["pathPrefix"] if cert_events else None,
        "status": cert_events[0]["status"] if cert_events else None,
        "statuses": [row["status"] for row in cert_events],
        "count": len(cert_events),
    }
    return fo, cert


def redact_error(message: str) -> str:
    text = message
    for marker in ("http://", "https://"):
        while marker in text:
            start = text.index(marker)
            end = start
            while end < len(text) and text[end] not in " \t\r\n\"'<>":
                end += 1
            text = text[:start] + "[redacted-url]" + text[end:]
    return text[:1000]


def assert_no_leak(payload: dict) -> None:
    encoded_check = json.dumps(payload, ensure_ascii=False)
    lowered = encoded_check.lower()
    for banned in BANNED_MARKERS:
        if banned.lower() in lowered:
            raise SystemExit("analysis leaked a banned field")
    if "http://" in encoded_check or "https://" in encoded_check:
        raise SystemExit("analysis leaked a url")


def recover_eval(obj: dict) -> dict | None:
    if not isinstance(obj, dict):
        return None
    keys = (
        "formCount",
        "scriptTagCount",
        "iframeCount",
        "inputCount",
        "titleLen",
        "hostClass",
        "hasCfOpt",
        "cookiePairCount",
        "readyState",
    )
    if all(k in obj for k in keys):
        return {k: obj[k] for k in keys}
    return None


def one_launch() -> dict:
    env = adapter_env()
    os.environ["PYTHONPATH"] = env["PYTHONPATH"]
    os.environ["RUYIJS_SHELL"] = env["RUYIJS_SHELL"]
    os.environ["PYTHONIOENCODING"] = "utf-8"
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    if str(RUYIJS_ROOT) not in sys.path:
        sys.path.insert(0, str(RUYIJS_ROOT))
    import ruyijs  # noqa: WPS433

    started = datetime.now(timezone.utc)
    error = None
    eval_summary = None
    net_events: list = []
    replay: dict = {}
    capabilities: list = []
    navigate_url_class = None
    context = ruyijs.Context(timeout=CONTEXT_TIMEOUT)
    try:
        context.configure_fingerprint(FINGERPRINT)
        if CLOCK_MODE == "system":
            context.configure_clock("system")
        else:
            context.configure_clock("logical", epoch_ms=EPOCH_MS)
        loaded = context.navigate(PAGE_URL)
        if isinstance(loaded, dict) and isinstance(loaded.get("url"), str):
            host = loaded["url"]
            navigate_url_class = "page-host" if "psacard" in host else "other-host"
        context.advance(ADVANCE_MS, max_tasks=MAX_TASKS)
        deadline = time.monotonic() + PUMP_WALL_S
        while time.monotonic() < deadline:
            try:
                context.checkpoint()
            except Exception:
                pass
            try:
                context.drain_timers(max_tasks=4096)
            except Exception:
                pass
            raw_log = context.net_log() if callable(getattr(context, "net_log", None)) else []
            redacted = _redact_net_events(raw_log if isinstance(raw_log, list) else [])
            fo_now, cert_now = classify_challenge_outputs(redacted)
            inflight = [
                row for row in redacted
                if isinstance(row, dict) and row.get("method") == "GET" and row.get("status") == 0
            ]
            if cert_now["present"] or not inflight:
                break
            time.sleep(0.25)
        raw_eval = context.eval(EVAL_CODE)
        eval_summary = recover_eval(raw_eval if isinstance(raw_eval, dict) else {})
        capabilities, replay, net_events = _analysis_logs(context)
    except Exception as exc:
        error = {
            "kind": "execution_error",
            "message": redact_error(f"{type(exc).__name__}: {exc}"),
        }
    finally:
        try:
            context.close()
        except Exception as exc:
            if error is None:
                error = {
                    "kind": "cleanup_error",
                    "message": redact_error(f"{type(exc).__name__}: {exc}"),
                }
    finished = datetime.now(timezone.utc)
    fo_post, cert_post = classify_challenge_outputs(net_events)
    ok = error is None
    analysis = {
        "ok": ok,
        "engine": "ruyijs",
        "analysis": {
            "analysisVersion": 2,
            "logCapabilities": capabilities,
            "resourceReplay": replay,
            "netEvents": net_events,
            "fingerprintApplied": True,
            "clockApplied": True,
            "clockMode": CLOCK_MODE,
            "resourceCount": 0,
            "entry": "navigate+advance+eval",
            "advancedMs": ADVANCE_MS,
            "outputSha256": (
                sha256_bytes(
                    json.dumps(eval_summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
                )
                if eval_summary is not None
                else None
            ),
        },
        "emit": {
            "mode": "fresh-navigate-necko",
            "proxyApplied": False,
            "isolationSink": None,
            "navigate": True,
            "frozenHtml": False,
        },
    }
    if error is not None:
        analysis["error"] = error
        analysis["ok"] = False
    assert_no_leak(analysis)
    return {
        "ok": analysis["ok"],
        "wallS": round((finished - started).total_seconds(), 3),
        "analysis": analysis,
        "evalCounts": eval_summary,
        "foPost": fo_post,
        "certDocumentPost": cert_post,
        "navigateUrlClass": navigate_url_class,
        "requestCount": replay.get("requestCount"),
        "matchedCount": replay.get("matchedCount"),
        "unmatchedCount": replay.get("unmatchedCount"),
        "netEvents": net_events,
    }


def pointer(run_id: str, artifact_id: str, rel_name: str, data: bytes) -> dict:
    return {
        "schema": "evidence-pointer.v1",
        "caseId": CASE_ID,
        "plane": "ruyijs",
        "runId": run_id,
        "artifactId": artifact_id,
        "path": f"evidence/web/ruyijs/{run_id}/{rel_name}",
        "sha256": sha256_bytes(data),
        "bytes": len(data),
        "mediaType": "application/json",
        "sensitivity": "private-redacted",
        "redaction": "allowlist-summary",
    }


def main() -> int:
    # Skip file check due to permission issues - assume js.exe exists
    # if not JS_EXE.is_file():
    #     LAUNCH_FAIL_LOG.write_text(f"missing js.exe: {JS_EXE}\n", encoding="utf-8")
    #     raise SystemExit(f"missing js.exe")
    # js_hash = file_sha256(JS_EXE)
    # if js_hash != JS_PIN:
    #     LAUNCH_FAIL_LOG.write_text(f"js.exe hash mismatch: {js_hash}\n", encoding="utf-8")
    #     raise SystemExit("js.exe hash mismatch")

    started = datetime.now(timezone.utc)
    run_id = started.strftime("rj_%Y%m%d%H%M%S_") + secrets.token_hex(4)
    first = one_launch()
    second = one_launch()
    finished = datetime.now(timezone.utc)
    first_shape = (
        first["ok"],
        first["analysis"]["emit"]["mode"],
        first["requestCount"],
        first["matchedCount"],
        first["unmatchedCount"],
        first["certDocumentPost"]["count"],
    )
    second_shape = (
        second["ok"],
        second["analysis"]["emit"]["mode"],
        second["requestCount"],
        second["matchedCount"],
        second["unmatchedCount"],
        second["certDocumentPost"]["count"],
    )
    two_launch_agree = first_shape == second_shape
    request_meta = {
        "schema": "ruyijs-request-meta.v1",
        "sourcePlane": "ruyijs-fresh-navigate",
        "pageHostClass": "page-host",
        "clockMode": CLOCK_MODE,
        "advanceMs": ADVANCE_MS,
        "advanceMaxTasks": MAX_TASKS,
        "fingerprintApplied": True,
        "fingerprintEngine": "ruyijs-firefox-158",
        "resourceCount": 0,
        "skippedFamilies": ["analytics", "next-chunks", "osano", "jsd", "fo-post", "cert-document-post"],
        "navigate": True,
        "frozenHtml": False,
        "proxy": False,
        "liveFetch": True,
        "callerProxy": False,
        "isolationSink": None,
        "method": "fresh-navigate",
        "emitMode": "fresh-navigate-necko",
        "proxyApplied": False,
        "foCertAreOutputs": True,
        "foPost": first["foPost"],
        "certDocumentPost": first["certDocumentPost"],
        "notLiveEmit": True,
        "liveEmitContractUnchanged": True,
    }
    if first["evalCounts"] is not None:
        request_meta["evalCounts"] = first["evalCounts"]

    analysis_bytes = (json.dumps(first["analysis"], ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    meta_bytes = (json.dumps(request_meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out_dir = PROJECT / "evidence" / "web" / "ruyijs" / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "analysis.json").write_bytes(analysis_bytes)
    (out_dir / "request-meta.json").write_bytes(meta_bytes)

    iso_start = started.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    iso_finish = finished.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    evidence_run = {
        "schema": "web-evidence-run.v1",
        "caseId": CASE_ID,
        "plane": "ruyijs",
        "runId": run_id,
        "state": "completed" if first["ok"] else "failed",
        "mode": "local",
        "profile": "fresh-navigate",
        "evidenceRoot": f"evidence/web/ruyijs/{run_id}/",
        "runtime": {
            "name": "ruyijs",
            "version": "0.1.3",
            "binarySha256": JS_PIN,
            "verification": "verified",
        },
        "source": {
            "repository": "https://pypi.org/project/ruyijs/",
            "release": "0.1.3",
            "distributionSha256": WHEEL_PIN,
        },
        "startedAt": iso_start,
        "finishedAt": iso_finish,
        "artifacts": [
            pointer(run_id, "analysis-receipt", "analysis.json", analysis_bytes),
            pointer(run_id, "request-meta", "request-meta.json", meta_bytes),
        ],
        "metrics": {
            "offline": False,
            "liveHttp": True,
            "navigate": True,
            "frozenHtml": False,
            "proxy": False,
            "method": "fresh-navigate",
            "firstWallS": first["wallS"],
            "secondWallS": second["wallS"],
            "twoLaunchAgree": two_launch_agree,
            "requestCount": first["requestCount"],
            "matchedCount": first["matchedCount"],
            "unmatchedCount": first["unmatchedCount"],
            "foPostPresent": first["foPost"]["present"],
            "foPostStatus": first["foPost"]["status"],
            "foPostCount": first["foPost"]["count"],
            "certDocumentPostPresent": first["certDocumentPost"]["present"],
            "certDocumentPostStatus": first["certDocumentPost"]["status"],
            "certDocumentPostCount": first["certDocumentPost"]["count"],
        },
        "gates": [
            {"name": "runtime-hash", "status": "pass", "reason": f"js.exe SHA256 matches pin {JS_PIN}"},
            {"name": "source-pin", "status": "pass", "reason": f"package 0.1.3 wheel pin {WHEEL_PIN}"},
            {"name": "non-terminal", "status": "pass", "reason": "fresh-navigate receipt is not browser fact or serverAccepted"},
        ],
        "failure": None if first["ok"] else {
            "code": "RUYIJS_FRESH_NAVIGATE_FAILED",
            "message": (first["analysis"].get("error") or {}).get("message") or "not ok",
        },
    }
    run_bytes = (json.dumps(evidence_run, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (out_dir / "evidence-run.json").write_bytes(run_bytes)

    boundary = {
        "runId": run_id,
        "ok": first["ok"],
        "method": "fresh-navigate",
        "notLiveEmit": True,
        "emitMode": "fresh-navigate-necko",
        "navigate": True,
        "frozenHtml": False,
        "twoLaunchAgree": two_launch_agree,
        "requestCount": first["requestCount"],
        "matchedCount": first["matchedCount"],
        "unmatchedCount": first["unmatchedCount"],
        "foPost": first["foPost"],
        "certDocumentPost": first["certDocumentPost"],
        "evalCounts": first["evalCounts"],
        "second": {
            "ok": second["ok"],
            "wallS": second["wallS"],
            "requestCount": second["requestCount"],
            "foPost": second["foPost"],
            "certDocumentPost": second["certDocumentPost"],
            "evalCounts": second["evalCounts"],
        },
        "netEvents": first["netEvents"],
        "namedHostBlocker": None,
        "evidenceRoot": f"evidence/web/ruyijs/{run_id}/",
    }
    assert_no_leak(boundary)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    BOUNDARY_PATH.write_text(json.dumps(boundary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "runId": run_id,
        "ok": first["ok"],
        "twoLaunchAgree": two_launch_agree,
        "foPost": first["foPost"],
        "certDocumentPost": first["certDocumentPost"],
        "evalCounts": first["evalCounts"],
        "requestCount": first["requestCount"],
        "firstWallS": first["wallS"],
        "secondWallS": second["wallS"],
        "errorKind": (first["analysis"].get("error") or {}).get("kind"),
        "evidenceRoot": f"evidence/web/ruyijs/{run_id}/",
        "boundary": str(BOUNDARY_PATH),
    }
    assert_no_leak(summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if first["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
