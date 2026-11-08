# -*- coding: utf-8 -*-
"""One live rerun of the click-install runner copy.

Does not claim diagnostic-causal-observer and does not modify the reviewed runner.
Stdout of this process is a redacted measurement. Raw engine output stays under evidence/.
"""
from __future__ import annotations

import hashlib
import http.cookiejar
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import uuid
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPCookieProcessor, HTTPErrorProcessor, Request, build_opener

ROOT = Path(r"D:\reverse_ENV\workspace\psa_solve")
REPO = Path(r"D:\reverse_ENV")
NODE = REPO / "tools/node/node.exe"
CLI = REPO / "mcp/ruyidom-mcp/dist/cli.js"
RUNNER = ROOT / "diagnostics/click-install-20261003/ruyidom_bridge.click-install.js"
BASE = ROOT / "evidence/web/click-install-20261003/restricted"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Keep(HTTPErrorProcessor):
    def http_response(self, request, response):
        return response

    https_response = http_response


def parse_orchestrate(html, page_url):
    import re
    match = re.search(r"(/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1[^\"'<>\s]*)", html)
    if not match:
        raise RuntimeError("fresh page has no orchestrate URL")
    result = urljoin(page_url, match.group(1))
    if urlparse(result).netloc != urlparse(page_url).netloc:
        raise RuntimeError("orchestrate host mismatch")
    return result


def fetch(out, target):
    jar = http.cookiejar.CookieJar()
    opener = build_opener(Keep(), HTTPCookieProcessor(jar))
    cookie_lines = []

    def get(url):
        request = Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        with opener.open(request, timeout=30) as response:
            body = response.read()
            cookie_lines.extend(response.headers.get_all("Set-Cookie") or [])
            return response.status, body

    status, html = get(target)
    if status != 403 or len(html) < 100:
        raise RuntimeError("fresh challenge status=%s bytes=%s" % (status, len(html)))
    orch = parse_orchestrate(html.decode("utf-8", "strict"), target)
    status2, script = get(orch)
    if status2 != 200 or len(script) < 1000:
        raise RuntimeError("fresh orchestrate status=%s bytes=%s" % (status2, len(script)))
    if not cookie_lines:
        raise RuntimeError("fresh cookie jar empty")
    (out / "challenge.html").write_bytes(html)
    (out / "orchestrate.js").write_bytes(script)
    (out / "cookies.txt").write_text("\n".join(cookie_lines) + "\n", encoding="utf-8", newline="\n")
    input_path = out / "fresh-input.json"
    input_path.write_text(json.dumps({
        "challengeHtmlPath": str(out / "challenge.html"),
        "orchestrateJsPath": str(out / "orchestrate.js"),
        "challengeUrl": target,
        "pumpMs": 30000,
        "patchHistory": True,
        "liveNetwork": True,
        "cookieFile": str(out / "cookies.txt"),
        "tracePath": str(out / "bridge-live.jsonl"),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return input_path, status, len(html), status2, len(script), len(cookie_lines)


def measure(output):
    run = output.get("run") or {}
    summary = run.get("result") if isinstance(run.get("result"), dict) else {}
    probe = summary.get("probe") if isinstance(summary.get("probe"), dict) else {}
    ring = summary.get("lookupRing") if isinstance(summary.get("lookupRing"), list) else []
    click_ring = [str(item) for item in ring if str(item).startswith("click:") or str(item).startswith("ptr:")]
    fo = []
    cert = False
    for row in summary.get("respLog") or []:
        if not isinstance(row, dict):
            continue
        path = str(row.get("path") or "")
        method = row.get("method")
        role = "cert-document" if "/cert/" in path else "challenge-fo" if "/fo/" in path else "other"
        if role == "cert-document" and method == "POST":
            cert = True
        if role != "challenge-fo":
            continue
        fo.append({
            "hostClass": row.get("hostClass"),
            "method": method,
            "status": row.get("status"),
            "reqLen": row.get("reqLen"),
            "contentType": row.get("contentType"),
            "setCookieNames": row.get("setCookieNames") if isinstance(row.get("setCookieNames"), list) else [],
        })
    chl = str(probe.get("chlOut") or "")
    chl_class = chl.split(":", 1)[0] if chl else ""
    return {
        "engineOk": output.get("ok"),
        "runExit": run.get("exitCode"),
        "timedOut": run.get("timedOut"),
        "clickRing": click_ring,
        "clickErr": probe.get("clickErr"),
        "clickArm": probe.get("clickArm"),
        "msgHit": probe.get("msgHit"),
        "chlClass": chl_class,
        "chlAlpha": probe.get("chlAlpha"),
        "forms": probe.get("forms"),
        "submits": probe.get("submits"),
        "fo": fo,
        "certDocumentPost": cert,
    }


def main():
    target = json.loads((ROOT / "diagnostics/bridge-input.json").read_text(encoding="utf-8"))["challengeUrl"]
    session = uuid.uuid4().hex
    out = BASE / session
    out.mkdir(parents=True, exist_ok=False)
    input_path, page_status, page_bytes, orch_status, orch_bytes, cookie_count = fetch(out, target)
    env = os.environ.copy()
    env["MOZ_FORCE_DISABLE_E10S"] = "1"
    env["MOZ_FORCE_DISABLE_FISSION"] = "1"
    proc = subprocess.run(
        [str(NODE), str(CLI), "run", "--script", str(RUNNER), "--input-file", str(input_path),
         "--timeout-seconds", "120", "--allow-network"],
        cwd=str(REPO),
        env=env,
        capture_output=True,
        timeout=150,
    )
    (out / "engine-stdout.json").write_bytes(proc.stdout)
    (out / "engine-stderr.txt").write_bytes(proc.stderr)
    parsed = {}
    try:
        parsed = json.loads(proc.stdout.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        parsed = {}
    redacted = measure(parsed)
    redacted.update({
        "sessionId": session,
        "wrapperExit": proc.returncode,
        "pageStatus": page_status,
        "pageBytes": page_bytes,
        "orchestrateStatus": orch_status,
        "orchestrateBytes": orch_bytes,
        "cookieLineCount": cookie_count,
        "runnerSha256": hashlib.sha256(RUNNER.read_bytes()).hexdigest(),
        "endedAt": now(),
    })
    (out / "measure.json").write_text(json.dumps(redacted, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"measure": str(out / "measure.json"), "sessionId": session}, ensure_ascii=False))


if __name__ == "__main__":
    main()
