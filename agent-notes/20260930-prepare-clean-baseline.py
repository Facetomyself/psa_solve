"""Build a byte-preserving diagnostic-cleanup candidate, never execute a target."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUT = ROOT / "diagnostics" / "clean-baseline-20260930"
NODE = Path(r"D:\reverse_ENV\tools\node\node.exe")
SOURCE = ROOT / "diagnostics" / "ruyidom_bridge.js"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    raw = SOURCE.read_bytes()
    start_marker = b'            "function wkLen(v)'
    end_marker = b'            "var ru=w.crypto&&w.crypto.randomUUID;"'
    assert raw.count(start_marker) == raw.count(end_marker) == 1
    start, end = raw.index(start_marker), raw.index(end_marker)
    assert start < end
    candidate = raw[:start] + raw[end:]
    for marker in (b"WKPROBE", b"wrapSubtle", b"ruyi-wk", b"var WW=nativeText", b"var OB=w.Blob"):
        assert marker in raw and marker not in candidate, marker
    original = OUT / "ruyidom_bridge.original.js"
    clean = OUT / "ruyidom_bridge.clean.js"
    if original.exists():
        assert original.read_bytes() == raw, "Refuse to replace a different archived original"
    else:
        original.write_bytes(raw)
    clean.write_bytes(candidate)
    assert raw[:start] == candidate[:start]
    assert raw[end:] == candidate[start:]
    assert SOURCE.read_bytes() == raw
    tests = []
    for path in (original, clean):
        result = subprocess.run([str(NODE), "--check", str(path)], capture_output=True, encoding="utf-8")
        tests.append({"test": "node-syntax-only", "file": path.name, "exitCode": result.returncode})
        assert result.returncode == 0, result.stderr
        # The hook is JS string concatenation. Parse only JSON string literals,
        # then syntax-check the assembled program without executing any of it.
        source = path.read_text(encoding="utf-8-sig")
        marker = '        win.__rtcS = 0;'
        hook = source[source.index(marker):]
        hook = hook[hook.index('          win.eval(') + len('          win.eval('):]
        hook = hook[:hook.index('\n          );')]
        chunks = []
        for line in hook.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.endswith('+'):
                line = line[:-1].rstrip()
            chunks.append(json.loads(line))
        embedded = OUT / (path.stem + '.embedded-syntax.js')
        embedded.write_text(''.join(chunks) + '\n', encoding="utf-8", newline="\n")
        result = subprocess.run([str(NODE), "--check", str(embedded)], capture_output=True, encoding="utf-8")
        tests.append({"test": "embedded-hook-syntax-only", "file": embedded.name, "exitCode": result.returncode})
        assert result.returncode == 0, result.stderr
    facts = ROOT / "contracts" / "auto-decision-facts.json"
    status = subprocess.run([str(NODE), r"D:\reverse_ENV\mcp\ruyidom-mcp\dist\cli.js", "status"], capture_output=True, encoding="utf-8")
    assert status.returncode == 0, status.stderr
    runtime = json.loads(status.stdout)
    (OUT / "runtime-status.json").write_text(json.dumps(runtime, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest = {
        "originalSha256": sha(raw), "cleanSha256": sha(candidate),
        "factsSha256": sha(facts.read_bytes()),
        "removedByteRange": [start, end],
        "removedSourceLines": [raw[:start].count(b"\n") + 1, raw[:end].count(b"\n")],
        "removedBytes": end - start,
        "unchangedPrefixSha256": sha(raw[:start]), "unchangedSuffixSha256": sha(raw[end:]),
        "allOtherBytesPreserved": True, "originalUnmodified": True,
        "removed": ["Worker prototype/instance wrappers", "sync blob read and Worker bootstrap", "createObjectURL text inspection", "BroadcastChannel probe", "Blob source rewrite", "crypto.subtle wrappers"],
        "kept": ["all code outside the one removed interval", "UA preference", "HTTP3 mapping", "native navigation fixes", "existing interaction path", "older observation hooks"],
        "scopeLimitation": "This is not a zero-instrumentation runner; older atob/Map/RTC/navigation/other observers remain unchanged.",
        "tests": tests, "networkExecuted": False,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"status": "candidate-prepared", "manifest": str(OUT / "manifest.json"), "syntaxTests": len(tests), "removedBytes": end-start}))


if __name__ == "__main__":
    main()
