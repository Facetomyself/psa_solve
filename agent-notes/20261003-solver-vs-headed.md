# Solver vs headed Chromium — 2026-10-03

Local evidence: causal observer `a7e045b6cf194921bb229b6741e59b8b` (2026-09-30).
Headed evidence: `evidence/web/v8trace-chromium/headed-20261003`.
No cookie values, tokens, or body bytes copied here.

## Same FO skeleton

Both runs send five `/fo/` POSTs and reach `text/html` on the fourth and fifth.

| hop | local req bytes | headed req bytes | local type | headed type |
| --- | ---: | ---: | --- | --- |
| page | 2252 | 2380 | text/plain | text/plain |
| cf | 4738 | 4748 | text/plain | text/plain |
| cf | 83372 | 92460 | text/plain | text/plain |
| cf | 86530 | 95735 | text/html | text/html + cf-chl-out |
| page | 8695 | 9132 | text/html + cf-chl-out + cf_clearance name | text/html + cf-chl-out + cf_clearance name |

## Where the solver leaves the pass path

Headed Chrome builds `form` about 0.2s after those html responses, then the cert document POST returns the cert verification page.

The local probe parsed the first top-level `cf-chl-out` body as `noform:::scr0:nosubmit` (length class 3488, no `<form`, no `.submit(`). About 10s later the page creates `h2/p/ol` diagnostic copy. `createElement("form")` is 0. `href` / `assign` / `replace` / submits are 0.

`cf_clearance` and widget `complete` are already true on that noform branch. A token length is recorded (`string/688`). Those signals are not the pass branch in the headed trace.

## Solver-side defect that matches the size gap

`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js` on `interactiveBegin` calls `w.__clickTs` or sets `clickErr=missing`. The live stdout is `clickArm=1`, `clickErr=missing`. The two large posts are about 9KB smaller than the headed posts. The early posts match.

The page script is following the noform html it was given. A missing `form` API does not explain this. Do not hand-post the token.
