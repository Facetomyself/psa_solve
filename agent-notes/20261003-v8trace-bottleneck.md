# 20261003 V8Trace bottleneck slice

Case: `psa-cf-5s-shield-20260815`. CLI only (`mcp/v8trace-mcp/dist/cli.js`). No stdio MCP. No Proxy. No host-getter patches. No auto-decision-facts write.

## Runtime

- patched Node `status`: ready, Node `v20.19.0`, SHA matches lock.
- Chromium `chromium-status`: lock-ready (required-file hash pass, Chromium 151.0.7922.72). **Launch is not ready.** `chromium/locales/` has no `en-US.pak`. Direct `chrome.exe --headless=new about:blank` FATAL `Check failed: !actual_locale.empty()` (crash key `LocaleDataPakExists-not_found_path`). Exit `0x80000003`. Do not treat lock-ready as capture-ready.

## Historical patched-Node runs (stub DOM)

All `challenge-fast` on `v8trace_orchestrate_runner.js`. elapsed ~0.05s. stdout `{ok, chlOptKeys:21, xhrCount:0}`. request-call only `node:net` fd open, not FO/document POST. createElement/submit only `define` of stubs, **zero** `envcall` createElement / form.submit. throw=1: `TypeError: T[rv(...)][rv(...)] is not a function`.

| runId | records | miss | throw | call | createElement envcall | FO/form |
|---|---:|---:|---:|---:|---:|---|
| v8-20260815070607-0a39cz | 1415 | 37 | 1 | 14 | 0 | none |
| v8-20260815071000-g8sotl | 1418 | 37 | 1 | 14 | 0 | none |
| v8-20260815075849-x7h32q | 1421 | 37 | 1 | 14 | 0 | none |

Query `--kinds call --prop createElement` on x7h32q: matched 0. `_cf_chl_opt` is a runner `set` of the injected object, not live CF.

These runs cannot explain headed form.submit vs FO `cf-chl-out` body-length 3488 → createElement(h2) diagnostic.

## Chromium Studio capture (opt-in kernelCompare; not browser fact)

URL from existing runner: `https://www.psacard.com/cert/143963534/psa`. preset `env-hooks`, duration 90s, not gated.

- interactive `c0f25fc8705f7376f`: failed in ~2s, `collector exited 1`. No window. Switched to headless as specified.
- headless `c9aa53202a6309169`: same fail. No events, no index, no receipt.

Secondary worker issue: worker `mkdir capture/` then collector requires a **new** output dir (`Capture output already exists`). Even with a fresh dir, Chrome dies on missing locale pak.

No `chromium-index` / bounded query. No form vs h2 observation on this plane.

Fact suggestion for main thread (do not write facts here): keep `browserFactPlane=ruyitrace`. Do **not** record `v8trace-chromium` as browser fact. Optional note `chromiumCapture=failed` / locale-pak gap. `kernelCompare` remains unsatisfied.

## New patched-Node gap catalog (explicit stub)

`run --profile challenge-fast --allow-failure` → `v8-20261003021537-lhw7em` (CLI state completed, targetExitCode 1).

- records 1421, miss 39, throw 1 (same TypeError), call 14.
- envcall: now / setInterval / setTimeout / Object.keys / promise internals.
- request-call: `node:net` open ×2 only.
- xhrCount=0. No FO. No document POST. No createElement envcall. No form.submit.
- **stub DOM, cannot explain 3488 diagnostic branch.**

Not an executor. Patches stay Gecko.

## stop-search

No new external request-boundary (method/url/status/body-length class or target submit appearing). This slice does not clear `experimentHygiene=stop-search`. Do not resume adjacent getter search.

## Receipts

None from round 1. Chromium gates evidence-index / evidence-receipt still pending on failed runs.

## Round 2 — Chromium headless env-hooks (after locale copy)

`chromium-status` lock-ready. Did **not** `chromium-sync --force`. Did **not** rerun patched Node. Did **not** write `auto-decision-facts.json`. Did **not** `chromium-receipt` (three gates not all pass).

Failed worker-owned starts after locale copy: `cac97b133cb5c4acc` (worker `mkdir capture/` then collector `Capture output already exists`; elevated Chrome de-elevate parent exits before CDP). 152 `en-US.pak` is **not** lock-blessed; 151 zip locales required to avoid `l10n_util.cc` DCHECK `$1`.

