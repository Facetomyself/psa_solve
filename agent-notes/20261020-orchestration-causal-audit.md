# Grok 反复误判的编排机制归因审计

日期：2026-10-20。仅静态检查当前代码、已有测试与既有证据；未运行目标、未写 facts 或源码、未恢复 paused goal。主线程本拍为 record_host_probe/blocked，本报告不消费它。

## 总结

**不是“只有 Grok 能力不行”，也不是“逆向主线全错”。当前存在可定位的编排薄弱点：把人的证据结论当类型化事实、把发动作当完成动作、把跨轮证据压缩成无作用域布尔值。它们会把一次推理失误放大成合法的后续调度。** Grok 对请求/响应长度混用、旧输入当在线基线仍负有直接执行责任；编排没有阻断这些错误。模型间相对能力与错误率没有同任务对照，无法据此量化。

下列“fact”表示可由当前代码/测试/已落盘证据核验；“inference”表示机制后果推断；未执行新的复现程序。

## 1. [fact] typed fact record 只核验文件存在/hash，不核验“文件是否证明该事实”

**代码位置：** `skill/web-reverse/scripts/web_case.py:3356–3392,3446–3476`。

- `_record_evidence` 验证项目内路径、存在性、SHA-256；未解析证据 JSON 的 schema、raw 来源、session、runner、目标请求或 boundary delta。
- `fact_record_command` 直接 `payload[key] = value`，normalize 枚举后记账。verified token 是 **value 的 hash**（3462–3470），不是从 raw 求出的结论；judgment 记录路径，未保存“哪个 raw 字段证明哪个判断”的可校验关联。
- 测试 `skill/web-reverse/tests/test_web_case.py:2504–2542` 用仅有 `{"ok":true}` 的 JSON 成功登记 `hostProbe=same-surface`，恰好确认当前验证承诺只到文件完整性和 revision。
- 本案实证：最新审计已证明 content-open/document-uri 两轮 raw 都是 `bodyBytes=0,responseBytes=241280`，人工 receipt 却记作不同长度类；hash 完整也无法纠正语义错。

**反事实：** 换强模型会降低填错概率，但相同错误依然能被系统接受。正确模型也无法把“系统接受”当成证据正确。

**建议：** 不删 fact ledger/CAS，而把 `hostProbe`、hygiene 恢复等关键事实改为专用 receipt 类型，由确定性 reducer 从固定 raw 字段计算；分 requestBodyLength/responseBodyLength、local handler/external wire、challenge/background。人工只能解释关联，不直接决定机器可算的 delta。

## 2. [fact] 调度在“发出 rerun”时就写成 awaiting-record，没有证明 runner 真执行，更未绑定 fresh/session/config

**代码位置：** `web_case.py:2071–2090,3582–3623`；`_executor_name` 在 1898–1901；freshness 完成验收约束在 806–810。

- `rerun_host_baseline` 的 `same-runner` 只是 constraints 字符串；选择 executor 仅看 ruyidom 状态与 noOfflineFallback。
- 发出该动作立即带 `factWrites={hostProbe:awaiting-record}`（2090），`next_command` 立即持久化（3617–3618）。没有执行 receipt 才准转换的检查，也没有活进程 handle/terminal receipt 验证。
- 测试 `test_web_case.py:2652–2702` 连续调用两次 `next_command`，未运行任何目标，就从 environment_patch 到 awaiting-rerun，再到 awaiting-record；第三次提示“同一 runner 已重跑”。这不是仅未测边角，是当前状态机明确允许的行为。
- 通用 next 的该分支没有绑定 runner hash、父进程 e10s/fission、材料 epoch、session/cookie provenance。资源过期检查 806–810 仅在 workflow status=verified 才触发；资源刷新路线 3008–3013 依赖人工先分类 resource-drift/session-state。
- 本案于是出现 Node rerun 代替 RuyiDOM stamped executor、RuyiDOM 同路径但父环境不同、20 天前材料仍能被叫作在线 baseline；正式 next 无法独立识别这些差异。

**反事实：** 即使更强模型误点一次 next 或重入会话，仍可能得到“已经重跑”的假前提。正确执行者若丢了上轮 receipt，只能人工回溯，不是机器保证同 runner。

**建议：** `issued → running → completed → classified` 分离；发动作不等于执行。rerun receipt 必须绑定 patch/base runner hash、executor/runtime、input hashes、session provenance、关键父环境、真实 terminal 状态。保留离线固定样本用途，但明确不得升级为 fresh live acceptance。

## 3. [fact + inference] dualCondition / hostProbe 的作用域过粗：一面证明可以无声流到另一面；unknown 也未 fail closed

