# Web Case Index

Case: `psa-cf-5s-shield-20260815`

Read only the files in `web_case.py next` → `docs.read`. Use this index for current status. Do not open `experiments.md` unless a section is named.

## File Map

| File | Read when |
| --- | --- |
| interfaces.md | new endpoint or request boundary |
| request-chain.md | call order, challenge versus business |
| crypto-parameters.md | signer, hash, encryption, encoding |
| risk-analysis.md | challenge, throttle, lease, scale |
| environment-patch.md | RuyiDOM or host patch |
| pure-compute.md | browser-free generator |
| experiments.md | named rejected route only |
| index.md | current status only |

## Current State

- 2026-11-07：**状态迁移（权威总览见 `../../docs/status-20261107.md`）**。ruyijs 线已生产化（fresh-navigate ~12s 全链到 cert readback；clearance 导出给 curl_cffi 同 IP+UA 复用 → 业务 200），workspace.json 的 hold_challenge/patching 状态未同步（调度器 `web_case.py next` 因 facts 键 ruyijsLiveEmit 版本不匹配崩溃）。Node 桥定性为 capture-only：消变体同字节下 FO r1 后第二层键控解码不收敛（调用方 f8 无界自旋，非慢），不再作为完成门；10-23 及以前的 form.submit/blocker 记录属旧路线，被 11-07 变体轮换实锤重新定性（跨会话材料不可混用）。静态 payload 链：FO r1 body = 明文对象 → v0 内部加密 → 自定义 base64；alphabet 可静态提取；CfReverse LZ 配方不适用。诊断产物 `diagnostics/atob-diff-20261107/`。
- 2026-10-23：第二个 blob Worker 返回之后，记深度 2 及以上最热的 Reflect.apply 被调。第一页没有第二次 worker 返回，回执页是 `node-postd2-live-2`（06:49:42Z）。编排 200 / 250108，页面字节 5726，title length 16，cookie 文件 2 对。challenge-fo 在武装时已经是 200。这不是证书 document POST。求解 stdout 未解析。Reflect.apply 46000001 次。深度 0 进入 102 次。深度 1 进入 10915 次。深度 2 及以上 45988984 次。身份表 13 行，溢出 0。最热一行 20904027 次，份额 p10to50，非原生，元数 3plus，名字长度类 len2，接收者 undefined，首参 number，参数个数 1，返回 number 且稳定，未抛。它与 form.submit、createElement、createElementNS、requestSubmit、setAttribute、getAttribute、appendChild 都不是同一函数。源码宿主记号全否。form.submit、createElement、createElementNS 都是 0。拒绝原因是 script-number。没有点名能发出证书 document POST 的宿主读取，没有改宿主。没有改写 Node `env.js`，没有新的官方 baseline。进程在 18 秒被切断，wall 18081 毫秒，没有同租约读回。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。`next` 没有 factWrites。盖章 `2026-10-23T06:51:56Z` 仍是 `authorize_form_construction_surface` / `blocked`。见 `agent-notes/20261023-post-d2.md`。
- 2026-10-21：同一改动的前一回 `c9e876f152f046e483ce6d7c89228cba` 在 helper 里扫描整段空白，慢脚本落在 helper 第 830 行，已收成只看首尾。更早的 `d05075ea12b04dc29246d5ecd148db78` 仍是源文件外第 1337364 列。scope 都没变。完成轴没有写。
- 2026-10-20：探针记为 `boundary-unchanged`。11:48Z 两次新鲜 Node 重跑没有证书 document POST，同租约读回仍是 403 挑战页。完成轴保持 false。见 `diagnostics/shadowroot-repair-20261020/node-rerun-receipt.json`。
- 2026-10-20：两次新鲜 Node 求解都没有证书 document POST，同租约读回仍是挑战页。`serverAccepted` 保持 false。见 `agent-notes/20261020-node-solver-sessions.md`。
- Case status: `patching`
- Current stage: `environment-patch`
- Current hypothesis: 分叉位于顶层 clearance FO response → DOM branch。旧有头样本创建 form 并提交；本轮本地转到排障 DOM。3488/3792 只是长度标签，不能作为通过判据或根因。
- Exit criterion for this stage: 同一会话业务页 readback 200，再写 `serverAccepted`。
- Last slice: 2026-10-20 返回 ShadowRoot 的 append 存在性为 blocked。append 实现已经会留下子节点，patched 日志里调用没有落到该 root；第一段缺失构造 `Document.createElement` 本拍未打开。见 `agent-notes/20261020-shadowroot-existence.md`。

