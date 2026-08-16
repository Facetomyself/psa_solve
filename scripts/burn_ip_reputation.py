# -*- coding: utf-8 -*-
"""连续快速请求破坏 IP 信誉（触发 CF 对 IP 的挑战判定升级）。

用法：python burn_ip_reputation.py [--count 40] [--gap 0.35]
默认 40 个 SN 页面请求、间隔 0.35s，用 urllib（非浏览器指纹，CF 判定为可疑客户端）。
输出每次请求的状态码分布。
"""
import argparse
import random
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:140.0) Gecko/20100101 Firefox/140.0"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--gap", type=float, default=0.35)
    args = parser.parse_args()

    stats = {}
    for i in range(args.count):
        sn = random.randint(1, 99999999)
        url = f"https://www.psacard.com/cert/{sn}/psa"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            resp = urllib.request.urlopen(req, timeout=15)
            code = resp.status
            resp.read()
        except urllib.error.HTTPError as e:
            code = e.code
            try:
                e.read()
            except Exception:
                pass
        except Exception:
            code = 0
        stats[code] = stats.get(code, 0) + 1
        if (i + 1) % 10 == 0:
            print(f"[{i+1}/{args.count}] {stats}", flush=True)
        time.sleep(args.gap)

    total = sum(stats.values())
    chl = stats.get(403, 0)
    print(f"done: {stats}  total={total}  挑战率={chl/total:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
