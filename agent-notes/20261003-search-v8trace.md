# Search evidence: Cloudflare managed challenge after clearance → diagnostic / no form

Date: 2026-10-03  
Query family: managed challenge (`challenge-platform` `h/b/fo`, `cf-chl-out`, Turnstile non-interactive) staying on “verification taking longer / diagnostic template” instead of creating a form after a clearance-class response.  
Scope: public discussion/methods only. No credentials, cookie values, tokens, fingerprints, or raw challenge payloads.

Search path: user-level `search-layer` (client web search + `search.py --mode deep --intent exploratory`, two rounds, 12 subqueries) → `pavedpath-code` (`gh search issues/code`, `gh api` README, `gh pr/issue view`). Subagents skipped: single ecosystem, controller-run `gh`.

## 1. Endpoint map (public)

Current live path (HAR dumps on GitHub, not official docs):

- GET `/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1?ray=…` (also `h/g`).
- POST `/cdn-cgi/challenge-platform/h/b/fo/<opaque>:<epoch>:<opaque>/<ray>/<id>` — telemetry / flow.
- GET `https://challenges.cloudflare.com/turnstile/v0/b/…/api.js` and widget `…/turnstile/f/av0/rch/…`.
- More POSTs to `challenges.cloudflare.com/.../h/b/fo/...` then same-origin `h/b/fo`.

Older research still names `flow/ov1` instead of `fo`:

- https://github.com/scaredos/cfresearch (archived) — Managed Challenge: orchestrate → POST `BASEURL/flow/ov1/...` with `v_{ray}` + `cf-challenge` → Turnstile iframe → more flow POSTs → **final POST to the target URL** with `md` / `sh` / `aw` / `cf_ch_cp_return` containing `{"managed_clearance":"ni"}` → then a new `cf_clearance` cookie.
- `fo` in current captures is the same slot as historical `flow/ov1`. It is **not** “form”.

`cf-chl-out` / `cf_chl_out` / `cf-chl-out-s` / `Cf-Chl-Gen`:

- Appear as **orchestration headers/cookies** on flow/fo replies, not as a documented success flag.
- Survey listing (header existence only): https://webtechsurvey.com/response-header/cf-chl-out
- cfresearch (older wording): second/fourth flow POST replies include encoded `cf_chl_out` / `cf-chl-out-s`.
- Official docs do **not** define `cf-chl-out` as “clearance complete”.

Public method implication: XHR/fetch POSTs to `h/b/fo` can happen (and even return `cf-chl-out`) **without** the **document navigation POST** that cfresearch calls the “final request”. That final step is the historical `form.submit` / resource-type `document` POST to the page host.

## 2. 3488 vs larger HTML — not a public root cause

Public sources talk about **page size bands**, never a 3488-byte constant:

- Crawler commit (strong-marker scan regardless of size): modern managed pages **100–300 KB**, old detectors bailed at **80 KB**. https://github.com/us/crw/commit/b3e81585594c030a922df72af1a811d4fb8cc0d5
- Pydoll write-up: first-stage challenge script described as a **~226 KB** string-table VM; fail path **re-serves the interstitial with a new Ray ID**. https://pydoll.tech/docs/deep-dive/fingerprinting/cloudflare-challenge/

False positives for the query “3488”:

- https://github.com/filebrowser/filebrowser/issues/3488 — Turnstile `api.js` path bug, issue **number** 3488.
- Unrelated 3488-byte nginx mailing-list attachment.

Local case notes (already in `workspace/psa_solve/docs/web/`) treat 3488/3792 as **decoded `cf-chl-out` body length labels**, with an explicit counterexample that length is not causal. Public search did **not** find any third-party paper that uses 3488 as a challenge-class discriminator.

## 3. Cookie name present, no form.submit / no document POST

Official:

- `cf_clearance` is issued **after** a verified challenge/Turnstile (or Turnstile **pre-clearance**), bound to that visitor/device, default Challenge Passage ~30 min, `SameSite=None; Secure; Partitioned`.
  - https://developers.cloudflare.com/cloudflare-challenges/concepts/clearance/
  - https://developers.cloudflare.com/fundamentals/reference/policies-compliances/cloudflare-cookies/
  - https://developers.cloudflare.com/turnstile/additional-configuration/hostname-management/pre-clearance/
- Cookie **name** on the site partition can exist from the **widget / non-interactive** path while the interstitial still has not done the **page-host document POST**. Official text does not promise that cookie presence implies `form` creation.

Public reports that “cookie / 200 / solved” ≠ finished navigation:

- https://github.com/FlareSolverr/FlareSolverr/issues/1664 — solver says solved / HTTP 200, site still blocked.
- https://github.com/FlareSolverr/FlareSolverr/issues/1667 — `cf_clearance` discussed as present/recognized by one client, solver still not treating the session as a completed challenge.
- https://github.com/sarperavci/CloudflareBypassForScraping/issues/41 — imported `cf_clearance` into Firefox still challenged (partition / fingerprint mismatch).
- https://dev.to/bshahin/cloudflare-cfclearance-why-it-expires-and-how-to-stop-the-re-challenge-loop-do9 — cookie is TTL- and context-bound; `cf-mitigated: challenge` means rejected, not “name exists”.

