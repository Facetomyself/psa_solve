# Canonical receiver pairing / 2026-10-05

## Scope

Read-only evidence processing for the historical canonical run `rt_20260929103550_341b734038`. No browser capture, target evaluation, string-table evaluation, VM patch, Node target/canary, network, runner modification, or dispatcher/state writes were performed. The helper reads captured JSON and NDJSON as data only.

## New proven pairing

- The first inline script in the exact HTTP packet configured by `runtime/mirror-canary.js` has UTF-16 length **238636** and UTF-8 SHA-256 **05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262**.
- `runtime/realm-probe-result.json` contains an existing `realmEval` record with that exact length/hash before diagnostic rewriting. This is a byte-content hash computed from the captured script, not a resource class-label hash. The executable diagnostic script was rewritten afterward; executable byte equality is not claimed.
- The browser stack URL equals that packet's URL. Browser document columns must include the inline script's **19390**-character document prefix. Comparing document columns directly with inline offsets previously obscured a real same-source pair.
- The unique local expression containing the `attachShadow` probe starts at inline offset **213698** within `It` (function starts at **210156**).
- `trace_process_48444.ndjson:97`, seq98: `Document.get body`, `It`, document column **233091**, maps to inline offset **213700**, inside this expression.
- `trace_process_48444.ndjson:98`, seq99: `Element.attachShadow`, `It`, document column **233112**, maps to inline offset **213721**, inside the same unique expression.
- Getter return and next-call receiver have equal full identity records: class **HTMLBodyElement**, JS id **00000000000000ec**, native id **3805db5994f53f9b**. Return class is **ShadowRoot**. The two records are adjacent in this process, with equal timestamps; `origin_call_id=0`, so no direct JSCall linkage is claimed.

Alignment levels: **original-source identical** and **original-source call-site aligned** are proven separately: the existing local xCall record names the expression, that expression is unique in the hash-matched original script, and the browser offsets map inside it. **Same dynamic invocation, same executable bytes, same live session state and local receiver-origin identity are not proven.** Historical local error columns around214416 and the realm probe's rewritten214308 are instrumentation-relative, not original inline offsets; they are not compared directly with browser233112.

## Local interpretation and remaining gap

The historical local probe reports `attachShadow` with constructor label **HTMLScriptElement**, from the same original inline source and the unique source expression now paired above. This is stronger than merely finding similar names across fresh and old runs.

The local mirror has a proven static model defect: `makeElement()` defaults to `SCRIPT` and gives that object `HTMLScriptElement.prototype`; `documentStub.body` is created using this zero-argument factory. `createElement` and `createElementNS` also discard the requested tag. Thus the mirror's body has exactly the constructor label observed by the local probe.

However, the existing local record never captured `receiver === document.body`, tagName, ownerDocument, stable receiver identity or the decoded first key. The source's `x` alias is assigned using an unresolved computed property. No string-table or target execution was used to resolve it. **The exact browser call receiver is now proven BODY; the exact historical local receiver's creation provenance remains indirect.** A static model defect is not yet an experimentally proven cause of the complete failure or a patch-parity result.

Shadow options are represented only as generic Object identity in the DOM trace. Do not infer `mode`, attachShadow behavior completeness, or submission success from this evidence. Local FO count remains zero in the historical result.

## Dispatcher contract review

`skill/web-env-patcher/SKILL.md` execution surface and `references/pause-boundaries.md` rule20 require `stop-search` / `refuse_host_enumeration` to remain a blocked stop, prohibit new Node/canary/realm side tracks, and do not let the incomplete goal clear the gate. `web_case.py` `_experiment_hygiene_decision` returns the refusal whenever hygiene is `stop-search`; receipt contents do not clear it automatically.

This redacted fixture is an **evidence artifact**, not an authorization receipt and not a dispatcher action. The active blocked action contains no grant to record a semantic receipt as gate-passed, replace hygiene with `ok`, mark a host probe moved, or execute a repair. Main-thread report/findings or evidence pointers can describe this new fact without changing those gate fields, subject to the active stamped action. This slice makes no state/contract changes and asserts no automatic unblocking.

## Deliverables and next requirement

- `agent-notes/canonical-receiver-pair-20261005/receiver-fact.redacted.json`: source hash, safe offsets, process/site and browser identity join, local observed class, input artifact hashes and limitations. No raw URL parameters, target source, challenge tokens or response fields are embedded.
- `agent-notes/canonical-receiver-pair-20261005/build_fixture.py`: reproducible data-only extraction/assertions, UTF-8/LF output.
- Helper verification: exit0; same original source hash and same-source unique-call mapping asserted; browser BODY identity join asserted. No target or runner tests executed.

Minimal missing evidence: authorized local receiver-origin capture at this same source call, ideally receiver/body equality plus tag/owner document/creation identity, followed only under an explicit permitted dispatcher action by a single-surface factory/document-typing experiment and an unchanged-input rerun. This slice does not propose adding `attachShadow` to HTMLScriptElement.
