# 下午运行态、正式时间线与重复核验 / 2026-10-21

## 核验范围

19:03–19:06 +08:00只读快照，对照中午c0a927...（13:03:23终态；当时报告约13:04）。主线程已给repair_submit_host_behavior / blocked；本切片不next、不record、不执行目标/网络/重跑/终止/恢复，不改facts/goal/dispatcher或原运行产物。

脱敏机器证据：`diagnostics/afternoon-audit-20261021/runtime/` 的 `execution-timeline.redacted.json`、`processes.redacted.json`、`state-scope.redacted.json`、`session-activity.redacted.json`、`reverification-notes.redacted.json`、`final-state-check.redacted.json`。没有保存完整进程命令、会话消息正文或凭据值。

## 1. 当前不是在等待活的PSA目标进程

- Grok主进程有两份：PID3592（昨18:53启动）、PID39660（今天14:27启动）；每个各挂3个常驻ruyidom/ruyitrace/v8trace MCP。
- 19:04进程快照未见psa runner/xpcshell/firefox目标执行进程。最新正式collector PID不在存活运行时PID集合中。
- 项目state=failed、pid=null，current仍指向baseline `356e17e4159e4aee8da0a6cc37d3d8c8`。最终只读复核仍为同一run，观察期间没有新正式执行替换它。
- 两个Grok main会话元数据/terminal仍活跃到19:05；最近子agent的元数据止于18:00前后。不能把main会话活跃、MCP常驻当成目标仍在运行。
- 会话registry已在14:27切到第二main。两客户端可能共享此项目，但本切片没有证明它们同时运行目标或发生写入竞态；需要协调的是case所有权，不能凭双进程就指控某次错误来源。

## 2. 下午新增正式运行

从中午anchor `c0a92703cc7144cd8b1804fe406c69fc` 终止13:03:23.669之后，到19:04快照共 **23次execution、23个scope**。全部variant=baseline、status=failed、exitCode=1、timedOut=false；没有patched正式执行、completed成功终态。

正式receipt累计墙钟 **508.079秒**，只覆盖这23个collector父进程，不含临时探针、模型等待、工具读写和实现修改；不能把它说成下午总目标耗时或CPU使用。

| 终止时间 | run前缀 | raw诊断位置 |
|---|---|---|
| 13:13:24 | 1fdcbce6 | 1:1337365 |
| 13:19:35 | b048030d | 1:1337365 |
| 13:23:30 | 9d5ad8f9 | 1:55371 |
| 13:27:47 | ede2f981 | 1:1337365 |
| 13:37:30 | e3522169 | 1:1337365 |
| 13:48:45 | 869824e6 | 1:1337365 |
| 14:07:48 | e9251003 | 1:1337365 |
| 14:22:36 | c9d67de1 | 1:1337365 |
| 14:29:51 | 31dafe09 | 1:1337365 |
| 14:39:20 | 71bd1c19 | 1:1337365 |
| 14:52:17 | 3d4afa40 | 1:1337365 |
| 14:57:41 | 12894c3b | 1:1337365 |
| 15:02:46 | 2cce87b6 | 1:1337365 |
| 15:17:33 | c33e6a1b | 1:1337365 |
| 15:28:20 | 8904782b | 1:1337365 |
| 15:49:32 | b882fe52 | 1:1337365 |
| 16:09:10 | b841fe67 | 1:1337365 |
| 16:29:46 | d3ec59e2 | 仅 summary |
| 17:12:55 | 7e9d471a | 1:1337365 |
| 17:22:56 | d6d9e711 | 1:1337365 |
| 17:53:39 | dd990f17 | 1:1337365 |
| 18:10:09 | f1e44ef3 | 1439:21 |
| 18:34:13 | 356e17e4 | 2:3028 |

最新baseline开始18:33:50前后、终止 **18:34:13.019**，仍failed。最新19:00笔记和19:03主线程盖章均晚于它；不是19:00又跑出了一份目标结果。

## 3. 相对中午有了哪些新证据、哪些只是重复

23份raw独立重哈希匹配execution引用。合计22条host-diagnostic、23条summary；host-observation/wire/necko/resp均为0。raw只有 **5种字节hash**：

- 1:1337365、matched=false：**19次**，同一hash，且与上午大批同位置raw完全相同。
- 1:55371、matched=false：1次，仍是上午已出现的位置。
- 仅summary：1次（16:29的d3ec59e2），不能当新观察或成功。
- 1439:21、matched=false：1次（18:10的f1e44ef3）。
- **2:3028、matched=false**：1次（最新18:34的356e17e4），是下午新的诊断位置，但不是scope的HTMLFormElement.submit 1:75507调用。

**有效增量**：从一个长期slow-script位置，确实出现了不同source形状/错误位置和更精细归因；不能说所有23次都严格完全相同输入、毫无新信息。

**未见目标边界突破**：这些正式raw没有真实host-observation，也没有目标wire或独立业务readback证明。collector本来不覆盖全部外部网络，所以严谨说法是“正式产物未证明目标请求/提交”，不是“整个执行绝无请求”。

