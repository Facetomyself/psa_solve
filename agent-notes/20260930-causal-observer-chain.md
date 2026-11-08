# Causal observer chain — 2026-09-30

status: classified (receipt remains `executed-hold`; harness only)
chainClass: **complete-to-diagnostic**
gate: `refuse_host_enumeration` / `turnGate=blocked` / `experimentHygiene=stop-search` / facts revision=4
proxy.type=0 preserved. No new host search. No environment_patch. Budget spent; do not second-claim.

Evidence:
- live summary: `agent-notes/20260930-causal-observer-live.md`
- receipt: `evidence/web/diagnostic-causal-observer/receipt.json`
- session: `evidence/web/diagnostic-causal-observer/restricted/a7e045b6cf194921bb229b6741e59b8b`
- claimId `90aa1f82-e1ee-447e-aeeb-2b9c0c865fb9` / sessionId `a7e045b6cf194921bb229b6741e59b8b`

Re-verify from raw probe (not summary-only): `hasFormCreate=false` (`forms=0`, no `createElement` tag=form), `hasSubmit=false` (`submits=0`, `submitEv=0`, no `form.submit` kind), `certDocumentPostObserved=false` (no `/cert/` in respLog). `inps=1` is an input without a form.

No new external request-boundary difference: same 7-row table as the live summary; 3488 is a length label of the opaque `cf-chl-out` body, not a boundary move. urllib→Gecko remains logical material handoff, not same TLS.

## Acceptance hops

Contract: FO request hash → response hash whose HEADER NAME set includes `cf-chl-out` (boolean only) → first DOM write/createElement after that response → form/submit **or** redacted diagnostic-copy class.

| hop | seq | kind | role / realm | method | status | protocol | reqLen | cf-chl-out name | body length class | tagShape bucket | textShape |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 14 | request | challenge-fo / page-host | POST | — | h3 | 8695 | n/a (request) | — | — | opaque (FO body hash prefix `a163b527a43f`) |
| 2 | 15 | response | challenge-fo / page-host | POST | 200 | h3 | 8695 | **true** (`cf-chl-out-s` also true) | **3488** (label only) | — | opaque (response hash prefix `1e2d4261adff`; `chlOut=noform`; `chlAlpha=3488:u64:out0`) |
| 3 | 16 | createElement | after hop-2 | — | — | — | — | — | — | other (`h2`) | diagnostic-copy |
| 4 | 16–25 + causalFinal | DOM tail | after hop-2 | — | — | — | — | — | — | other (`h2`,`p`,`ol` + `a`) | diagnostic-copy (no form-markup) |

Hop 4 is diagnostic-copy, not form/submit. Chain class = complete-to-diagnostic.

## Events after last challenge-fo response

Last (and only) causal `response` is seq=15, t=8802, pathClass=challenge-fo, status=200, len class 3488. `tInner=8802` (opaque decode at the same tick). `tH2=19064` (~10s later). All later causal events:

| seq | t | kind | tagShape bucket | textShape | notes |
| --- | --- | --- | --- | --- | --- |
| 16 | 19064 | createElement | other (`h2`) | diagnostic-copy | first DOM after hop-2 |
| 17 | 19065 | innerHTML | none | diagnostic-copy | len=39, no tags (text into diagnostic node) |
| 18 | 19066 | createElement | other (`p`) | diagnostic-copy | |
| 19 | 19066 | innerHTML | none | diagnostic-copy | len=89 |
| 20 | 19067 | createElement | other (`p`) | diagnostic-copy | |
| 21 | 19067 | innerHTML | none | diagnostic-copy | len=16 |
| 22 | 19067 | createElement | other (`ol`) | diagnostic-copy | |
| 23 | 19068 | innerHTML | none | diagnostic-copy | len=93 |
| 24 | 19068 | innerHTML | other (`a`) | unknown | len=84 |
| 25 | 19069 | innerHTML | other (`a`) | unknown | len=145 |

`tail` shape: `ce:div,ce:div,ce:h2,ce:p,ce:p,ce:ol,ce:li,ce:li`. No `ce:form`. No `form.submit`.

## Pre-response causal (not hop-3)

seq 1 `document.write` is the challenge bootstrap (tagShape includes `html,head,script,title,meta`; bucket=script; len=6059). seq 2–10 are interstitial `h2`/`p`/innerHTML **before** any FO. seq 11 is an earlier page-host FO request (POST 2252, hash prefix `a76a3fc22309`) whose XHR live row has `cf-chl-gen=true` and `cf-chl-out=false` (body bytes 106876, not a length-label 3488/3792). Those are not the acceptance hop-1/2 pair.

Top-level XHR wrapper saw `foSeen=2`. Necko respLog still has 5 challenge-fo POST h3 (page 2252 + 8695; challenge-host 4738 / 83372 / 86530). The extra three are not in `causalTrace` (iframe/widget). None of them is cert-document.

## Request/response boundary (role only; no URLs)

| order | role | realm | method | status | protocol | reqLen | cf-chl-out name | body length class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | other | page-host | GET | 200 | h3 | -1 | not in XHR live | — |
| 2 | challenge-fo | page-host | POST | 200 | h3 | 2252 | false (live row 1; `cf-chl-gen=true`) | 106876 (not 3488/3792) |
| 3 | challenge-fo | challenge-host | POST | 200 | h3 | 4738 | not in top-level XHR live | — |
| 4 | other | unresolved (`g` path class; h2) | GET | 200 | h2 | -1 | not in XHR live | chanLen 5307 |
| 5 | challenge-fo | challenge-host | POST | 200 | h3 | 83372 | not in top-level XHR live | — |
| 6 | challenge-fo | challenge-host | POST | 200 | h3 | 86530 | not in top-level XHR live | — |
| 7 | challenge-fo | page-host | POST | 200 | h3 | 8695 | **true** (live row 2) | **3488** |

No cert-document POST. 3488/3792 remain length labels, not pass/fail.

## causalFinal (keys only)

Present keys: `title`, `text`, `textLen`, `textSha256`.
Final DOM class: **diagnostic** (title keyword class diagnostic-copy; `textLen=717`; no form-word; no form-markup). Not form. Not unknown.

## Implications

- Observation of the contracted chain is complete: it lands on diagnostic-copy, not form/submit.
- Still `refuse_host_enumeration`. `widgetComplete` / exit 0 / `executed-hold` are not business pass.
- Do not restore adjacent host-field search. Do not write `serverAccepted` / `localReproduced`.
- The 3488 opaque payload is the already-recorded length label, not a new request-boundary difference.
