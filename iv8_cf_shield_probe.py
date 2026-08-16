# -*- coding: utf-8 -*-
"""iv8 对照：403 挑战页 + orchestrate 离线执行，观察缺口与提交请求。

按 iv8-rapid-verifier 纪律：offline bundle 模型，输出 pointer-only 摘要。
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import iv8

ROOT = Path(__file__).resolve().parent
MATERIAL = ROOT / "challenge-material"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def run() -> dict:
    challenge_html = (MATERIAL / "challenge-page-fresh.html").read_text(encoding="utf-8")
    orchestrate_js = (MATERIAL / "chl-page-orchestrate-fresh.js").read_text(encoding="utf-8")
    challenge_url = "https://www.psacard.com/cert/143963534/psa"
    import re as _re
    ray_match = _re.search(r"cRay: '([^']+)'", challenge_html)
    ray = ray_match.group(1) if ray_match else "unknown"
    orchestrate_url = (
        "https://www.psacard.com/cdn-cgi/challenge-platform/h/g/orchestrate/"
        f"chl_page/v1?ray={ray}"
    )

    env = {
        "navigator": {
            "userAgent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"),
            "platform": "Win32",
            "language": "en-US",
            "languages": ["en-US", "en"],
        },
        "screen": {"width": 1920, "height": 1080, "availWidth": 1920, "availHeight": 1040},
        "window": {"innerWidth": 1920, "innerHeight": 947},
        "location": {"href": challenge_url},
    }

    with iv8.JSContext(environment=env, time_mode="logical") as ctx:
        # createElementNS 桩：iv8 DOM 仿真缺该方法，orchestrate 用
        # createElementNS(ns, tag) 创建 CF 指纹 DOM 元素。
        ctx.eval(
            "if(typeof document.createElementNS !== 'function'){"
            "document.createElementNS = function(ns, tag){"
            "  var el = document.createElement(tag); return el;"
            "};}"
        )
        # 与 RuyiDOM 同款插桩：case 进度 + PJ 入口（对照两环境分叉点）
        import re as _re2
        orchestrate_js_probed = _re2.sub(
            r"case`(\d+)`:", r"case`\1`:window.__ruyiCaseNow=\1;", orchestrate_js
        )
        orchestrate_js_probed = orchestrate_js_probed.replace(
            "function PJ(Z,J,DN,X5,IV,Ip,Ii,Ia){(DN={Z:2121",
            "function PJ(Z,J,DN,X5,IV,Ip,Ii,Ia){window.__ruyiPJ=typeof J+','+String(J).slice(0,100);(DN={Z:2121",
        )
        snapshot = {
            "baseURL": challenge_url,
            "html": challenge_html,
            "resources": {
                orchestrate_url: {
                    "body": orchestrate_js_probed,
                    "status": 200,
                    "headers": [["content-type", "text/javascript"]],
                }
            },
        }
        snapshot = {
            "baseURL": challenge_url,
            "html": challenge_html,
            "resources": {
                orchestrate_url: {
                    "body": orchestrate_js,
                    "status": 200,
                    "headers": [["content-type", "text/javascript"]],
                }
            },
        }
        load_result = ctx.eval(
            "window.__iv8__.page.load(" + json.dumps(snapshot) + ")", to_py=True
        )
        # 推进事件循环（挑战求解 + 提交）
        for _ in range(6):
            ctx.eval("window.__iv8__.eventLoop.advance(3000)")
        net_log = ctx.eval("window.__iv8__.netLog.entries", to_py=True)
        chl_keys = ctx.eval("Object.keys(window._cf_chl_opt||{}).join(',')")
        case_now = ctx.eval("window.__ruyiCaseNow===undefined?'none':String(window.__ruyiCaseNow)")
        pj_info = ctx.eval("window.__ruyiPJ||''")
        dom_panel = ctx.eval(
            "JSON.stringify({ce:typeof document.createElement,"
            "cet:typeof document.createElementNS,"
            "doc:typeof document,win:typeof window,self:typeof self})"
        )
        cookie_names = sorted(
            {part.strip().split("=", 1)[0] for part in str(ctx.eval("document.cookie")).split(";") if part.strip()}
        )

    posts = [e for e in net_log if str(e.get("method", "")).upper() == "POST"]
    all_net = [
        {"method": str(e.get("method", "")), "url": str(e.get("url", ""))[:160]}
        for e in net_log
    ][:20]
    posts_summary = [
        {"url": str(e.get("url", ""))[:200], "bodyBytes": len(str(e.get("body", "")))}
        for e in posts
    ]
    return {
        "schema": "psa-cf-iv8-probe.v1",
        "plane": "iv8",
        "mode": "local",
        "status": "partial",
        "caseId": "psa-cf-5s-shield-20260815",
        "runtime": {
            "name": "iv8",
            "version": iv8.__version__,
            "v8Version": iv8.v8_version,
            "network": "offline-resource-bundle-only",
        },
        "source": {
            "repository": "https://github.com/HanZzzzz000/iv8",
            "commit": "950c9b937a510bb4c33909723ad3596807a44546",
        },
        "browserInput": {
            "challengeHtmlSha256": sha256_text(challenge_html),
            "orchestrateSha256": sha256_text(orchestrate_js),
        },
        "pageLoad": load_result,
        "caseNow": str(case_now),
        "pjInfo": str(pj_info),
        "domPanel": json.loads(str(dom_panel)) if dom_panel else None,
        "eventLoopAdvanced": 6,
        "postRequests": posts_summary,
        "allNetRequests": all_net,
        "chlOptKeys": str(chl_keys)[:300],
        "cookieNames": cookie_names,
        "limitations": [
            "Community Edition offline model: no real HTTP/TLS/proxy request",
            "challenge-platform POST would not reach CF servers",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps({
        "output": str(args.output),
        "posts": len(result["postRequests"]),
        "status": result["status"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
