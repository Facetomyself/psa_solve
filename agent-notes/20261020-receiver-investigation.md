# Receiver 有界静态排查 / 2026-10-20

## 范围与状态

主线程本拍实测 `next=refuse_host_enumeration / turnGate=blocked`。本切片仅静态读 receiver 工厂、probe 记录路径、dispatcher 及诊断合同；没有运行目标、Node/browser/network/canary，没有修改 facts、gate、runner 或 workspace.json。历史 trace 仅作离线证据。无运行句柄。

项目路径相对 `D:\reverse_ENV\workspace\psa_solve`；技能代码路径相对 `D:\reverse_ENV`。

## 1. 静态污染链已闭合到“哪些对象必错”，未闭合到“历史 x-call 取了哪一个”

| 步骤 | 精确位置 | 已证数据流 |
|---|---|---|
| 分配器默认类型 | `runtime/mirror-canary.js:45-47,60` | 缺 tag → tagName=SCRIPT → 原型置为 HTMLScriptElement.prototype |
| document 固定节点 | `runtime/mirror-canary.js:121-122` | head/body/documentElement 各自零参数 makeElement，故三者必被错误标为 SCRIPT；它们是独立分配，不是别名 |
| create 工厂 | `runtime/mirror-canary.js:114-115` | t 参数完全丢弃，createElement/NS 总调用零参数 makeElement，动态创建 tag 被污染 |
| global 引用 | `runtime/mirror-canary.js:145-151,198-200,215-218` | global.document 和 windowMirror.document 均引用 documentStub；documentStub.defaultView 回指 windowMirror。window/global 分离没有隔离 document |
| frame 入口 | `runtime/mirror-canary.js:239-245` | 只替换 currentScript 与 location.href 后间接 eval frameScript；未分配 iframe 专属 document，也未切换独立 realm，因此该路径继续可达已错型 body |
| probe 实际接收者 | `runtime/realm-probe-canary.js:96-106,115-123` | 选择 It 内唯一 x[第一计算键][第二计算键](b)；IIFE 的第一个实参为 x[第一计算键]，即真正 receiver；只将第二键转成 propertyKey 记录 |
| label 生成 | `runtime/realm-probe-canary.js:118-120` | 读取 receiver.constructor.name 得到文本标签；没有记录 tag、owning document、stable identity、body equality 或第一键 |

**fact**：错型对象的构造与共享 document 可达链已能直接从源代码闭合；不是仅据历史日志猜工厂 bug。

**inference**：如果 x-call 的 receiver 是 body 或由 createElement/NS 生成的节点，现有代码必然让 recorder 得到 SCRIPT 标签；这为历史读数提供了无需“真实 script 支持 attachShadow”的解释。

**unknown**：本次历史 x-call 的第一计算键及 receiver 来源仍缺。现有原始 source/call-site 对齐只证明“同一处调用”，不把 local receiver 自动变成 browser 的 BODY。既有只读审计已确认 x=h[aH(2153)] 未解析；见 `agent-notes/local-receiver-origin-audit-20261005.md:11-15`。本轮不执行字符串表/目标来强行闭合。

### 两个容易漏掉的静态细节

- 查询不等于工厂：`mirror-canary.js:76-110` 的 class 查询会保留匹配到的真实 tag，不应说所有节点都变 SCRIPT；但 `:51-52,117-119` 查询忽略 receiver/document scope、未命中伪造 DIV，重查重建对象，故 identity/ownership 仍不真实。
- frame 状态恢复只在成功路径：`:247-248` 的 location/currentScript 还原不在 finally；`:249-252` 捕获同步 eval 错误时不还原。**fact** 是失败路径可残留 frame 状态；**unknown** 是历史 It 异步错误是否经过该同步 catch，因此不能把它记作本次根因。

## 2. 最小缺失观测，精确到一个点

同源 hash、同唯一 call-site、不变输入下，在调用前一次记录：

