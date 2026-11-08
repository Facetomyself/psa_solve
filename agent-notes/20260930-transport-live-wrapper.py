"""One authorized fix_transport diagnostic. Reuses the existing fresh generator.

No diagnostic claim, no v2 budget changes, no target source rewriting, no retry.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import types
import uuid

REPO = Path(r"D:\reverse_ENV")
PROJECT = REPO / "workspace/psa_solve"
NOTES = PROJECT / "agent-notes"
STATE = NOTES / "20260930-transport-live.state.json"
SOURCE = PROJECT / "diagnostics/instrumentation-20260930-v2/ruyidom_bridge.instrumented.js"
FRESH = NOTES / "20260930-clean-baseline-wrapper.py"
NODE = REPO / "tools/node/node.exe"
CLI = REPO / "mcp/ruyidom-mcp/dist/cli.js"
FACTS = PROJECT / "contracts/auto-decision-facts.json"
RUN_ID = "e0b71e462e87439696301f2b211a7ea1"
BASE = PROJECT / "evidence/web/transport-diagnostic"
CONTROL = BASE / "control" / RUN_ID
RUN = BASE / RUN_ID
RUNNER = CONTROL / "transport-runner.js"
LOG_MODULES = "timestamp,sync,nsHttp:5,nsSocketTransport:5,neqo_transport:5,neqo_http3:5"
REPAIR = False


def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def arg_hash(argv):
    return hashlib.sha256(json.dumps(argv, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def pointer(path):
    return {"path": Path(path).relative_to(PROJECT).as_posix(), "sha256": digest(path), "bytes": Path(path).stat().st_size}


def state(**delta):
    value = read(STATE) if STATE.exists() else {}
    value.update(delta)
    value["updatedAt"] = now()
    write(STATE, value)
    return value


def capture(name, argv, *, env=None, timeout=40):
    started = now()
    p = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
    out, err = CONTROL / (name + ".stdout.json"), CONTROL / (name + ".stderr.txt")
    out.write_text(p.stdout, encoding="utf-8", newline="\n")
    err.write_text(p.stderr, encoding="utf-8", newline="\n")
    entry = {"name": name, "argv": argv, "argvSha256": arg_hash(argv), "startedAt": started, "endedAt": now(), "exitCode": p.returncode, "stdout": pointer(out), "stderr": pointer(err)}
    old = read(STATE)
    state(commands=old.get("commands", []) + [entry])
    if p.returncode:
        raise RuntimeError(name + "-failed")
    return p.stdout


TRANSPORT_HELPER = r'''
// Chrome-only readback. No writes to page globals or transport preferences.
function transportPrefSnapshot(stage, input, expectedHost) {
  try {
    var p = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
    var keys = ["network.http.http3.enable", "network.http.http3.backup_timer_delay", "network.http.http3.alt-svc-mapping-for-testing", "network.http.http3.force-use-alt-svc-mapping-for-testing", "network.process.enabled"];
    var values = {};
    for (var i = 0; i < keys.length; i++) {
      var k = keys[i], type = p.getPrefType(k), value = null;
      try { value = type === p.PREF_BOOL ? p.getBoolPref(k) : type === p.PREF_INT ? p.getIntPref(k) : type === p.PREF_STRING ? p.getCharPref(k) : null; } catch (_) {}
      values[k] = { type: type, userValue: p.prefHasUserValue(k), value: value };
    }
    var mapping = String(values[keys[2]].value || "");
    var hostMatches = expectedHost ? mapping.indexOf(String(expectedHost) + ";h3=\":443\"") >= 0 : null;
    appendTrace(String(input.tracePath || ""), {event:"transport-pref-snapshot", stage:stage, at:Date.now(), values:values, mappingMatchesPageHost:hostMatches});
  } catch (e) {
    appendTrace(String(input.tracePath || ""), {event:"transport-pref-snapshot", stage:stage, errorName:String(e && e.name || "error")});
  }
}
'''


def prepare():
    if STATE.exists() or CONTROL.exists() or RUN.exists():
        raise RuntimeError("one-shot-path-already-exists")
    CONTROL.mkdir(parents=True, exist_ok=False)
    raw = SOURCE.read_bytes()
    original = raw.decode("utf-8")
    edits = [
        ("RuyiDOM.main(function () {", TRANSPORT_HELPER + "\nRuyiDOM.main(function () {"),
        ("    var input = readInput();", "    var input = readInput();\n    transportPrefSnapshot(\"before-existing-pref-block\", input, null);"),
        ("    var pumpMs = Number(input.pumpMs || 15000);", "    transportPrefSnapshot(\"after-existing-pref-block\", input, pageHost);\n    var pumpMs = Number(input.pumpMs || 15000);"),
        ("      beforeParse: function (win) {", "      beforeParse: function (win) {\n        transportPrefSnapshot(\"after-profile-init-before-page-scripts\", input, pageHost);"),
        ("    dom.pump(pumpMs);", "    dom.pump(pumpMs);\n    transportPrefSnapshot(\"pump-ended\", input, pageHost);")]
    if REPAIR:
        edits.append(("      prefs.setBoolPref(\"network.http.http3.enable\", true);", "      prefs.setIntPref(\"network.proxy.type\", 0);\n      prefs.setBoolPref(\"network.http.http3.enable\", true);"))
    candidate = original
    for anchor, replacement in edits:
        if candidate.count(anchor) != 1:
            raise RuntimeError("ambiguous-snapshot-anchor")
        candidate = candidate.replace(anchor, replacement, 1)
    inverse = candidate
    for anchor, replacement in reversed(edits):
        inverse = inverse.replace(replacement, anchor, 1)
    if inverse.encode("utf-8") != raw:
        raise RuntimeError("source-preservation-failed")
    RUNNER.write_text(candidate, encoding="utf-8", newline="\n")
    facts = read(FACTS)
    if facts.get("firstDivergence") != "transport" or facts.get("experimentHygiene") != "ok":
        raise RuntimeError("authoritative-action-not-transport")
    argv = [str(NODE), str(CLI), "run", "--script", str(RUNNER), "--input-file", str(RUN / "fresh-input.json"), "--timeout-seconds", "120", "--allow-network"]
    initial = {"schema": "transport-live-operation.v1", "runId": RUN_ID, "status": "preparing", "terminal": "not-started", "action": "fix_transport", "turnGate": "blocked", "budgets": {"freshMaterialRounds": 1, "engineSpawns": 1, "repairPhases": 0}, "engineSpawnCount": 0, "commands": [], "factsRevisionBefore": facts.get("revision", facts.get("_revision", 0)), "factsSha256Before": digest(FACTS), "source": pointer(SOURCE), "runner": pointer(RUNNER), "freshGenerator": pointer(FRESH), "sourceReverseCheck": True, "changes": ["four chrome-only effective transport-pref snapshots", "native MOZ_LOG diagnostics"], "argv": argv, "argvSha256": arg_hash(argv), "environmentOverrides": {"MOZ_FORCE_DISABLE_E10S": "1", "MOZ_FORCE_DISABLE_FISSION": "1", "MOZ_LOG": LOG_MODULES, "MOZ_LOG_FILE": str(RUN / "gecko-transport.log")}, "targetNetworkExecuted": False, "v2BudgetModified": False, "historicalResponseReplay": False, "pageSourceOrHooksChanged": False, "serverAccepted": False}
    write(STATE, initial)
    if REPAIR:
        state(phase="same-transport-repair", phasePurpose="remove proven system HTTP application proxy only inside Gecko engine", authorizedRepairCause=pointer(NOTES / "20260930-transport-live.cause.json"), budgets={"freshMaterialRounds": 1, "engineSpawns": 1, "repairPhases": 1}, changedTransportVariable="network.proxy.type=0", additionalReadOnlyObservation="network.proxy.type in the existing four chrome snapshots", urllibProxyBehaviorChanged=False)
    capture("syntax", [str(NODE), "--check", str(RUNNER)])
    status = json.loads(capture("runtime-status", [str(NODE), str(CLI), "status"]))
    if not status.get("ok") or status.get("runtime", {}).get("status") != "healthy":
        raise RuntimeError("runtime-not-healthy")
    write(CONTROL / "runtime-status.json", status)
    state(status="prepared", terminal="reserved", runtimeHealthy=True)
    print(json.dumps({"status": "prepared", "runId": RUN_ID, "runnerSha256": digest(RUNNER), "sourceSha256": digest(SOURCE), "argvSha256": arg_hash(argv), "argv": argv, "scope": "one fresh logical session; same UA/imported-entry/real patches; chrome transport snapshots and native logging only"}))


def execute():
    s = read(STATE)
    if s.get("status") != "prepared" or s.get("engineSpawnCount") != 0 or RUN.exists():
        raise RuntimeError("one-shot-already-used")
    if digest(SOURCE) != s["source"]["sha256"] or digest(RUNNER) != s["runner"]["sha256"] or digest(FACTS) != s["factsSha256Before"]:
        raise RuntimeError("protected-source-or-facts-drift")
    spec = importlib.util.spec_from_file_location("psa_existing_fresh", FRESH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.RESTRICTED = BASE
    module.BASE = CONTROL
    module.STATE = STATE
    module.uuid = types.SimpleNamespace(uuid4=lambda: uuid.UUID(RUN_ID))
    module.state = state
    module.preflight = lambda: {"runtimeHealthy": True, "fixedSourceHashesVerified": True, "scope": "authorized-fix_transport; no claim/budget operation"}
    state(status="fresh-material-fetch-starting", wrapperPid=os.getpid(), terminal="running", targetNetworkExecuted=True, targetNetworkStartedAt=now())
    provenance = module.fetch_fresh()
    material = read(RUN / "source-receipt.json")
    for a in material["artifacts"]:
        if digest(a["path"]) != a["sha256"]:
            raise RuntimeError("fresh-artifact-hash-mismatch")
    inp = read(RUN / "fresh-input.json")
    if not (inp.get("liveNetwork") is True and inp.get("patchHistory") is True and inp.get("pumpMs") == 30000 and not inp.get("foResponseManifest") and not inp.get("debugThrow") and not inp.get("traceEval")):
        raise RuntimeError("fresh-input-scope-mismatch")
    if inp["tracePath"] != str(RUN / "bridge-live.jsonl"):
        raise RuntimeError("trace-root-mismatch")
    write(RUN / "operation-binding.json", {"schema": "fix-transport-operation-binding.v1", "authorizedAction": "fix_transport", "runId": RUN_ID, "factsRevision": s["factsRevisionBefore"], "factsSha256": s["factsSha256Before"], "originalRunner": s["source"], "diagnosticRunner": s["runner"], "runnerReverseCheck": True, "argv": s["argv"], "argvSha256": s["argvSha256"], "input": pointer(RUN / "fresh-input.json"), "sourceReceipt": pointer(RUN / "source-receipt.json"), "freshProvenance": pointer(provenance), "environmentOverrides": s["environmentOverrides"], "budgets": s["budgets"], "notAV2Claim": True, "v2BudgetModified": False})
    if digest(SOURCE) != s["source"]["sha256"] or digest(RUNNER) != s["runner"]["sha256"] or digest(FACTS) != s["factsSha256Before"]:
        raise RuntimeError("last-moment-source-or-facts-drift")
    env = dict(os.environ)
    env.update(s["environmentOverrides"])
    started = now()
    with (RUN / "engine-stdout.json").open("wb") as stdout, (RUN / "engine-stderr.txt").open("wb") as stderr:
        child = subprocess.Popen(s["argv"], cwd=str(REPO), stdout=stdout, stderr=stderr, env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        state(status="engine-running", terminal="running", onlineExecuted=True, wrapperPid=os.getpid(), cliPid=child.pid, cliPidAlive=True, engineSpawnCount=1, engineStartedAt=started, operationBinding=pointer(RUN / "operation-binding.json"))
        print(json.dumps({"status": "engine-running", "runId": RUN_ID, "wrapperPid": os.getpid(), "cliPid": child.pid, "argvSha256": s["argvSha256"]}), flush=True)
        code = child.wait()
    ended = now()
    receipt = {"schema": "fix-transport-execution.v1", "runId": RUN_ID, "spawned": True, "pid": child.pid, "startedAt": started, "endedAt": ended, "exitCode": code, "argv": s["argv"], "argvSha256": s["argvSha256"], "stdout": pointer(RUN / "engine-stdout.json"), "stderr": pointer(RUN / "engine-stderr.txt"), "nativeLogs": [pointer(p) for p in RUN.iterdir() if p.is_file() and p.name.startswith("gecko-transport")], "binding": pointer(RUN / "operation-binding.json")}
    write(RUN / "execution-receipt.json", receipt)
    output = read(RUN / "engine-stdout.json")
    summary = module.classify(output, code)
    write(RUN / "boundary-summary.json", summary)
    engine = output.get("run", {})
    state(status="terminal-evidence-ready", terminal="completed" if code == 0 and engine.get("exitCode") == 0 and not engine.get("timedOut") else "failed", onlineExecuted=True, wrapperPid=None, cliPid=child.pid, cliPidAlive=False, engineEndedAt=ended, exitCode=code, engineExitCode=engine.get("exitCode"), timedOut=engine.get("timedOut"), rawDirectory=str(RUN), executionReceipt=pointer(RUN / "execution-receipt.json"), boundarySummary=pointer(RUN / "boundary-summary.json"), harnessHealthy=summary.get("harnessHealthy"), forms=summary.get("forms"), submits=summary.get("submits"), serverAccepted=False)
    print(json.dumps({"status": "terminal-evidence-ready", "runId": RUN_ID, "exitCode": code, "engineExitCode": engine.get("exitCode"), "timedOut": engine.get("timedOut"), "forms": summary.get("forms"), "submits": summary.get("submits"), "nativeLogFiles": len(receipt["nativeLogs"])}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "execute"])
    args = parser.parse_args()
    try:
        prepare() if args.phase == "prepare" else execute()
    except Exception as error:
        state(status="failed", terminal="failed", wrapperPid=None, errorType=type(error).__name__)
        print(json.dumps({"status": "failed", "errorType": type(error).__name__}))
        sys.exit(1)
