from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import subprocess
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
BASELINES = {
    "diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js": {
        "sha256": "a6f0e51a8b8c99019678a508385cc21f66fd3205e08c512d3ccc8888a32433d6",
        "mode": "active-transport-fixed",
        "out": "diagnostics/causal-observer-transport-fixed",
        "runner": "ruyidom_bridge.causal-observer.transport-fixed.js",
        "receipt": "agent-notes/20260930-causal-observer-transport-fixed-receipt.json",
        "fixture": "agent-notes/20260930-causal-observer-transport-fixed-fixtures.json",
    },
    "diagnostics/clean-baseline-20260930/ruyidom_bridge.clean.js": {
        "sha256": "32cef74e67164611750ac2870546a2a4283f8b519ec4756e3a8f949fa3c0cd94",
        "mode": "historical-synthetic-comparison-only",
        "out": "diagnostics/causal-observer-20260930",
        "runner": "ruyidom_bridge.causal-observer.js",
        "receipt": "agent-notes/20260930-causal-observer-receipt.json",
        "fixture": "agent-notes/20260930-causal-observer-fixtures.json",
    },
}
DEFAULT_BASELINE = "diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js"


def build_paths(baseline_arg: str) -> dict[str, object]:
    supplied = Path(baseline_arg)
    resolved = (supplied if supplied.is_absolute() else PROJECT / supplied).resolve()
    try:
        relative = resolved.relative_to(PROJECT).as_posix()
    except ValueError as exc:
        raise ValueError("baseline must stay inside project") from exc
    if relative not in BASELINES:
        raise ValueError("baseline is not in the reviewed allowlist")
    config = dict(BASELINES[relative])
    source_hash = sha(resolved.read_bytes())
    if source_hash != config["sha256"]:
        raise ValueError("reviewed baseline hash mismatch")
    out = PROJECT / str(config["out"])
    runner = out / str(config["runner"])
    stem = runner.name.removesuffix(".js")
    return {
        **config,
        "relative": relative,
        "base": resolved,
        "out": out,
        "runner": runner,
        "embedded": out / f"{stem}.embedded-syntax.js",
        "helperTest": out / "synthetic-helper-test.js",
        "receipt": PROJECT / str(config["receipt"]),
        "fixture": PROJECT / str(config["fixture"]),
    }


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def quote_payload(payload: str, indent: str) -> str:
    return indent + json.dumps(payload, ensure_ascii=False) + " +"


