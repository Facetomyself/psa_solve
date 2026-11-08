# Receiver Static Review / 2026-10-05

## Scope And Gate

- Project: `D:/reverse_ENV/workspace/psa_solve`.
- Read-only audit of existing runner source and existing `runtime/realm-probe-result.json`; only this artifact is written.
- Current `workspace.json`: `next=refuse_host_enumeration`, `turnGate=blocked`.
- No target JavaScript execution, canary run, network, browser, new host API, code patch, fact update or gate release.
- Rules: `skill/web-reverse/SKILL.md:13`, `skill/web-env-patcher/SKILL.md:13`, `skill/web-env-patcher/references/pause-boundaries.md:87`. A static runner defect is not a new external request boundary and does not release the hold.

## Findings

### 1. Confirmed: Mirror Factory Converts Non-Script Requests To Script Nodes

`runtime/mirror-canary.js:45` defines `makeElement(tagName, className)`; line 47 defaults any absent/falsy tag name to `SCRIPT`. Line 60 assigns `HTMLScriptElement.prototype` to every resulting `SCRIPT` node.

| Entry | Source | Statically established result |
| --- | --- | --- |
| `document.createElement(t)` | `runtime/mirror-canary.js:114` | Ignores `t`, calls `makeElement()`; even `div`, `body`, `iframe` become `tagName=SCRIPT`, inherited constructor `HTMLScriptElement`. |
| `document.createElementNS(ns,t)` | `runtime/mirror-canary.js:115` | Ignores both arguments; same script result. |
| `document.head` / `document.body` | `runtime/mirror-canary.js:121` | Both initialized by `makeElement()`; neither is a HEAD/BODY node. |
| `document.documentElement` | `runtime/mirror-canary.js:122` | Initialized by `makeElement()`; becomes SCRIPT rather than HTML. |
| `document.currentScript` | `runtime/mirror-canary.js:131` | Explicit `makeElement("SCRIPT")`; the factory's script choice is appropriate for this entry. |

This is a provable implementation defect in the mirror harness, independently of any Cloudflare behavior. A target lookup of `document.body` in this harness can report constructor name `HTMLScriptElement` solely because of the factory.

### 2. Query Methods Are Inaccurate, But Not Uniformly Script-Typed

- `getElementById`, line 117: ignores the requested ID and returns a fresh DIV, not a script node and not an actual matching node.
- Document `querySelector` / `querySelectorAll`, lines 118-119, and element variants, lines 51-52: only the class-search helpers can identify matches; other selectors or misses return a fabricated DIV / one-element DIV array instead of a truthful match or `null` / empty list.
- `findClassElement`, lines 76-85, and `findClassElements`, lines 88-110, reconstruct elements from the original top-level `challengeHtml`, preserving the parsed tag name. Script typing only follows an actual parsed SCRIPT tag in those branches. Lines 103-109 also manufacture A nodes for a few hard-coded class names.
- `head`, `body` and `documentElement` are distinct factory allocations, not aliases of one shared object. Their element query methods ignore `this` entirely and use the same top-level `challengeHtml`; a body query is not scoped to that body, and repeated lookups reconstruct nodes rather than preserving DOM identity. This is a shared wrong lookup implementation, not proof of a shared receiver object.
- Therefore, do not generalize the finding as "all node factories are HTMLScriptElement". `body`, `head`, `documentElement`, `createElement` and `createElementNS` are definitely affected; the query factories have separate selection/identity defects.

### 3. Recorded Receiver Name Is A Constructor Label, Not A Browser Brand

`runtime/realm-probe-canary.js:118` computes receiver text from `__rpRecv.constructor.name`, with fallbacks. It does not record `tagName`, `nodeName`, object identity, owning document, `receiver===document.body`, creation site, selector or the decoded first lookup key.

Existing `runtime/realm-probe-result.json` records:

- Base: `runtime/mirror-canary.js`; `exitCode=0`.
- `xCall.propertyKey=attachShadow`, `xCall.receiver=HTMLScriptElement`.
- Expression: `x[bf(CW.IZ)][bf(CW.IM)](b)`.
- `foRequests=0`, `serverAccepted=false`; an uncaught TypeError is retained in `runnerRecords`.
- `sourceSha256` describes the instrumented mirror source, not a matched fresh browser source or the isolated runner.

