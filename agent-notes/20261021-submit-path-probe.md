# 2026-10-21 submit path probe

Scope `9a0d32e12aad8ccb` stays on `HTMLFormElement.submit` at line 1 column 75507. Official baseline receipt `evidence/host-executions/0530703a73ca4f1f85827d89795bb2f1` is still exit 1. `validate_execution` rejects it, so `next` stays `verify_host_execution` / `blocked`. This note is not a host-observation.

Diagnostic is the Oct 5 challenge page plus orchestrate bytes, `document-principal.js` only (cookie, sandbox clock, sandbox `window`/`self` identity). No collector edit. No completion booleans.

Measured on the fast path:

- Realm identity stays `new-global:same`. Sandbox clock stays `skew` for this saved page.
- `document.forms` stays 0. `HTMLFormElement.submit` calls stay 0. iframes stay 0. `document.scripts` ends at 3.
- The only uncaught console error is `Prompter.sys.mjs:1288`. `Services.ww.openWindow` is not the object the prompter calls. `Prompter.pickPrompter` is not the path. `getPrompt` runs once and the modal `openWindowPrompt` throws.
- Quieting that modal removes the console error and still leaves forms at 0 and submit calls at 0.
- Serving the saved local turnstile script answers both script GETs (`served` 4, blocked shape left is favicon only). No iframe and no form appear.
- With a heavy debugger, line 1 columns 56823 and 75745 throw a caught TypeError in equal counts until the run ends. Those columns are call sites inside the interpreter. The fast path does not raise them. Column 75507 still has no form receiver and no submit call.

Official `host run --variant baseline` was not repeated. A silent run would replace the exit 1 receipt and still fail validation, because the collector only emits a host-observation from a script error at line 1 column 75507.
