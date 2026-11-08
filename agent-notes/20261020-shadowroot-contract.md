# BODY.attachShadow / ShadowRoot：同源消费合同 / 2026-10-20

## 状态与真实增量

本拍 dispatcher 仍为 `refuse_host_enumeration / blocked`；无 live 句柄。未执行 challenge、target JS、浏览器、网络或新增 API 探针；未修改原 runner、facts、gate、合同、goal/next/闩字段。

**本轮真正新增的是 canonical 同一 ShadowRoot 的消费数据流，而不是“模型单测通过”。** 已确认 root 返回后实际承接 3 次 appendChild 和 6 次 querySelector；6 次查询都能连到已创建、已赋 id、已插入该 root 子树的原节点，含重复返回同一个节点。这把“只补一个空 {} 返回”的方案直接排除。

产物目录：`diagnostics/shadowroot-contract-20261020/`；机器证据见 `evidence-contract.json`、`consumption-provenance.json`、`query-tree-joins.json`。所有结论来自既有 trace 的数据解析，不执行 trace 内目标代码。

## 1. 参数与返回：哪些可确定

- Canonical source：`05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`；run `rt_20260929103550_341b734038` / pid48444。
- 原始 trace：`evidence/web/ruyitrace/rt_20260929103550_341b734038/raw/domtrace/trace_process_48444.ndjson`，500472 行，SHA-256 `ee9e83c5bbe29db7a7d285dea0f870cc77b463551b8fe0b135c63616dc14137d`，与此前 source-pair 回执一致。
- `:97` 的 body getter return 与 `:98` attachShadow receiver 为同一 HTMLBodyElement；`:98` 接收一个 Object 参数，返回 ShadowRoot identity。
- 上轮 local 同 source/唯一 call-site 动态证明 receiver===document.body；typing-only 对照后 BODY.attachShadow 仍不可调用。证据：`diagnostics/receiver-provenance-20261020/{observed-receipt,control-receipt}.json`。
- **未知：mode/delegatesFocus/其它 options 深值。** canonical DOM args 是泛型 Object；补充 10 月 5 日 run 的 detail 仍 identity-only，且其 source 不同，不能跨源借值。`agent-notes/jscall-detail-decode-20261005.md` 已明确此限制。
- 对 canonical source 只作文本检查：It 内调用前 b={}，接着通过 computed key/value 配置；没有 mode/open/closed 明文字面量。未执行字符串表/decoder，不能从名字或经验猜 closed。

## 2. 同 root 实际后续消费合同

以下行号均指上面的 canonical trace；join 以同 run/pid 的非零 native identity 为准，不混跨进程 JS ID。

