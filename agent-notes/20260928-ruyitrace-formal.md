# 2026-09-28 formal RuyiTrace

## next override

`web_case.py next --project D:\reverse_ENV\workspace\psa_solve` returned `action=ruyidom_run` (browser fact already present; local RuyiDOM before opcode/v8trace). User override: run a formal RuyiTrace anyway. browser-control stayed skipped. Not ruyipage, not CDP, not the old public `ruyi_trace_*` tools, and `traceEnabled` was not set.

## product hit

`article/web-reverse/products.md` has no standalone Cloudflare managed-challenge subsection. The matching row is Cloudflare 5s challenge (`challenge-platform`, interstitial, `cf_chl_` / `cf_clearance`). Child product doc was not read. 2026-08-16 challenge-material was not used as this round's input. Prior bundle `rt_20260902054213_014bc111c5` (runtime 3.1.0, profile challenge-fast) was contrast only.

## capture

- runtime_status before start: appVersion 3.3.0, BuildID 20260913011646, verification=verified. No runtime_sync.
- runId: `rt_20260928061614_ee71af43b2`
- mode interactive, durationSeconds 70, profile dom-observe, fingerprintMode baseline, proxy direct, sensitivity private-redacted, gated false
- URL class: cert page on www.psacard.com (same path as the prior contrast request)
- startedAt 2026-09-28T06:16:14.714Z, capture_stop requested at the end of the window, finishedAt 2026-09-28T06:17:48.803Z
- capture_status: state completed, phase completed, artifactCount 298, partitions cookie/descriptor/domtrace/eval/event/http_packet/storage. Artifact pointers were not listed.
- JSCall was not enabled. jscall partition is empty.

## counts

Indexed `http_packet` events only. No cookie, token, fingerprint, Set-Cookie, or body values.

| path class | events |
|---|---|
| orchestrate (`.../orchestrate/chl_page/v1`) | 2 |
| `/cdn-cgi/challenge-platform/` fo | 8 |
| eb/managed | 0 |
| jsd/oneshot | 2 |

Main document GET status 403. `cf-mitigated` appeared once, value `challenge`, on that GET. Same path also has one POST 200 without that header. This is presence of a managed-challenge window, not a solve success or failure, and not serverAccepted.

## gates

- runtime-hash pass, evidence-index pass, evidence-receipt pass
- integrityReceipt artifact `receipt-fe80c7e81d7b`, sha256 `c32374d0b74e94bba7c61e0e365042b83930bb72b67482a280f366067b76ad5c`, receipt `integrity=pass`
- HTTP writer and sampled DOMTrace/cookie/descriptor/eval/event/storage writer tails: dropped_* = 0, io_errors = 0
- `web_case.py run --plane ruyitrace --run-id rt_20260928061614_ee71af43b2` succeeded. web-case status remains `patching`. Stages were not changed.

## pointers

- `evidence/web/ruyitrace/rt_20260928061614_ee71af43b2/evidence-run.json`
- `evidence/web/ruyitrace/rt_20260928061614_ee71af43b2/receipt.json`
