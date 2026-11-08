# 主线方法、编排与模型能力的因果审计 / 2026-10-20

## 范围与结论

本轮是暂停状态下的只读归因分析。未执行 next、record_host_probe 记账、target、runner、测试、网络、fresh 材料采集或事实变更；只新增本报告。主线程已知本拍为 record_host_probe / blocked；不消费此 action，不恢复 goal。

审阅指定六份报告；其中任务简称 grok-latest-judgment-audit.md 的实际文件为 `agent-notes/20261020-grok-latest-judgment-audit.md`。最新证据时界据该报告为22:20的回执，未取得对应阶段 Grok 对话全文；不把旧 last-copy（本机最后写入16:41）当作最新言论。对最新执行记录的判断引用该审计，不冒称本轮逐份重审 raw trace。所有项目路径相对 `D:\reverse_ENV\workspace\psa_solve`。

**总判断（inference）**：当前已经足以确认“实验谱系/测量口径/流程接力有具体问题”，而不足以确认“Grok 底层模型能力不行”或“补环境主线根本走错”。这是不同层级的因果判断，不能按错误数量给三者拍百分比分摊。

- **fact**：多个已证错误会直接破坏结论可信度：request/response 字段换口径、旧材料被叫 live、跨 runner 传递因果、constructor 标签被当对象来源。
- **fact**：有真实技术进展：BODY 来源、closed 参数、同 root 子树消费合同已闭合；实际修复消除首个 TypeError；principal 也有真实变化。不能把“仍未过盾”倒推为所有工作无效。
- **unknown**：未完成的挑战到底还剩哪些机制、服务端选择哪些风险信号、哪种模型在同任务条件下更可靠；当前材料不能定性模型家族的能力上限。

## 1. 多 runner / 多版本 / 历史材料怎样破坏因果

### 1.1 不同停止阶段，不能合成一条原因链

**fact**：裸 curl 初始 GET只收到挑战文档；历史 Node mirror 在FO之前出错；RuyiDOM 一度完成 widget/五段FO后进入排障DOM。这是三个不同阶段和执行面。`20261020-blocker-review.md:12-16,20-27,50-58`。

**inference**：拿裸curl403解释“RuyiDOM末段未submit”，或拿 Node 的 SCRIPT 接收者解释 Gecko 五段FO后的排障，都是把一个实验的处理效应错误迁移到另一条链。应该先问同输入/同runner/同源调用点在哪，再谈共同根因。

### 1.2 同一原始 source，不等于同会话、同 executable、同 realm

**fact**：canonical iframe 与 local 原 source 可对齐；但旧 mirror 页面/API来自9月28日、iframe来自9月29日，且 frame共享global/document。固定旧样本能用来复现局部首错，不能证明 fresh/live parity。`20261020-receiver-provenance-run.md:78-82`；`20261020-shadowroot-repair.md:24-30`。

**fact（据最新审计）**：10月20日后续 RuyiDOM在线诊断仍注入9月30日challenge/orchestrate/cookie；allowNetwork=true不会刷新旧session。它是旧输入的loader/principal回归样本，不是新鲜求解基线。`20261020-grok-latest-judgment-audit.md:18-24`。

**unknown**：旧材料是否已经造成服务器过期拒绝；最新审计明确FO=0、尚未发到那一步，不能把过期从风险猜测升级为本次根因。

### 1.3 引擎名字和外观版本不是同一实验因子

**fact**：历史RuyiDOM是135 base加UA155外观，browser事实来自另一锁定Firefox；同h3只证明协议类，不等于同TLS/QUIC/realm实现。`20261020-blocker-review.md:25-27`。

**inference**：跨这些版本比较仍有价值，但结论必须是“有差异的候选范围”，而不是控制住其它因素后得到的唯一原因。切换runner或版本后沿用同一个firstDivergence标签，会掩盖实验已换题。

### 1.4 报告和合同本身也在变化

**fact**：当前 `20261020-shadowroot-repair.md:15-17,76` 明确旧claim/次数/15秒规则后来被移除；源skill当前也加入same-surface续跑规则。历史执行当时的receipt事实仍有效，但历史“下一步不能跑”的流程判定不必继续成立。

**inference**：读到旧报告就重放旧停点，或把当前代码拿去解释历史运行而不带revision，会产生“永远说同一个阻塞”的人为循环。这既可能是编排状态设计不足，也可能是代理没有重新绑定当前合同，不能先怪目标网站。

## 2. 补环境：方法错误，还是执行方式错误

### 已有证据支持的方法

**fact**：browser在同source/call-site对BODY调用attachShadow；local动态确认receiver就是body且方法不可调用。typing-only改对标签仍报错；真正补入该方法/返回root后，原TypeError消失。`20261020-receiver-provenance-run.md:54-66,78-79`；`20261020-shadowroot-repair.md:43-63`。

