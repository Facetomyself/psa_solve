# 晚间后段纠偏与正式异常身份复核 / 2026-10-21

## 界限与观察期新增运行

本轮22:22–22:26 +08:00只读审计，对比20:18前次快照。主线程已给repair_null_receiver_identity / run，但本切片是审计，**没有消费run、next、record、补跑、网络、终止、补丁或改facts/goal**。

观察期间Grok自己于22:25新签scope并启动baseline69cede48；本切片未触发它，只读现有终态补入报告。因此不能用22:24时仍为02b1的旧快照结案。

脱敏证据：`diagnostics/late-correction-audit-20261021/runtime/` 的 `execution-timeline.redacted.json`（最初4次）、`observation-window-update.redacted.json`（观察期间第5次）、`scope-and-consumers.redacted.json`、`processes.redacted.json`、`session-activity.redacted.json`。无完整命令/消息/凭据原值。

## 1. 20:18后新增5次正式baseline，仍无新目标边界

截至22:26共 **5次execution/5个scope**，全baseline、failed、exitCode1、timedOut=false，无patched或completed。正式collector墙钟合计约 **45.389秒**，不包括临时探针或模型/工具等待。

| 开始 | 结束 | run前缀 | scope前缀 |
|---|---|---|---|
| 20:29:52 | 20:30:01 | 0cd81ead | 5247b2e5d92d |
| 20:45:24 | 20:45:33 | 722438ae | 87371cc117da |
| 21:24:55 | 21:25:04 | 64d3a405 | 688e9a44f3f1 |
| 21:34:21 | 21:34:30 | 02b1aecb | 727d4f60c833 |
| 22:25:32 | 22:25:41 | 69cede48 | 665de0cea144 |

5份raw均独立hash匹配execution引用，全部是同一222字节hash `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。它还与20:18前8187、下午356e相同。

每份仅host-diagnostic+summary：2:3028、base object、matched=false。没有host-observation、也没有此collector捕获的wire/necko/resp。scope仍HTMLFormElement.submit 1:75507，3028不是submit。无请求行只代表本collector没有捕获/证明目标请求，不能外推整个环境没有网络。

最新 **69cede48...于22:25:41.260结束**，约9.080秒，PID27020已退出。新helper虽变了，正式raw没有变，不能把“获准一次行为修改”说成已推动目标调用/业务提交。

## 2. 真实新增证据是正式run里的异常身份side

前三次0cd81ead/722438ae/64d3a405的side仍194字节；21:34正式baseline02b1更换collector runner到c563864c...，同run目录side变为452字节，hash `450f5442a04a346eedc3f8d4a59839dbde85df251cfd737b0e4ce1074f553304`。

02b1 side写入21:34:21.630，位于该正式execution21:34:21.099–21:34:30.179窗口内，和新runner/scope吻合；新增身份不是只存在于早先临时probe笔记。核实字段：SecurityError/insecure=true，sourceForm=injected、sourceClass=about-blank-injected、parentLine1447、sourceLineLength0、keywordAtColumn=false、stackShape=other，receiverId为**字符串null**（不是stable对象ID）。

观察期间新69cede48的side与02b1 **字节hash完全相同**。所以22:25行为改动没有改变正式可观测异常身份。

**已纠偏**：先前只凭绑定文件function关键字推API的问题，已经补入正式采集的异常/来源类别。

**仍未知**：receiver究竟是什么、哪个具体host API抛错、应如何修复；SecurityError和parentLine1447不自动等于Location/contentWindow/window/submit。

## 3. side未被execution引用封存的信任边界

最新execution仅带raw/stdout/stderr hash引用，没有side引用字段；新增身份也不在222字节raw里。因此raw完整性通过不等于side从运行以来不可变。

本审计独立锁定当前side hash和时间，能证明现在读到的产物形状与run关联，但不能倒推从未被同权限过程编辑。新gate若依据side身份放行，需技术侧核查其校验合同，不能把同目录side直接叫“execution哈希已认证的新事实”。

## 4. 绑定一致性与本轮gate/goal变化

22:24对scope727d...实际load_scope通过，并对5直接绑定+13dependency共18文件全部实hash匹配，无漂移。观察期间scope改成665de0...、helper变为41e7a8fe...；22:26再次load_scope和18文件实hash也全匹配。

这排除了快照当时“helper比scope新”的stale问题。它不证明gate新政策正确，也不证明同baseline：5个scope是5组被重签的条件，并非同一固定环境严格对照。

21:38后先核验旧function门因新来源字段不满足，再有合同/门回归、22:11只读parent1447接线、22:14明确不写完成轴，22:20放宽为repair_null_receiver_identity/run。**22:20这一下本身只是执行许可改变**；22:25才实际有新helper/scope/target运行，其结果仍同raw/side失败。不得将两者时序混成“改门就已修复”。

## 5. 当前活态与消费者拒放

22:26运行时进程快照无psa runner/xpcshell/firefox。Grok3592、39660及各3个MCP常驻仍在；第三个19:35见过的Grok客户端已不在快照，无法推断退出原因/任务。两个main仍可模型/terminal活动，但无目标活句柄需等待。

最新state=failed、pid=null、current69cede48。只读消费者在02b1和新69cede48两组scope均实际复验：verified_classification拒绝（host cycle is not classified）、_verified_host_pair=False、serverAccepted/localReproduced/requestBoundaryAligned三轴False。旧pair/classification没有被当新scope通过。

## 最终结论

- **有工具支持的纠正**：正式collector补录异常身份，当前完整执行依赖绑定一致；不像前一轮只有临时SecurityError探针。
- **目标进展未证明**：5次/5scope全失败，同raw、后两次同side、无host-observation；最新终态22:25:41而非22:20盖章。
- **新偏差风险**：receiver仍空时放开一处未点名host行为，以及side没有纳入execution hash引用。具体API归因/门合法性由配套技术审计判断，不把政策改宽当技术修复。

本切片没有越过审计范围；只记录既有Grok新run终态，不重启、不干扰、不消费主线程run动作。
