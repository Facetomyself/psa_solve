# 10-22晚间纠偏与正式运行证据审计

## 范围

20:01–20:04 +08:00只读快照，对比14:32报告（当时最新5c3f...终态14:02:29）。本slice没有next/record/run/测试/目标/网络/终止，没有改源码、goal、facts或运行产物；主线程给出的repair_submit_host_behavior / blocked不在本slice消费。

证据目录 `diagnostics/evening-correction-audit-20261022/runtime/`：`execution-timeline.redacted.json`、`scope-and-consumers.redacted.json`、`processes.redacted.json`、`final-state-check.redacted.json`。无完整命令/会话/凭据原值。

## 1. 新增正式执行和当前终态

14:32后新增 **10次execution / 10个scope**，全部baseline、failed、exitCode1、timedOut=false；无patched或completed。正式collector墙钟合计 **235.456秒**，不含临时探针、实现/单元测试、模型和工具等待。

| 结束时间 | run前缀 | 正式raw诊断位置 |
|---|---|---|
| 14:35:36 | 5d586535 | 1:1337365 |
| 14:59:54 | 13e79448 | 1:1337365 |
| 15:29:14 | ecfae641 | 3:544 |
| 15:51:42 | 847e1482 | 3:544 |
| 16:08:19 | 388141dd | 1:34 |
| 16:22:56 | 1bffab3b | 3:544 |
| 17:59:49 | 5e9b1196 | 3:544 |
| 19:09:52 | 6b9b8eff | 3:544 |
| 19:23:19 | 31affd81 | 3:544 |
| 19:42:02 | 40b28d0a | 3:544 |

最新 **40b28d0a4e224679920a7f70c9a1b110** 结束 **19:42:02.695**，约22.923秒，PID35896已退出。scope e9dbde8d...，state failed/pid=null；观察期末仍为该run，没有新终态替换它。

## 2. 从1337365到3:544：有变化，但不是提交观察

10份raw实hash均匹配execution引用，合计host-diagnostic10、summary10。raw只有3种形态：1:1337365两次、3:544七次、1:34一次。全部matched=false，host-observation/wire/necko/resp均0。

3:544第一次见于15:29的ecfae641；其后7次该位置raw hash全是 `3279db9672ab9473b7db77fa43888d05254a826d908eaa41bef9722573665bee`，对应side hash也全相同 `00eaba2f96231c937406f8f1c9856de2b5c66a84721e0ec21c5c6cb99a1f7464`。最新split cache Function-realm改动与上一31affd81在raw/side上完全一致。

**可证**：较下午旧1337365确有本地停止位置/输出形态改变，不能说所有10次完全同动态执行。

**不可证**：3:544不是目标HTMLFormElement.submit 1:75507，没有receiver与该submit匹配；新列也没有独立动态source hash支撑。scope绑定源与token来源的同列不能自动推出同一动态脚本，更不能证明目标算法更接近业务完成。

## 3. 正式side出现新观测字段，但编译匹配仍是未命中

当前side935字节，已进入execution.side引用并独立实hash核验。它不是单独AI笔记，现有正式字段包括：

- lengthWatch=seen，lengthColumn=55373；
- lengthSource=call-argument，lengthObject=number、lengthHolder=primitive、lengthProto=none；
- lengthThis=Sandbox，lengthCalleeEntry=eval，lengthRealm=Sandbox；
- compileEntry=unmatched，compileRealm=unmatched，compileMatch=absent；
- debuggee=released；scriptError为kind other、class slow-script、sourceForm token、sourceClass other，3:544。

这些身份字段使“length是何种对象/从何处采样”比上轮没有marker更可核查，这是采集信息的真实增量。但它支持的是特定采样分类，不是已验证缺失宿主API或完成提交。

尤其 **compile unmatched/absent不是成功命中**。它也不证明整次执行绝无eval/Function编译，只表示当前规则未匹配到目标编译观察。不能用helper装上LeadingPad、Function ownflag/constructor、toString spoof或两条split-cache安装路径，倒推真实目标编译/split调用已被接管。

当前正式side没有split-cache hit/miss/call计数、目标split receiver/source/参数长度的可关联事件。将安装路径执行完等同于实际缓存命中/语义正确，证据仍不足；缓存与realm的语义评估由技术切片负责，不在此处凭未变raw反推。

## 4. 本轮纠偏落实与待验行为分开

15:03 Number.prototype.length隔离、15:33 eval ownflag及后续Function/toString/split-cache改动有笔记和新scope/正式baseline对应；实现迭代确实进入过正式执行，不是全部停在纸面计划。

但每个新scope是新的helper/条件快照，不能把10个baseline当同一固定基线下的严格因果对照；也不能只看新scope/笔记数量就算推进。7次相同raw/side说明正式观测在3:544停留，尚没有这些后续干预的目标效果证据。

toString或构造器属性是否语义等价、split缓存返回新数组是否保持全部行为，是代码层问题，本运行态切片没有执行单元测试或语义验证。不得以日志字段不报错替代该验收。

## 5. scope、完整性与旧事实消费者

当前实际load_scope成功；runner/runtime/input/source/config与13项dependencies合计 **18份绑定文件全部实hash匹配**。helper当前626e1672...，未发现比scope新的stale。state→execution与execution→side实际verify_ref均通过。

verified_classification仍拒绝（host cycle is not classified）；_verified_host_pair=False；serverAccepted/localReproduced/requestBoundaryAligned三轴False。旧pair/classification没有被误当当前scope新通过。

文件绑定一致只证明本快照和scope对应，不能证明内容语义正确；上述拒绝意味着当前证据链仍未完成，而非业务验收已被绕过。

## 6. 真实运行态与限制

20:03快照无psa runner/xpcshell/firefox目标进程，最新PID35896不存活。Grok客户端3592、35200、54100及其MCP仍在线；没有依据把这些常驻客户端都归给PSA，也不推断并行写入。模型在线不等于目标正在跑。

所有receipt timedOut=false且有summary；exit1是正式失败终态，不能笼统称OS崩溃或外层超时kill。窄collector无网络行只说明未捕获/证明目标请求，不能推出全环境无HTTP活动。

## 结论

**真实增量**：本地错误位置与采样身份有变化，新length/realm字段被正式side封存，依赖和结果引用完整性保持。

**目标结果仍不足**：10次全失败、7次3:544同raw/side，无正式目标host-observation或业务网络证据；split/编译路径仍缺命中支持。

**主要偏差警戒**：不要把包装器/缓存安装与实际命中混为一谈，不要把采样primitive或内联token位置直接命名为缺失宿主；保持实际调用证据、语义等价和业务readback三层分离。当前无活目标句柄需等待，本slice不实施后续动作。