HELPERS = [
    "function hashText(input){var ascii='';try{ascii=unescape(encodeURIComponent(String(input==null?'':input)));}catch(eUtf){ascii=String(input==null?'':input);}function rr(v,a){return v>>>a|v<<32-a;}var mp=Math.pow,mw=mp(2,32),words=[],bit=ascii.length*8,hash=[],k=[],pc=0,comp={};for(var cand=2;pc<64;cand++){if(!comp[cand]){for(var x=0;x<313;x+=cand)comp[x]=cand;hash[pc]=(mp(cand,.5)*mw)|0;k[pc++]=(mp(cand,1/3)*mw)|0;}}ascii+='\\x80';while(ascii.length%64-56)ascii+='\\x00';for(var i=0;i<ascii.length;i++){var j=ascii.charCodeAt(i);words[i>>2]|=j<<((3-i)%4)*8;}words[words.length]=bit/mw|0;words[words.length]=bit;for(j=0;j<words.length;){var w=words.slice(j,j+=16),old=hash.slice(0);hash=hash.slice(0,8);for(i=0;i<64;i++){var w15=w[i-15],w2=w[i-2],a=hash[0],e=hash[4];var t1=hash[7]+(rr(e,6)^rr(e,11)^rr(e,25))+((e&hash[5])^((~e)&hash[6]))+k[i]+(w[i]=i<16?w[i]:(w[i-16]+(rr(w15,7)^rr(w15,18)^(w15>>>3))+w[i-7]+(rr(w2,17)^rr(w2,19)^(w2>>>10)))|0);var t2=(rr(a,2)^rr(a,13)^rr(a,22))+((a&hash[1])^(a&hash[2])^(hash[1]&hash[2]));hash=[(t1+t2)|0,a,hash[1],hash[2],(hash[3]+t1)|0,e,hash[5],hash[6]];}for(i=0;i<8;i++)hash[i]=(hash[i]+old[i])|0;}var out='';for(i=0;i<8;i++)for(j=3;j+1;j--){var b=hash[i]>>j*8&255;out+=(b<16?'0':'')+b.toString(16);}return out;}",
    "function tagShape(s){var out=[],m,re=/<\\/?([a-z][a-z0-9-]{0,15})\\b/ig;s=String(s==null?'':s);while((m=re.exec(s))&&out.length<12)out.push(String(m[1]).toLowerCase());return out.join(',');}",
    "function scriptClass(url){url=String(url||'');if(url.indexOf('challenges.cloudflare')>=0||url.indexOf('/challenge-platform/')>=0)return 'challenge';if(url.indexOf('blob:')===0)return 'blob';try{if(w.location&&w.location.host&&url.indexOf(String(w.location.host))>=0)return 'page';}catch(eLoc){}return 'other';}",
    "function callerBrief(){var st='';try{st=String((new Error()).stack||'');}catch(eSt){}var ls=st.split(/\\n/);for(var i=0;i<ls.length;i++){var line=String(ls[i]||'');if(!line||line.indexOf('callerBrief')>=0||line.indexOf('pushCausal')>=0)continue;var m=line.match(/^(.*?)@(.+):(\\d+):(\\d+)$/)||line.match(/^\\s*at\\s+(.*?)\\s+\\((.+):(\\d+):(\\d+)\\)$/);if(m)return {scriptClass:scriptClass(m[2]),fn:String(m[1]||'').slice(0,48),line:Number(m[3])||0,column:Number(m[4])||0};}return {scriptClass:'unknown',fn:'',line:0,column:0};}",
    "function pushCausal(kind,data){if(!w.__causal||w.__causal.length>=64)return;var row={seq:++w.__causalSeq,t:Date.now()-w.__t0,kind:String(kind||'unknown'),caller:callerBrief()};data=data||{};for(var k in data)if(Object.prototype.hasOwnProperty.call(data,k))row[k]=data[k];w.__causal.push(row);}",
    "function shapeRecord(v){var s='';try{s=String(v==null?'':v);}catch(eS){}return {len:s.length,sha256:hashText(s),tagShape:tagShape(s)};}",
    "function pathClass(v){v=String(v||'');if(v.indexOf('/cdn-cgi/challenge-platform/')>=0&&v.indexOf('/fo/')>=0)return 'challenge-fo';if(v.indexOf('/cert/')>=0)return 'cert-document';return 'other';}",
    "function redactVisibleText(v){var s='';try{s=String(v==null?'':v);}catch(eTxt){}s=s.replace(/https?:\\/\\/\\S+/gi,'{url}').replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}/gi,'{email}').replace(/\\b[A-Za-z0-9_.-]{24,}\\b/g,'{token}').replace(/\\b(?:\\d[ -]?){6,}\\b/g,'{number}').replace(/\\s+/g,' ').trim();return s.slice(0,480);}",
    "function finalVisible(){var title='',text='';try{title=String(w.document&&w.document.title||'');}catch(eTitle){}try{var b=w.document&&w.document.body;text=String(b&&(b.innerText||b.textContent)||'');}catch(eBody){}return {title:redactVisibleText(title),text:redactVisibleText(text),textLen:text.length,textSha256:hashText(text)};}w.__causalFinal=finalVisible;",
]


