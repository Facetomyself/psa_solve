# -*- coding: utf-8 -*-
"""bridge 冒烟：本地 mock server 验证 CF_CAPTURE_ONLY 管道协议（不碰真实站点）。

流程：mock_orch.js 发两轮 XHR（POST /fo + GET /after），capture 分支把 request
输出 stdout，Python 转发到本地 mock server，envelope 回灌 stdin，验证：
  - runtime_request 输出与字段完整
  - 回灌后 JS 事件链推进（第二轮请求发出 = onload 被触发）
  - set-cookie 回灌 -> __captureHasClearance -> result.hasClearance=true
跑完自动清理临时目录。
"""
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = r"D:\reverse_ENV\workspace\psa_solve"
NODE = r"D:\reverse_ENV\tools\node\node.exe"
TMP = os.path.join(ROOT, "tmp_bridge_smoke")
os.makedirs(TMP, exist_ok=True)

PORT = 48081
FO_COUNT = {"n": 0}


class MockHandler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _reply(self):
        body = b"ok-material" * 100
        if self.path == "/fo":
            FO_COUNT["n"] += 1
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=UTF-8")
            self.send_header("Set-Cookie", "cf_clearance=smoke-clearance; path=/; Secure")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/after":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"after-ok")
        else:
            self.send_response(404)
            self.end_headers()

    do_POST = _reply
    do_GET = _reply


def main():
    srv = HTTPServer(("127.0.0.1", PORT), MockHandler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    page = os.path.join(TMP, "mock_page.html")
    open(page, "w", encoding="utf-8").write(
        "<script>window._cf_chl_opt = {cHash: \"x\", cRay: \"y\"};</script>")
    orch = os.path.join(TMP, "mock_orch.js")
    open(orch, "w", encoding="utf-8").write(f"""
var xhr = new XMLHttpRequest();
// 第一轮用相对 URL：capture 分支必须按 target origin 解析为绝对地址
xhr.open("POST", "/fo");
xhr.setRequestHeader("Content-Type", "text/plain;charset=UTF-8");
xhr.onload = function() {{
  if (xhr.status === 200) {{
    var c = new XMLHttpRequest();
    c.open("GET", "http://127.0.0.1:{PORT}/after");
    c.onload = function() {{}};
    c.send();
  }}
}};
xhr.send("fo-body-smoke");
""")

    env = dict(os.environ)
    env["CF_CAPTURE_ONLY"] = "1"
    env["CF_TARGET_URL"] = f"http://127.0.0.1:{PORT}/cert/1/psa"
    proc = subprocess.Popen(
        [NODE, os.path.join(ROOT, "runtime", "run.js"), page, orch, "__cf_bm=smokebm"],
        stdout=subprocess.PIPE, stdin=subprocess.PIPE,
        text=True, encoding="utf-8", env=env)

    requests_seen = []
    result = None
    deadline = time.time() + 60
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if msg.get("type") == "runtime_request":
            requests_seen.append(msg)
            print(f"[bridge] {msg['request_id']} {msg['method']} {msg['url']} "
                  f"body={msg.get('body','')[:30]!r}")
            import urllib.request
            req = urllib.request.Request(
                msg["url"], data=msg.get("body", "").encode() if msg.get("body") else None,
                method=msg["method"])
            resp = urllib.request.urlopen(req, timeout=10)
            raw = resp.read()
            sc = resp.headers.get("Set-Cookie", "")
            envelope = {
                "type": "response",
                "request_id": msg["request_id"],
                "status": resp.status,
                "headers": {"content-type": resp.headers.get("Content-Type", "")},
                "set_cookies": [c.strip() for c in sc.split(",") if "=" in c.strip()],
                "body": raw.decode("utf-8", errors="replace"),
            }
            proc.stdin.write(json.dumps(envelope, ensure_ascii=False) + "\n")
            proc.stdin.flush()
        elif msg.get("type") == "result":
            result = msg
            break
    proc.stdin.close()
    try:
        proc.wait(timeout=10)
    except Exception:
        proc.kill()
    srv.shutdown()

    ok = True
    checks = []
    checks.append(("runtime_request 两轮", len(requests_seen) == 2))
    checks.append(("第一轮 POST /fo body 完整", requests_seen and
                   requests_seen[0]["body"] == "fo-body-smoke"))
    checks.append(("相对 URL 已解析为绝对地址", requests_seen and
                   requests_seen[0]["url"] == f"http://127.0.0.1:{PORT}/fo"))
    checks.append(("第二轮 GET /after（onload 事件链推进）", len(requests_seen) == 2 and
                   requests_seen[1]["method"] == "GET"))
    checks.append(("result.hasClearance", bool(result and result.get("hasClearance"))))
    checks.append(("requestCount=2", bool(result and result.get("requestCount") == 2)))
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
        ok = ok and passed

    # 清理临时目录
    import shutil
    shutil.rmtree(TMP, ignore_errors=True)
    print("SMOKE_" + ("OK" if ok else "FAILED"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
