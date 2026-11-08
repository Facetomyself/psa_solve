# Grok 最新判断审计（2026-10-20）

## 范围与结论

本轮仅静态读取当前工作树与既有 trace，不执行目标、不补丁、不修改事实或调度、不恢复已暂停的求解 goal。最新证据界限为 22:20 的 `ruyidom-document-uri-receipt.json`（相关文档 22:21 更新）；未取得与此阶段对应的 Grok 对话全文，以下审计对象是其实际落盘回执和实现，不凭旧 last-copy 推断最新口头主张。

**有新的记账错误：最新“orchestrate 返回长度发生边界变化”被原始 trace 直接反证。另一个实质问题是仍以 9 月 30 日历史 challenge/cookie 运行 10 月 20 日在线诊断，不能据此验收 fresh live 求解。principal 修正确实改变了本地安全上下文，但这不等于已解决 Node ShadowRoot 卡点。**

## 1. P1：最新边界长度对照混用了 request body 和 response body，制造不存在的 classDelta

- 位置：`diagnostics/shadowroot-repair-20261020/ruyidom-content-open-receipt.json:22`，`ruyidom-document-uri-receipt.json:27,39–40`。
- 声称：前轮 handler GET orchestrate 为 `bodyLengthClass=0`，本轮为 `20000+`，据此记录“新增 20000+、移除 0”。
- 原始反证：`ruyidom-content-open-trace.jsonl:2` 与 `ruyidom-document-uri-trace.jsonl:2` 的同类 script row 都是 `bodyBytes=0, responseBytes=241280, served=true, responseStatus=200`；21:19 principal trace 同行也相同。
- 生产字段定义：`diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js:963–967` 明确把请求 hash/body 写成 `bodyBytes`，把本地映射返回源码长度写成 `responseBytes`。GET 请求 body 为 0 和响应脚本 241280 本就同时成立，不是前后改变。
- 触发与影响：跨轮从 `bodyBytes` 切到 `responseBytes` 却仍比较同一个 `bodyLengthClass`，把日志口径改变记成宿主行为推进。且 `served=true` 是本地 resource handler 命中，不是新发出的外部 orchestrate 请求。
- 修正建议：按 request/response 方向分开 schema，并从两份 raw 重建同口径分类。删除这条虚假的 orchestrate delta。不要直接断言整轮毫无变化：favicon/chain 等真实外部变化和 principal/异常变化应独立保留、解释。

## 2. P1：最新在线基线仍注入 20 天前的 challenge、orchestrate、cookie，不能用于 fresh challenge 因果验收

- 位置：`diagnostics/shadowroot-repair-20261020/ruyidom-document-uri-input.json:2–3,8`；content-open/principal 输入也沿用同一路径。
- 证据：三项都来自 `evidence/web/transport-diagnostic/3355e716c80b4c60b07c8caa5c2d2a57/`；这组 challenge、orchestrate、cookies 文件最后写入为 2026-09-30 19:16:53。最新 10 月 20 日 raw 的 handler 回源仍为同一个 241280 字符注入脚本。
- 触发与影响：以 `allowNetwork=true/liveNetwork=true` 发起运行，并不把历史 nonce、cookie、页面配置自动刷新到本次会话。因此这可作为固定旧输入的本地 principal/resource-loader 回归样本，但不能代表 fresh live baseline，更不能把 FO=0 直接归为当前线上真实 challenge 的宿主缺口。
- 修正建议：保留固定样本诊断身份；之后要做在线求解验证时，重新采集同会话输入与 cookies，记录 fresh provenance，并保持父进程 e10s/fission 设置一致。
- 限制：本审计未证明“这次就是服务端因过期拒绝”。事实上没有 FO；观察到的是本地异常和早停，不能再把过期猜测写成新根因。

## 3. P2：两条执行链的证据不能相互替代，当前新卡点尚未被 receiver 定位

- 位置：`runtime/lib/patches.js:18,43–53` 将 ShadowRoot surface 装在 vanilla Node 全局及 HTMLBodyElement；RuyiDOM bridge 最新变化则是 `diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js:518–519` 加载 `document-principal.js`。
- 这不是同一个执行面：最新 RuyiDOM 的 cert principal、null getEntries、undefined querySelector，不构成 Node ShadowRoot append 补丁成功或失败的证明。Node 20:37 回执仍是 `runtime/run.js`、空请求类、orchestrate/async errors；RuyiDOM 22:19 回执则是原生 Gecko document 替换路线。
- 最新原始错误在 `ruyidom-document-uri-trace.jsonl:5` 的 summary.scriptSites：`S[Gb(...)] is null` 后访问 getEntries；另一个为 `S[xS(...)][xS(...)] is undefined` 后访问 querySelector。
- 只能确认 receiver 为空/未定义；不能由此推出真实 `performance.getEntries` 或 `Document.querySelector` API 缺失，更不能推断该接收者就是先前 ShadowRoot。当前未见 Grok 对此作出明确 API 缺失的落盘判断，所以本条是**验证范围缺口和下一步归因约束**，不是认定它已经犯了该猜测错误。
- 修正建议：分开保存 Node 与 RuyiDOM baseline、patch 与 runner 指纹、输入来源及首错；后续先锁定首错 receiver/realm/创建阶段，勿按异常字符串直接补 API。

## Grok 本轮成立的判断

1. principal 问题不是凭空猜测：旧 trace 有 about:blank SOP load deny；最新 trace 的 lookup principal 与内部 documentURI 变为证书页面类，loadDenies 为空。独立 `principal-probe.json` 也证明内部 URI 与 title，但 targetExecuted=false，覆盖范围仅为小样本。
2. 最新脚本已执行到不同本地错误，可以认定本地执行形态变了；不应因为 FO=0 就抹掉这一进展。
3. 所有最新回执仍是 FO=0、POST=0、forms=0、submits=0；保留 serverAccepted/localReproduced/requestBoundaryAligned=false 正确。脚本 `ok=true` 是 harness 结果，不是业务通过。
4. `orchestrate-error.json` 不把空消息 TypeError 认定为 createElement 缺陷，这个纠偏正确。

## 对 boundary-moved 的精确界限

工作流允许 method/url/status/body-length 类真实变化，不要求每次都必须出现 FO 才算移动。所以不能仅凭 FO=0 宣布所有 boundary-moved 非法。content-open 的新增 `/g/chains/...` 确实出现在真实 necko/response 中；principal 轮还有相关响应消失。但此类 `hostClass=other`、`secDest=''` 的链下载和 favicon 变化，现有证据未关联到 challenge JS 的必要前置请求，不能用来证明 ShadowRoot patch 有效或挑战推进。应把**真实后台网络差异**、**本地 handler 命中**、**挑战/业务边界**拆开，而不是只算集合有无变化。facts hygiene 当前为 ok 是现状，不是本审计认可这些变化具有目标因果性的结论。

## 证据与下一步

- 脱敏、可重算字段对照：`diagnostics/grok-latest-audit-20261020/trace-comparison.redacted.json`。
- 首先更正回执口径，不在本审计中改 facts；其次固定一条有效、fresh、同 runner/同配置基线，再定位首错对象。长期 goal 继续保持暂停。
- 未读取或输出 Cookie/token/指纹原值；未执行任何 target 或网络实验。
