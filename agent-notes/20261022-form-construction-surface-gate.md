# 2026-10-22 form construction surface gate

The case gate now treats a repeated in-file line 3 column 544 token stop as spent. `web_case.py next` returned `authorize_form_construction_surface` / `blocked` at `2026-10-22T16:23:41Z`, session `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`.

The current baseline and its immediate prior both die on line 3 column 544, kind `other`, class `slow-script`, sourceForm `token`, sourceClass `other`, with no errorName, receiverState, or receiverId. A first stop with no matching prior still returns `repair_submit_host_behavior`. Nearby columns and other scriptError shapes still return `verify_host_execution`.

The authorized surface is `Document.createElement` through `HTMLFormElement.submit`, or one other Node host change that can emit the certificate document POST. The decision forbids rewriting Node `env.js` and forbids completion facts. This beat did not add a host API, did not edit the helper, did not rebind the scope, and did not run a new baseline or Node session.

Unchanged: helper `7a5996854ea9d800955fba83683292afb6098473e4f11c901a578e77427fce43`, scope `c8e9652b6374511c8c9bcc30cf43e50a8bb1b67252f55e33091206c848607488`, baseline `a5c33751e7a24338bd7dc2959c349599`. `localReproduced`, `serverAccepted`, and `requestBoundaryAligned` stay false. `experimentHygiene` stays `ok`. `hostProbe` stays null.