23个scope代表配置/依赖不断重签，不能把名称都叫baseline理解为严格同baseline对照；scope越多也不代表离业务成功越近。19次相同raw证明正式观测长时间停在同一结果类，但不自动抹去未被此窄collector捕获的小探针差异。

## 4. pair/classify状态没有随笔记推进

当前项目磁盘上的pair.json和classification.json仍来自昨23:49、23:51，scope前缀777d3a...；它们不匹配当前75fe61cf...。昨classification是boundary-unchanged，不能被拿来证明今天submit scope已有正式配对/分类。

本次统计没有今天当前scope的pair/classify正结果，没有新的readback产物。最新scope仍property=HTMLFormElement.submit、receiver=HTMLFormElement、callsite=1:75507。完成轴没有因本轮审计改变。

## 5. 18:39以后确有重复核验，19:00是改门不是新运行

`20261021-verify-line-3028.md`（18:39）、`verify-3028-still-blocked.md`（18:40）、`official-failure-record.md`（18:47）、`next-still-verify.md`（18:49）都引用同一356e17e4、同一scope/exit1/matched=false结果，并明确说没有改helper/没有重跑。

这几拍是**同一证据和状态的重复验证/解释**，没有新增目标观测。不能把多份笔记或反复next盖章统计成多次目标推进。18:52的kind-other说明仍分析同一个门为何不放行。

19:00的 `20261021-function-keyword-gate.md` 明确只加一条放行逻辑：2:3028恰落在function关键字最后一个字符、side class/kind=other且无sourceForm/sourceClass时，从verify_host_execution变成repair_submit_host_behavior。笔记同时承认没有点名具体缺失API，也没有改helper/重签scope/重跑baseline。

所以这个变化是**工作流授权条件改变**，不是新的修复成功/HostObservation/业务结果。其技术充分性由另一审计切片检查；本切片只确认时序与“门变了但run没有变”。

## 6. 当前依赖快照与exit1的准确含义

当前scope显式绑定13项dependencies，加runner/runtime/input/source/config共18份绑定文件。11项小于2MiB的dependency独立实hash匹配；geckoXul/Node大文件不在本切片重复重hash，不能声称整个load_scope已由本切片再验证。

全部23次timedOut=false、存在summary；它们的正式终态是failed，但不能因exit1笼统称为OS崩溃、外层超时kill或Grok挂死。当前门仍依据失败baseline做归因，并未有completed目标观察。

## 结论与限制

**fact**：下午23次正式baseline/23scope全失败，19次raw与上午同一结果；最新新位置2:3028未命中submit。当前没有目标活句柄，只有模型/MCP活动。

**fact**：18:39–18:49是同一run重复核验；19:00变的是工作流门，而非目标结果。当前pair/classify仍是旧scope。

**inference**：有局部诊断与实现分支变化，但目标证据链尚未闭合；下午相当一部分工作是重复验证/门条件解释，而不是可验收业务推进。

**unknown**：临时探针完整效果、所有外部网络行为、两个Grok客户端各自写入归属以及新放行条件是否有充足技术依据。本报告不读取旧last-copy推断这些事实，也不替技术审计下根因判决。


## 19:09补核：双Grok归属与旧产物的实际消费者

为避免仅凭同cwd/双进程就推断P1冲突，本轮定向解析两个main当前保留的工具调用结构，只保存路径/工具类型/结果是否存在，不保存命令、正文、reasoning或凭据。证据：`cross-session-writes.redacted.json`、`consumer-verification.redacted.json`。

- 第一main（旧会话）：6条保留user中1条出现psa_solve，10次终端调用引用项目；写入psa notes/docs、web_case.py和对应tests。
- 第二main（14:27会话）：9条保留user没有psa_solve引用，终端调用中0次引用psa_solve；当前保留写入涉及ruyihttp、SKILL/架构/工具文档、.gitmodules等，没有写入这批psa文件。
- 两者当前保留写入路径没有交集，**没有证据认定两个Grok正在同时修改同批psa文件**，不将这一点升级为P1。它们同仓编辑规范/工具仍可能影响工作环境，但那是另一个需具体diff证明的风险；compaction也意味着本结论不覆盖已丢弃的完整历史。

随后实际只读调用现有消费者（不执行next/record/目标）：

- `host_evidence.verified_classification(project)`拒绝，ValueError：host cycle is not classified。
- `web_case._verified_host_pair(project)`返回False。
- 当前serverAccepted/localReproduced/requestBoundaryAligned三轴仍为False。

因此，旧pair/classification虽然仍在磁盘，但当前消费者并未把它们当成已验证新结果。准确结论是“未形成当前scope的新闭环”，不能说“旧pair已经被误用放行”。

连续verify/next可包含合理的状态复核，不能仅凭重复就叫浪费；这里可确认的是多轮条件和run未变、没有新增目标观测，应归为记账/门禁调试，而非目标执行推进。
