import os, sys, json
for key in ("HTTP_PROXY","HTTPS_PROXY","http_proxy","https_proxy","ALL_PROXY","all_proxy"):
    os.environ.pop(key, None)
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.path.insert(0, r"D:\reverse_ENV\tools\web-reverse")
import ruyijs

URL = "https://www.psacard.com/cert/67417377/psa"
FP = {
    "navigator": {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:158.0) Gecko/20100101 Firefox/158.0", "platform": "Win32", "language": "en-US", "languages": ["en-US", "en"]},
    "screen": {"width": 1920, "height": 1080, "availWidth": 1920, "availHeight": 1040, "colorDepth": 24},
    "viewport": {"width": 1920, "height": 939, "devicePixelRatio": 1},
}

def trial(name, pre):
    ctx = ruyijs.Context(timeout=120)
    err = None
    try:
        for label, fn in pre:
            fn(ctx)
        ctx.navigate(URL)
        ctx.advance(6000, max_tasks=100000)
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"[:300]
    extra = ""
    try:
        extra = str(ctx.eval("JSON.stringify({t:(document.title||'').length,rs:String(document.readyState),opt:!!window._cf_chl_opt})"))[:120]
    except Exception as exc:
        extra = "evalErr:" + f"{type(exc).__name__}: {exc}"[:120]
    try:
        ctx.close()
    except Exception:
        pass
    print(name, "| err:", err, "| eval:", extra, flush=True)

nav = ("navigate", lambda c: c.navigate(URL))
trial("D:navigate-only", [])
trial("E:clock+navigate", [("clock", lambda c: c.configure_clock("system"))])
trial("F:fp+navigate", [("fp", lambda c: c.configure_fingerprint(FP))])
trial("G:fp+clock+navigate", [("fp", lambda c: c.configure_fingerprint(FP)), ("clock", lambda c: c.configure_clock("system"))])