def transform(source: str) -> tuple[str, list[dict[str, object]]]:
    lines = source.splitlines()
    output: list[str] = []
    edits: list[dict[str, object]] = []

    def replace_once(payload: str) -> str:
        original = payload
        if payload == "w.__bridgeHdr=[];w.__liveRes=[];":
            payload += "w.__causal=[];w.__causalSeq=0;"
        elif payload == "var fs=FP.submit;FP.submit=nativeText(function(){w.__submits++;return fs.apply(this,arguments);},'submit');":
            payload = "var fs=FP.submit;FP.submit=nativeText(function(){w.__submits++;try{pushCausal('form.submit',{});}catch(eCausalSubmit){}return fs.apply(this,arguments);},'submit');"
        elif payload == "DP.write=nativeText(function(){w.__writes++;return dwr.apply(this,arguments);},'write');":
            payload = "DP.write=nativeText(function(){w.__writes++;try{var joined='';for(var wi=0;wi<arguments.length;wi++)joined+=String(arguments[wi]==null?'':arguments[wi]);pushCausal('document.write',shapeRecord(joined));}catch(eCausalWrite){}return dwr.apply(this,arguments);},'write');"
        elif payload.startswith("try{var EP=cw.Element&&cw.Element.prototype;"):
            needle = "}catch(eIh2){}return ihs.call(this,v);"
            replacement = "}catch(eIh2){}try{pushCausal('innerHTML',shapeRecord(s));}catch(eCausalIh){}return ihs.call(this,v);"
            if payload.count(needle) != 1:
                raise ValueError("innerHTML hook anchor mismatch")
            payload = payload.replace(needle, replacement)
        elif payload == "var el=origCreate.apply(this,arguments);":
            payload = "var el=origCreate.apply(this,arguments);try{var causalTag=String(name||'').toLowerCase();if(causalTag==='form'||causalTag==='h2'||causalTag==='p'||causalTag==='ol')pushCausal('createElement',{tag:causalTag});}catch(eCausalCreate){}"
        elif payload.startswith("xp.open=nativeText(function(method,url){"):
            needle = "this.__bm=method;this.__bn=[];"
            if payload.count(needle) != 1:
                raise ValueError("XHR open hook anchor mismatch")
            payload = payload.replace(needle, "this.__bm=method;this.__bn=[];this.__cu=pathClass(url);")
        elif payload.startswith("xp.send=nativeText(function(){"):
            request_needle = "try{var pb=arguments[0];"
            request_add = request_needle + "try{if(this.__cu==='challenge-fo'){var causalReq=arguments[0]==null?'':String(arguments[0]);pushCausal('request',{method:String(this.__bm||'GET').toUpperCase(),len:causalReq.length,sha256:hashText(causalReq),pathClass:this.__cu});}}catch(eCausalReq){}"
            if payload.count(request_needle) != 1:
                raise ValueError("XHR request hook anchor mismatch")
            payload = payload.replace(request_needle, request_add)
            early = "xhr.addEventListener('loadend',function(){if(w.__liveRes.length>=8)return;var names=[];"
            if payload.count(early) != 1:
                raise ValueError("XHR loadend hook anchor mismatch")
            payload = payload.replace(early, "xhr.addEventListener('loadend',function(){var names=[];")
            header_end = "}catch(eH){}"
            response_observer = header_end + "try{if(names.indexOf('cf-chl-out')>=0){var causalBody='';try{causalBody=String(xhr.responseText||'');}catch(eCausalBody){}pushCausal('response',{status:xhr.status||0,len:causalBody.length,sha256:hashText(causalBody),pathClass:xhr.__cu||'other'});}}catch(eCausalResp){}if(w.__liveRes.length>=8)return;"
            if payload.count(header_end) != 1:
                raise ValueError("XHR response header anchor mismatch")
            payload = payload.replace(header_end, response_observer)
        elif payload.startswith("chlOut:String(window.__chlOut||''),"):
            payload += "causalTrace:(window.__causal||[]),causalFinal:(typeof window.__causalFinal==='function'?window.__causalFinal():{}),"
        if payload != original:
            edits.append({"anchorSha256": sha(original.encode()), "replacementSha256": sha(payload.encode()), "anchorBytes": len(original.encode()), "replacementBytes": len(payload.encode())})
        return payload

    inserted_helpers = False
    for line in lines:
        match = re.match(r'^(\s*)("(?:\\.|[^"\\])*")\s*\+$', line)
        if not match:
            output.append(line)
            continue
        indent, token = match.groups()
        payload = json.loads(token)
        changed = replace_once(payload)
        output.append(quote_payload(changed, indent))
        if payload == "return fn;}":
            if inserted_helpers:
                raise ValueError("helper insertion anchor repeated")
            for helper in HELPERS:
                output.append(quote_payload(helper, indent))
            edits.append({"insertAfterSha256": sha(payload.encode()), "insertedHelpers": len(HELPERS), "insertedBytes": sum(len(x.encode()) for x in HELPERS)})
            inserted_helpers = True
    if not inserted_helpers:
        raise ValueError("helper insertion anchor missing")
    expected_edits = 9
    if len(edits) != expected_edits:
        raise ValueError(f"expected {expected_edits} edits, saw {len(edits)}")
    return "\n".join(output) + "\n", edits