| 位置 | 实际操作 | 已确认语义 |
|---|---|---|
| :181 | root.appendChild(style) | 参数 HTMLStyleElement 与返回对象 identity 相同 |
| :752 | root.appendChild(div) | 参数 HTMLDivElement 与返回 identity 相同 |
| :797/:814 | root.querySelector(#id) | 两次返回同一 SVGSVGElement，不是每次制造新节点 |
| :802/:809 | root.querySelector(#id) | 各返回此前创建的两个 HTMLDivElement |
| :812/:816 | root.querySelector(#id) | 各返回此前创建的另两个 SVGSVGElement |
| :907 | root.appendChild(iframe) | 参数 HTMLIFrameElement 与返回 identity 相同 |

六个 querySelector 参数都是简单 #id；原值不写报告。回执保存 selector 形状、匹配布尔与位置，不保存指纹/选择器原值。

### 节点创建、id 赋值与子树关系已闭合

| query 行 | creation 行 / 方式 | set id 行 | 查询当时到 root 深度 | 结果 |
|---|---|---|---|---|
| 797、814 | 207 / createElementNS | 211 | 5 | 同一节点，id 精确匹配 selector |
| 802 | 201 / createElement | 202 | 3 | id 精确匹配 |
| 809 | 189 / createElement | 190 | 2 | id 精确匹配 |
| 812 | 411 / createElementNS | 412 | 4 | id 精确匹配 |
| 816 | 377 / createElementNS | 378 | 4 | id 精确匹配 |

数据处理仅重建 trace 里真实 appendChild 的 parent links，在每次 query 时检查是否归属于该 ShadowRoot；六次均 true。此组节点不是凭 innerHTML 文本猜出来，也无需用顶层旧 HTML 快照查询：它们有显式 createElement/NS、set id 和 appendChild 链。不能把该局部结论扩成“整个挑战不需要 innerHTML/HTML parser”。

### open / closed 能否进一步约束

定向检查该 BODY 的 shadowRoot accessor 与该 root 的 mode accessor：本 trace 未观察到对应读取，因此无法排除 open/closed 任一模式。closed 同样可以通过 attachShadow 返回值持有 root 并进行 append/query；“后续能用 root”不证明 open。

trace 尾部 session_stopped.complete=true；这里只说明该 producer 的结束状态。property hooks 未覆盖的行为或其它 realm 仍可能存在，不能把未观察写成“浏览器没有读取”。

## 3. 精准双条件证据与正式规则

`skill/web-env-patcher/references/existence.md` 要求 browser 已触达 + local 确实缺失。BODY.attachShadow 已满足这项**证据条件**：canonical browser :97-98 与上轮 local 真实 body identity/不可调用记录可配对。

这不等于**执行授权和完成条件**成立：

- `skill/web-reverse/scripts/web_case.py:2701-2703` 在后续 env 分支前返回卫生决定；`:2516-2524` 对 stop-search 返回 refuse_host_enumeration/blocked。
- `contracts/workflow-artifacts.v1.json:1088-1095` 的 environmentPatchGate 仍 not-ready，patchCoverageIds 为空。新的 root 合同不是新的外部请求边界，不满足 pause-boundaries 第 20 条的恢复事实。
- 正式 `fact record`（`web_case.py:3354-3361`）只接受 allow-listed decision keys，不接受任意 ShadowRootContract/receiverProvenance 字段。不能通过改 hostBlocker/firstDivergence 或把 hygiene 写 ok 让这种结构性证据变成 boundary-moved。
- 现有一次性诊断入口锁定原 RuyiDOM profile，并不包含本次 BODY.attachShadow 行为修改；本轮因此只写 artifact，不伪造新 fact schema，不调用写事实命令，不运行修正后的挑战。

结论：应记录为“精准 existence-miss 与返回消费合同证据已补齐，正式行为修正仍受 hold 约束”。不是重复要求用户批准常规操作，而是明确 dispatcher 尚无匹配的执行动作。一般 goal 不会自动解闸。

## 4. 独立、严格有界的宿主单元实现

`shadow-model.cjs` / `shadow-model.test.cjs` 只测试宿主机制，不导入目标、旧 runner、网络或服务端响应。41 assertions 通过，`test-receipt.json`，可复测：

`D:\reverse_ENV\tools\node\node.exe D:\reverse_ENV\workspace\psa_solve\diagnostics\shadowroot-contract-20261020\shadow-model.test.cjs`

实现的有限合同：BODY 显式 open/closed；返回独立 ShadowRoot/DocumentFragment/Node 链；host/ownerDocument/parent identity；appendChild 返回原节点、重挂接/循环拒绝；root 内简单 #id 递归查询、miss=null、重复返回同节点、隔离其它 root。用 WeakMap 私有状态、错误 receiver 拒绝，不用通用 Proxy 兜底。

**实现边界必须说透**：这是 standalone model，不是 native 实现，不伪造 Function.prototype.toString 的 [native code]；不宣称完整 WebIDL/descriptor/brand parity。只支持 BODY host 和 mode；未建模选项/selector/cross-document 操作显式拒绝，属于模型“不支持”而不是宣称浏览器也拒绝。没有 HTML parser、CSS/rendering、SVG namespace/full SVG type、iframe realm、events/slotting/layout、完整 ShadowRoot 生命周期。没有接入 runner，没有观察目标消费它，没有证明自然走出一个新请求。

41 assertions 只证明这些手写单元语义自洽，**不构成 goal progress 的充分证明**；本轮与目标直接相关的进展是第 2 节从真实 root identity 提取的 3 append / 6 query / creation-id-tree 数据流。

## 5. 长期真实交付标准与收口

`workspace.json:4` 当前 goal 明确：Node 独立求解，浏览器仅 oracle；同一 fresh 输入/session 完成自然请求响应、目标提交、parity 和约 5 秒后同 lease 独立业务 readback 200。当前 auto-decision-facts 仍 localReproduced=false/requestBoundaryAligned=false/serverAccepted=false。

修复一个 TypeError、执行 41 个单测、拿到 ShadowRoot、浏览器 POST200，均不能替代该交付。旧 mirror 使用历史混合输入且无真实网络，尤其不能算 fresh/live parity。

**本轮收口**：返回 root 的实际必需合同已从“未知空对象”收窄到“独立树、原节点 append/#id 查询及身份保持”；mode 深值、完整对象品牌/namespace、host 后续行为仍未知。无新 live 边界，不改 gate、不执行挑战对照。下一项正式动作需要把这一精确 surface 的证据与可执行一次性受审诊断/dispatcher 规则接上；不是改卫生事实，也不是继续枚举字段。RuyiDOM 五跳后 response→diagnostic 因果仍独立未解。