## Route And Landing Decisions

- Product hit: Cloudflare managed challenge。当前现场是点击挑战。
- Active evidence plane: 权威 baseline/receipt/workflow 为 `rt_20260929103550_341b734038`。`rt_20261005125421_1d84c46dcd` 是最新观察补充，未晋升为 canonical input。本地执行 RuyiDOM CLI。
- Landing primary: `env-patch`
- Contracts: workflow `blocked`；lineage `diagnostic-only`
- Latest static review: `agent-notes/receiver-static-review-20261005.md`。mirror 的 body/head/root/createElement 被错型为 SCRIPT；接收者记录仅为 constructor.name。尚未证明 It 的来源，不补 HTMLScriptElement.attachShadow；无新运行/请求边界，纯 Node 目标与 blocked 保持。
- Latest trace correction: `agent-notes/firefox-receiver-provenance-20261005.md`。真实浏览器已看到 `HTMLDivElement/HTMLBodyElement.attachShadow`、`HTMLFormElement.submit` 和 cert document POST 200；这只修正 browser fact，不等于 `serverAccepted`。
- Latest comparison: `agent-notes/trace-compare-20261005.md`。同 run body/div identity 链已证；新旧 iframe source hash 不同，尚无 local pairing。iframe complete=false / JSCall dropped_gate=611 / 17 函数达到阈值；receipt pass 不代表全覆盖。不修 runner、不解闸。
- Latest pairing: `agent-notes/canonical-receiver-pair-20261005.md` 已把旧 baseline 与 local 原始 inline hash 和唯一 call site 对齐（HTML 前缀19390解释列号差）；浏览器 receiver 来源为 BODY，local 仍缺 receiver/body equality。新 run detail 的4个目标call已解码并按pid完成identity join，见 `agent-notes/jscall-detail-decode-20261005.md`；options仍identity-only。未执行target或patch，dispatcher保持blocked。
- Receiver-origin audit: `agent-notes/local-receiver-origin-audit-20261005.md`。computed x 初始化与历史输出不能证明 local body identity。FO=0、parity目录空、独立readback缺失；所需同点local动态记录仍被当前合同禁止。没有新的执行进展，不再重复已有数据审计。

## Blocker

- Stuck point: `form.submit` 没有发生。本地 `forms` 0，`mapMax` 38，尾部是排障页。证书 document POST 缺失。
- Current measured facts: 锁定 RuyiDOM Firefox 135 base（UA override=155）；widget `complete`、Turnstile nested document、站点分区 `cf_clearance` 均存在。关闭 engine-local 系统应用代理继承后，5 条 FO 实测恢复 h3；forms/submits 仍 0，无证书 POST/readback。
- Causal-observer live (restricted): harnessHealthy=true，widgetComplete=true，forms=0，submits=0，causalEventCount=25（document.write / createElement / innerHTML / request / response），hasFormCreate=false，hasSubmit=false，causalFinalPresent=true，certDocumentPostObserved=false。7 条边界：page GET h3、5× challenge-fo POST h3、1× unresolved GET h2；无 cert-document POST。
- Causal-observer chain class: `complete-to-diagnostic`。hop1 page-host FO POST reqLen=8695 → hop2 同请求 `cf-chl-out` 响应（header name 存在，body 长度标签 3488，opaque/noform）→ hop3 首次 DOM 为 createElement h2（约 10s 后）→ hop4 排障 `h2/p/ol/li`，无 form。不是新的外部请求边界。
- Ruled out: 残留 cookie、应用层代理、解码首字节打分。
- Hold: transport 差异经 native log 与单变量 live 复验已修复；凭证/CAS 将 firstDivergence 收回 environment-gap、hygiene 收回 stop-search（revision=4），业务验收字段仍 false。不继续网络相邻 prefs 或宿主 getter 枚举。
- Scope: 不执行 orchestrate 字符串表或 VM opcode，不以第二份脚本完整性为前提；Worker 旧零计数仅限被观察域。真实清理基线、能力快照、response→DOM 因果 live receipt 均已完成；因果链仍无 form/submit。

