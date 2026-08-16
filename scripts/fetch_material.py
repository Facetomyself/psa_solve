# -*- coding: utf-8 -*-
"""抓取新鲜 CF 挑战材料：403 页 + orchestrate JS + __cf_bm cookie。

输出到 challenge-material/<epoch>/，并打印摘要。

代理（可选，环境变量）：
  CF_PROXY      Cliproxy 代理 URL（http://user:pass@host:port）
  CF_PRE_PROXY  socks5 隧道（如 ssh -D，级联到代理网关）
  CF_TARGET_URL 目标页面 URL

材料抓取刻意使用非浏览器 TLS（curl_cffi 不带 impersonate）——触发 CF 挑战 403。
"""
import json
import os
import re
from datetime import datetime

from curl_cffi import requests as cr
from curl_cffi.const import CurlOpt

BASE = r"D:\reverse_ENV\workspace\psa_solve\challenge-material"
TARGET = os.environ.get("CF_TARGET_URL", "https://www.psacard.com/cert/143963534/psa")
PROXY = os.environ.get("CF_PROXY", "")
PRE_PROXY = os.environ.get("CF_PRE_PROXY", "")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) "
      "Gecko/20100101 Firefox/140.0")


def curl_kwargs():
    kw = {"timeout": 30, "allow_redirects": False}
    if PROXY:
        kw["proxy"] = PROXY
        opts = {}
        if PRE_PROXY:
            opts[CurlOpt.PRE_PROXY] = PRE_PROXY
        if opts:
            kw["curl_options"] = opts
    return kw


def fetch(url, headers=None):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    r = cr.get(url, headers=h, **curl_kwargs())
    cookies = []
    raw_sc = r.headers.get("set-cookie", "")
    if raw_sc:
        # curl_cffi 合并多个 Set-Cookie 为逗号串
        cookies = [c.strip() for c in raw_sc.split(",") if "=" in c]
    return r.status_code, dict(r.headers), cookies, r.content


def main():
    epoch = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = os.path.join(BASE, epoch)
    os.makedirs(outdir, exist_ok=True)
    print(f"[epoch] {epoch} -> {outdir}")
    if PROXY:
        print(f"[proxy] enabled (pre-proxy: {PRE_PROXY or 'direct'})")

    # 1. 403 page
    st, hdrs, cookies, body = fetch(TARGET)
    print(f"[page] HTTP {st}, {len(body)} bytes, {len(cookies)} set-cookies")
    html = body.decode("utf-8", errors="replace")
    page_path = os.path.join(outdir, "challenge-page.html")
    open(page_path, "w", encoding="utf-8").write(html)

    # 2. parse orchestrate URL + cH + cRay
    m = re.search(r"\.src = '([^']*orchestrate[^']*)'", html)
    if not m:
        m = re.search(r'src = "([^"]*orchestrate[^"]*)"', html)
    orch_rel = m.group(1) if m else None
    cH = re.search(r"cH: '([^']*)'", html)
    cRay = re.search(r"cRay: '([^']*)'", html)
    print(f"[orchestrate] rel={orch_rel}")
    print(f"[cH] {cH.group(1)[:30] if cH else '?'}... [cRay] {cRay.group(1) if cRay else '?'}")

    if orch_rel:
        orch_url = "https://www.psacard.com" + orch_rel
        st2, h2, c2, ob = fetch(orch_url, headers={"Referer": TARGET})
        print(f"[orchestrate-js] HTTP {st2}, {len(ob)} bytes")
        open(os.path.join(outdir, "chl-page-orchestrate.js"), "wb").write(ob)
    else:
        print("[orchestrate-js] NOT FOUND in page — inspect manually")

    # 3. save manifest
    cf_bm = [c for c in cookies if c.startswith("__cf_bm=")]
    summary = {
        "epoch": epoch,
        "url": TARGET,
        "httpStatus": st,
        "setCookies": cookies,
        "cfBm": cf_bm,
        "orchestrateRel": orch_rel,
        "cH": cH.group(1) if cH else None,
        "cRay": cRay.group(1) if cRay else None,
        "savedAt": datetime.now().isoformat(),
    }
    json.dump(summary, open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8"),
              indent=1, ensure_ascii=False)
    print(f"[manifest] {os.path.join(outdir, 'manifest.json')}")
    print("[done]")


if __name__ == "__main__":
    main()