An exit code of 0 is not successful solving: the retained error and zero request boundary remain negative. The recorder's name is compatible with a wrongly typed body or any wrong `createElement` result, and is also compatible with an actual script object. Existing evidence cannot distinguish these origins.

### 4. Isolated Iframe Runner Is A Different Baseline

- Mirror frame execution, `runtime/mirror-canary.js:238`: swaps `documentStub.currentScript` and the window URL, then indirect-evals the frame script into the shared mirror/global environment (line 245). It retains the same incorrectly typed `documentStub.body` and does not create a separate iframe document.
- `realm-probe-canary.js:11`, `:151`, `:172`, `:178`: reads the mirror source, instruments eval, launches that source in a child process. It does not import `lib/iframe-realm.js`.
- `runtime/run.js:19` routes only `frame` mode into `runOfflineFrame`. Other modes load `code.js` (`:33`, `:93`), outside this requested audit.
- `runtime/run.js:238`, `:300` imports and constructs the isolated iframe module for frame mode.
- `runtime/lib/iframe-realm.js:342` materializes a plain element object with the supplied tag name. `:485-493` finds/builds HEAD and BODY, `:497-500` propagates requested creation tags, and `:507-514` selects actual materialized nodes or returns null.
- That module does not assign `HTMLScriptElement.prototype` to its materialized nodes. Its constructor stubs at `:648-650` do not make those objects correctly branded browser elements either; tag preservation is not full prototype/brand parity.

The isolated runner does not contain the mirror's unconditional SCRIPT factory defect. Its behavior cannot be used as if it were a rerun or validation of the instrumented mirror baseline.

## Source And Response Limits

- Mirror page/orchestrate material is hard-coded to a 2026-09-28 capture (`runtime/mirror-canary.js:10`), while its frame packet is a 2026-09-29 capture (`:11`). The isolated frame entry also points at the September 29 packet (`runtime/run.js:246`).
- Existing realm result identifies the September 29 frame script length 238636 and SHA-256 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`.
- `agent-notes/20261004-realm-probe.md:66` reports September 29 browser `It` calling `Element.attachShadow` on `HTMLBodyElement`; line 70 reports fresh October 5 `Q` on `HTMLBodyElement`. The latter is not source-aligned with the historical local `It` source; matching API/receiver category is insufficient to map exact closures or offsets.
- No raw trace was read in this audit. Browser observations above are taken from the existing curated summary, not independently revalidated from raw evidence.
- `docs/web/environment-patch.md:64` supports only the observed RuyiDOM chain `complete-to-diagnostic`, without form/submission. Response body length, opaque response interpretation, TLS/session selection or response-consumption hypotheses are not established root causes.
- Mirror error before any FO request cannot explain the distinct RuyiDOM live failure after five FO requests and clearance. No claim of such causality is made.

## Minimal Missing Evidence

1. For attributing the old mirror TypeError: a receiver-origin/identity receipt at the already identified call, including owning document, actual tag and whether it is `document.body` or a node returned by a factory. Existing constructor-name-only recording lacks this. No new experiment was performed or authorized here.
2. For target parity: a browser/local pair with the same frame source hash and corresponding call site, plus the same runner baseline and coherent session/resource provenance. The fresh October 5 browser call and historical September 29 local expression are not this pair.
3. For clearing the active hold: an eligible new external request boundary difference, not a constructor label or opaque-byte/body-length hypothesis. The present static finding does not provide this.
4. For completion: cert-document POST boundary and independent same-lease business readback remain absent, as summarized in `docs/web/environment-patch.md:72-74`.

## Disposition

Confirmed runner defect; target causality unproven. Keep `no-browser-fact` for the literal local `HTMLScriptElement.attachShadow` claim, without treating that label as trustworthy browser typing. Do not add `attachShadow` to `HTMLScriptElement` to accommodate the mislabeled harness. No code or workflow facts changed; `refuse_host_enumeration` / `blocked` remains in force.
