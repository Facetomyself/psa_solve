# 2026-10-20 与 2026-10-21 实质进展对比

## 0. 比较口径

这份报告回答“和昨天相比，到底多解决了什么”，不是重新做一次全量审计，也不执行目标、网络、测试、补丁、next 或事实写入。

- **昨天终点**：不能只取 22:20 的审计。已补核 10 月 20 日 **23:48–23:49** 的正式 Performance.getEntries baseline/patched、browser pair 与分类回执。
- **今天终点**：截至已读取的 **13:04** 新笔记和对应正式 baseline `c0a92703cc7144cd8b1804fe406c69fc`；不是 12:52 的 `13a5d2e...`。最新慢脚本列又回到 `1:1337365`。
- **完成含义不变**：浏览器能访问、局部首错消失、工具 exit 0、静态资源被提供、脚本超时位置变化，都不是“Node 独立求解 + 真实提交 + 同会话业务验收完成”。
- **不能串错链**：Node iframe mirror、RuyiDOM 原生 Gecko、真实 Firefox browser oracle 是三条执行链；下文逐条列，不把它们拼成一条看似连续的进度条。

## 1. 一句话结论

**两天不是完全没进展：昨天已经实证消除了 Node 的 BODY.attachShadow 首错，并在深夜建立了 Performance 存在性对照；今天最大的新增，是把本地运行/证据基础设施补得更可追踪，观察到了更多 Performance/RTC/iframe 生命周期，同时修掉了若干审计指出的污染。**

**但从目标交付看，没有新的可验证业务里程碑：今天尚未证明 fresh 的求解请求、submit、证书 POST、parity 或同会话 readback。最新仍在本地慢脚本，且两处列号往返，不能说“已经从 getEntries 推进到 submit 前最后一关”。**

## 2. 总对比表

| 维度 | 10 月 20 日结束前已有什么 | 10 月 21 日截至 13:04 新增什么 | 算不算实质进展 | 能证明到哪里／不能证明什么 |
|---|---|---|---|---|
| 站点可用性与 TLS 归因 | curl 停在挑战；真实 Firefox 同出口约 6 秒后进入证书页，页面 fetch 为 200 | 本轮没有新的、可替代该对照的 fresh 业务验收 | **昨天已完成的纠偏，不是今天新突破** | 排除“现有证据已证明 TLS 无法模拟/站点永远拒绝”的过强断言；不证明 Node 求解 |
| Node receiver 类型 | 同源调用的 receiver 锁为 document.body，SCRIPT 是本地错型 | 今日主要工作在 Gecko runner，不是同一个 Node mirror 的下一次闭环 | **昨天的真实定位仍有效，今天没有新 Node 完成证据** | 知道该修 BODY 行为，不应给 SCRIPT 硬加 API |
| attachShadow 模式与行为 | 静态恢复 mode=closed；固定输入 baseline/patched 后原 attachShadow TypeError 消失 | 当前 Gecko 自身已有原生 DOM；今天没有把 Node 这组修复再做同 source 完整消费验证 | **昨天已越过一个局部本地边界** | 有真实返回 root；但随后空树 query 返回 null，未证明完整 ShadowRoot/子树 parity |
| 性能对象存在性 | 深夜正式 baseline 缺 Performance/getEntries，patched 安装后对象+方法存在，工具运行完成；已 browser pair，分类 boundary-unchanged | 后续又加入资源条目读取、Observer 通知、now/timeOrigin 等 | **有局部行为设施增量** | 可以比昨天更具体描述本地环境；不能把 callable/present 当成实际调用返回值等价 |
| RuyiDOM 文档身份 | about:blank/SOP 问题被定位；晚间内部 principal/URI 变为页面类，load deny 消失，随后暴露 null/undefined receiver | 继续保留身份修复，开始更细分 sandbox/window/Function/Date 关系 | **本地初始化和诊断前移** | 不代表清关响应被正确消费，也不能拿 Gecko 身份修复替代 Node 成功 |
| RTC 生命周期 | 曾因 offer promise/回调缺观测而不明确 | 新探针记录 createOffer 兑现、setLocalDescription、have-local-offer、gathering complete | **诊断知识有增加** | 说明本地某些 API/异步阶段真的走过；没有证明完整浏览器指纹/网络 parity |
| iframe 生命周期 | 缺乏创建/连接过程证据，末态经常 iframe=0 | 记录 createElement iframe、append、connected parent=yes，末态仍可 0 | **消除了一个“可能从没创建”的未知** | 创建/连接不等于导航成功或 Turnstile 运行完成，更不等于 submit |
| 固定资源覆盖 | 主要喂 orchestrate，其他请求可能被挡 | 加入保存的 api.js、cert 资源、iframe HTML、page/cloud FO 明文映射 | **离线夹具覆盖增加** | 加一条 handler 规则不等于目标真的发了 FO；历史返回体不证明 fresh session 一致性 |
| 慢脚本定位 | getEntries/null 等早期本地异常，还有调度/runner 混用风险 | 记录 slow-script 位置、side、脚本限额/退出原因，细分源行内/外、Date/performance compartment 假设 | **卡点分类更细，但不是已证根因** | 55371 与 1337365 来回，不是连续过关；还没有同一 eval 输入进入/返回的闭合证据 |
| scope 与执行证据 | 新 host 工具链开始落地，但关键 helper/底层依赖曾漏锁 | 当前 scope 已含 **13 项 dependencies**，helper 改动重签 scope，priorScope 保留；真实进程回执仍拦失败 | **最扎实的今日基础设施进展之一** | 更能知道“究竟跑了哪份环境”；hash 不证明语义正确，也不是防全权限伪造签名 |
| 等价性与实验卫生 | 早晨一度存在直接按模式跳过 eval 的捷径 | 捷径已撤，真 eval 恢复；但引入同步 XHR/Observer 干预 | **一部分纠错是正进展，一部分新行为是负担** | 撤 eval 污染值得保留；同步时序不能当 native 等价修复，不能用其结果证明真实求解推进 |
| 交付验收 | Node/parity/fresh submit/readback 未闭合 | 最新 serverAccepted/localReproduced/requestBoundaryAligned 仍 false | **目标验收无新增通过项** | 不能报成功，也不能估计百分比或还差几步 |

