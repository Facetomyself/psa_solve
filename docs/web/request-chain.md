# Request Chain

Case: `psa-cf-5s-shield-20260815`

Ordered calls. Keep the challenge chain separate from the business chain. The machine contracts are `contracts/request-parameter-lineage.v1.json` and `contracts/workflow-artifacts.v1.json`.

## Notes

- 有头 `rt_20260929103550` 是空配置档。顺序：证书 GET 403，无 Cookie，写下 `__cf_bm`；orchestrate GET 200；页面 `/fo/` 请求 2252，h3；Turnstile 主机三包 `/fo/` 不带页面 cookie；页面清关 `/fo/` 请求 8780，正文 3792，写下 `cf_clearance`；证书 document POST 请求 2221，状态 200。
- 本地最新对照：同一角色顺序，第一包页面 `/fo/` 已是 h3，请求 2252。清关请求 8770，正文 3488。站点分区有 `cf_clearance`。`forms` 0，`submits` 0。没有证书 POST。`window.KP` 未定义。
- 卡点在清关响应之后：有头走进 `createElement("form")` 和 `form.submit`，本地画出 `h2/p/ol`。`firstDivergence=environment-gap`，`requestBoundaryAligned=false`，`experimentHygiene=stop-search`。cookie 名和 `/fo/` 200 都不是 `serverAccepted`。
- 生成表的 endpoint phase 列固定写 unverified。阶段以下面的 stateful flow 为准：`cert-post` 和 `business-readback` 仍是 `triage-only`。
- 有头 `rt_20260929103550` 的路径类是 `/h/b/`（`/h/g/` 计数 0）。主站 `/fo/` 2 次，Turnstile 主机 `/fo/` 3 次。点击这一轮的「三次」先标在 Turnstile 主机，不和主站清关包合成一个序号。无感模型仍是主站 fo1、fo2，本轮没有另开无感挑战。
- Turnstile `api.js` 在该 run 的响应正文是 86732 字节，sha256 `76763bb46224400a11af989831d62d06629aba6f67d50cac96afae4a590adf59`，摘到 `diagnostics/live/turnstile-api.js`。它不是 live 目录里那份 237276 字节的 orchestrate。可读完整性谓词是 iframe 的 `reloadApiJsRequest`，第二份脚本仍是 not-identified，替换返回没有发生。
- 2026-09-30 本地顶层窗口：两次页面 `/fo/` open 之间造出第二个小于 1 KB 的 blob Worker。引导确认它启动了，但 `postMessage` / `onmessage` 没有被调用。`crypto.subtle` 的 encrypt、decrypt、sign、digest、importKey 也没有被调用。清关类仍是 3488，没有 form。形状见 `diagnostics/live/worker-live-shape.json`。

<!-- generated:request-chain -->
Endpoint order follows the lineage array. Stateful steps follow workflow-artifacts.statefulFlows.

| order | phase | endpoint | method | path |
| --- | --- | --- | --- | --- |
| 1 | unverified | cert-document-get | GET | /cert/ |
| 2 | unverified | orchestrate-get | GET | /cdn-cgi/challenge-platform/orchestrate |
| 3 | unverified | page-fo | POST | /cdn-cgi/challenge-platform/fo/ |
| 4 | unverified | clearance-fo | POST | /cdn-cgi/challenge-platform/fo/ |
| 5 | unverified | cert-document-post | POST | /cert/ |

| order | phase | step | producer | consumer | verification |
| --- | --- | --- | --- | --- | --- |
| 1 | other | cert-challenge-flow/cert-get | cert-get | orchestrate | triage-only |
| 2 | challenge | cert-challenge-flow/orchestrate | orchestrate | page-fo-state | triage-only |
| 3 | challenge | cert-challenge-flow/page-fo-state | page-fo-state | widget-fo | triage-only |
| 4 | challenge | cert-challenge-flow/widget-fo | widget-fo | clearance | triage-only |
| 5 | challenge | cert-challenge-flow/clearance | clearance | cert-post | triage-only |
| 6 | business | cert-challenge-flow/cert-post | cert-post | business-readback | triage-only |
| 7 | business | cert-challenge-flow/business-readback | business-readback |  | triage-only |
<!-- /generated:request-chain -->
