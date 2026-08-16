# -*- coding: utf-8 -*-
"""
demo.py — PSA CF 5s 盾 vanilla Node 补环境一键 Demo

用法：
  python demo.py                 # 用最新已抓材料求解 + 验证
  python demo.py --fresh         # 实时抓取新鲜挑战材料再求解
  python demo.py --no-verify     # 只求解不验证

流程：材料发现 -> vanilla Node 补环境求解（含真实提交）-> 提取 cf_clearance -> 验证。
运行时：vanilla Node（tools/node/node.exe），无 RuyiDOM/浏览器依赖。
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime

from curl_cffi import requests as curl_requests
from curl_cffi.const import CurlOpt

ROOT = r"D:\reverse_ENV\workspace\psa_solve"
RUNTIME_DIR = os.path.join(ROOT, "runtime")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
MATERIAL_ROOT = os.path.join(ROOT, "challenge-material")
NODE = r"D:\reverse_ENV\tools\node\node.exe"
PYTHON = r"D:\reverse_ENV\.venv\Scripts\python.exe"
TARGET_URL = "https://www.psacard.com/cert/143963534/psa"

# TLS 指纹是关键变量（Node TLS 被 CF 拒、Firefox 指纹放行——curl_cffi impersonate）
IMPERSONATE = "firefox"


def log(msg, level="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    tag = {"info": " .. ", "ok": " OK ", "bad": " !! ", "step": ">>> "}[level]
    print(f"[{ts}] {tag}{msg}")


def find_latest_material():
    epochs = [
        d for d in os.listdir(MATERIAL_ROOT)
        if os.path.isfile(os.path.join(MATERIAL_ROOT, d, "manifest.json"))
    ]
    if not epochs:
        raise RuntimeError("无材料：先运行 scripts/fetch_material.py（需触发挑战的 IP）")
    epochs.sort(reverse=True)
    latest = os.path.join(MATERIAL_ROOT, epochs[0])
    manifest = json.load(open(os.path.join(latest, "manifest.json"), encoding="utf-8"))
    return latest, manifest


def fetch_fresh_material():
    log("实时抓取挑战材料（需当前 IP 会触发 CF 挑战）", "step")
    r = subprocess.run(
        [PYTHON, os.path.join(SCRIPTS_DIR, "fetch_material.py")],
        capture_output=False,
    )
    if r.returncode != 0:
        raise RuntimeError("材料抓取失败")


def load_cliproxy_env():
    """从 skill/proxy-usage/.env 读 Cliproxy 账密，拼 Rand（机房）账号 + 级联隧道。"""
    env_path = r"D:\reverse_ENV\skill\proxy-usage\.env"
    cfg = {}
    try:
        for line in open(env_path, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    except OSError:
        return None, None
    base = cfg.get("CLIPROXY_USER", "")
    password = cfg.get("CLIPROXY_PASS", "")
    host = cfg.get("CLIPROXY_HOST", "us.arxlabs.io")
    port = cfg.get("CLIPROXY_PORT", "3010")
    if not base or not password:
        return None, None
    rand_account = f"{base}-region-Rand"
    from urllib.parse import quote
    proxy = f"http://{quote(rand_account, safe='')}:{quote(password, safe='')}@{host}:{port}"
    pre_proxy = ARGS.pre_proxy or "socks5h://127.0.0.1:18081"
    return proxy, pre_proxy


def build_env():
    env = dict(os.environ)
    env["CF_TARGET_URL"] = ARGS.url
    if ARGS.ua:
        env["CF_USER_AGENT"] = ARGS.ua
    if ARGS.referer:
        env["CF_REFERER"] = ARGS.referer
    if ARGS.cliproxy_rand:
        proxy, pre_proxy = load_cliproxy_env()
        if proxy:
            env["CF_PROXY"] = proxy
            if pre_proxy:
                env["CF_PRE_PROXY"] = pre_proxy
    return env


def run_node_solve(page_path, orch_path, cookie):
    log("vanilla Node 补环境求解（orchestrate 执行 + 真实提交）", "step")
    r = subprocess.run(
        [NODE, os.path.join(RUNTIME_DIR, "run.js"), page_path, orch_path, cookie],
        capture_output=True, text=True, timeout=120, env=build_env(),
    )
    result = None
    for line in r.stdout.strip().splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                result = json.loads(line)
            except json.JSONDecodeError:
                continue
    if result is None:
        raise RuntimeError(f"Node 求解无输出：stderr={r.stderr[:300]}")
    return result


def main():
    global ARGS
    parser = argparse.ArgumentParser(description="PSA CF 5s 盾 vanilla Node 补环境 Demo")
    parser.add_argument("--fresh", action="store_true", help="强制拉取新材料")
    parser.add_argument("--use-cached", action="store_true", help="使用缓存材料（跳过自动拉新）")
    parser.add_argument("--no-verify", action="store_true", help="只求解不验证")
    parser.add_argument("--url", default=TARGET_URL, help="目标页面 URL（复用其他目标时指定）")
    parser.add_argument("--ua", default=None, help="User-Agent（默认 Firefox 140）")
    parser.add_argument("--referer", default=None, help="Referer（默认等于页面 URL）")
    parser.add_argument("--cliproxy-rand", action="store_true",
                        help="经 Cliproxy Rand（机房 IP）链路：材料抓取 + 提交 + 验证")
    parser.add_argument("--pre-proxy", default=None,
                        help="socks5 级联隧道（默认 socks5h://127.0.0.1:18081）")
    ARGS = parser.parse_args()
    args = ARGS

    # 1. 材料：默认自动拉新（材料缺失或超过时效窗口）
    latest, manifest = find_latest_material()
    age_min = 0
    if manifest.get("savedAt"):
        try:
            age_min = (datetime.now() - datetime.fromisoformat(manifest["savedAt"])).total_seconds() / 60
        except ValueError:
            pass
    if args.fresh or (not args.use_cached and age_min > 5):
        if args.fresh:
            log("强制拉取新材料", "step")
        else:
            log(f"最新材料已过时效窗口（{age_min:.0f} 分钟），自动拉新", "step")
        fetch_fresh_material()
        latest, manifest = find_latest_material()
        age_min = 0

    log("挑战材料", "step")
    page_path = os.path.join(latest, "challenge-page.html")
    orch_path = os.path.join(latest, "chl-page-orchestrate.js")
    if manifest.get("httpStatus") != 403 or not os.path.isfile(orch_path):
        log(f"材料无效（httpStatus={manifest.get('httpStatus')}）——当前 IP 可能不触发 CF 挑战（直通 200）", "bad")
        log("需要会触发挑战的 IP 再运行；换 IP 后重跑本命令", "bad")
        sys.exit(1)
    cookie = manifest.get("cfBm", [""])[0].split(";")[0] if manifest.get("cfBm") else ""
    log(f"epoch={os.path.basename(latest)}  ray={manifest.get('cRay')}  age={age_min:.0f}min")

    # 2. Node 求解（Node XHR 在求解过程中真实发送 fo 提交）
    result = run_node_solve(page_path, orch_path, cookie)
    submits = result.get("submits", [])
    errors = result.get("errors", [])
    log(f"JS 错误数 = {len(errors)}")
    for e in errors[:3]:
        log(f"{e.get('stage')}: {e.get('message', '')[:100]}", "bad")
    log(f"捕获提交数 = {len(submits)}")
    for s in submits:
        log(f"{s['method']} {s['url'][:100]}...  bodyLen={s['bodyLen']}")

    # 3. 提取 Node 求解响应下发的 cf_clearance 与轮换 __cf_bm（Node XHR 已真实提交一轮）
    clearance = ""
    bm_new = ""
    for r in result.get("responses", []):
        sc = r.get("setCookie", "")
        for part in sc.split(","):
            part = part.strip()
            if part.startswith("cf_clearance="):
                clearance = part.split(";")[0]
            if part.startswith("__cf_bm="):
                bm_new = part.split(";")[0]

    # 4. 提交 + 验证（curl_cffi Firefox TLS 指纹——Node TLS 被 CF 拒的关键变量）
    if args.no_verify:
        if clearance:
            log(f"cf_clearance={clearance[13:53]}...（Node XHR 提交响应）")
        log("跳过验证（--no-verify）")
        sys.exit(0)
    log("curl_cffi（Firefox TLS 指纹）提交 + 验证", "step")

    ff_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:155.0) Gecko/20100101 Firefox/155.0",
        "Accept": "*/*",
        "Content-Type": "text/plain",
    }
    page_headers = {
        "User-Agent": ff_headers["User-Agent"],
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    def demo_curl_kwargs():
        kw = {"timeout": 30, "impersonate": IMPERSONATE}
        if ARGS.cliproxy_rand:
            proxy, pre_proxy = load_cliproxy_env()
            if proxy:
                kw["proxy"] = proxy
                if pre_proxy:
                    kw["curl_options"] = {CurlOpt.PRE_PROXY: pre_proxy}
        return kw

    bm_value = bm_new.split("=", 1)[1] if bm_new else cookie.split("=", 1)[1]
    ck = {"__cf_bm": bm_value}

    # 用完整载荷（第二轮 fo）经 curl_cffi 发送
    last = submits[-1] if submits else None
    if last and last.get("fullBody"):
        url = last["url"]
        if url.startswith("/"):
            url = "https://www.psacard.com" + url
        r = curl_requests.post(url, data=last["fullBody"], headers=ff_headers, cookies=ck,
                               **demo_curl_kwargs())
        log(f"fo 提交：HTTP {r.status_code}  cf-chl-out={'有' if r.headers.get('cf-chl-out') else '无'}")
        sc = r.headers.get("set-cookie", "") or ""
        for part in sc.split(","):
            part = part.strip()
            if part.startswith("cf_clearance="):
                clearance = part.split(";")[0]
            if part.startswith("__cf_bm="):
                ck["__cf_bm"] = part.split(";")[0].split("=", 1)[1]

    if not clearance:
        log("未获取 cf_clearance（提交被拒或材料过期）", "bad")
        sys.exit(1)
    ck["cf_clearance"] = clearance.split("=", 1)[1]
    log(f"cf_clearance={clearance[13:53]}...")

    # 验证（curl_cffi 同指纹 + 内容校验防空壳假 200）
    r2 = curl_requests.get(args.url, headers=page_headers, cookies=ck, **demo_curl_kwargs())
    content = r2.content
    head = content[:4000]
    title_m = __import__("re").search(rb"<title>([^<]*)</title>", content)
    title = title_m.group(1).decode("utf-8", "replace").strip() if title_m else ""
    # 真实页面判定：HTTP 200 + 非挑战页 title + 体量 > 50KB
    # （挑战页恒定 "Just a moment..." + ~5.6KB；空壳 200 约 3KB）
    is_challenge = "Just a moment" in title or b"challenge-platform" in head
    is_real = r2.status_code == 200 and not is_challenge and len(content) > 50000
    log(f"HTTP {r2.status_code}  size={len(content):,}  title={title[:50] or '(无)'}")

    if is_real:
        log("内容校验通过：真实页面（非挑战页）", "ok")
        log("serverAccepted = TRUE", "ok")
    else:
        if r2.status_code != 200:
            log("HTTP 非 200", "bad")
        elif is_challenge:
            log("内容校验失败：返回的是挑战页（clearance 未生效）", "bad")
        else:
            log("内容校验失败：页面特征不符（空壳或异常响应）", "bad")
        log("serverAccepted = FALSE（时效/IP 信誉/载荷被拒）", "bad")
        sys.exit(1)


if __name__ == "__main__":
    main()
