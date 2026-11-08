"""One-shot causal-observer live wrapper. Default preflight is strictly offline.

Fresh materials preserve the historical urllib/UA135 -> Gecko handoff.
This is a logical challenge/cookie session, NOT a single TLS connection.
Raw inputs/output are only written below the project's gitignored evidence/.
Independent from cleanup and instrumentation v1/v2 receipts.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import http.cookiejar
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
from urllib.parse import urljoin, urlparse
from urllib.request import build_opener, Request, HTTPErrorProcessor, HTTPCookieProcessor

ROOT = Path(r"D:\reverse_ENV\workspace\psa_solve")
REPO = Path(r"D:\reverse_ENV")
PY = REPO / ".venv/Scripts/python.exe"
NODE = REPO / "tools/node/node.exe"
CASE = REPO / "skill/web-reverse/scripts/web_case.py"
CLI = REPO / "mcp/ruyidom-mcp/dist/cli.js"
CONTRACT = REPO / "skill/web-reverse/scripts/diagnostic_causal_observer.py"
RESTRICTED = ROOT / "evidence/web/diagnostic-causal-observer/restricted"
STATE = ROOT / "agent-notes/20260930-causal-observer-live-state.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"


def load_contract():
    spec = importlib.util.spec_from_file_location("diagnostic_causal_observer", CONTRACT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C = load_contract()


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def state(**delta):
    value = read(STATE)
    value.update(delta)
    value["updatedAt"] = now()
    write(STATE, value)


def preflight():
    assert digest(ROOT / C.SOURCE) == C.PROFILE["sourceStableSha256"]
    assert digest(ROOT / C.RUNNER) == C.PROFILE["runnerSha256"]
    assert digest(ROOT / C.BASE / "profile.json") == C.PROFILE["profileSha256"]
    facts = read(ROOT / "contracts/auto-decision-facts.json")
    assert facts.get("experimentHygiene") == "stop-search"
    assert facts.get("serverAccepted") is False
    assert facts.get("ruyidomNetwork") == "live"
    assert not (ROOT / C.RECEIPT).exists()
    result = subprocess.run([str(NODE), str(CLI), "status"], capture_output=True, encoding="utf-8")
    assert result.returncode == 0
    runtime = json.loads(result.stdout)
    assert runtime["ok"] is True and runtime["runtime"]["status"] == "healthy"
    RESTRICTED.parent.mkdir(parents=True, exist_ok=True)
    write(RESTRICTED.parent / "runtime-status.json", runtime)
    proxy_names = [k for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "CF_PROXY", "CF_PRE_PROXY") if os.environ.get(k)]
    return {
        "hashesValid": True,
        "runtimeHealthy": True,
        "proxyEnvironmentNames": proxy_names,
        "handoff": "urllib-UA135-cookie-material-to-Gecko; not same TLS",
        "observer": C.PROFILE["id"],
        "independentReceiptsUntouched": True,
    }


class Keep(HTTPErrorProcessor):
    def http_response(self, request, response):
        return response
    https_response = http_response


def parse_orchestrate(html, page_url):
    match = re.search(r"(/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1[^\"'<>\s]*)", html)
    if not match:
        raise ValueError("fresh page has no expected orchestrate URL; no fallback allowed")
    result = urljoin(page_url, match.group(1))
    assert urlparse(result).netloc == urlparse(page_url).netloc
    return result


def fetch_fresh():
    preflight()
    target = read(ROOT / "diagnostics/bridge-input.json")["challengeUrl"]
    session = uuid.uuid4().hex
    out = RESTRICTED / session
    out.mkdir(parents=True, exist_ok=False)
    jar = http.cookiejar.CookieJar()
    opener = build_opener(Keep(), HTTPCookieProcessor(jar))
    cookie_lines, events = [], []
    state(status="fresh-material-fetch-running", sessionId=session, rawDirectory=str(out),
          wrapperPid=os.getpid(), enginePid=None, terminal="running", onlineExecuted=False,
          materialNetworkStartedAt=now())

    def get(url, role):
        request = Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        with opener.open(request, timeout=30) as response:
            body = response.read()
            cookies = response.headers.get_all("Set-Cookie") or []
            cookie_lines.extend(cookies)
            events.append({"role": role, "status": response.status, "bytes": len(body),
                           "at": now(), "urlSha256": hashlib.sha256(url.encode("utf-8")).hexdigest()})
            return response.status, body

    try:
        status, html = get(target, "challenge")
        assert status == 403 and len(html) > 100, "expected fresh 403 challenge"
        orch_url = parse_orchestrate(html.decode("utf-8", "strict"), target)
        status, script = get(orch_url, "orchestrate")
        assert status == 200 and len(script) > 1000, "expected fresh orchestrate body"
        assert cookie_lines and list(jar), "fresh cookie jar is empty"
        (out / "challenge.html").write_bytes(html)
        (out / "orchestrate.js").write_bytes(script)
        (out / "cookies.txt").write_text("\n".join(cookie_lines) + "\n", encoding="utf-8", newline="\n")
        input_path = out / "fresh-input.json"
        write(input_path, {
            "challengeHtmlPath": str(out / "challenge.html"),
            "orchestrateJsPath": str(out / "orchestrate.js"),
            "challengeUrl": target,
            "pumpMs": 30000,
            "patchHistory": True,
            "liveNetwork": True,
            "cookieFile": str(out / "cookies.txt"),
            "tracePath": str(out / "bridge-live.jsonl"),
        })
        captured = now()
        artifacts = [{"role": role, "path": str(out / name), "sha256": digest(out / name),
                      "bytes": (out / name).stat().st_size}
                     for role, name in (("challenge", "challenge.html"), ("orchestrate", "orchestrate.js"),
                                        ("cookies", "cookies.txt"), ("input", "fresh-input.json"))]
        receipt_path = out / "source-receipt.json"
        write(receipt_path, {
            "schema": "psa-fresh-material-receipt.v1", "sessionId": session, "capturedAt": captured,
            "network": "live", "sameSession": True, "foreignResponseReplay": False, "artifacts": artifacts,
            "transport": "urllib UA135 -> Gecko cookie/material handoff; NOT same TLS",
            "events": events,
            "limitations": [
                "same logical challenge session, not same engine/TLS",
                "CookieJar and fail-closed fresh directory differ from historical fetch; not runner-only single-variable experiment",
            ],
        })
        provenance = out / "provenance.json"
        write(provenance, {
            "schema": C.SCHEMA_PROVENANCE, "sessionId": session, "capturedAt": captured,
            "network": "live", "sameSession": True, "foreignResponseReplay": False,
            "inputPath": str(input_path), "inputSha256": digest(input_path),
            "sourceReceiptPath": str(receipt_path), "sourceReceiptSha256": digest(receipt_path),
        })
        state(status="fresh-material-ready", freshInputPrepared=True, provenancePath=str(provenance),
              wrapperPid=None, terminal="completed", materialNetworkEndedAt=now())
        return provenance
    except Exception:
        write(out / "fetch-failure.json", {"errorType": "FetchFailed", "events": events, "endedAt": now()})
        state(status="fresh-material-failed", wrapperPid=None, terminal="failed", freshInputPrepared=False)
        raise


def classify(output, exit_code):
    run = output.get("run") or {}
    summary = run.get("result") or {}
    if not isinstance(summary, dict):
        summary = {}
    probe = summary.get("probe") or {}
    healthy = bool(exit_code == 0 and output.get("ok") is True and run.get("exitCode") == 0
                   and not run.get("timedOut") and summary.get("ok") is True
                   and isinstance(probe, dict) and "evalError" not in probe)
    observed = bool(summary.get("ok") is True and "evalError" not in probe)
    forms = probe.get("forms") if observed else None
    submits = probe.get("submits") if observed else None
    causal = probe.get("causalTrace") if observed and isinstance(probe.get("causalTrace"), list) else []
    kinds = [str(row.get("kind")) for row in causal if isinstance(row, dict)][:64]
    final = probe.get("causalFinal") if observed and isinstance(probe.get("causalFinal"), dict) else {}
    boundaries = []
    for row in summary.get("respLog", []):
        path = str(row.get("path", ""))
        role = "cert-document" if "/cert/" in path else "challenge-fo" if "/fo/" in path else "other"
        host = row.get("hostClass")
        boundaries.append({
            "order": len(boundaries) + 1, "role": role,
            "realm": "page-host" if host == "page" else "challenge-host" if host == "cf" else "unresolved",
            "method": row.get("method") if row.get("method") in ["GET", "POST", "OPTIONS"] else "other",
            "status": row.get("status"), "requestBytes": row.get("reqLen"),
            "responseHeaderBytes": row.get("respLen"), "channelBytes": row.get("chanLen"),
            "protocol": row.get("proto"), "documentDestination": row.get("secDest") == "document",
        })
    cert_post = any(r["role"] == "cert-document" and r["method"] == "POST" for r in boundaries)
    return {
        "harnessHealthy": healthy,
        "businessAccepted": False,
        "businessAcceptanceStatus": "not-proven",
        "forms": forms,
        "submits": submits,
        "causalEventCount": len(kinds) if observed else None,
        "causalKinds": kinds,
        "hasFormCreate": "createElement" in kinds and any(
            isinstance(row, dict) and str(row.get("kind")) == "createElement" and "form" in str(row.get("tag") or row.get("tagShape") or "")
            for row in causal),
        "hasSubmit": any(k in ("submit", "HTMLFormElement.submit") for k in kinds),
        "causalFinalPresent": bool(final),
        "widgetComplete": "complete" in str(probe.get("msgHit", "")).split(","),
        "certDocumentPostObserved": cert_post,
        "requestBoundaryTable": boundaries,
        "limitations": [
            "no new independent business-content readback",
            "urllib-to-Gecko material handoff is not same TLS",
            "older observation hooks retained",
        ],
    }


def run_once(provenance):
    preflight()
    provenance = Path(provenance).resolve()
    assert provenance.is_relative_to(RESTRICTED)
    p = read(provenance)
    out = provenance.parent
    independent_before = {str(name): (ROOT / name).read_bytes() if (ROOT / name).is_file() else None
                          for name in C.INDEPENDENT_RECEIPTS}
    claim_cmd = [str(PY), str(CASE), "diagnostic-causal-observer", "--project", str(ROOT),
                 "--phase", "claim", "--opt-in", "--provenance", str(provenance)]
    claim_result = subprocess.run(claim_cmd, capture_output=True, encoding="utf-8")
    (out / "claim-stdout.json").write_text(claim_result.stdout, encoding="utf-8", newline="\n")
    (out / "claim-stderr.txt").write_text(claim_result.stderr, encoding="utf-8", newline="\n")
    assert claim_result.returncode == 0, "claim rejected; no engine spawned"
    claim = json.loads(claim_result.stdout)
    sidecar = read(ROOT / claim["claimBindingPath"])
    assert sidecar["bindingSha256"] == claim["claimBindingSha256"]
    binding = sidecar["binding"]
    argv = binding["argv"]
    assert "--allow-network" in argv and str(ROOT / C.RUNNER) in argv
    assert str(Path(p["inputPath"])) in argv
    stdout_path, stderr_path = out / "engine-stdout.json", out / "engine-stderr.txt"
    started, pid, code, spawned = None, None, None, False
    launch_error = None
    env = dict(os.environ)
    env["MOZ_FORCE_DISABLE_E10S"] = "1"
    env["MOZ_FORCE_DISABLE_FISSION"] = "1"
    state(status="causal-observer-claimed-not-started", claimId=claim["claimId"],
          wrapperPid=os.getpid(), cliPid=None, enginePid=None, terminal="reserved", onlineExecuted=False)
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            for relative, expected in binding["protectedHashes"].items():
                assert digest(ROOT / relative) == expected
            for relative, expected in binding["runtimeHashes"].items():
                assert digest(REPO / relative) == expected
            assert digest(ROOT / C.RUNNER) == binding["runnerSha256"]
            assert digest(ROOT / C.SOURCE) == binding["sourceStableSha256"]
            assert digest(provenance) == binding["provenanceSha256"]
            assert digest(p["inputPath"]) == p["inputSha256"]
            assert digest(p["sourceReceiptPath"]) == p["sourceReceiptSha256"]
            for artifact in read(p["sourceReceiptPath"])["artifacts"]:
                assert digest(artifact["path"]) == artifact["sha256"]
            for key, value in binding["environment"].items():
                assert env.get(key) == value
            assert datetime.now(timezone.utc) <= datetime.fromisoformat(claim["executeBefore"].replace("Z", "+00:00"))
            child = subprocess.Popen(argv, stdout=stdout, stderr=stderr, env=env,
                                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            started = now()
            pid, spawned = child.pid, True
            state(status="causal-observer-running", sessionId=p["sessionId"], wrapperPid=os.getpid(),
                  cliPid=pid, enginePid=None, terminal="running", onlineExecuted=True, startedAt=started,
                  claimId=claim["claimId"], provenancePath=str(provenance), engineSpawnCount=1)
            code = child.wait()
    except Exception:
        launch_error = "LaunchFailed"
        if not spawned:
            started = None
    finally:
        receipt = {
            "schema": C.SCHEMA_EXECUTION, "claimId": claim["claimId"],
            "claimBindingSha256": claim["claimBindingSha256"], "spawned": spawned, "pid": pid,
            "startedAt": started, "endedAt": now(), "exitCode": code, "argv": argv,
            "stdoutPath": str(stdout_path), "stdoutSha256": digest(stdout_path),
            "stderrPath": str(stderr_path), "stderrSha256": digest(stderr_path),
        }
        receipt_path = out / "execution-receipt.json"
        write(receipt_path, receipt)
        state(status="causal-observer-exited", wrapperPid=None, cliPid=pid, terminal="exited",
              exitCode=code, endedAt=receipt["endedAt"])
    try:
        output = read(stdout_path)
    except Exception:
        output = {}
    result = classify(output, code)
    write(out / "boundary-summary.json", result)
    recorded = subprocess.run(
        [str(PY), str(CASE), "diagnostic-causal-observer", "--project", str(ROOT),
         "--phase", "record", "--opt-in", "--execution-receipt", str(receipt_path)],
        capture_output=True, encoding="utf-8")
    (out / "record-stdout.json").write_text(recorded.stdout, encoding="utf-8", newline="\n")
    (out / "record-stderr.txt").write_text(recorded.stderr, encoding="utf-8", newline="\n")
    independent_after = {str(name): (ROOT / name).read_bytes() if (ROOT / name).is_file() else None
                         for name in C.INDEPENDENT_RECEIPTS}
    assert independent_before == independent_after
    state(status="causal-observer-recorded" if recorded.returncode == 0 else "causal-observer-record-failed",
          boundarySummaryPath=str(out / "boundary-summary.json"), harnessHealthy=result["harnessHealthy"],
          businessAccepted=False, causalEventCount=result.get("causalEventCount"),
          forms=result.get("forms"), submits=result.get("submits"), launchErrorType=launch_error)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["preflight", "fetch", "run"])
    parser.add_argument("--provenance", type=Path)
    args = parser.parse_args()
    if args.phase == "preflight":
        print(json.dumps(preflight()))
    elif args.phase == "fetch":
        print(json.dumps({"provenancePath": str(fetch_fresh())}))
    else:
        assert args.provenance, "provenance required"
        print(json.dumps(run_once(args.provenance)))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({"ok": False, "errorType": "WrapperFailed"}))
        sys.exit(1)
