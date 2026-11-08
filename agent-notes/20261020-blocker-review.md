# psa_solve 卡点审计与方向分析 / 2026-10-20

## 审计边界与执行状态

- 本轮先执行 `web_case.py next --project D:\reverse_ENV\workspace\psa_solve`；实际返回 `action=refuse_host_enumeration`、`turnGate=blocked`。
- 只读本地项目及 `C:\Users\mengma\.grok\last-copy.txt`；未联网、未运行 target JS、未启动 Node/canary/浏览器、未改 runner/合同/门禁/业务事实。仅新增本报告。
- 无运行句柄。历史 `rt_20261005125421_1d84c46dcd` 仅为离线材料。
- 引用项目内路径相对 `D:\reverse_ENV\workspace\psa_solve`；报告不包含 Cookie/token/指纹原值。`last-copy.txt` 是会变化的会话快照，以下行号对应本轮读取版本。

## 执行摘要

1. **fact**：三个现场必须分开：裸 curl 只拿挑战文档；RuyiDOM live 完成 widget/五段 FO 后进入排障 DOM；历史 mirror Node 在 FO=0 时已有错型 receiver/TypeError。它们不是一个“TLS 卡住”的共同证据。
2. **fact**：`chlOut=noform` 是本地正则分类，不是服务端显式拒绝码；不透明正文上未找到 `<form` 不能推出服务端没有发成功指令。
3. **fact**：最早可确认的结果相关分叉窗口为“末次 page-host FO response → 消费/计时 → DOM 分支”；真正首个因果分叉仍未知，不能把 `environment-gap` 合同标签当已证根因。
4. **inference**：Node 下一项最有价值工作是定位已 source/call-site 配对处的 receiver 来源，纠正 factory/document typing 的单一机制；不是给 HTMLScriptElement 硬塞 attachShadow。此实验当前不获门禁许可。
5. **fact**：浏览器内同源 fetch 已展示短期业务备选可行性，但不能替代 Node 独立求解、local parity 或同 lease 业务验收。

## 1. 四层因果模型：哪里已证、哪里没有

### A. 传输层 / TLS / HTTP 版本

- **fact**：10 月 20 日 curl 两次实际 HTTP/2、403 challenge；真实 Firefox 151 也先进入 challenge，再约 6 秒后取得证书页。证据 `agent-notes/20261020-transport-cause.md:7-15`。
- **fact**：curl 探针 `temp/transport_cause_probe.py:25-35,65-68` 只是两个独立 GET，没有执行 challenge，也没有同会话求解后的重放。因此不是保持 challenge 执行和会话不变、只替换 TLS 的实验。
- **inference**：curl 停在初始 challenge 最直接的已知解释是“尚未执行题目”；这不排除 TLS/HTTP/浏览器信号参与风控，但排除了从这组结果直接断言 TLS 是唯一根因。
- **unknown**：Firefox 151 这次真实协商 h2 还是 h3、服务器对各类指纹的具体决策、代理是否是 h3 未协商的充分原因。探针没有 Firefox 网络表，也没有直连/同会话单变量对照。看到 h2 回退不等于已定位代理内部机制。
- **fact**：9 月 30 日 RuyiDOM 曾有系统应用代理继承导致 h3 回退；修复后五条 FO 实测 h3，仍无 form/submit/证书 POST。传输回退已被局部因果修复，但并未修复业务结果。`docs/web/environment-patch.md:18-22`。
- **unknown**：两者同为 h3 不表示 TLS/QUIC/底层引擎全部一致，也不能断言本地剩余失败与传输完全无关。RuyiDOM 是 135 base + UA override，不是升级到 155；材料交接为 urllib→Gecko 逻辑交接，并非同 TLS 导航。`docs/web/environment-patch.md:31,42,64`。

### B. Challenge 执行 / widget 完成

