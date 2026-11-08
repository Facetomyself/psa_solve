# Local receiver origin audit / 2026-10-05

## Scope and decision

Read-only audit of existing local artifacts. No target evaluation, string-table or VM execution, Node target/canary run, trace, network request, runner edit, dispatcher write, or gate change was performed.

**Decision: cannot close the local receiver origin.** The historical local diagnostic records `receiver=HTMLScriptElement` for `attachShadow`, but they do not record `receiver === document.body`, tag name, owner document, stable object identity, creation call, or the decoded computed property key. The browser evidence proves a `HTMLBodyElement` receiver at the paired source call; it does not prove that the historical local object is the same dynamic object.

## Static data-flow checks

- The hash-matched inline source contains `function It(...)` and the unique paired expression `x[bf(CW.IZ)][bf(CW.IM)](b)` at inline offset `213698`.
- Near the script bootstrap, the source assigns `h=this||self,x=h[aH(2153)]`. This proves only that `x` is the result of a computed property read from `h`; `aH(2153)` was not resolved and no VM/string-table execution was allowed.
- No direct assignment from `document.body` to `x` is established by the allowed static text. The two subsequent computed keys and the receiver-producing property chain remain unresolved.
- The mirror's `makeElement(tagName, className)` defaults to `SCRIPT`, assigns `HTMLScriptElement.prototype` for that tag, and `documentStub.body`, `head`, and `documentElement` are created with the zero-argument factory. `document.createElement` and `createElementNS` also discard the requested tag. This is a **static forced factory type** and explains how a body-like stub can acquire the observed constructor label; it is not dynamic receiver provenance.
- `realm-probe-result.json` has an **existing observed label** (`HTMLScriptElement`) and `foRequests=0`; it has no dynamic identity fields. The browser/local same-source join does not add those fields.

## Completion evidence audit

| Requirement | Existing authoritative evidence | Result |
|---|---|---|
| Node core/reference runtime source | `runtime/run.js`, `runtime/code.js`, `runtime/lib/{config,host-globals,host-dom,host-async,transport}.js` | Core entry and modular host/transport sources exist; no completed Node parity receipt |
| Network response pipeline | `runtime/lib/transport.js`; canary response-state contract in `runtime/mirror-canary.js` | Pipeline exists, but historical local probe has `xhrCount=0`, `deliveryEvents=[]`; no local clearance/FO boundary |
| Parity | `evidence/web/parity/` is empty; workflow contract has parity pending | Missing; no `parity-result.v1` proving no first divergence |
| Test/readback | No project `test.py` or `landing/test.py` was found; contracts keep `serverAccepted=false` and no independent same-lease readback receipt | Missing |

## Minimal missing local dynamic record

Under an explicitly permitted future dispatcher action, one unchanged-input local record must capture at this exact source call: receiver/body equality (or a stable receiver identity joined to `document.body`), `tagName`, `constructor.name`, `ownerDocument` identity, and the receiver's creation/provenance marker. This audit does not execute it and does not authorize a factory patch.

## Contract boundary

The active `refuse_host_enumeration` / `experimentHygiene=stop-search` action forbids opening a Node/canary/realm side track and forbids adding an adjacent host field. The next executable repair is therefore **not permitted by the current contract**; only existing-data documentation can proceed until a new external request-boundary difference is authorized.
