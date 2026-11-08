# 固定输入 receiver provenance：执行与单一修正对照 / 2026-10-20

## 授权和门禁

用户在已明确描述“一次 hash 锁定、固定输入、仅记录 receiver 来源的离线诊断”之后回复“不需要我批准什么，需要排查就去做就行”。本轮将其作为该限定诊断及一次最小模型修正对照的明确授权，不将其扩展成在线宿主枚举。

Dispatcher 仍为 refuse_host_enumeration / blocked；本轮没有改 facts、gate、合同、原 runner、workspace.json 或业务验收轴。此次实验是独立诊断副本，不是恢复 live 主线或通过 environmentPatchGate。

## 输入与执行约束

目录：`diagnostics/receiver-provenance-20261020/`。

- `input-receipt.json` 锁定 4 份历史输入快照的 bytes/SHA-256（challenge HTML、orchestrate、API、frame packet），`input-verification.json` 证实两次运行后均未变。
- 原 mirror 与 realm wrapper 只读复制到 restricted；builder 复用原 wrapper 的唯一 It call-site 重写逻辑。原始 iframe source SHA-256 为 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`，两次运行均实际记录此 hash，candidate=1。
- `artifact-receipt.json` 锁定诊断 builder、断网 preload、单元测试、两个执行副本与原始副本的 hashes。
- 只执行 2 次 target runner（原逻辑观测 + body typing 单一对照），每次外层 timeout=15 秒，runner 本身 5 秒终止；实测各约 5.06 秒、exit0、stderr 空。exit0 仅表示诊断进程退出。
- 不冻结时间/随机源，不声称字节级确定性；固定的是输入/source 与其他 shim 代码。此观察依赖对象身份，不依赖随机数或不透明服务端字节。

## 断网与回放约束

`offline-preload.cjs` 拦截 http/https/http2/net/tls/dgram/dns/undici、子进程、worker/cluster、inspector 模块导入及 getBuiltinModule 路径，阻断网络/进程相关 process.binding；fetch/WebSocket/EventSource fail closed。独立 guard checks 12/12 通过，见 `guard-tests.json`。

副本保留 XHR.open/send 的无网络请求记录器，但 __deliver 显式拒绝；mirror 原有空 fetch stub 改成显式拒绝。不执行任何响应回放，不注入 FO 成功包。历史 frame packet 仅作为 source 输入，不交付服务端响应给 XHR。两次运行 xhrCount=0、deliveryEvents=0，日志无 OFFLINE_BLOCKED 标记。

限制：这是仓库诊断脚本已知 JS 网络入口的 fail-closed 防护，不是操作系统级隔离证明；没有修改系统防火墙/代理。执行副本的 require/process 暴露仍属于旧 mirror 模型，未称其为生产安全沙箱。

## 已确认的新动态事实

证据：`observed-receipt.json` 的 receivers[0] 及 sourceAlignment[0]；原始 stdout 仅留 restricted，不在聊天回传。

| 字段 | 原逻辑观测 |
|---|---|
| receiver stable ID | object-2 |
| receiver === document.body | true |
| receiver === head/root/currentScript | 均 false |
| receiver.tagName / constructor.name | SCRIPT / HTMLScriptElement |
| creation provenance | makeElement，requestedTag=null |
| body ID | object-2，与 receiver 相同 |
| document ID | object-4 |
| ownerDocument | 自有数据属性不存在；没有伪造值 |
| realm / document 关系 | mirror-shared-global；global.document、window.document 均为同一 documentStub |
| propertyKey | attachShadow |
| 运行错误边界 | 原 __rpRecv[__rpKey] is not a function 仍出现 |
| XHR / 响应投递 | 0 / 0 |

这次补齐了历史只读审计缺失的关键证明：**同原始 source、同唯一 call-site，local receiver 确实就是被错型成 SCRIPT 的 document.body，不是真实 script 元素。** 来源链为零参数 makeElement → documentStub.body → frame 共享 document → It 的 computed receiver → attachShadow 调用。

稳定 ID 是同进程 WeakMap side channel，只用于创建→使用 join，不向目标对象加 tag/ownerDocument/identity marker，也不冒称跨进程 native identity。ownerDocument 读取只查 own data descriptor，不调用 getter；缺失保持缺失。realm 标记来自本诊断分配/共享 document 记录，不是虚构浏览器 realm。

观测仍重写了既有 It 调用表达式，并会增加日志/耗时，不是零扰动；它保留原 receiver/method 调用且不吞异常。本轮第一处已知 TypeError、FO=0 边界与历史诊断一致，未见观测把它推动到下一请求边界。没有单独第三次“无观察”target 运行。

## 一次最小修正对照

证据：`control-receipt.json`、`body-typing-control.diff`、`factory-unit-tests.cjs` / `.json`。

唯一机制：document.body 的 tag/prototype typing。只将 body 的零参数工厂改为 makeElement('BODY')，为 BODY 使用独立 HTMLBodyElement.prototype；不改 head/root、createElement/NS、queries、ownerDocument、realm，不添加 attachShadow/ShadowRoot 或任何新方法。

对照结果：同 source/call-site、receiver ID=body ID、receiver===body 仍 true；tag/constructor 从 SCRIPT/HTMLScriptElement 变为 BODY/HTMLBodyElement；同一个 attachShadow 方法不可调用 TypeError 仍出现，XHR/投递仍为 0。

单元测试 12/12：分别验证原版/对照的 body tag、constructor、head 不变、body/head 非别名、attachShadow 仍 undefined、其他 createElement 错型未被顺手修复。此测试隔离 factory/document 构造，不运行目标。

**结论 1（fact）**：工厂错型与历史 receiver 的来源污染已被动态证实，不能再把 HTMLScriptElement.attachShadow 当待补浏览器 API。

**结论 2（fact / 反证）**：仅修正 body tag/prototype 不足以移除首个 TypeError。真正的调用仍是 BODY.attachShadow，而旧 mirror 对此没有 callable 实现；不能把“改对 constructor 标签”称作环境修复成功。

**结论 3（unknown）**：正确 BODY.attachShadow / ShadowRoot 行为是否能推进 Node FO、后面还有哪些缺口、是否与 RuyiDOM live 五跳后排障同根因。本轮不补该方法、不摸相邻字段，不从这一结果外推完整求解。

## 完整性与收口

`protected-verification.json`：原 mirror、原 realm wrapper、auto-decision-facts、dispatcher-turn 4 份受保护文件 SHA-256 全部未变。旧目录中未找到同名 environment-patch-gate.v1.json，因此未把不存在文件伪装成已校验；其他合同未写入。

本轮产物均在新诊断目录及本报告。原始材料/控制台留 restricted，含历史目标上下文，不复制进回复；没有 commit/push。

**下一步定位已收窄**：若未来继续同一诊断路线，应以浏览器 BODY receiver 的证据讨论 attachShadow 调用合同及返回 ShadowRoot 的实际必需行为，不能向 SCRIPT 上硬补，也不能把 typing-only 的负结果接成成功。本轮没有再开一轮执行。次数上限已取消。RuyiDOM live response→diagnostic 仍是独立未解问题，业务事实保持 false。

## 对 BODY.attachShadow 下一步资格的明确判断

- 证据资格：已具备 BODY.attachShadow 的 existence-miss 双条件证据。canonical browser 相同原始 source/唯一 call-site 的 BODY getter→attachShadow→ShadowRoot identity 见 `agent-notes/canonical-receiver-pair-20261005.md:9-17`；本轮同点 local receiver===body 且方法不可调用见 `observed-receipt.json`、`control-receipt.json`。这比先前 SCRIPT constructor 标签强，足以把候选 surface 从“错型 script”收窄为“BODY.attachShadow 的调用/返回行为”。
- 因果资格：没有证明 factory 错型是 TypeError 的充分原因。typing-only 对照未新增方法，错误不变；正确类型与可调用方法是两项不同要求。body 错型解释接收者标签污染，不足以解释或修复全部异常。
- 执行资格：证据进展不自动修改 dispatcher/gate。本轮用户限定授权不包含补 attachShadow，本 slice 当时没有追加实现。次数上限已取消，不构成以后不能再跑的理由。env-patcher 的正式环境补丁仍要求其 gate/dispatcher 条件成立，不能自行标 ready。若主线程明确组织新的单一 surface 诊断，候选应是 BODY/Element 上浏览器实际调用合同，不是 SCRIPT API；参数 mode 深值、返回 ShadowRoot 的具体使用行为仍需最小证据，不宜臆造。
- 可重复无目标单元测试：`D:\reverse_ENV\tools\node\node.exe D:\reverse_ENV\workspace\psa_solve\diagnostics\receiver-provenance-20261020\factory-unit-tests.cjs`（12 assertions，只执行 factory/document 构造，不执行 target）。
- 输入来源限制：保留原 mirror 的历史混合材料（9 月 28 日页面/API 与 9 月 29 日 iframe）；仅用于复现该历史 local 首错，不冒充 coherent fresh/live session，更不作为服务器响应回放或业务 parity。