**判断（inference）**：这支持“用浏览器事实定位host语义缺口，再做单机制对照”这条方法。不能据此说完整Node环境已可行，更不能反过来说补环境是错误路线。

### 明确不可靠的执行方式

1. **fact**：只看constructor.name曾把错误body伪装成SCRIPT；必须追实际创建/身份/realm，而不是按报错API名称给SCRIPT补方法。`20261020-receiver-provenance-run.md:27-50,62-64`。
2. **fact**：本地noform只是opaque XHR文本的正则分类，不是服务端拒绝码；3488/3792也不是可优化分数。`20261020-blocker-review.md:34-40`。
3. **fact**：最新orchestrate“长度类移动”把request bodyBytes=0和responseBytes=241280混成前后变化；served=true还是本地handler命中，不是外部请求。`20261020-grok-latest-judgment-audit.md:9-16`。
4. **fact**：修ShadowRoot后，root没有append却遇到query miss/null；不能为了跨过异常制造假节点。`20261020-shadowroot-repair.md:48-63`。
5. **inference**：只让TypeError不断向后移动，缺少同source正确分支/真实消费合同/目标请求证据，会变成补stub游戏；错误更晚出现不必然意味着更靠近业务成功。

### 局部成功与业务成功应使用不同语言

- 首错方法从不可调用变为真实返回并被消费，是**局部机制已证进展**。
- principal从about:blank变成证书URI、SOP deny消失，是**安全上下文本地进展**；不能迁移为NodeShadowRoot成功。最新审计`:26-38`。
- 新favicon/chain请求是**真实网络变化**，但未证明是challenge必要边；不能直接当host修复有效。最新审计`:41-43`。
- harness OK、unit tests、POST200、独立fresh同lease业务readback分别是不同门槛，不能互相替代。

## 3. Opaque VM 与 host 边界怎样定位才合理

**fact**：此前有些重要信息不需要恢复整个VM：仅凭browser/local身份和原source调用点可定位body；仅凭字面量表与同源事实锚的同余约束可恢复mode=closed；没有执行VM/decoder。`20261020-shadow-options-static.md:9-42`。

**合理做法（inference）**：把VM先当黑盒，比较它已经触达的外部边界：资源/realm→receiver创建和读写→异步回调→请求意图→wire response→DOM/提交→业务readback。一次只回答首个可对齐的因果问题，不按opaque字节变化“打分”。

**边界条件**：

- 若明确是错误receiver/realm/返回形状，优先修调用合同，而非反编译整个VM。
- 若缺口只能定位到不透明VM内部且看不到可判别host输入/输出，必须承认当前观测不能归因；不能无限补宿主，也不能因为VM难就宣布无法模拟。
- 某轮VM输出不同，先排除source/session/clock/资源漂移；不同版本输出差异本身不能证明handler语义缺失。
- 是否值得深入VM取决于明确恢复目标和可验收fixture，不由“函数很混淆”自动触发。

**unknown**：现在尚无证据证明成功分支依赖不可仿真的浏览器内部秘密；同样没有证据证明只靠继续补DOM最终必能完成。应保留两种不确定性。

## 4. 能不能证明 Grok 模型能力不足

**不能从现有材料作该因果结论（unknown）**。缺少同输入、同工具权限、同一技能/状态快照、同任务预算的对照，也没有最新完整Grok对话。错误可指认到具体输出，但“某代理这次推理错”与“底层模型能力不够”不是同一命题。

已有支持的更窄结论：

- **fact**：bodyBytes/responseBytes误配是一次具体测量/实现/复核失败；能够指出错误字段和反证，不必争模型排名。
- **inference**：跨runner因果迁移、由null receiver猜API缺失若发生，是具体推理规范失败；目前最新审计`:31`明确未见Grok落盘作出后一个猜测，不应替它制造一条罪状。
- **unknown**：它是否在读到相同schema定义和原始记录后仍会坚持错误，还是此前被过时摘要/混乱规范误导。
- **inference**：若环境让多个模型都反复犯同一错误，优先检查输入/合同/measurement；若只有某模型在规范化条件下稳定失败，才有能力差异的条件性证据。都不等于广义智力结论。

## 5. 本助手也必须承担的部分

**fact**：本助手早期多次将报告收口在“需要另一次正式授权/不能继续”，先后完成了receiver审计、独立41项模型单测、mode静态恢复，再接上目标对照；报告可见 `20261020-blocker-review.md:91-102`、`20261020-shadowroot-contract.md:54-76`、`20261020-shadow-options-static.md:52-64`。这不是只有Grok才有的执行摩擦。

**自审（inference）**：

