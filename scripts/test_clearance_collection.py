# -*- coding: utf-8 -*-
"""验证 cf_clearance 能否支撑持续采集：
sticky 出口拿 clearance -> 同出口同指纹连续请求多个页面 -> 统计 200/403。

用法：python test_clearance_collection.py [--count 20]
前置：ssh -N -D 127.0.0.1:18081 oracle-newapi-primary
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import quote

from curl_cffi import requests as cr
from curl_cffi.const import CurlOpt

ROOT = r"D:\reverse_ENV\workspace\psa_solve"
NODE = r"D:\reverse_ENV\tools\node\node.exe"
RUNTIME_DIR = os.path.join(ROOT, "runtime")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
MATERIAL_ROOT = os.path.join(ROOT, "challenge-material")
PRE_PROXY = "socks5h://127.0.0.1:18081"


def load_cliproxy():
    cfg = {}
    for line in open(r"D:\reverse_ENV\skill\proxy-usage\.env", encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    base = cfg.get("CLIPROXY_USER", "")
    password = cfg.get("CLIPROXY_PASS", "")
    host = cfg.get("CLIPROXY_HOST", "us.arxlabs.io")
    port = cfg.get("CLIPROXY_PORT", "3010")
    # sticky：固定 sid + t-30（30 分钟同出口）——clearance 与出口 IP 绑定
    sticky_account = f"{base}-region-Rand-sid-colltest1-t-30"
    proxy = f"http://{quote(sticky_account, safe='')}:{quote(password, safe='')}@{host}:{port}"
    return proxy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()

    proxy = load_cliproxy()
    curl_kw = {"proxy": proxy, "curl_options": {CurlOpt.PRE_PROXY: PRE_PROXY},
               "timeout": 30, "impersonate": "firefox"}

    # 1. 确认 sticky 出口 IP
    ip1 = cr.get("https://api.ipify.org", **curl_kw).text.strip()
    print(f"[sticky] 出口 IP: {ip1}")

    # 2. 材料抓取（非浏览器 TLS 经同出口触发 403）
    env = dict(os.environ)
    env["CF_PROXY"] = proxy
    env["CF_PRE_PROXY"] = PRE_PROXY
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS_DIR, "fetch_material.py")],
                       env=env, capture_output=True, text=True, timeout=90)
    epochs = [d for d in os.listdir(MATERIAL_ROOT)
              if os.path.isfile(os.path.join(MATERIAL_ROOT, d, "manifest.json"))]
    epoch = sorted(epochs)[-1]
    m = json.load(open(os.path.join(MATERIAL_ROOT, epoch, "manifest.json"), encoding="utf-8"))
    bm = m["cfBm"][0].split(";")[0]
    print(f"[material] epoch={epoch} ray={m['cRay']}")

    # 3. Node 求解（直连产载荷——TLS 无关）
    r = subprocess.run(
        [NODE, os.path.join(RUNTIME_DIR, "run.js"),
         os.path.join(MATERIAL_ROOT, epoch, "challenge-page.html"),
         os.path.join(MATERIAL_ROOT, epoch, "chl-page-orchestrate.js"), bm],
        capture_output=True, text=True, timeout=120)
    result = None
    for line in r.stdout.strip().splitlines():
        if line.strip().startswith("{"):
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                pass
    if not result or not result.get("submits"):
        print("[solve] 失败", r.stderr[:200])
        sys.exit(1)
    last = result["submits"][-1]
    url = last["url"]
    if url.startswith("/"):
        url = "https://www.psacard.com" + url
    print(f"[solve] submits={len(result['submits'])} bodyLen={last['bodyLen']}")

    # 4. curl_cffi Firefox 指纹经 sticky 出口提交 -> clearance
    ff_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0",
        "Accept": "*/*",
        "Content-Type": "text/plain",
    }
    ck = {"__cf_bm": bm.split("=", 1)[1]}
    r = cr.post(url, data=last["fullBody"], headers=ff_headers, cookies=ck, **curl_kw)
    clearance = ""
    for part in (r.headers.get("set-cookie", "") or "").split(","):
        part = part.strip()
        if part.startswith("cf_clearance="):
            clearance = part.split(";")[0]
        if part.startswith("__cf_bm="):
            ck["__cf_bm"] = part.split(";")[0].split("=", 1)[1]
    if not clearance:
        print("[clearance] 未获取（提交被拒）status=", r.status_code)
        sys.exit(1)
    ck["cf_clearance"] = clearance.split("=", 1)[1]
    print(f"[clearance] 获取成功 {clearance[:30]}...")

    # 5. 持续采集测试：同出口同指纹同 cookie 连续请求 N 个页面
    page_headers = {
        "User-Agent": ff_headers["User-Agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    stats = {}
    print(f"[collect] 连续请求 {args.count} 个页面...")
    for i in range(args.count):
        sn = 143963534 + i * 7
        u = f"https://www.psacard.com/cert/{sn}/psa"
        try:
            resp = cr.get(u, headers=page_headers, cookies=ck, **curl_kw)
            code = resp.status_code
            title_m = re.search(rb"<title>([^<]*)</title>", resp.content[:3000])
            title = title_m.group(1).decode("utf-8", "replace") if title_m else ""
            chl = "Just a moment" in title
            key = "403-challenge" if (code == 403 or chl) else str(code)
        except Exception as e:
            key = f"err:{str(e)[:30]}"
        stats[key] = stats.get(key, 0) + 1
        print(f"  [{i+1}/{args.count}] {u.split('/cert/')[1]} -> {key}", flush=True)
        time.sleep(0.3)

    # 6. 出口一致性复核
    ip2 = cr.get("https://api.ipify.org", **curl_kw).text.strip()
    print(f"\n[result] 采集统计: {stats}")
    print(f"[sticky] 出口一致性: {ip1} -> {ip2} {'一致' if ip1 == ip2 else '不一致(轮换)'}")
    ok_count = stats.get("200", 0)
    print(f"[conclusion] clearance 持续采集成功率: {ok_count}/{args.count} "
          f"({'可行' if ok_count >= args.count * 0.8 else '不稳定'})")


if __name__ == "__main__":
    main()
