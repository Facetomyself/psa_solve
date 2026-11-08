# Firefox receiver provenance trace（2026-10-05）

## Run

- Run: `rt_20261005125421_1d84c46dcd`
- Request: fresh `https://www.psacard.com/cert/67417377/psa`
- Runtime: RuyiTrace 3.3.0 / interactive / baseline fingerprint / direct proxy / 60s / traceLimit 500000
- Trace switches: narrow Turnstile `MOZ_DOM_JSCALL_SCRIPT_URL`、`DETAIL_SCRIPT_URL`、`SOURCE`；`MOZ_DOM_JSCALL_NATIVE=1`；`DETAIL_NATIVE=createElement,createElementNS,querySelector,getElementById,getElementsByTagName,attachShadow`
- Receipt: `integrity=pass`，395 artifacts，1,091,879,093 bytes，1,352,457 indexed records。该 pass 仅证明产物/索引完整；关键 writer dropped/io_errors 为 0，但 JSCall `dropped_gate=611`，iframe 与业务进程 DOMTrace `complete=false`；不能宣布调用全覆盖。

## Direct facts

1. Turnstile API call：`Element.attachShadow` receiver `HTMLDivElement`，return `ShadowRoot`；source 是 `https://challenges.cloudflare.com/turnstile/v0/b/.../api.js`，trace file `raw/domtrace/trace_process_51372.ndjson:83044`。
2. Challenge iframe call：`Element.attachShadow` receiver `HTMLBodyElement`，return `ShadowRoot`；source 是 `https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/...`，trace file `raw/domtrace/trace_process_50068.ndjson:102`。
3. 没有本 run 的 `HTMLScriptElement.attachShadow` 记录。Native 参数只保存为 Object identity，不能从该 trace 断言 `mode` 值。
4. Orchestrate 真实提交：`HTMLFormElement.submit` 被调用一次，receiver class `HTMLFormElement`，source `.../orchestrate/chl_page/v1?ray=...`，trace file `raw/domtrace/trace_process_51372.ndjson:90886`。
5. HTTP packet index 随后记录同一证书 URL 的 document `POST 200`（index line 12 / `seq=41`），响应 hash `3632bcb6...`；初始 document GET 为 403。该 run 因而补齐了 browser 侧 `form.submit → cert document POST 200` 边界。

## Interpretation

- 同 run 的 iframe `get body → attachShadow` 和 API `createElement('div') → attachShadow` identity 链已证实。但新 inline source 为 238893 chars / hash `eee05641...`，历史 local 为 238636 / `05102bb...`，尚不能把新 df 对应到旧 It，也未证明历史 local receiver 的来源。不支持直接给 HTMLScriptElement 加 attachShadow，不等于已经定位全部 target 根因。
- 它也证明浏览器侧提交链存在，当前 RuyiDOM 的 `forms=0` / `submits=0` 是真实 execution divergence 的边界，已经比“清关 cookie 是否存在”更具体。
- 该 run 仍不是 `serverAccepted=true`：document POST 200 不是独立同 lease 业务 readback。必须在同一 lease 上另做约 5 秒后的业务 GET/readback，并保存 200 证据后才可写验收字段。

## Limits and next step

- `jscall.detail.bin` 的 native object 参数仍是 identity-only；未证明 `{mode:'closed'}` 等深参数，也未建立每个 local runner node 到 browser nativeId 的跨 run 映射。
- Chromium 不需要为 `attachShadow` 再采一份普通 `env-hooks`：其现有 hooks 没有 attachShadow/submit 覆盖，且 wrapper 不能组合完整 native detail、correlations 和 response bodies；直接重采仍会是 partial 对照。
- 保持 `environmentPatchGate=not-ready`、`localReproduced=false`、`requestBoundaryAligned=false`、`serverAccepted=false`。当前 Node 目标缺同源 local pairing，不能仅凭 browser POST 200 跳入 local solver 验收；已结束的 browser lease 也不能冒充新的约 5 秒 readback。先对现有 detail/source 做窄解码和证据配对，不能再试相邻 host getter。

## 2026-10-05 Comparison Correction

- 详细对照见 `agent-notes/trace-compare-20261005.md`。iframe 17 个函数达到 per_func_limit 1024；total limit 100000 是配置，实际 `dropped_limit=0`，不要误写为 total limit hit。iframe `sources_unavailable=3`。
- submit 后的 POST 时序可见，但 HTTP `originCallId=0` / `no_source_context`，不是完整因果 linkage。已观测记录可用，未观测行为不能据此作缺失证明。
- 新 run 保留为 observational supplement；权威 activeRuns/receipt/workflow 仍锁定旧 9 月 29 日基线，不拼接两套 inputs 做 parity。本轮对照没有执行新实验或 runner 修正。

## Evidence

- Receipt: `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/receipt.json`
- Request: `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/request.json`
- DOM trace: `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/raw/domtrace/`
- HTTP index: `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/raw/http_packet/index.jsonl`
