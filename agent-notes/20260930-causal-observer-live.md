# Causal observer live — 2026-09-30

status: done (receipt=`executed-hold`; harness only, not business acceptance)

- receipt: `evidence/web/diagnostic-causal-observer/receipt.json`
- claim-binding: `evidence/web/diagnostic-causal-observer/claim-binding.json`
- session dir: `evidence/web/diagnostic-causal-observer/restricted/a7e045b6cf194921bb229b6741e59b8b`
- boundary summary: that session `boundary-summary.json`
- claimId: `90aa1f82-e1ee-447e-aeeb-2b9c0c865fb9`
- spawned: true
- cliPid: 18944
- exitCode: 0
- profile: `psa-20260930-causal-observer-transport-fixed`
- argv: Node + RuyiDOM CLI `run --allow-network` + reviewed observer; timeout 120s; pumpMs 30000
- proxy.type=0 preserved; no environment_patch; no host enumeration

## Restricted classification

- harnessHealthy: true
- widgetComplete: true
- forms: 0
- submits: 0
- causalEventCount: 25
- causalKinds: document.write, createElement (×7), innerHTML (×14), request (×2), response (×1)
- hasFormCreate: false
- hasSubmit: false
- causalFinalPresent: true
- certDocumentPostObserved: false
- businessAccepted: false (`not-proven`; executed-hold is harness, not `serverAccepted`)

## Request boundary table (role / method / status / protocol only)

| order | role | realm | method | status | protocol | document |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | other | page-host | GET | 200 | h3 | false |
| 2 | challenge-fo | page-host | POST | 200 | h3 | false |
| 3 | challenge-fo | challenge-host | POST | 200 | h3 | false |
| 4 | other | unresolved | GET | 200 | h2 | false |
| 5 | challenge-fo | challenge-host | POST | 200 | h3 | false |
| 6 | challenge-fo | challenge-host | POST | 200 | h3 | false |
| 7 | challenge-fo | page-host | POST | 200 | h3 | false |

No cert-document POST. 3488/3792 remain length labels only, not pass/fail.

## Independent receipts (byte-identical; not consumed)

| receipt | status (unchanged) |
| --- | --- |
| diagnostic-cleanup-baseline | executed-hold |
| diagnostic-instrumentation | claimed-not-started |
| diagnostic-instrumentation-v2 | executed-hold |

factsUnchanged: true (`experimentHygiene=stop-search`, `serverAccepted=false`, `ruyidomNetwork=live`, `firstDivergence=environment-gap`, `revision=4`). `localReproduced` left false. `web_case.py` record returned `refuse_host_enumeration` / `turnGate=blocked`.

## Limitations

- no new independent business-content readback
- urllib UA135 fetch → Gecko is logical cookie/material handoff, not same TLS / same navigation
- older observation hooks retained (not a zero-instrumentation runner)
- budget is 1 and spent; failure would not refund; do not second-claim
- causalFinal present without form/submit does not authorize adjacent host search
