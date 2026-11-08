# 2026-10-03 headed Chromium capture

Direct collector capture. Not a browser fact. No `chromium-receipt`. No `auto-decision-facts.json`. No patched Node. No `chromium-sync --force`.

- Node: locked runtime `V8Trace-optimized-20261002\runtime\node.exe` (Node 24)
- CLI: same tree `app\v8-trace\cli.js` `capture`
- Chrome shim: `temp\agent-runs\chrome-dne.exe` (`--do-not-de-elevate` in front of locked Chromium 151)
- Output: `workspace\psa_solve\evidence\web\v8trace-chromium\headed-20261003\capture`
- Run directory name: `headed-20261003`
- Window: visible, title class cert-verification, about 1265x1380, before the collector exited
- Runner process exit: 1. On-disk summary is `captureConclusion=collected` and `integrityConclusion=partial` (this CLI's contract for partial is exit 2). Treat as collected.

Flags that matter: `headless=false`, `hooks=true`, `cpuProfile=false`, `nativeTimeline=false`, `opcode=false`, `rawCdp=false`, `maxBytes=1073741824`, `maxEvents=200000`, `durationSeconds=120`.

## 1. Headed product

`launch.json` args do not contain `--headless=new` or any headless flag. `options.headless=false`. `browser.json` product token is `Chrome`, not `HeadlessChrome`. UA product token is `Chrome`. `browserVersion` `Chrome/151.0.7922.72`. Browser exit code 0. stderr is 14 untagged lines (DevTools listen, GCM, ssl_client, egl). No de-elevate failure and no CDP-before-exit.

## 2. Cert document

| t_s | method | type | status | encoded | cf-mitigated header name |
|---:|---|---|---:|---:|---|
| 0.696 | GET | Document | 403 | 4139 | yes |
| 31.335 | POST | Document | 200 | 24653 | no |

The POST has post data and initiator type `other` (not `script`). It is not a redirect hop.

## 3. `/fo/`

Five HTTP requests, all `POST` / `XHR` / status 200. Header-name presence is the response header map, not `getResponseHeader` calls.

| t_s | class | encoded | cf-chl-out | cf-chl-out-s |
|---:|---|---:|---|---|
| 2.149 | fo-pagehost | 81560 | no | no |
| 3.484 | fo-cf | 575840 | no | no |
| 12.079 | fo-cf | 86784 | no | no |
| 30.453 | fo-cf | 8472 | yes | yes |
| 31.137 | fo-pagehost | 4953 | yes | yes |

`XMLHttpRequest.getResponseHeader` lookups: `cf-chl-out` ×3, `cf-chl-out-s` ×3. Lookups are not the same fact as response header names. Five `XMLHttpRequest.open` POST calls used a relative `/fo/` class path (no host on the argument). One later relative open was challenge-platform but not `/fo/`.

## 4. createElement

`Document.createElement` enter counts include `form` 3 and `h2` 2. Full tag map is in the sibling json.

- `h2` at t=1.718s and 1.731s. First `/fo/` is t=2.149s, so h2 is 0.431s and 0.418s **before** the first FO. Interstitial UI. Not the ~10s-after-FO diagnostic h2.
- `form` at t=31.317s, 34.450s, 35.458s. The first is 18ms before the cert Document POST. The later two are after that POST.

## 5. submit

No env event whose binding contains `submit`. No `HTMLFormElement` binding. Diagnostic hooks do not install `HTMLFormElement.submit`, so a missing binding does not prove the method was not called. The cert-path Document POST above is the navigation fact.

## 6. Stop line

`stopReason=duration`. `eventCount=29622`. `integrityConclusion=partial`. `criticalGapCount=6`, all `response-body-unavailable` (1 classed fo-pagehost, 5 other). Two non-critical `request-open-at-stop`. Counts: lifecycle 387, http 1636, env 27056, script 512, console 30, exception 1. `recordedBytes` 167372273. Duration 121.476s from `startedAt` 2026-10-03T03:07:09.777Z. Not a byte-budget cut. Hook gap count 0.

## Against headless `c266ff812e0facbf7`

Headless was HeadlessChrome, cert GET 403 only, three FO XHR 200 with encoded lengths 413/925/163, no `cf-chl-out` response header name, `form=0`, no document POST, `stopReason=budget` near 58s / 256MiB. This headed run still has the early h2, and it also has the later form element plus a cert-path Document POST 200 after two FO responses that carry `cf-chl-out` and `cf-chl-out-s` header names. That is the headed completion branch, not the headless diagnostic-only branch. It is not the previously hypothesized 3488-body then ~10s h2 sequence.

Do not register `browserFactPlane=v8trace-chromium`. Runtime-hash / evidence-index / evidence-receipt were not all passed on this direct collector directory.

## Pass check

The stuck point for this case is the missing cert document POST and the diagnostic DOM. This headed window passes that browser step.

- Cert Document GET 403 body is the challenge page (`Just a moment`, about 6KB).
- `cf_clearance` set-cookie name appears at t=31.313s on the page-host `/fo/` XHR 200, and again at t=34.058s on a page-host `/cdn-cgi/` XHR 200. Values were not recorded here.
- Cert Document response at t=31.887s is HTTP 200, about 153KB, title class cert verification, with a certification-number marker.
- Local Gecko `serverAccepted` stays false. This file is a headed Chromium observation, not the local solver readback.
