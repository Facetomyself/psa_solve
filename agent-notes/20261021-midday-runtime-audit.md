# 午间运行态与正式执行时间线 / 2026-10-21

## 核验界限

本轮13:00–13:02 +08:00只读快照，对照上次08:36审计。主线程已给本拍repair_submit_host_behavior / blocked；本切片没有next/记账/目标执行/网络/终止/恢复/补丁，也没有修改goal/facts。仅新增本报告及 `diagnostics/midday-audit-20261021/runtime/` 脱敏证据。

机器证据：`execution-timeline.redacted.json`（逐run路径、scope/hash/终态/raw事件），`processes.redacted.json`（无命令行），`scope-dependencies.redacted.json`，`session-activity.redacted.json`（无消息正文）。

## 1. 当前活句柄与会话活动

- OS进程快照仍是Grok主进程PID3592及3个常驻MCP：ruyidom32960、ruyitrace43920、v8trace53716。未发现psa runner或xpcshell/firefox目标进程。
- 正式host state当前failed、pid=null；最新baseline `13a5d2e4...` 已结束，PID不在存活运行时PID集合中。没有需要继续等的目标执行句柄，没有重启任何东西。
- Grok主会话lastActiveAt更新到13:02:14，最新terminal日志13:00:26；会话层仍有活动，不足以判断正在采样、只读分析还是等待模型调用。
- 最新可识别子agent创建于10:18，lastActiveAt10:24；另一个早晨子agent止于08:40。没有证据把常驻MCP进程说成一个仍在执行目标的子agent。
- 不读取旧last-copy推断当前状态；它仍是10月20日16:41旧副本。本次会话元数据只用于活动时刻，不冒充完整对话或任务进度。

## 2. 相对08:08最新终态，增加了什么正式执行

从08:08:58之后到13:01快照，共新增 **15次正式execution、14个scope**；variant全部baseline，status全部failed、exitCode全部1、timedOut全部false，没有正式patched对照。累计receipt墙钟340.79秒。

**340.79秒只统计这15份正式collector执行**，不含临时小探针、模型/工具等待、读取和实现修改，不能倒推出上午总运行时间或总算力。

| 开始 | 终止 | run前缀 | scope前缀 | raw诊断列（line均1） |
|---|---|---|---|---|
| 08:35:44 | 08:36:07 | 78492058 | 9a0d32e12aad | 55371 |
| 08:53:38 | 08:54:00 | 76d1701a | cb5b775a43f2 | 1337365 |
| 09:05:55 | 09:06:18 | 35d601aa | 963fff7353f4 | 1337365 |
| 09:20:41 | 09:21:04 | bfd29989 | 66687399f484 | 1337365 |
| 09:38:20 | 09:38:43 | 329f75aa | 66687399f484 | 1337365 |
| 10:57:42 | 10:58:05 | 9014e236 | 07cbb17b2b5b | 1337365 |
| 11:14:15 | 11:14:38 | 18857b7a | bbb6ae5e84a9 | 1337364 |
| 11:22:03 | 11:22:26 | 6ac768b6 | 2827dd8dcdb9 | 1337365 |
| 11:28:36 | 11:28:59 | da06f146 | 7908e6c40b60 | 1337365 |
| 11:41:13 | 11:41:36 | 92cee734 | e2916aec1bfc | 1337365 |
| 11:49:19 | 11:49:41 | 8232a2da | c9650afd06bd | 1337365 |
| 11:55:27 | 11:55:50 | 1adb8824 | 9776d304a143 | 55371 |
| 12:33:25 | 12:33:47 | fedb3277 | 272255021f2d | 1337365 |
| 12:41:27 | 12:41:50 | f970b6fc | 40ffac4b2c67 | 1337365 |
| 12:50:25 | 12:50:48 | 13a5d2e4 | 2d6dfc952924 | 55371 |

最新run `13a5d2e400e74067934b6155d4063651`：12:50:25.446–12:50:48.157，约22.711秒；failed/exit1/timedOut=false。`agent-notes/20261021-window-date-inpage.md` 最后修改12:52:18，与该正式回执可以时序对上。