1. 遵守当时active gate是正确的，但把门禁冲突反复交还用户、没有更早把“已证同一属性”与“相邻字段搜索”拆开接到正式工作流，造成了可避免的等待。这个责任属于编排契约与本助手的执行判断共同部分，不能包装成谨慎就算完成任务。
2. 模型单测41/38项有开发价值，但其因果相关性低于一次same-input目标对照。只报告通过数容易制造忙碌感。本助手后续报告已明确单测不构成goal进展的充分证据；应一开始就把这种证据等级写清。
3. 把mode未知当作继续推进的重大缺口，曾高估其必要性：正确API读取传入options.mode，本不需要硬编码历史closed。后来静态报告`:44-48`才纠偏。
4. 诊断中使用baseline/patched设计和单次timeout便于控制实验，但不应把本助手/父代理自拟次数或秒数提升为用户的长期任务预算。当前源skill明确禁止自造该类限制，旧合同也已修改。这是流程和解释问题，不是目标反逆向机制。
5. 先前的局部修复是在历史混合输入下进行，明确只能复现首错，不能据此评价fresh线上求解优劣。若本助手也继续拿这些结果充当整体主线成功，那与被审计问题同类。

因此，本报告不作“换成本助手就能搞定”式自我优越归因。

## 6. 低成本交叉对照设计（仅设计，本轮不执行）

### 冻结三个脱敏fixture，先测判断再测执行

| fixture | 相同输入 | 参考结论与考点 |
|---|---|---|
| F1 测量方向 | 两行raw request/response记录+字段生产定义 | 不能把GET body0与response241280算前后delta；区分local handler与wire |
| F2 receiver/source | 小段factory、constructor日志、source/call-site/identity证据 | SCRIPT标签不等于实际script；辨别已证body、未知因果与正确最小对照 |
| F3 调度接力 | 当前版本skill片段+冻结的same-surface/paused/hostProbe状态 | 区分同面续跑、相邻枚举、暂停只分析；不自造审批/预算，不修改完成轴 |

不得把本报告答案直接放进fixture；必须提供足以判断的原始证据与字段定义，剥离model身份、之前结论、凭据和无关大上下文。reference由独立审阅者预先锁定，不能事后按某模型答案改判据。

### 最省成本的对照顺序

1. 两个待比较模型先在**同一份简化且无歧义合同**下，各独立做三个fixture，输出统一结构：fact/inference/unknown、证据指针、最小可证伪动作、停止条件。先看这6份只读判断，不访问真实站点。
2. 只对分歧或失败项，给两个模型补同一份原始项目合同/状态快照，比较判断是否被复杂编排改变；必要时再调换输出顺序复测。无需一开始铺开昂贵全量bench。
3. 若要比较工具执行能力，另用合成的本地无网络测试仓库，同hash输入、同工具和明确验收；不得拿一个模型继承前人的修复结果与另一个模型的冷启动比较。

### 如何区分责任

- 同一模型简化合同正确、原合同错误，且另一模型同样受影响：支持**编排/提示复杂性**解释。
- 不同模型在相同清晰输入下对同项重复分歧，盲审reference一致：支持**该具体任务上的模型能力/稳健性差异**，不外推所有逆向能力。
- 两模型都因缺必要材料无法判断：支持**任务定义/证据面不足**，不计作能力失败。
- 判断正确但工具回执与代码行为不符：先定位**实现/工具adapter/验证链**，而不是用聊天解释掩盖。
- 本地fixture都通过但fresh线上都失败：说明**主线覆盖/状态/目标难度仍未解决**，不是模型测试已证明求解成功。

记录每项真实错误类型、证据质量、是否通过验收、总工具动作与返工量；不凭文字流畅/篇幅/测试数打分，不产出“模型占几成”的伪精确归因。

## 7. 优先三条改进

1. **先统一实验谱系，再继续求解**：每个可对照实验绑定runner+engine/真实版本+source hash+session/freshness+realm+patch摘要。固定旧样本回归与fresh live验收分名分账；一个当前实验只沿一条主执行链，不禁止其它链作oracle，但跨链必须有明确映射证据。
2. **把测量与进展等级做成机器合同**：request/response、handler/wire、意图/send/readback分字段；自动拒绝跨方向delta。阶段分别报执行健康、身份/局部语义、正确目标路径、目标wire、业务readback，绝不让favicon移动或单测数自动晋升为挑战进展。
3. **精简同面接力并做小规模盲对照**：让已证同一属性的修复→复跑→记账有清晰唯一入口，停相邻枚举不等于停全部诊断；不反复问常规批准、不把claim当用户任务预算。用上述6份只读fixture先判断模型/提示/合同哪里真的出错，暂停期间只做设计，不擅自恢复目标。

## 最终归因

- **已证（fact）**：具体记录口径错误、材料新鲜度问题、跨执行链证据边界、局部宿主模型缺陷，以及本助手也有过度门禁和弱相关单测的流程摩擦。
- **较强判断（inference）**：先修实验/测量/调度接力，比现在直接更换模型或推翻补环境路线更有证据支持；这是修复优先级，不是责任百分比。
- **仍未知（unknown）**：Grok模型家族能力是否不足、主线最终是否可完整Node实现、最新失败的充分根因。没有同条件对照就不定性，不继续凭猜测为任何代理开脱或定罪。