## 3. 昨天已经实证解决的，不应被今天的失败抹掉

### 3.1 Node 的 attachShadow 首错确实消除了

证据：`agent-notes/20261020-shadowroot-repair.md`，`diagnostics/shadowroot-repair-20261020/{baseline.execution.json,patched.execution.json,boundary-comparison.json,receipt.json}`。

这组是最有价值的局部对照，因为 baseline/patched 用同一 canonical source/callsite，差异精确落在 BODY.attachShadow/返回 root 的行为：

- baseline：方法不可调用；
- patched：读取真实 mode=closed，生成 root；
- 再往后：root.querySelector 真实返回 null，随后 zF 对 null.appendChild 报错。

这解决了“receiver 是什么／是不是该给 SCRIPT 补 API／mode 有没有证据／方法是否真的存在”这些具体未知。它没有解决子树为什么没挂上，更没有产生真实 send。两边只有一次未 send 的 POST open 意图。

因此，今天 Gecko 里又卡住，**不意味着昨天这个 Node 局部修复无效**；反之，也不能说今天 Gecko 里的慢脚本就是昨天 root.querySelector 的“后续下一关”。两个 runner、输入和表面不同。

### 3.2 昨晚 23:49 已有正式 Performance 对照，不能漏算

定向核对的真实执行：

- baseline `0e16a86e105344c4b9a5083555481a5a`：exit 0、completed，Performance/getEntries 缺失观察；
- patched `099a1099048f47b994cd67ff3b7e2fd1`：exit 0、completed，base=object/getEntries=function；
- 同 scope `777d3a2f...`、同 source `06e1a7a4...`；
- `contracts/host-evidence/pair.json` 留有 browser run/trace/packet/baseline 绑定；
- `classification.json` 的结果是 **boundary-unchanged，targetBefore=0、targetAfter=0**。

这里有一个必须保留的证据限制：collector 的 patched `present` 分支根据 base object + getEntries function 写入固定 callsite，不是截到该方法在原调用点成功返回。side 的 access、receiverId 仍 null，后面错误在 2:30625。所以最稳妥的说法是“正式存在性/可调用状态对照跑通，局部错误形态改变”，不是“Performance API 返回语义已经 parity 通过”。

这项发生在昨天，不应把它全部算到今天；也不能从它的工具 completed 推导业务 localReproduced=true。

## 4. 今天新增的实质价值主要在哪

### 4.1 比昨天更清楚“环境实际做了什么”

今天把一些此前只有末态的对象，补出了生命周期：Observer 曾 observe；资源读取能拿到条目；RTC offer 曾兑现，local description 曾写入；iframe 曾创建并连接到父节点。

这些会改变下一步排查方向。例如，“结束时 iframe=0”不能再推成“从来没建过 iframe”；“没有 submit”不能再简单推成“所有异步 API 都没执行”。这种排除误判的价值是真实的，尽管它不是业务请求成功。