cfresearch’s **success criterion** is the **final target POST** (`managed_clearance: ni`), not the earlier `fo` POSTs and not the cookie name alone.

## 4. Diagnostic / “taking longer” template vs form

Official product language:

- Challenge solve issues (Turnstile **and** Managed Challenge share the Challenge Platform): https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/
- Merged docs PR: https://github.com/cloudflare/cloudflare-docs/pull/33039 (2026-09-08) — collect HAR + console with Preserve log / Disable cache; WebView notes.
- Custom challenge pages use `::CF_WIDGET_BOX::`, `::RAY_ID::`, `::CLIENT_IP::`, `::GEO::` and **do not require an author-written `<form>`**; the widget is injected. https://developers.cloudflare.com/cloudflare-challenges/challenge-types/challenge-pages/additional-configuration/
- User-facing stall copy: “Verification is taking longer than expected…” — treated as solve-timeout / client environment, not as a second challenge type.

Public method for stall: disable extensions / ETP, clock sync, allow `challenges.cloudflare.com`, run https://debug.challenges.cloudflare.com/, collect HAR. No public write-up maps “decode `cf-chl-out` → `createElement(h2/p/ol/li)` instead of `form`”.

Local classification `complete-to-diagnostic` (opaque/noform after `cf-chl-out`) is **not** named in public sources. Closest public analogue is Pydoll’s “fo telemetry scored server-side; fail re-serves interstitial”.

## 5. V8/Chrome vs Firefox/Gecko — discussed, but at a different layer

Official: current Chrome, Firefox, Safari, Edge supported; **automated browsers not supported**. https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/

Community (client Firefox vs Chrome, not JS-engine VM internals):

- https://community.cloudflare.com/t/challenge-redirect-loop-on-firefox/567810 — ETP / canvas third-party block → loop.
- https://community.cloudflare.com/t/turnstile-not-working-on-firefox-when-enhanced-tracking-protection-is-enabled/689169
- https://community.cloudflare.com/t/turnstile-error-600010-persistent-on-firefox-151-amd-gpu-edge-passes-seamlessly/930150 — Gecko false-positive vs Edge.
- https://community.cloudflare.com/t/another-turnstile-problem-in-chrome/443331 — opposite: Firefox auto-pass, Chrome checkbox fail.
- https://community.cloudflare.com/t/turnstile-client-solve-in-chrome-is-twice-as-slow-as-firefox/809782 — Chrome slower than Firefox on widget solve.
- https://github.com/brave/brave-browser/issues/45608 — Brave shields-off still fails Turnstile; Chrome/Firefox/Safari OK.

**Not found:** public analysis that SpiderMonkey vs V8 (or Gecko vs Blink) after a `cf-chl-out` body decode is what chooses diagnostic template vs `form.submit`. No public method of the form “patch Gecko to match V8 so 3488 becomes form”.

## 6. Ranked public methods (problem-fit)

| Source | Fit | What it actually says | Adapt locally? |
| --- | --- | --- | --- |
| Official clearance + solve-issues + PR 33039 | High | Cookie is visitor-bound; stall is client/HAR; Managed ≡ Turnstile platform | Use HAR/console contract; do not treat cookie name as form-done |
| scaredos/cfresearch | Medium, stale paths | Success = **final page POST** with `managed_clearance: ni`; earlier flow POSTs are probes | Map `flow/ov1` → current `h/b/fo`; keep the **document POST** as the completion gate |
| pydoll.tech + autoscrape-labs/pydoll (~7.1k, MIT, active) | Medium | Real Chromium executes VM; `h/b/fo` POST is opaque telemetry; fail re-serves interstitial | Engine note: Chromium-centric; does not explain Gecko diagnostic branch |
| crw size-detector commit | High for 3488 question | Challenge HTML size is **not** a reliable class | Keep treating 3488/3792 as labels |
| FlareSolverr issues 1664/1667 | Medium | “Solved” + cookie ≠ accepted next request | Same as local “cookie name, no cert document POST” |
| Firefox community ETP threads | Low for this stall | Explains **user Firefox** loops, not RuyiDOM form skip after clearance decode | Only if live Firefox ETP is in the loop |
| CF-Clearance-Scraper / hawk-go / similar | Reject as method | Automation cookie farms; paths (`orchestrate/managed/v1`) lag; cookie reuse fails | Do not copy |

## 7. Rejected / weak

- Treating `h/b/fo` as “form” because of the letters `fo`.
- Treating HTML/body length 3488 as root cause (no public constant; local docs already contradict).
- Custom challenge-page HTML samples that lack `<form>` (official widget placeholder, unrelated to interstitial VM).
- Employment-verification / nginx 3488-byte noise from the length query.
- Grok/web-search prose that invented a full diagnostic HTML template; only official placeholder docs are kept.

## 8. Confidence

Public evidence is **strong** on: (a) `fo` = flow telemetry, (b) completion historically is a **page-host document POST**, (c) cookie name can exist without that POST, (d) 3488 is not a published discriminator, (e) Firefox vs Chrome is discussed only as privacy/ETP/Turnstile UX.

Public evidence is **weak/absent** on: a documented “after `cf-chl-out` decode, Gecko draws diagnostic `h2/ol` instead of `form`” method. That branch remains a **local observer-chain** finding, not a paved open-source path.