- **fact**：RuyiDOM widget complete、站点分区出现 cf_clearance 名字、最后 FO 带 cf-chl-out(-s) 名；这些证明走过若干挑战阶段，不证明主站业务已接受。`docs/web/request-chain.md:9-12`，`agent-notes/20260930-causal-observer-chain.md:24-29,60-68`。
- **unknown**：清关材料的值、作用域、当前会话有效性、后续请求是否实际携带并被接受。本轮刻意不读取/披露值；仅名称不足以核验这些语义。

### C. 服务端响应与页面消费

- **关键 fact**：`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js:1395` 在 XHR loadend 中对 `responseText` 用 `/<form\b/i` 和 `/\.submit\s*\(/` 做正则，生成 `form/noform`、`submit/nosubmit`；不是解析服务端协议状态，也不是服务端返回了名为 noform 的字段。
- 同一行同时统计 opaque 字符形状，说明“没有明文 form”与“客户端执行后是否创建 form”是不同问题。将 `noform` 叫作服务端拒绝、或者因为它给本地回灌成功样本，均无证据依据。
- **fact**：受限 causal observer 将末次 FO response seq15 对到之后 seq16 的 h2 创建与后续排障 DOM；响应到首个 h2 约 10 秒。无 form/submit/证书 POST。`agent-notes/20260930-causal-observer-chain.md:20-29,31-48`。
- **unknown**：这 10 秒是协议要求、等待回调/消息、未满足状态、超时兜底还是某个异常的后果；现有证据只有顺序与时间，不含那个决策点的条件值。
- **fact**：3488/3792 只是长度标签，本地也有 3792/forms0 反例。不能当分数、通过谓词或补丁优化目标。`docs/web/environment-patch.md:33`。

### D. form.submit / 业务接受

- **fact**：浏览器 run 中确有 HTMLFormElement.submit，随后同进程证书 document POST 200。`agent-notes/trace-compare-20261005.md:50-56`；底层 DOMTrace 位于 `evidence/web/ruyitrace/rt_20261005125421_1d84c46dcd/raw/domtrace/trace_process_51372.ndjson:90886`。
- **fact**：POST 的 originCallId=0/no_source_context，故是强时序关联，不是已经完成的 submit→channel call-id 因果 join。浏览器 POST 200 也不是 Node 的 serverAccepted。`agent-notes/trace-compare-20261005.md:52-56`。
- **fact**：本项目已观察到的成功样本确有 document POST，故它是本项目当前样本的请求边界目标；但“所有 managed challenge 都必须提交 3 hidden”不是本轮项目证据证明的跨版本通则。
- **unknown**：本轮审阅的项目摘要没有独立核验该 POST 恰好 3 个 hidden。`last-copy.txt:289` 的这一断言来自文章总结而非本轮核查的项目 DOM/form-body 证据。本轮按任务范围不读取文章全文，也不将该数目升级成协议合同。
- **fact**：本地缺 form + submit + 证书 POST 的组合证据比单凭某一个请求没抓到更强；但“请求表记全了”仍应限定观察器/realm/网络覆盖，不是绝对所有通道无遗漏证明。顶层 causalTrace 实际未包含 iframe 的三条 FO，需由 Necko 表补齐。`agent-notes/20260930-causal-observer-chain.md:14,54-68`。

## 2. 真正确认到哪一个最早分叉

| 现场 | 已证最早有用边界 | 不能据此声称 |
|---|---|---|
| 裸 curl 对浏览器 | 初始 GET 都拿 challenge；后者运行页面并继续 | TLS 单独拒绝 curl、HTTP3 必须成功 |
| RuyiDOM 对有头 | 末次 FO 响应及消费后，排障 DOM 对 form/submit/POST | 首个 causative getter 已找到、服务端已明确发拒绝指令 |
| mirror Node 对 canonical browser | 同原始 source/唯一 call-site，browser BODY attachShadow，local constructor label SCRIPT；local FO=0 | 二者同 invocation/local body identity 已证、此错解释 RuyiDOM 后段失败 |

