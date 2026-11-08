# host API diff — 2026-11-02

status: done  
handles: browser `rt_20260929103550_341b734038`；ruyijs `rj_20261102153528_cc268870`  
evidence: `evidence/host-api-diff-ruyijs-20261102.json`

## 结论

cert POST seq 60（`startMs=1790678197718`）之前，challenge 栈（`challenges.cloudflare.com` / `cdn-cgi` / `turnstile` / `orchestrate`）触达的 content 宿主面在 ruyijs `method=eval` 下均存在：`missTokens=[]`，`namedGap=null`。

未再发 `Element.attachShadow` 存在性刀。osano/analytics/jsd/next-chunks 为 cert 之后 post-solve，未进评测。fo-post / cert-document-post 是 challenge 输出，不是 named API。

## 依据

- DOMTrace 流式扫描 unique content API 205（cap 80 写入 `challengeApis`），含 `Navigator.gpu` / `GPU.requestAdapter` / `Worker.terminate` / `RTCPeerConnection.*` / `XMLHttpRequest` / `matchMedia` / `contentWindow` / `currentScript` / `HTMLFormElement.submit`。
- 本地 `run_ruyijs.py method=eval`（fresh Context，无 navigate / proxy / parameter-analysis）。函数存在且可安全调用记 `call=ok`；会出网的 `Worker`/`XHR.send`/`RTC.createOffer`/`form.submit` 只核 `typeof`/`prototype`，`call=skip`。
- `resource://gre` 首帧（`PeerConnectionImpl`、`windowGlobalChild`、`documentGlobal`、`mozIsTextField`）是 Firefox chrome 实现，不是 content 缺口；content 替代面 `RTCPeerConnection` / `HTMLFormElement.submit` 本地为 function。
- Performance* 首次探针因无 navigation entry 误报 undefined；`PerformanceEntry.prototype` / `PerformanceResourceTiming.prototype` 描述符存在，已清 miss。

## live emit

`liveRuyijsEmitPath.existsInShippedCode=false`。适配器只有 `eval` 与 `parameter-analysis`；后者绑定 no-egress sink。env-patcher 仍是 `load_page`+`put_resource`，不 `navigate`。库内 `Context.navigate` 不是 convert-allowed LIVE 路径。隔离导致 FO/cert 完不成，不是某个 content API 缺失。

未写 `dualCondition` / `serverAccepted` / `localReproduced` / `requestBoundaryAligned`。
