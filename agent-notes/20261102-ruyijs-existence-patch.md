# ruyijs existence patch — 2026-11-02

- status: blocked
- slice: `slice-ruyijs-env-patch-existence-20261102`
- executor: ruyijs 0.1.3（js.exe pin `18f8adc6cc4350aea909a50a53a8d5d891271844c82c76d00f482a2b6d04034f`）
- readRef: existence only。未打开 appearance / detection-checklist / hard-standards。
- 点名的那一个面：`Element.attachShadow`（receiver class `HTMLBodyElement`，返回 class `ShadowRoot`）

## 双条件

| 边 | 结果 | 证据 |
| --- | --- | --- |
| browser fact 读过 | 成立 | canonical `rt_20260929103550_341b734038` `raw/domtrace/trace_process_48444.ndjson` line 98 / seq 99：`type=call` `interface=Element` `member=attachShadow` `thisObj.class=HTMLBodyElement` `returnObj.class=ShadowRoot`。脱敏配对见 `agent-notes/canonical-receiver-pair-20261005/receiver-fact.redacted.json` |
| ruyijs 本地缺 | 不成立 | `diagnostics/ruyijs-env-patch-20261102/pre-patch-existence.json`：`protoType=function` `bodyType=function` `call=ok` `errName=""`。补前核对 eval 只证明该面存在且 closed ShadowRoot 可返回，不是缺 |

核对 eval 不是新的 completed ruyijs evidence-run，也没有 `web_case.py run`。同一条离线形状：fingerprint + logical clock + put_resource×4 + load_page + advance(5000,maxTasks=32)，无 navigate / proxy / live HTTP。

## 没有编 patch

- 本地 `HTMLBodyElement.prototype.attachShadow` 与 `document.body.attachShadow` 都是 function，调用 `{mode:'closed'}` 返回 ShadowRoot。
- console `entryCount=0` `errorCount=0` `missTokens=[]`：页面脚本没有给出 `is not a function` / `is not defined` 的存在性缺口名。
- requestBoundary 仍是 count=4 methods=GET,POST matchedCount=2。这与分析 run `rj_20261102062310_d7463f5c` 相同，不能当成某个 API 缺失；`fo-post` / `cert-document-post` 仍在 skippedFamilies，本拍未 live fetch。
- iframeCount=0 formCount=0 只说明未出 iframe/表单，不等于 `attachShadow` 不在。
- 未调用 `Context.expose` / `Context.set`。未改 Node `env.js` / `runtime/lib/*.js`。未写 `hostProbe` / `serverAccepted` / `localReproduced` / `requestBoundaryAligned` / `parameterAnalysis`。

## 阻塞

双条件不齐：有 browser 读，没有本地 miss。禁止发明下一个宿主面。

## 建议的下一步

父级再跑 schedule.py next。