**判断**：`firstDivergence=environment-gap` 是当前调度分类（`contracts/auto-decision-facts.json:4-9`），不是排除了传输/session/服务端决策所有替代解释之后的根因证明。最精确说法是“已定位最早结果相关可比窗口，尚未定位第一个导致结果不同的条件”。

## 3. receiver 模型污染：确证与边界

### 已确证（fact）

- mirror 默认 makeElement 为 SCRIPT、body/head/root 以及 createElement/NS 丢 tag，查询忽略 this、miss 伪造 DIV；iframe 间接 eval 仍共享 document/global。`agent-notes/trace-compare-20261005.md:82-87`，源位置 `runtime/mirror-canary.js:47,60,114-122,241-245`。
- local recorder 仅写 constructor.name，没有 tag/ownerDocument/identity/body equality。`runtime/realm-probe-canary.js:118-120`；审计 `agent-notes/local-receiver-origin-audit-20261005.md:7,11-15`。
- 已完成历史 canonical browser 与 local **原始 source 相同 + 唯一 source call-site 对齐**；HTML 文档前缀 19390 解释了先前列号不符。browser body getter 与 attachShadow receiver 同 identity。`agent-notes/canonical-receiver-pair-20261005.md:9-17`。
- 因而早期“缺 source pairing”的旧结论已被后续证据部分更新，不能继续把该问题原样当唯一阻塞。但动态 local receiver 来源尚未补齐。

### 高价值推断（inference）

- mirror 的 body 错型足以解释为什么 recorder 可能写出 SCRIPT 标签；因此应先审身份/工厂，不应往 SCRIPT 补 attachShadow。此推断比“浏览器真的对 script 调用 attachShadow”有更强静态支持。
- 这只能作为 mirror 首错的候选机制，不是完整 Node 求解根因，更不是已完成五段 FO 的 RuyiDOM 后段失败原因。两条 pipeline 必须分别建因果账。

### 未知（unknown）

- local receiver 究竟来自 document.body、createElement、查询还是实际 script；computed x 键仍未解析。`agent-notes/local-receiver-origin-audit-20261005.md:11-15`。
- attachShadow options 的 mode 等深值未采集；现有 detail 只有对象 identity。不给 closed/open 猜值。
- 新 run 不是 canonical input；部分 DOMTrace complete=false、JSCall dropped_gate/per_func 限流和 sources_unavailable 存在。产物 integrity pass 不是行为全覆盖。`agent-notes/trace-compare-20261005.md:58-78,96-101`。

## 4. 当前最值得验证的假设（仅设计，不获本轮执行许可）

| 优先级 | 假设 | 最小判别证据 | 若否定则如何收窄 |
|---|---|---|---|
| P1 / Node | mirror factory/document typing 污染了已配对调用 receiver | 同不变输入/同原始 call-site 的 receiver-body equality、tag、ownerDocument、creation identity；随后单 surface typing 对照 | 若 receiver 真为 script 或修复后仍同错，放弃“body 错型解释这次调用”，不补相邻 API |
| P1 / RuyiDOM | 最后 FO 后某个等待/状态/异常使正常消费转入 timeout diagnostic | 同一 live session 中请求/响应引用、任务/计时/异常到首个排障 DOM 的窄因果记录；不检查 opaque 字节“高低分” | 若响应被正确执行且明确返回终止状态，转向服务端 decision/session；若缺回调/消息则定位单一语义机制 |
| P2 / RuyiDOM | urllib→Gecko 材料与 session/engine provenance 差异改变后续决策 | coherent fresh session 的起始导航→材料→FO→业务边界链；只改一个已观察差异，保留真实值 | 不混同“同 h3”与“同 TLS”；若链已一致则收窄执行消费路径 |
| P3 / transport | TLS/HTTP 细节仍参与最终拒绝 | 先有可比 challenge 执行和 coherent session，再做仅传输变化的配对 | 当前裸 GET 对比不满足前置；先换库没有高判别价值 |

不推荐：相邻 getter 扫描、追逐 opaque 首字节/长度、拼接旧 nonce/cookie/body、强制跳成功分支、同时修 factory+query+ShadowRoot+form transport。这些会把因果对照搅混。

