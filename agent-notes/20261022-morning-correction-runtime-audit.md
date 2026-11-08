# 10-22早间纠偏闭合与正式执行复核

## 范围和证据

08:17–08:19 +08:00只读快照，对照昨22:26审计的终点69cede48（22:25:41结束）。主线程已给repair_submit_host_behavior / blocked，本切片没有next/record/run/目标/网络/测试/终止，没有修改facts、goal、源码或原运行产物。

证据目录 `diagnostics/morning-correction-audit-20261022/runtime/`：`execution-timeline.redacted.json`、`scope-and-consumers.redacted.json`、`processes.redacted.json`、`session-activity.redacted.json`、`final-state-check.redacted.json`。仅身份类别、hash、计数与终态，未保存命令/消息正文或凭据原值。

## 1. 正式执行：27次/26个scope，仍没有成功观察闭环

69cede48之后新增 **27次execution / 26个scope**，全部variant=baseline、status=failed、exitCode=1、timedOut=false；没有patched、completed或有效当前scope的pair/classify。

正式collector累计墙钟 **287.094秒**。这不包括临时Debugger/AST/安装体/行列probe、模型等待、工具读写或实现时间，不能当整夜目标总耗时或总算力。

27份raw全部独立实hash匹配各自execution引用。合计host-diagnostic26条、summary27条，**host-observation/wire/necko/resp仍为0**。raw共有10种hash，对应若干错误位置/早停形态：

| 正式诊断位置 | 次数 | 最后终态 |
|---|---:|---|
| 2:3028 | 3 | 00:19:21 |
| 仅summary | 1 | 00:38:26 |
| 3:487 | 1 | 01:03:05 |
| 3:586 | 3 | 02:11:31 |
| 2:16322 | 1 | 02:47:06 |
| 1:98085 | 9 | 05:01:24 |
| 1:76877 | 5 | 05:16:59 |
| 3:80263 | 1 | 05:20:52 |
| 1:30458 | 1 | 05:41:26 |
| 1:55371 | 2 | 06:31:30 |

这比昨晚只有同一3028多了真实的本地错误/执行形态变化，但每条diagnostic仍matched=false。不同错误列不自动等于challenge/业务更近，也不能把全部27次叫完全同条件的空转。

## 2. 上轮side完整性缺口已实际闭合到当前链

上轮execution未引用side hash，新gate却依据side身份。本轮可核实的纠正：

- 27份新execution中 **26份带side引用，26份side实hash全部匹配**；另一份早退仅summary，没有side，不冒称它也具备完整身份。
- 最新a11a7f0a的state→execution引用实际 `verify_ref` 通过；execution→side引用实际 `verify_ref` 通过。side路径固定为该run目录的submit-host-side.json。
- 当前工具代码在收集器执行结束时登记side reference；现有side验证逻辑同时检查hash和同run固定路径。该结论来自只读代码/实际正向校验，没有执行篡改单测或重跑目标。

因此，当前side不再只是同目录但脱离execution引用的文件。这是**证据封存的实质改正**，不是单纯新增AI笔记。它仍不构成本机特权不可伪造的密码学信任根，也不为旧缺失引用的历史文件补签。

## 3. 最新正式baseline与新增身份

最新 **a11a7f0a2c1c4b8290fd25d9b2f57048** 的终态在 **06:31:30.377**，约22.722秒，PID26812，exit1、timedOut=false、status failed。当前scope614ff6bf...、state failed/pid=null。

raw223字节，hash731459ca...；side640字节，hashca42cb1f...。这两份分别与上一bf38ae97（06:10:17终态）完全相同：最后一次newglobal释放改动没有移动正式raw/side。

最新正式side记录：kind other、class slow-script、sourceForm token、sourceClass other、位置1:55371；debuggee=released，j5Entries=2、jjEntries=2、calleeEntry=2，calleeBase=Sandbox；propertyName=Function及其观察列存在。receiver仍没有稳定ID。scope目标submit仍1:75507。

这些字段支持“调试器探针曾触发、随后已释放”的局部执行事实，不能升级为submit接收者或已确定缺失API。被观察到Function/别名也不代表它就是报错的host原因。

## 4. 06:31之后的新产出主要是静态/诊断分析，不是新正式执行

06:42–08:12的alias/loop/switch-condition/condition-callee/neq-operands笔记仍引用a11a7f0a，没有新签scope/helper/runner和正式baseline。最终复读state也仍为该run，观察期间没有新执行替换它。

最新8:12笔记把55371的条件恢复为普通不等比较、右值0、左值来自this实例字段的length；并明确没有点名宿主、没有据此改helper。这种“未定位host就不硬补”的收束比凭短别名猜API更稳健。

但是，这些是**静态源码数据流/临时AST或Debugger分析**；其数学恢复正确性由技术切片复核。不能写成正式runtime操作数已被采到，也不能把笔记越来越详细当目标触达了submit。正式回执里的raw没有增加相应操作数或host-observation。

当前门仍说55371挡住75507、允许同scope一项host行为；这个许可没有提供具体宿主名字。本切片只确认run/状态事实，不消费许可或用它补API。

## 5. 当前scope与实际消费者都未误放旧结果

实际只读调用load_scope成功，并对5直接绑定+13dependency共 **18文件全量实hash**，全部匹配当前scope。当前helper/runner没有晚于scope造成已发现的stale。

只读消费者结果：verified_classification拒绝（host cycle is not classified）；_verified_host_pair=False；serverAccepted/localReproduced/requestBoundaryAligned三轴仍False。旧pair/classification没有被当成当前scope通过，准确说是目标证据链未完成。

失败baseline的exit1不等于OS崩溃或外层timeout；存在summary且timedOut=false，应保留正式失败终态口径。raw零网络行也仅说明该窄collector无捕获/证明，不代表全环境绝无请求。

## 6. 活进程和句柄

08:18进程快照无psa runner、xpcshell、firefox目标进程，最新PID26812已不存活。没有可继续等待或poll的目标句柄，未restart任何进程。

Grok客户端3592、39660及各3个MCP常驻仍在，另有昨22:43启动的Grok52208；本切片不推断第三客户端任务/项目。已知PSA主会话元数据仍更新至08:18，另一main止于昨21:45。模型/会话活动不等于目标正在跑；不从旧last-copy推断夜间工作。

## 结论

- **已落实**：side进入正式execution hash引用并正确复验；完整scope依赖匹配；Debugger终态及更多局部身份有实际产物。
- **仍未达成**：27次/26scope全失败，无正式host-observation/目标wire或业务readback证明，最新正式终态停在06:31，而不是08:12。
- **新偏差警戒**：不能把静态比较器/实例字段分析包装成runtime host缺口，也不能把side观察列/Function名字当submit因果；最新笔记尚未据此硬补，这是值得保留的纠偏。

本报告不执行目标或验证测试，不恢复goal；仅固定本次真实可比快照及其限制。
