# 晚间纠偏落实与运行回执复核 / 2026-10-21

## 范围与快照

20:16–20:18 +08:00只读审计，以19:09下午报告为基准。本切片没有next/record/run/网络/终止/恢复目标，没有改facts/goal/source/原运行产物；只新增本报告和 `diagnostics/evening-correction-audit-20261021/runtime/` 脱敏证据。

主线程本拍仍repair_submit_host_behavior / blocked。该动作存在不代表目标已修复，以下均从实际文件hash、正式execution终态、CIM进程及只读consumer验证得出，不以AI笔记自述替代验收。

机器证据：`execution-and-helper.redacted.json`、`processes.redacted.json`、`consumer-validation.redacted.json`、`known-session-activity.redacted.json`。不包含完整命令行、消息正文、Cookie/token或指纹原值。

## 1. 上轮纠偏是否真正落盘

**已核实的纠正增量**：当前helper `document-principal.js` SHA-256为 `27aaae184eecb16b2e04231679abc1e70923ceb024d9aa0264012b22c29314a0`，独立实hash与当前scope中helper绑定完全一致。当前scope为222d589a...，不是沿用下午旧helper hash。

定向文本检查：`stripLargeTrailingRegex`、`installLargeEvalStrip`两名已不存在，未见 `__watchEval=true` 强开。结合19:32 `20261021-isolate-eval-strip.md` 和19:36正式回执，这支持“不等价大eval剥空白已撤出默认helper，并且新helper进入正式scope”的纠偏落实。

这是运行态/落盘一致性核验，不是对所有改名/间接代码的完整等价性证明；eval、Location、window identity改动的技术正确性由另一切片查。不能因为撤掉一个错误改写就宣称3028根因已消除。

## 2. 19:09后实际新增正式运行

新增 **4次正式execution、4个scope**，全部baseline、status=failed、exitCode=1、timedOut=false；没有patched或completed正式终态。

| 开始 | 结束 | run前缀 | scope前缀 | receipt墙钟秒 |
|---|---|---|---|---:|
| 19:34:41 | 19:34:50 | dd3f7a27 | 7eb3e7dd9771 | 9.078 |
| 19:56:07 | 19:56:16 | 9d37d27a | 2e241bf099f9 | 9.078 |
| 20:05:13 | 20:05:22 | 0b68c289 | cef99760eca4 | 9.077 |
| 20:13:54 | 20:14:03 | 8187e4d9 | 222d589a3142 | 9.078 |

正式collector累计36.311秒；不含临时探针、单元测试、模型/工具等待和实现修改，不能当整小时总耗时。最新8187e4d9...于 **20:14:03.994** 结束，随后20:14:48的page-window-identity笔记落盘。

每个scope的runner/source hash相同，但helper发生过修改、scope随之重签；“全部baseline”不是同一不变baseline的严格A/B对照。只能按各scope的固定输入诊断事实读取，不能将4次失败当成某一个单变量因果实验。

## 3. 新正式结果是否支持目标推进

4份raw均独立hash匹配execution引用，且全部同一hash `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，222字节，也与下午356e17e4的raw完全相同。

全部raw仅有host-diagnostic和summary：line2:3028、base=object、matched=false。host-observation/wire/necko/resp为0；stdout/stderr均为空。scope仍点名HTMLFormElement.submit 1:75507，当前3028并非该submit调用的正式观察。

**可支持的结论**：错误改写的隔离和若干宿主身份行为调整已落盘，并被新的正式baseline实际执行；没有把失败写成成功，也没有将3028写成host-observation。

**不能支持的结论**：4次正式raw丝毫未变，因而不能说Location primitive/proto守卫/window identity已推进到新的正式目标边界、证书提交或业务读回。它们可能有局部机制价值，但目前没有被此正式collector证明。

9.1秒比下午约22.7秒短，也不能自动解读为性能改善或更接近求解；它可能只是更早退出。exit1和summary存在仅能定为collector失败终态，不能据此说OS崩溃或外层timeout杀进程。

## 4. 临时探针不等于正式scope观察

19:32笔记里的非正式探针报告SecurityError、about-blank-injected等更完整身份；官方side/raw仍只有kind/class/line/column等窄字段。临时探针的真实异常信息不能自动补入另一份正式回执，也不能靠同列号证明抛错来自绑定的orchestrate源文件。

单元/抽取安装体测试、3028比较器分析、Location/identity局部probe可支撑各自机制假说，不能替代当前scope的host-observation或business readback。本切片没有重跑这些临时探针、没有统计其总耗时，也没有用笔记里的“测试通过”作为正式目标成功。

同样，raw没有网络行只说明此窄collector没有捕获/证明请求；不能推出整个执行环境绝无HTTP活动。

## 5. 当前活态与旧证据消费者

- Grok客户端PID3592、39660仍在，各自有3个常驻MCP；另有19:35启动的Grok PID58592。本切片没有证明第三客户端属于psa项目，不推断其任务或并发写入。
- 未发现psa runner、xpcshell或firefox目标进程。最新formal PID18436已不在运行时PID集合内。state=failed、pid=null，最终复读current仍为8187e4d9...，无活目标句柄需继续等。
- 两个已知main会话仍有近期元数据/terminal活动；会话活跃不代表目标正在跑。未读取会话正文或新查第三会话，不用旧last-copy推断本轮操作。
- 实际只读调用 `verified_classification` 仍拒绝：ValueError host cycle is not classified；`_verified_host_pair` 返回False。当前serverAccepted/localReproduced/requestBoundaryAligned三轴均False。

因此，旧pair/classification没有被当前消费者误当成新通过结果；准确结论是当前scope仍未形成新的可验证闭环，而不是“它已经拿旧pair骗过门”。

## 结论

**上轮纠偏有真实落实**：不等价strip已撤出、helper hash与新scope一致，后续正式baseline确实执行过。

**本轮正式求解推进仍未证明**：4次/4scope全部失败、同一222字节raw、0个host-observation，没有正式目标边界移动。Location/window identity局部试验不能升级为提交修复成功。

**当前不必等待目标进程自然完成**：没有目标活句柄，只有Grok客户端/常驻MCP活动；若继续，需要先解决来源/receiver的可验证归因和collector覆盖，而不是把重复同raw或新笔记数量当进度。具体技术建议由另一审计报告承担，本切片不实施。
