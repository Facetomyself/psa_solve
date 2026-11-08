# ruyijs_parameter_analysis

- status: done（state=`completed`，不是 browser fact / localReproduced / serverAccepted）
- runId: `rj_20261102062310_d7463f5c`
- runtime: ruyijs 0.1.3 / js.exe SHA256 `18f8adc6cc4350aea909a50a53a8d5d891271844c82c76d00f482a2b6d04034f` / verification=verified
- wheel: `2431fb75e282450a9b4963fa6fd0fc99607ca0d1eb054a43b5b653bee872d021`
- evidence: `evidence/web/ruyijs/rj_20261102062310_d7463f5c/`
- source: canonical ruyitrace `rt_20260929103550_341b734038` 403 HTML（5755 B，sha `cac7003a…`）+ 4 条已捕获 GET 200 资源；无 live recapture、无 navigate、无 proxy
- calls: configure_fingerprint（Firefox 158，不是 RuyiTrace 159）→ configure_clock(logical) → put_resource×4 → load_page → advance(5000ms,maxTasks=32) → eval；Context timeout=120s；wall 17s
- hostSurfaces: console, net
- requestBoundary: count=4 methods=GET,POST matchedCount=2
- outputSha256: `4819899a2c1f28e40799db892bf759d2b79a59553d8623323409ada87d300223`
- eval 计数（无原值）：formCount=0 scriptTagCount=3 iframeCount=0 inputCount=0 titleLen=16 hostClass=page-host hasCfOpt=true cookiePairCount=0 readyState=complete
- 观察（留给 `record_parameter_analysis`，本拍未写 facts）：离线 load_page 未建 form、未出证书 document POST。未改 host，未写 `parameterAnalysis` / `serverAccepted` / `localReproduced` / `requestBoundaryAligned`

## 阻塞

- 无。工具拍已落盘。下一拍应由 dispatcher 给 `record_parameter_analysis`。
