# Firefox trace plan: receiver provenance

Date: 2026-10-05. Scope: read-only settings/contract audit; no capture, browser, target access, MCP start, migration apply, gate edit or acceptance fact update. Handles: none.

## Decision

A new trace is useful only if it captures fresh, source-aligned receiver provenance together with the local execution of that same source. Repeating the existing DOM-only pass will not resolve the harness typing defect or prove `localReproduced`/`serverAccepted`. First use the current DOM records' receiver identities to locate body/query/creation operations; new capture should answer a named gap those records cannot answer.

The recent run `rt_20261005054520_0e24cdbc08` used `interactive`, 90 s, traceLimit 500000, `dom-observe`, `gated=false`, `fingerprintMode=baseline`, direct proxy, `private-redacted`. Its receipt has integrity pass, 346 artifacts, 1,100,849,317 bytes and no extraIndexed entries. `raw/domtrace/trace_process_52288.ndjson:98` records `Q`/column 172017 calling `Element.attachShadow`, receiver `HTMLBodyElement`, return `ShadowRoot`. `thisObj` includes `id` and `nativeId`; `argsObj` contains shallow `Object`, not the `mode` property. This is not the historical local `It` source and cannot establish its exact creation/query origin.

## Confirmed settings and boundaries

- `profile` is a label; selected switches come from `preset ?? profile`, then explicit `switches` overrides (`capture.ts:331`). There is no preset list/composition field. A `jscall-detail` capture with the four env switches must specify those switches explicitly.
- Worker owns `MOZ_DOM_TRACE=1`, trace path/run id/limit/gate and output directories (`worker.ts:121`). Caller cannot override those or any `*_FILE`/`*_DIR`. The core captures DOM operations, descriptor, eval and HTTP; existing records prove receiver/return class and identities. Core serialization of a generic object argument is shallow; raising string limits does not add object property depth.
- `env-probe` adds `MOZ_DOM_ABSENT_PROBE=1`, `MOZ_DOM_IFACE_PROBE=1`, `MOZ_DOM_HOST_MUTATION=1`, `MOZ_DOM_ENV_INVENTORY=1`. These cover names/interface availability/mutations/inventory, not receiver creation provenance or deep arguments. Inventory writes once per process. Add it only if a concrete interface/prototype question remains.
- `jscall-detail` adds JSCall, total limit 100000, per-function limit 1024, function stats and MAX_VALUE_BYTES=1024. It does not select any detailed function until `MOZ_DOM_JSCALL_DETAIL_SCRIPT_URL` or `DETAIL_NATIVE` is supplied.
- `MOZ_DOM_JSCALL_SCRIPT_URL` controls which calls are recorded, not parameter depth. `MOZ_DOM_JSCALL_DETAIL_SCRIPT_URL` selects JS functions' arguments, this and return. `MOZ_DOM_JSCALL_DETAIL_NATIVE` selects native names; native object parameters are identity-only, not object contents. It automatically enables native records if `JSCALL_NATIVE` was omitted, but setting `MOZ_DOM_JSCALL_NATIVE=1` explicitly makes the intended configuration reviewable.
- URL/name filters are case-sensitive substring lists separated by comma/semicolon, not regex or wildcard. Native filtering is by unqualified name and can match unrelated browser functions; avoid broad `load` or unrestricted native detail.
- Decoder exposes `argN`, `this`, `return`, type, bytes, truncated/unreadable/identity-only flags (`scripts/jscall_decode.py:139`). Stable identities start `#`; `?` means unstable and must not be joined. Which DOM identity field joins the JSCall value must be verified on actual paired records, not assumed from matching hex width.
- Normal JSCall `.bin` is indexed with `.dict.jsonl`, up to 200000 records. `.detail.bin` remains an artifact: indexer does not expand it. Decode using `jscall_decode.py --values`; storing detail is not evidence that MCP query returns the values. JSCall has no timestamps, file order is leave order and call_id is enter order; parent ids are not always immediate caller under JIT.

## Minimum useful fresh Firefox capture

Only after dispatcher permits capture, verify runtime `appVersion=3.3.0`, `verification=verified`, Firefox 155.0.1/BuildID 20260913011646. Use `mode=interactive`, `fingerprintMode=baseline`, `gated=false`, a fresh profile/session, and bounded duration ending after the response branch. Do not replay response bodies, cookies or tokens.

For this specific provenance hypothesis (not the generic env-patch default):