## 3. raw归约：推进与重复的强弱证据

15份raw均已独立重哈希匹配各自execution引用。它们全部只有1条host-diagnostic及1条summary，合计15+15条；host-observation、wire、necko、resp均为0。

仅有 **3种不同raw字节hash**：

- 1:1337365 / matched=false：11次，完全同一raw hash。
- 1:55371 / matched=false：3次（08:35的78492058、11:55的1adb8824、12:50的13a5d2e4），完全同一raw hash。
- 1:1337364 / matched=false：1次（11:14的18857b7a）。

因此，12:52笔记描述的页内Date改动在正式collector可见边界上，是从源外1337365回到源内55371；**最新raw与11:55以及08:35对应raw完全相同**。这是一条可核验的“回到既有错误状态”证据，不是首次出现的新host-observation或业务突破。

但不能反向说所有实验没有任何变化：14个scope说明配置/依赖快照不断改变，局部probe可能测到了Date/realm差异。这个切片只评价正式运行态和已捕获边界，不重做技术侧对Date实现的判断。

**业务边界**：这15份正式raw没有证据证明FO、证书document POST或业务readback发生。严格说是“没有被此collector捕获/证明”，而不是靠两行raw宣称机器绝无其它网络活动；临时探针读取/回放本地资源也不算独立线上求解。

## 4. exit1不等于进程崩溃

最新run在约22.7秒后结束且timedOut=false；raw仍有summary。正式工具终态是failed，但仅凭exit1不能认定操作系统崩溃、外层timeout杀进程或Grok本身挂死。

已知笔记把它解释为slow-script/解释器循环未到submit调用点；submit的scope仍是line1:75507。1:55371不是1:75507，matched=false也没有被写成host-observation。此处只能保留“目标调用点未形成正式观察”的失败分类；根因和collector归因门由技术切片负责。

## 5. baseline与执行依赖是否真的相同

当前scope为 `2d6dfc952924...`，property=HTMLFormElement.submit、receiver=HTMLFormElement、callsite=1:75507。它已经绑定13项dependencies：Gecko四个二进制、GeckoLib、helper、Node、CLI、Turnstile API、certRoot、iframe、两份FO资源。

相较早晨helper漏绑的状态，这种依赖显式化是实质的证据链改进。运行态审计独立重哈希了13项中的11份小于2MiB文件，全部与当前scope一致；geckoXul与Node因体积较大，本切片不重复技术侧大文件校验，只记录expected hash/存在/大小，不宣称完整load_scope验证通过。

不能因为15次都叫baseline就认为是在对同一不变环境重跑：它们分属14个scope，helper和资源集发生过变化。反过来，scope不同也不能自动认定挑战有推进；请求/业务结果仍须raw证明。目前能确认的是“依赖/realm局部迭代，正式目标观测仍未建立”。

## 6. 临时探针、守护残留与剩余限制

12:52笔记的date-ok12是helper抽取后的单元/安装体探针，不是业务求解终态。本轮没有重跑该测试，也没有用笔记中的通过数替代实际execution。

当前没有需要清理的psa残留守护进程；活着的是Grok及MCP。没有看到新的目标活句柄可等待，不因模型还活着就继续等待“collector自然完成”。

临时探针总数、它们的完整运行时间与网络范围不在本切片计数中；会话compaction也使不能从现存chat行数还原上午所有模型/工具动作。进程/文件快照是瞬时观察，之后Grok继续活动可能产生新run，应按下一快照增量计算。

## 最终分类

- **fact**：新增15次正式baseline都失败，raw只有3种且没有host-observation/目标wire证据；最新终态12:50:48。
- **fact**：当前无目标runner活句柄，Grok主会话仍在活动；依赖manifest已较早晨加强。
- **inference**：午间有局部执行模型/clock定位，但正式结果表现为重复/回退到既有错误列，尚非目标业务突破。
- **unknown**：Date/realm改变是否修复了必要前置、slow-script充分根因、未捕获临时探针完整效果。不要用新笔记数量、scope数量或exit1单一状态替代这些判断。
