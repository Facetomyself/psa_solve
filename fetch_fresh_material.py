# -*- coding: utf-8 -*-
"""抓取新鲜 CF 挑战材料：403 页 + orchestrate JS + __cf_bm cookie。

输出到 challenge-material/<epoch>/，并打印摘要。
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime

BASE = r"D:\reverse_ENV\workspace\psa_solve\challenge-material"
TARGET = "https://www.psacard.com/cert/143963534/psa"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) "
      "Gecko/20100101 Firefox/140.0")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, headers=None, timeout=25):
    h = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    opener = urllib.request.build_opener(NoRedirect)
    try:
        resp = opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        # 403 challenge 页是预期响应
        cookies = e.headers.get_all("Set-Cookie") or []
        return e.code, dict(e.headers), cookies, e.read()
    body = resp.read()
    cookies = resp.headers.get_all("Set-Cookie") or []
    return resp.status, dict(resp.headers), cookies, body


def main():
    epoch = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = BASE + "\\" + epoch
    import os
    os.makedirs(outdir, exist_ok=True)
    print(f"[epoch] {epoch} -> {outdir}")

    # 1. 403 page
    st, hdrs, cookies, body = fetch(TARGET)
    print(f"[page] HTTP {st}, {len(body)} bytes, {len(cookies)} set-cookies")
    html = body.decode("utf-8", errors="replace")
    page_path = outdir + "\\challenge-page.html"
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
        open(outdir + "\\chl-page-orchestrate.js", "wb").write(ob)
    else:
        print("[orchestrate-js] NOT FOUND in page — inspect manually")

    # 3. save cookies (__cf_bm etc.)
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
    json.dump(summary, open(outdir + "\\manifest.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"[manifest] {outdir}\\manifest.json")
    print("[done]")


if __name__ == "__main__":
    main()