def extract_first_eval(source: str) -> str:
    lines = source.splitlines()
    for start, line in enumerate(lines):
        match = re.match(r'^\s*("(?:\\.|[^"\\])*")\s*\+?$', line)
        if not match or json.loads(match.group(1)) != "(function(){":
            continue
        parts: list[str] = []
        for current in lines[start:]:
            item = re.match(r'^\s*("(?:\\.|[^"\\])*")\s*\+?$', current)
            if not item:
                if not current.strip():
                    continue
                break
            payload = json.loads(item.group(1))
            parts.append(payload)
            if payload.endswith("})();"):
                break
        joined = "".join(parts)
        if "w.__wk=0" in joined and joined.endswith("})();"):
            return joined + "\n"
    raise ValueError("embedded script extraction failed")


def helper_fixture_source() -> str:
    helpers = "\n".join(HELPERS)
    return """'use strict';
var window={__t0:Date.now()-10,__causal:[],__causalSeq:0,location:{host:'example.test'},document:{title:'Troubleshooting 123456789 user@example.test',body:{innerText:'Visit https://secret.test/a token abcdefghijklmnopqrstuvwxyz012345 for support.'}}};
var w=window;
""" + helpers + """
pushCausal('request',{pathClass:'challenge-fo'});
pushCausal('response',{status:200,len:3488,sha256:hashText('fixture-response'),pathClass:'challenge-fo'});
pushCausal('document.write',shapeRecord('<h2>fixture secret</h2><p>help</p>'));
pushCausal('createElement',{tag:'h2'});
var result={sha256abc:hashText('abc'),events:w.__causal,final:finalVisible()};
process.stdout.write(JSON.stringify(result));
"""


def run_node(node: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(node), *args], text=True, encoding="utf-8", capture_output=True, check=True)