Live capture that produced events: `c266ff812e0facbf7` (collector via `--do-not-de-elevate` shim, preset `env-hooks`, 90s requested, **not gated**). Collector `stopReason=budget` at ~58s (`startedAt` 02:33:47Z → `finishedAt` 02:34:45Z). `eventCount` 3185 / `recordedBytes` ~256MiB. `integrityConclusion=partial`. Critical gap `capture-byte-budget`. CLI `capture-status` stays `state=queued` / `phase=preparing` because worker never owned the collector; `capture-stop` only moved phase to `flushing`.

`chromium-index`: http 159, script 266, env 2620, console 29 (`indexedRecords` 3074; lifecycle.jsonl present but not in index partitions). Gates: runtime-hash pass, evidence-index pass, evidence-receipt **pending**.

Bounded `chromium-query` (limit 20, partitions required):

| selector | returned | note |
|---|---:|---|
| env text createElement | 20 (truncated) | Document.createElement live |
| env text form | 20 (truncated) | substring noise; **zero** tag `form` / HTMLForm |
| env text submit | 0 | no form.submit envcall |
| env text h2 | 7 | includes two createElement("h2") |
| http text `/fo` | 12 | three FO XHR POST cycles |
| http url cf-chl-out | 0 | |
| http kind POST | 0 | kind is CDP event type, not method |

JSONL scan (sanitized): GET cert Document **403** `cf-mitigated` challenge. `Document.createElement` enter tags: script/div/span/iframe/input/textarea/…; **form=0**. createElement("h2") at 02:33:49.256Z and 02:33:49.277Z (~T+1.3s, **before** first FO). FO XHR POST 200 encodedDataLength **413** (psacard `/cdn-cgi/challenge-platform/h/b/fo`), then **925** and **163** (challenges.cloudflare.com same path class). All FO `type=XHR`. **No document POST. No cf-chl-out.** HeadlessChrome / turnstile path.

This is **not** the headed form.submit success branch and **not** the 3488-body → ~10s diagnostic h2. `stop-search` / `refuse_host_enumeration` unchanged. Do not register `browserFactPlane=v8trace-chromium`. `serverAccepted` false.

## 2026-10-03 retry after locale copy

Main thread copied 228 locale paks from `tools/chromium/chrome-win` (152.0.7923.0) into the locked 151 tree. `en-US.pak` is 595458 bytes. These files are outside the lock `requiredFiles`, so lock-ready still does not mean the pak is blessed.

- `cac97b133cb5c4acc`: headless, collector exit 1 in ~2s, `Chrome exited before CDP startup` code 0. No events.
- `c266ff812e0facbf7`: headless `env-hooks` collected. Chrome/151.0.7922.72. counts lifecycle 111, http 159, env 2620, script 266, console 29. `stopReason=budget` at 256 MiB, `integrityConclusion=partial`. Index exists (`indexedRecords=3074`). `evidence-run.json` stayed `queued` in the wrapper. Not a browser fact. No receipt.

Bounded counts (no URL, cookie, or body):

- `Document.createElement` tags include `h2` 2 and `p` 7. Tag `form` is absent. No `HTMLFormElement.submit`, `Document.write`, or `innerHTML` binding.
- `XMLHttpRequest.open` is `POST` `/fo/` ×3. `getResponseHeader` saw names `cf-chl-out` ×2 and `cf-chl-out-s` ×2.
- Three `request-complete` FO rows are HTTP 200. Post body lengths 2370, 4791, 92439. No page-host document POST class.
- This headless window shows the diagnostic element branch and no form branch. Byte budget cut the tail, so a later form is not observed and also not ruled out past the cutoff.

`stop-search` stays. This capture does not add a new external request boundary that would reopen adjacent host getters. Patches stay on Gecko.

## Reconciliation

Round 2 timing wins over the tag counts above. The two `createElement("h2")` calls are at ~T+1.3s, before the first FO, so they are interstitial UI. They are not the ~10s diagnostic `h2` after a 3488 `cf-chl-out` body. `getResponseHeader("cf-chl-out")` calls do not mean the response carried that header; the HTTP query for `cf-chl-out` is 0. FO responses in this window are XHR 200 with encoded lengths 413 / 925 / 163. Cert document GET is 403 `cf-mitigated`. No form, no document POST.