## Next Minimal Action

- Action: `refuse_host_enumeration`。causal-observer receipt 仍是 `executed-hold`，这是已有证据，不是任务次数上限。链已 `complete-to-diagnostic`，不恢复相邻字段搜索，不写 `serverAccepted`。
- Required evidence: 同一外部宿主缺口的 browser-fact receipt，然后 `environmentPatchGate` 才能 ready；请求边界要到 cert document；独立 readback 200 之后才写 `serverAccepted`。这四项现在都缺。已有受限因果分类不能当业务通过。
- Stop condition: 相邻宿主字段停止。真实双条件补丁保留。proxy.type=0 保持。
- Completion target: Node 独立求解与请求响应闭环，浏览器仅作 oracle。不能拿 browser POST 200 或只通过 DOM 桩测试当作 Node 完成；本地 parity、目标请求和独立同 lease readback 均待证。

## Last Experiment

- Pointer: `agent-notes/20260930-causal-observer-chain.md`（chainClass=`complete-to-diagnostic`）；采集摘要 `agent-notes/20260930-causal-observer-live.md`；receipt `evidence/web/diagnostic-causal-observer/receipt.json`（`executed-hold`，claimId `90aa1f82-e1ee-447e-aeeb-2b9c0c865fb9`）。transport 闭环仍见 `agent-notes/20260930-transport-live.md`。
- Active clean baseline: `diagnostics/clean-baseline-20260930/ruyidom_bridge.stable-transport.js`；observer 是 reviewed transport-fixed 副本，保留 `network.proxy.type=0`。cleanup / instrumentation v1 / v2 独立 receipt 未改。
- Limitation: urllib UA135 → Gecko 是逻辑 cookie/材料交接，不是同 TLS/同导航。`executed-hold` 与 widget complete 都不是业务通过。顶层 light-DOM 最终 iframe=0 不代表未加载 iframe。

<!-- generated:index -->
- Case: `psa-cf-5s-shield-20260815`
- Status: `patching`
- Stage: ``
<!-- /generated:index -->
## 2026-10-20 Shadow options static recovery

- 同 canonical source / 唯一 BODY.attachShadow call-site 的 options 已纯静态恢复为 mode=closed：字面量表和 browser-fact key anchors 的索引同余约束，无 target/decoder 执行。mode 应读取调用实参，不硬编码历史值。
- 证据：`agent-notes/20261020-shadow-options-static.md`、`diagnostics/shadow-options-static-20261020/options-receipt.json`。仍 `refuse_host_enumeration` / `blocked`，不改 gate/facts；下一步需要受准的单 surface 行为集成，不再重复 mode 静态审计。
## 2026-10-20 Scoped ShadowRoot repair

- 用户明确授权的固定hash、断网单surface修复已正式check/claim/execute/record，baseline/patched各1次；未改全局gate/hygiene。patched按真实实参创建closed root，原attachShadow不可调用错误消失。
- 下一错误为root空树querySelector返回null后的zF/null.appendChild；没有伪造命中或继续补API。两边只有相同1次未send的POST open意图，无FO/业务请求边界。
- 回执：`diagnostics/shadowroot-repair-20261020/receipt.json`；报告：`agent-notes/20261020-shadowroot-repair.md`。surface tests38/38、receipt tests4/4；Node/live验收仍未完成，dispatcher保持refuse_host_enumeration/blocked。
