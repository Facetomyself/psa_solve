import os, sys
for key in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(key, None)
os.environ["PYTHONIOENCODING"] = "utf-8"
import ruyijs

URL = "https://www.psacard.com/cert/67417377/psa"
FP = {
    "navigator": {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0", "platform": "Win32", "language": "en-US", "languages": ["en-US", "en"]},
    "screen": {"width": 1920, "height": 1080, "availWidth": 1920, "availHeight": 1040, "colorDepth": 24},
    "viewport": {"width": 1920, "height": 939, "devicePixelRatio": 1},
}
ctx = ruyijs.Context(timeout=120)
ctx.configure_fingerprint(FP)
ctx.configure_clock("system")
ctx.navigate(URL)
ctx.advance(6000, max_tasks=100000)

for name, code in [
    ("innerText", "(function(){return document.body.innerText.length})()"),
    ("textContent", "(function(){return document.body.textContent.length})()"),
]:
    try:
        print(name, "->", str(ctx.eval(code))[:80], flush=True)
    except Exception as exc:
        print(name, "-> ERR:", f"{type(exc).__name__}: {exc}"[:160], flush=True)
try:
    ctx.close()
except Exception:
    pass