def build(node: Path, baseline_arg: str) -> dict[str, object]:
    paths = build_paths(baseline_arg)
    base = paths["base"]
    out = paths["out"]
    runner = paths["runner"]
    embedded_path = paths["embedded"]
    helper_test = paths["helperTest"]
    fixture_path = paths["fixture"]
    receipt_path = paths["receipt"]
    assert isinstance(base, Path) and isinstance(out, Path) and isinstance(runner, Path)
    assert isinstance(embedded_path, Path) and isinstance(helper_test, Path)
    assert isinstance(fixture_path, Path) and isinstance(receipt_path, Path)
    source = base.read_text(encoding="utf-8")
    generated, edits = transform(source)
    out.mkdir(parents=True, exist_ok=True)
    runner.write_text(generated, encoding="utf-8", newline="\n")
    embedded = extract_first_eval(generated)
    embedded_path.write_text(embedded, encoding="utf-8", newline="\n")
    helper_test.write_text(helper_fixture_source(), encoding="utf-8", newline="\n")

    run_node(node, "--check", str(runner))
    run_node(node, "--check", str(embedded_path))
    run_node(node, "--check", str(helper_test))
    fixture_result = json.loads(run_node(node, str(helper_test)).stdout)
    if fixture_result["sha256abc"] != "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad":
        raise ValueError("embedded SHA-256 helper failed known-answer test")
    kinds = [row["kind"] for row in fixture_result["events"]]
    if kinds != ["request", "response", "document.write", "createElement"]:
        raise ValueError(f"causal fixture ordering failed: {kinds}")
    serialized = json.dumps(fixture_result, ensure_ascii=False)
    for secret in ("secret.test", "user@example.test", "abcdefghijklmnopqrstuvwxyz012345"):
        if secret in serialized:
            raise ValueError("sensitive fixture value leaked: " + secret)

    fixture_doc = {
        "schema": "causal-observer-synthetic-fixtures.v1",
        "networkUsed": False,
        "targetExecuted": False,
        "expectedEventKinds": kinds,
        "knownAnswerSha256": fixture_result["sha256abc"],
        "redactedFinal": fixture_result["final"],
        "sensitiveLeakCheck": "pass",
    }
    fixture_path.write_text(json.dumps(fixture_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    diff = list(difflib.unified_diff(source.splitlines(), generated.splitlines(), fromfile=str(base.relative_to(PROJECT)), tofile=str(runner.relative_to(PROJECT)), lineterm=""))
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    generated_bytes = generated.encode()
    source_bytes = source.encode()
    forbidden_added = ["foResponseManifest", "foreignResponseReplay", "runProgram(", "opcode", "debugger"]
    added_text = "\n".join(line[1:] for line in diff if line.startswith("+") and not line.startswith("+++"))
    hits = [item for item in forbidden_added if item in added_text]
    if hits:
        raise ValueError("forbidden addition in observer diff: " + ",".join(hits))
    proxy_pref = 'prefs.setIntPref("network.proxy.type", 0);'
    source_proxy_count = source.count(proxy_pref)
    output_proxy_count = generated.count(proxy_pref)
    if paths["mode"] == "active-transport-fixed" and (source_proxy_count, output_proxy_count) != (1, 1):
        raise ValueError("transport-fixed proxy preference was not preserved exactly")
    if paths["mode"] != "active-transport-fixed" and output_proxy_count != 0:
        raise ValueError("historical clean unexpectedly acquired transport preference")
    receipt = {
        "schema": "causal-observer-build-receipt.v1",
        "status": "static-verified-not-authorized",
        "baselineMode": paths["mode"],
        "source": str(base.relative_to(PROJECT)).replace("\\", "/"),
        "sourceSha256": sha(source_bytes),
        "sourceBytes": len(source_bytes),
        "output": str(runner.relative_to(PROJECT)).replace("\\", "/"),
        "outputSha256": sha(generated_bytes),
        "outputBytes": len(generated_bytes),
        "sourceUnchangedAfterBuild": sha(base.read_bytes()) == sha(source_bytes),
        "transportPreference": {
            "name": "network.proxy.type",
            "value": 0 if output_proxy_count else None,
            "sourceCount": source_proxy_count,
            "outputCount": output_proxy_count,
            "preserved": source_proxy_count == output_proxy_count,
        },
        "edits": edits,
        "unifiedDiff": {"addedLines": added, "removedLines": removed, "sha256": sha("\n".join(diff).encode())},
        "staticChecks": {"outerNodeCheck": "pass", "embeddedNodeCheck": "pass", "helperFixtureNodeCheck": "pass"},
        "fixture": fixture_doc,
        "constraints": {
            "networkUsed": False,
            "targetExecuted": False,
            "factsChanged": False,
            "receiptsChanged": False,
            "bodyReplacementAdded": False,
            "responseReplayAdded": False,
            "environmentGetterAdded": False,
            "vmOrOpcodeInstrumentationAdded": False,
            "realRunAuthorized": False,
        },
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", type=Path, default=PROJECT.parents[1] / "tools/node/node.exe")
    parser.add_argument("--baseline", default=DEFAULT_BASELINE, help="reviewed baseline path; defaults to stable transport-fixed")
    args = parser.parse_args()
    receipt = build(args.node.resolve(), args.baseline)
    print(json.dumps({"status": receipt["status"], "baselineMode": receipt["baselineMode"], "outputSha256": receipt["outputSha256"], "fixture": "pass"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