## 5. 门禁是否形成证据死锁

- **fact**：是，当前门禁同时禁止 Node/canary/realm 新侧轨；已知最小 local provenance 证据需要执行一次不变输入动态记录，因此现行 action 无法产生这项证据。既有只读审计已经明确耗尽，不应重派同一份审计。`agent-notes/local-receiver-origin-audit-20261005.md:26-32`。
- **fact**：仅证明静态 runner defect 不满足当前 stop-search 重开条件。当前规则要求新的外部请求边界差异，且不是 opaque 字节/相邻字段；不允许把 hygiene 手改 ok 或把不完整目标当授权。`agent-notes/canonical-receiver-pair-20261005.md:29-33`。
- **inference**：这属于工作流取证许可不足，不是“模拟已被证明不可能”。本轮不改门禁，也不把浏览器已有 POST 偷换成本地新 boundary-moved。

### 合法重开需要满足的事实/授权

1. **现规则路线**：有可信、coherent input/session 的新外部请求边界差异（method/url/status/body-length class/目标提交出现等，且不是重复的 opaque 标签），经既有事实登记/CAS 流程接纳后再运行 next；仍只能执行返回的 action。
2. **若新边界无法在 hold 内获取**：同输入、同 call-site 的 local receiver provenance 可以继续取证，不另设次数或秒数。不能手改 stop-search，也不能伪造 boundary-moved。必须保持 goal、业务完成轴和原真实补丁不变；输出最小 identity 字段。
3. provenance 确认后，才讨论 factory/document typing 单 surface 对照；不自动授权 attachShadow、query、ShadowRoot 或整个 runner 重写。
4. 再往后仍须本地完整 FO/业务请求边界、parity、同 lease 独立业务 readback。当前 parity 目录空、无现成 test.py/readback receipt，不能用 exit0 或浏览器业务成功替代。`agent-notes/local-receiver-origin-audit-20261005.md:19-24`。

## 6. 业务备选与长期目标分轨

### 短期业务路线：browser-owned request RPC

- **fact**：控制面 Firefox 151 内 fetch 200/cert 分类已有两轮记录，说明可行性成立。`agent-notes/20261020-browser-js-rpc.md:3-9`，最新 JSON `agent-notes/20261020-browser-js-rpc.json`。
- **边界**：它是同源页面内 fetch PoC，Cookie/token 留浏览器，不是已经具备 API/session 池/并发/重试/失效恢复的完整 RPC 服务；标题/长度分类也不是完整业务字段正确性验证。
- **建议**：如果业务要先跑通，可另行明确一个浏览器采集/RPC 目标和验收合同：浏览器持有会话及网络、只返回清洗后的业务字段、串行 canary、会话过期重建、业务字段校验。不要导出 Cookie 再给 curl 并宣称等价。
- 不写 Node 的 localReproduced/serverAccepted，不把浏览器控制核的观察升级成 RuyiTrace browser fact。

### 长期研究路线：Node 独立求解

- mirror 的 FO=0 首错先归因；RuyiDOM 后段 response-to-diagnostic 独立归因。完成每条最小因果证据后才合流。
- 成功标准仍为 Node 自身 coherent fresh challenge→FO→证书请求→独立业务 readback；浏览器仅 oracle，不参与运行期代算/发包。

## 最终判定

**fact**：已证浏览器路径可用、RuyiDOM 后段不提交、mirror 模型确有污染；未证 TLS 唯一根因、未证服务器显式 noform 拒绝、未证不可模拟。

**下一步最高价值**：先解决“单次、不变输入、source-aligned local provenance 是否有明确可执行 action”的取证许可；若有，再验证 factory/document typing 一个机制。RuyiDOM 则需要对最后 FO 的响应消费/约 10 秒排障分支补真正的决策因果，而不是换库或追字节。

**当前阻塞**：`refuse_host_enumeration` / `blocked`；本轮只读收口，不执行上述候选实验，不修改门禁。