证据：`agent-notes/20261021-form-gate-probe.md`，`20261021-observer-notify.md`，对应的 `iframe-parent.json` 与历史 side。

### 4.2 环境指纹和运行回执可追溯性显著增强

当前 13 项依赖包括：Gecko exe/xul/plugin/mozglue/lib、helper、Node、CLI、Turnstile API、cert 静态体、iframe HTML、page FO、cloud FO。

相比昨天“Python collector 的 hash 没变但内部动态加载 helper 改了”，今天能在 scope 里发现 helper/runtime/资源漂移，并保留 priorScope。对长时间、多轮排查非常有用，因为可以更可靠地区分到底是“同一问题重跑”还是“运行环境换了一版”。

这属于**排查可靠性建设**，不能当作“挑战算法已恢复了 13 项”。依赖项数量也不是进度百分比。

### 4.3 失败被保留为失败，没有再用 exit/summary 乱报成功

最新 submit raw 只有 diagnostic + summary，exitCode=1，正式执行拒绝通过；慢脚本列没有被伪装成 submit host-observation，业务完成三轴仍 false。

这个改进不显眼，但比“日志看起来跑完就升成功”靠谱得多。它不能解决卡点，却能减少后续在错误前提上继续堆补丁。

## 5. 为什么不能说“从昨天的 getEntries 推进到今天的 submit 前最后一关”

至少有三组不能直接相减的输入：

1. **Node BODY/ShadowRoot**：历史 iframe inline source `05102bb5...`，分析的是 iframe DOM bootstrap；
2. **昨晚 Performance collector**：source `06e1a7a4...`，浏览器 canonical orchestrate 的 2:30602 存在性周期；
3. **今日 submit collector**：source `262a1bf5...`，10 月 5 日保存的 orchestrate，scope 目标是 1:75507 的 HTMLFormElement.submit。

今天选择了 submit 作为观察目标，不等于当前执行已经到达 submit。最新 actual diagnostic 是 slow-script `1:1337365`，匹配 false；目标点 1:75507 没有 receiver 观察。

而且 12:52 页内 Date 修改时落点曾回到 55371，13:04 页内 performance.now 修改后又回到 1337365。**这说明不同干预会改变终止位置，不说明连续地跨过了一关又一关。**对“那次 eval 已返回／跨区 Date 是根因”的断言，现有证据最多支持相关性假设，尚未完成相同输入、source identity、enter/return、compartment 的因果链。

## 6. 今天哪些行为还会拖后腿

### 6.1 不能把改变事件循环当成 native 环境补齐

当前 helper 默认把 XHR send 的完成回调提前到 send 返回前，且不检查 async；PerformanceObserver 的回调也提前到 observe 返回前同步执行。这样确实可能让忙循环看见之前看不到的状态，但那是改语义，不是已证的浏览器行为。

因此，这两处应该作为**隔离的因果干预**或回到真实异步对照，而不是稳定 baseline 的“已修复项”。否则新增的 Date/performance 时间实验都混在非原生时序上，定位结论容易越跑越偏。

证据：`document-principal.js` 中 `installInlineXHR`、`runObserverNotify`；`agent-notes/20261021-inline-xhr.md`、`20261021-observer-notify.md`；详见 `20261021-midday-technical-audit.md`。

### 6.2 历史 FO 明文映射不等于真实 FO 前移

今天喂入的 page/cloud FO 响应是固定历史材料。资源 shape 命中只说明 handler 有能力返回那份文件；目前正式 raw 不记录请求消费，所以没有证明目标真的走到了那些 FO。

即使后面命中了，它仍只是离线回放，不是 fresh 服务器响应。按粗 URL 形状反复回同一份历史正文，还没有证明适用于同形状后续阶段。静态资源哈希正确只证明“文件没变”，不证明“这次请求就该收到它”。

### 6.3 不能把第 55371 列的特许动作当双条件根因证据

新工作流允许对那一慢脚本位置继续一处宿主修补，这是一条明确的调度授权，不是实际浏览器 receiver/property 观察。放行本身不说明缺哪一个 API，更不说明补丁语义正确。

## 7. 真实网络能力：历史最好结果、昨天新结果、今天当前结果要分开