**代码位置：** `web_case.py:1334–1395,1512,1674–1678,2000–2013,2567–2599,3171–3195`。

- dualCondition 为全局 bool/default None；hostProbe 为全局枚举；authorizedSurface 只需是非空字符串。没有 browser/local receipt pair + source/callsite + receiver/property + runner + epoch 的结构化绑定和失效规则。
- `same-surface && dualCondition=true` 就可重新开环境 patch；代码无法判定“same”真是哪一个 surface，也无法判断旧浏览器证据是不是当前 runner 中的 receiver。
- environment-gap 路线仅在 dualCondition **is False** 时拒绝（3171），None 在非其他阻挡条件下仍可走 `_environment_patch_decision`（3195）。所以双条件必需在此处没有完整落实为 fail closed。
- 因而表面上有严格门禁，实际关键语义仍靠模型记住。跨 source、realm、Node/RuyiDOM 和多个补丁时特别容易漂移。

**反事实：** 更强模型也可能沿用旧 true 而被放行；正确模型发现确凿的新 receiver 行为时，又可能被旧 global stop-search/boundary-unchanged 拦住，必须手工改 hostProbe/authorizedSurface 才能表达新证据。

**建议：** 引入单个 active repair scope（不是再加十个 bool）：scopeId、property、receiver provenance、browser/local pair、source epoch、runner fingerprint、parent scope；换 scope 自动使旧 dualCondition 无效。真实同 surface 继续修允许宿主行为推进判据；探索下一面仍保留 stop-search，不要整块拆掉防护。

## 4. [fact + inference + unknown] 正确的反枚举目标，被粗粒度边界与多份“当前状态”放大成绕门和上下文漂移

**代码/文档位置：** `web_case.py:2039–2069,2564–2605`；`skill/web-reverse/SKILL.md:12–14,50–63`；`docs/agent-architecture.md:165,186,219–225`。

- boundary-unchanged 就停在 refuse；same-surface 开口存在，因而“所有不改变网络的修复都绝对不能做”不成立。但机器未结构化区分修复期的本地错误推进与探索期外部边界，执行者容易把它理解成每刀都必须找到新网络差异。
- 规则只要求 method/url/status/body 长度类变化，未把 background requests 与 target causal boundary 机器区分。本案链下载/favicons 真变化可以被记为 boundary-moved，但不证明 challenge 推进；再加第 1 项错口径，形成“为了下一步找 delta”的激励风险（inference，不断言 Grok 有主观绕门动机）。
- 文档只应读 docs.read、主线程只接短摘要是合理降噪；然而项目同时保留 analysis-progress、next-plan、docs/web/environment-patch、agent-notes、workspace/facts，多处带“当前”且语义冲突。当前 analysis-progress 的 Current State 仍有 9 月 29 日 stop-search，environment-patch 的旧 Blocker/生成 gate/not-ready 与最新 hygiene=ok 并存。已有事实证明重复真相未清理，但“这是 Grok 本次错误的直接原因”仍只是 inference。
- 未取得 Grok 最新完整执行轨迹，无法量化其究竟漏读了哪份文件，也无法分离模型、prompt 长度、工具调用和调度压力的贡献（unknown）。

**反事实：** 正确模型仍要自行仲裁冲突摘要；换强模型不能消除来源冲突。全面取消停点会恢复无穷枚举，代价更大。

**建议：** 维持主线 browser fact → local single-surface → same-runner → target parity → independent acceptance。把机器当前状态收成一份自动生成视图，其余文件明确 history/obsolete；报告统一附 epoch/runner/scope。gate 拦的是无证枚举，不应把合法本地修复和业务网络推进混成一个标量。

## 归责与优先级

1. **直接执行错误**：Grok 混用 request/response 长度、跨 runner 验证、历史材料冒充 fresh 验证。这些不是逆向理论造成的，模型/执行者应承担。
2. **编排可修缺陷**：事实只验 hash 不验结论、next 先记“跑完”、证据无 scope 绑定，确实能放大并固化这些错误；应优先修成机器保证，而非继续加口头禁令。
3. **主线不宜推翻**：真实浏览器事实、同点 receiver、行为而非常量补丁、独立业务验收、CAS、stop-search 和不透明字节不评分，都仍有价值。
4. **模型能力结论有限**：可认定 Grok 本案执行可靠性不足；不能凭单模型一条复杂轨迹证明换某模型必好，也不能给各因素编百分比。应在相同冻结证据包上盲测“指出真实 delta、区分 runner、拒绝 stale/fake receipt”再比较。

证据基线：`agent-notes/20261020-grok-latest-judgment-audit.md` 与其脱敏 trace 对照。本轮仅新增本报告，未修改运行态或事实。