- receiver===document.body、receiver===document.head/documentElement/currentScript；
- receiver.tagName / nodeName / constructor.name；
- receiver.ownerDocument 与当前 document 的 stable identity/equality；
- 第一计算键及 creation/query 来源 marker（仅结构性值，不输出凭据/参数）；
- 保留原方法调用与原异常，不吞异常、不补 API、不替换响应。

这只是最小诊断输出合同，不是执行授权。身份确证后才有条件验证 factory/document typing 单一 surface；不要并修 queries、attachShadow、ShadowRoot、form transport。mirror FO=0 的首错仍不能解释 RuyiDOM 五段 FO 后的排障分支。

## 3. 正式诊断入口核查

### Dispatcher 优先级

- `skill/web-reverse/scripts/web_case.py:2701-2703` 先调用卫生判定并立即返回。
- `:2516-2524` 对 stop-search 无条件返回 refuse_host_enumeration/blocked，保留真实双条件补丁并禁止相邻字段。
- `:2920-2921` 的 fix_session_provenance 是 session-state 分支，位于上述 return 之后，且对象是 Cookie/storage writer，不是 receiver provenance。不能把两个 provenance 名称混用，不能改 firstDivergence 绕过。
- `skill/web-env-patcher/references/pause-boundaries.md:87-99` 要求新的外部请求边界差异才能恢复，普通“开始/继续”不豁免。

### 已注册入口及适用性

`web_case.py:3856-3898` 的四个一次性命令为 diagnostic-cleanup-baseline、diagnostic-instrumentation、diagnostic-instrumentation-v2、diagnostic-causal-observer；其余 parser 子命令注册在 `:3900-4026`，没有 receiver/local-provenance 专用命令。

- cleanup 是固定 hash、delete-only 的 RuyiDOM 候选；不能传任意 Node runner。合同见 `skill/web-reverse/references/diagnostic-cleanup-baseline.md` 的“不是 caller 自报的白名单”。
- instrumentation/v2 的 `scripts/diagnostic_instrumentation.py:90-108,169-174`（v2 相同对应区间）校验固定 case/profile、clean 和 instrumented RuyiDOM runner，不能把 mirror 或 realm-probe 当参数塞进去。
- causal observer 是固定 transport-fixed RuyiDOM response→DOM 观察器，非 receiver probe；`skill/web-reverse/references/diagnostic-causal-observer.md` 明确只批准 reviewed profile，不能自报新 runner。
- 现有 causal receipt `evidence/web/diagnostic-causal-observer/receipt.json:2-8` 为 executed-hold，字段 `budget: 1` 是当时的计数，不是任务上限。

**结论**：在本次检查的 dispatcher、已注册诊断适配器及当前阶段 references 中，没有适用于 mirror receiver-origin 的可执行一次性诊断入口。已有命令的 `--provenance` 是绑定 fresh challenge 材料的文件，不是通用“允许记录 receiver 来源”的授权开关。

通用命令合同为 `web_case.py diagnostic-<已审查动作> --project <绝对路径> --phase check|claim|record --opt-in`，claim 另需相应 schema 的 --provenance，record 另需 --execution-receipt；本轮未执行这些命令，也没有给 receiver 缺口伪造可运行命令。

## 4. 收口与真正阻塞

**已推进**：把污染源闭合为“丢 tag 工厂→固定 document 节点→global/window 共用 document→frame eval 仍共享→probe 只看 constructor 标签”，并核实正式入口没有覆盖这个缺失观测。

**不能升级的结论**：没有证明历史 local receiver===body；没有证明修复后越过首错；没有 local parity/FO/业务 readback；没有修改任何门禁。

**下一步条件**：继续动态排查仍要有不变输入的 receiver-provenance 证据，或符合现有规则的新外部请求边界差异。不另设一次性次数或秒数。当前“开始排查”只授权本拍静态调查。
