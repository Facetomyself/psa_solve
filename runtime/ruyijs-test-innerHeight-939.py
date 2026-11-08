#!/usr/bin/env python3
import sys
import json
from pathlib import Path

sys.path.insert(0, r"D:\reverse_ENV\temp\ruyijs-test-env\Lib\site-packages")
import ruyijs

# 使用正确的 group: viewport (不是 window)
fingerprint = {
    "navigator": {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0",
        "platform": "Win32",
        "language": "en-US",
        "languages": ["en-US", "en"],
        "hardwareConcurrency": 8,
    },
    "screen": {
        "width": 1920,
        "height": 1080,
        "availWidth": 1920,
        "availHeight": 1040,
        "colorDepth": 24,
    },
    "viewport": {
        "width": 1920,
        "height": 939,   # 关键：对齐 RuyiTrace innerHeight
        "devicePixelRatio": 1,
    },
}

url = "https://www.psacard.com/cert/67417377/psa"
print(f"ruyijs {ruyijs.__version__}")
print(f"Testing fresh-navigate with viewport 1920x939")
print(f"Target: {url}\n")

try:
    context = ruyijs.Context(timeout=150.0)
    context.configure_fingerprint(fingerprint)
    print("Fingerprint configured OK")
    context.configure_clock("logical", epoch_ms=1793644803000)
    
    print("Navigating...")
    loaded = context.navigate(url)
    loaded_url = loaded.get('url') if isinstance(loaded, dict) else 'N/A'
    print(f"Loaded: {loaded_url}")
    
    print("Advancing 8 seconds...")
    context.advance(8000, max_tasks=100000)
    
    net_log = context.net_log()
    print(f"Net log events: {len(net_log)}")
    
    def classify(events):
        fo = []
        cert = []
        for e in events:
            if not isinstance(e, dict) or e.get('method') != 'POST':
                continue
            u = str(e.get('url', ''))
            if '/cdn-cgi/' in u:
                fo.append(e)
            elif '/cert/' in u:
                cert.append(e)
        return fo, cert
    
    fo_posts, cert_posts = classify(net_log)
    print(f"\n=== Results ===")
    print(f"FO POST count: {len(fo_posts)}, statuses: {[e.get('status') for e in fo_posts]}")
    print(f"Cert POST count: {len(cert_posts)}, statuses: {[e.get('status') for e in cert_posts]}")
    
    # show all events
    print(f"\n=== All net events ===")
    for i, e in enumerate(net_log):
        if isinstance(e, dict):
            print(f"  [{i+1}] {e.get('method')} status={e.get('status')} url={str(e.get('url',''))[:120]}")
    
    context.close()
    print("\n=== Test completed ===")
    if cert_posts:
        print("SUCCESS: Cert POST present!")
        sys.exit(0)
    elif fo_posts and any(e.get('status') == 200 for e in fo_posts):
        print("PARTIAL: FO POST 200 but no cert POST")
        sys.exit(1)
    else:
        print("FAILED")
        sys.exit(2)
except Exception as exc:
    print(f"ERROR: {exc}")
    import traceback
    traceback.print_exc()
    sys.exit(3)