| 时间/执行面 | 已有网络证据 | 不应推导的结论 |
|---|---|---|
| 历史 RuyiDOM live（9 月 30 日，昨天已知） | 曾真实走过 5 条 FO，widget complete/清关 cookie 名出现，随后排障 DOM，未见证书 document POST/readback | 不能说项目“从没走到过 FO”；也不能说因为有 clearance 名就已完成业务 |
| 昨天真实 Firefox oracle | 同出口挑战后能进入证书页，页面 fetch 200/真实业务体 | 不能当成 Node/RuyiDOM 独立求解完成 |
| 昨天 Node 单 surface 对照 | 固定输入断网，仅 open 意图，未 send | 不能按 open 意图记 FO moved |
| 昨晚 Performance 双运行 | 正式局部存在性对照，classification external target 0→0 | 工具 completed 不等于请求/业务 completed |
| 今天当前 submit baseline | 离线固定材料 + 本地 handler，失败；raw 无完整 wire 事件 | 不能证明 fresh 求解进展，也不能由无请求记录反证历史 live 能力退化 |

所以不能简单说今天“比昨天网络更差”：今天这份离线模型本来就不是昨天真实 live runner 的同配置对照。但也没有证据说今天已超过历史 5 FO 的最好运行边界。

## 8. 哪些成果可以保留，哪些要隔离

### 可以保留

- BODY receiver/callsite/closed options 的同源证据和局部首错修复回执；
- 原生 DOM 身份/principal/SOP 的确证及最小修复；
- 已观察到的资源/RTC/iframe 生命周期证据，保持它们的诊断范围；
- dependencies hash、真实进程终态、raw 与 scope 绑定、priorScope；
- AI claim、工具运行成功、请求边界、业务成功分开记账；
- 早晨已撤掉 pad eval 捷径，不应重新加回。

### 需要隔离为诊断干预，不能直接作为生产 native 修复

- 同步 XHR/Observer、未知 status 合成 200；
- 历史时间锚点和静态 FO 响应回灌；
- 只由慢脚本列变化推导出来的 Date/performance 根因结论；
- 仅验证 helper 自定义行为的单元测试，不能包装成 browser parity。

## 9. 下一段最短、且不继续兜圈的验证路径

本报告不执行下列步骤，也不在这里自造新的次数/时限合同。

1. **先明确交付执行面。**如果最终仍是纯 Node，就把 Gecko 当诊断层，别把它的局部结果当 Node 跑通；Node 与 Gecko 分别维护当前首错和输入版本。
2. **冻结一个语义可信的基线。**保留必要身份修复与完整指纹，把同步 API 干预隔离出去；为静态夹具明确 replay 身份，不把它称为 live。
3. **补当前缺的观测，而不是继续猜宿主。**对已出现的同一输入，拿 eval enter/return/input hash、实际 Date/performance Realm/receiver 与资源 handler 消费事件；先区分是时间、资源、回调，还是目标循环条件。
4. **再做同 source、同 runner 的一处行为对照。**必须看到明确的局部行为差异或实际请求边界，而不是只看 warning 列号变化。
5. **局部模型能自然出请求后再跑 fresh live。**输入、响应、session 和资源来自本次运行；看到自然 FO/submit/证书 POST 后，才做最终 runtime、parity 与独立同会话 readback。不能回灌历史 FO 替代这一步。

## 10. 最终评价

今天最实在的收获是：**更可靠地保存并解释了失败，扩大了可观察的本地生命周期，修了环境指纹和 eval 污染等排查基础问题。**

但从“做成一个能独立完成挑战的客户端”这个原始目标看，**尚无新的正式通过里程碑**。当前主要工作仍是搭建与纠正诊断模型，不是已经恢复了完整提交链。评价 Grok 应同时记住这两点：不能把它一晚上的工作全判为零，也不能用改了多少 helper、跑了多少轮、warning 位置变化来冒充求解进度。

## 主要证据索引

- `agent-notes/20261020-shadowroot-repair.md`、`20261020-shadow-options-static.md`
- `agent-notes/20261020-transport-cause.md`、`20261020-grok-latest-judgment-audit.md`
- `evidence/host-executions/0e16a86e105344c4b9a5083555481a5a/`、`099a1099048f47b994cd67ff3b7e2fd1/`（昨天深夜）
- `contracts/host-evidence/pair.json`、`classification.json`（scope 777d... 的历史 Performance 周期，不是当前 submit scope）
- `agent-notes/20261021-overnight-technical-audit.md`、`20261021-midday-technical-audit.md`
- `agent-notes/20261021-window-date-inpage.md`、`20261021-performance-now-compartment.md`
- `evidence/host-executions/c0a92703cc7144cd8b1804fe406c69fc/`（13:04 最新已读运行）
- `contracts/host-evidence/{scope.json,state.json}`、`contracts/auto-decision-facts.json`
