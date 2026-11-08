# Node solver sessions / 2026-10-20

Two fresh processes of `runtime/run.js`. Each process fetched its own challenge page and orchestrate script, then ran that entry. No browser session, cookie, or historical challenge body was copied in.

## Request class

| | session 1 | session 2 |
| --- | --- | --- |
| page fetch | 403, title length 16 | 403, title length 16 |
| orchestrate fetch | 200 | 200 |
| solver requests | none | none |
| certificate document POST | no | no |
| orchestrate stage | TypeError, empty message | TypeError, empty message |
| same-lease read about 5s later | status 403, pageKind challenge, title length 16 | status 403, pageKind challenge, title length 16 |

The two runs agree: the certificate document POST did not happen, and the readback is still the challenge document.

## Browser oracle

`agent-notes/trace-compare-20261005.md` records the headed oracle: clearance exchange, then certificate document POST status 200. That POST alone is not `serverAccepted`. The Node runs have no clearance exchange and no document POST, so the classes do not agree.

## Facts

`serverAccepted`, `localReproduced`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `stop-search`. These captures do not contain a request-boundary difference other than an empty request list.

## Host change in this round

Returned ShadowRoot `appendChild` now keeps a caller-supplied child that was not pre-tracked. The id query then returns that same child. A missing id stays null. Surface test: 39 passed, `targetExecuted=false`. `Document.createElement` was not opened. The Node environment shim was not rewritten.

## Stamped rerun / 2026-10-20T11:48Z

`web_case.py next` stamped `rerun_host_baseline` and persisted `hostProbe=awaiting-record`. The same Node entry was run again from two fresh sessions. Receipt: `diagnostics/shadowroot-repair-20261020/node-rerun-receipt.json`.

| | session 1 | session 2 |
| --- | --- | --- |
| started | 2026-10-20T11:48:56.424Z | 2026-10-20T11:49:34.951Z |
| page fetch | 403, 5598 bytes, title length 16 | 403, 5598 bytes, title length 16 |
| orchestrate fetch | 200, 262128 bytes | 200, 250866 bytes |
| solver request classes | none | none |
| solver response classes | none | none |
| certificate document POST | no | no |
| orchestrate stage | error, stage name only | error, stage name only |
| same-lease read about 5s later | 403, challenge, title length 16, body length class 5000-19999 | 403, challenge, title length 16, body length class 5000-19999 |

The two runs agree. The append change did not change method, URL class, status, body-length class, or whether the certificate document POST appeared. Classification for this record is `boundary-unchanged`.

## Parity against the headed oracle

The headed oracle in `agent-notes/trace-compare-20261005.md` has a clearance exchange and then a certificate document POST, method POST, status 200. These Node runs have no solver request, so they have no method, URL class, status, or body-length class for that exchange or that POST. The classes do not agree. The 403 challenge readback is not the certificate page.