```json
{
  "profile": "receiver-provenance",
  "preset": "jscall-detail",
  "mode": "interactive",
  "durationSeconds": 60,
  "traceLimit": 500000,
  "gated": false,
  "fingerprintMode": "baseline",
  "switches": {
    "MOZ_DOM_JSCALL_SCRIPT_URL": "/cdn-cgi/challenge-platform/h/b/turnstile/",
    "MOZ_DOM_JSCALL_DETAIL_SCRIPT_URL": "/cdn-cgi/challenge-platform/h/b/turnstile/",
    "MOZ_DOM_JSCALL_NATIVE": "1",
    "MOZ_DOM_JSCALL_DETAIL_NATIVE": "createElement,createElementNS,querySelector,getElementById,getElementsByTagName,attachShadow",
    "MOZ_DOM_JSCALL_SOURCE": "/cdn-cgi/challenge-platform/h/b/turnstile/"
  }
}
```

Replace the URL substring with the actual targeted family observed in the current fresh script map; the h/b path is not a universal constraint. Include the page orchestrate family only if the gap moves to its response callback. Do not indiscriminately trace all CF or all page JS. `SOURCE` saves executed source through the core eval writer; a URL filter can miss anonymous/eval source names, so verify actual saved artifacts instead of assuming coverage.

Core DOM records should provide body/getter/query/create return identity, attachShadow receiver/return class and initiating source location. Native detail should provide primitive creation/selector arguments and object identity. Script detail may expose the wrapper's argument content and callback invocation; it is not a guarantee of deep native options such as `{mode:'closed'}`. The current runtime has no confirmed generic depth switch. `env-probe` is optional, not required for this narrow identity problem. Keep opcode, BASELINE, full event, builtin-error, IDB value, API overrides and unrestricted closure capture off.

For the separate response-to-form hypothesis, HTTP packet already supplies real request/response artifacts. Core XHR/event/callback records plus targeted script detail may connect response callbacks to DOM actions; no single preset guarantees callback registration+entry+response causality. Acceptance requires proving that chain in the collected records. Deepening JSCall does not convert a clearance response or cert POST into the required independent business readback.

## Closure and acceptance of the evidence run

Graceful capture_stop is mandatory to drain the asynchronous writers. Check core/HTTP writer stats and final `jscall_stats`: dropped_* and io_errors must be zero, no reached/truncation limit relevant to the target window. Index normal JSCall before querying; explicitly decode detail sidecars with dictionaries and save bounded target excerpts. Match source/hash and fresh session provenance before comparing local and browser receivers. No cross-run id joins. Receipt integrity pass alone does not prove semantic coverage or completeness after limits.

## Contract migration check

`web_case.py migrate-contracts --project ... --case-class challenge --check` returned `migration-required`, missing `[metadata.currentHead]`, revision 3. No apply was performed.

This label is misleading if read as a missing JSON field. The actual `contracts/case-metadata.v1.json` has **top-level** currentHead `6346bdeaf96416ab5e29eec5f402a3633e12f925`. `case_metadata_errors()` compares `metadata.get('currentHead')` against `_repository_head()` and uses the same error label for mismatch. `_repository_head()` runs git in dispatcher ROOT, `D:\reverse_ENV`, not the project repository.

At audit time root HEAD was `fa8d5fe7f6ab5e0212515e4b2ed8da0421662383`; project HEAD was `1bc5ca86f9103cf66376699614b7119e580841af`. Therefore the cause is stale root HEAD metadata, not absent field/nesting and not a project HEAD defect. Explicit migration may refresh metadata/revision through the dispatcher action, but it does not unlock the underlying host-probe stop gate or establish new browser facts.

## Sources

- `skill/web-reverse/references/ruyitrace-capture.md`, `ruyitrace-fpfile.md`
- `mcp/ruyitrace-mcp/config/capture-presets.v1.json`
- `mcp/ruyitrace-mcp/docs/domtrace-cheatsheet.md`
- `mcp/ruyitrace-mcp/src/capture.ts`, `worker.ts`, `indexer.ts`, `jscall-decode.ts`
- `mcp/ruyitrace-mcp/scripts/jscall_decode.py`
- `skill/web-reverse/scripts/web_case.py:1140`, `:1215`
- Latest run request/receipt and the single receiver record cited above; `agent-notes/receiver-static-review-20261005.md`, `20261004-realm-probe.md`, `20261003-v8trace-settings-audit.md`

Remaining blocker: current dispatcher contract migration is unresolved; source-aligned receiver creation/query evidence is not yet established. This plan starts no new experiment and does not authorize host enumeration.
