"""Read existing evidence only; never evaluate captured JavaScript."""
import hashlib
import json
import re
from pathlib import Path

PROJECT = Path(r"D:\reverse_ENV\workspace\psa_solve")
OUTPUT = Path(__file__).resolve().parent
RUN = "rt_20260929103550_341b734038"
RAW = PROJECT / "evidence/web/ruyitrace" / RUN / "raw"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


packet_path, = (RAW / "http_packet").glob("*turnstile_f*.json")
packet = json.loads(packet_path.read_text(encoding="utf-8"))
html = packet["responseBody"]["text"]
match = re.search(r"<script[^>]*>([\s\S]*?)</script>", html, re.I)
assert match is not None
source = match.group(1)
source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
expression = "x[bf(CW.IZ)][bf(CW.IM)](b)"
assert source.count(expression) == 1
call_offset = source.index(expression)
function_offset = source.index("function It(")
probe_path = PROJECT / "runtime/realm-probe-result.json"
probe = json.loads(probe_path.read_text(encoding="utf-8"))
probe_lines = [json.loads(line) for line in probe["probeLines"]]
local_source, = [row for row in probe_lines if row.get("sha256") == source_hash]
assert local_source["length"] == len(source.encode("utf-16-le")) // 2
trace_path = RAW / "domtrace/trace_process_48444.ndjson"
records = []
with trace_path.open(encoding="utf-8") as handle:
    for line_number, line in enumerate(handle, 1):
        row = json.loads(line)
        if row.get("seq") in (98, 99):
            records.append((line_number, row))
assert len(records) == 2
(getter_line, getter), (call_line, call) = records
assert getter["member"] == "get body" and call["member"] == "attachShadow"
assert getter["valueObj"] == call["thisObj"]
assert getter["stack"][0]["file"] == call["stack"][0]["file"] == packet["url"]
sites = []
for kind, line_number, row in (("body-get", getter_line, getter), ("attachShadow", call_line, call)):
    stack = row["stack"][0]
    assert stack["func"] == "It" and stack["line"] == 1
    inline_offset = stack["col"] - 1 - match.start(1)
    assert call_offset <= inline_offset < call_offset + len(expression)
    sites.append({"kind": kind, "traceLine": line_number, "seq": row["seq"],
                  "documentColumn": stack["col"], "inlineUtf16Offset": inline_offset,
                  "withinUniqueLocalExpression": True})
fixture = {
    "kind": "read-only-canonical-receiver-fact", "runId": RUN, "pid": 48444,
    "source": {"inlineUtf8Sha256": source_hash,
               "inlineUtf16Length": local_source["length"],
               "inlineStartDocumentOffset": match.start(1),
               "localRecordedSourceHashMatches": True,
               "localOriginalSourceWasInstrumentedAfterHash": local_source["rewritten"],
               "documentUrlMatchesStack": True,
               "functionName": "It", "functionOffset": function_offset,
               "expressionOffset": call_offset, "expressionUnique": True,
               "classLabelHashUsed": False},
    "browser": {"sites": sites, "bodyClass": getter["valueObj"]["class"],
                "identityJoin": {"jsId": getter["valueObj"]["id"],
                                 "nativeId": getter["valueObj"]["nativeId"],
                                 "getterReturnEqualsCallReceiver": True,
                                 "adjacentRecords": call_line == getter_line + 1},
                "returnClass": call["returnObj"]["class"],
                "originCallId": call["origin_call_id"]},
    "local": {"observedReceiverLabel": probe["xCall"]["receiver"],
              "observedPropertyKey": probe["xCall"]["propertyKey"],
              "foRequests": probe["foRequests"], "identityProvenanceRecorded": False,
              "recordedExpressionMatchesUniqueOriginalSourceSite":
              probe["xCall"]["expression"] == expression},
    "alignment": {"originalSourceIdentical": True,
                  "originalCallSiteAligned": True,
                  "sameDynamicInvocationProven": False,
                  "sameExecutableBytesProven": False,
                  "sameLiveSessionStateProven": False},
    "staticModel": {"documentBodyFactoryDefaultsToScript": True,
                    "scriptTagReceivesHTMLScriptElementPrototype": True,
                    "xAliasPropertyDecoderNotExecuted": True,
                    "completeLocalDataflowProven": False},
    "limitations": ["Local label is constructor.name, not browser branding.",
                    "Local receiver===document.body/tag/ownerDocument/identity not recorded.",
                    "Static x alias uses an unresolved computed property; no decoder executed.",
                    "Original bytes match; instrumented executable bytes do not claim parity.",
                    "Native args contain Object identity only; shadow mode is unknown.",
                    "origin_call_id is zero; no direct JSCall correlation is claimed.",
                    "No new runner, target, network, patch, gate or hygiene-state execution."],
    "inputs": [{"path": path.relative_to(PROJECT).as_posix(), "sha256": sha256(path)}
               for path in (packet_path, trace_path, probe_path,
                            PROJECT / "runtime/mirror-canary.js",
                            PROJECT / "runtime/realm-probe-canary.js")]
}
destination = OUTPUT / "receiver-fact.redacted.json"
destination.write_text(json.dumps(fixture, ensure_ascii=True, indent=2) + "\n", encoding="utf-8", newline="\n")
print(json.dumps({"sourceHashMatched": True, "sourceLength": local_source["length"],
                  "browserIdentityJoined": True, "sites": sites,
                  "localIdentityProven": False, "output": str(destination)}))
