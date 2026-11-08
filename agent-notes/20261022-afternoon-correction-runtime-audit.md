# 10-22下午纠偏与执行证据复核

## 范围和快照

14:29–14:32 +08:00只读审计，对比早08:19快照（当时最新a11a...终态06:31:30）。本切片不消费主线程repair_function_prototype_constructor / blocked，不next/record/run/目标/网络/测试/终止；没有改源码、goal、facts或原运行产物。

证据在 `diagnostics/afternoon-correction-audit-20261022/runtime/`：`execution-timeline.redacted.json`、`scope-and-consumers.redacted.json`、`processes.redacted.json`、`final-state-check.redacted.json`。只存路径/hash/计数和终态，不回命令/消息/凭据正文。

## 1. 正式执行增量

早间快照后新增 **20次execution / 19个scope**，全部baseline、failed、exitCode1、timedOut=false。没有patched、completed或当前scope验证过的pair/classify。

正式collector累计墙钟 **442.394秒**；不包括临时Debugger/AST、语法检查、安装体单测、模型等待和文件读写，不能当整个上午/下午的目标或CPU总耗时。

首个新增终态08:28:38，最新 **5c3f17cbcf0d4eefa23ba7ebef89787f** 终态 **14:02:29.401**，约22.920秒，PID15636已退出。scope b183fa22...，state failed/pid=null。14:06是该baseline笔记，14:26是新写入位置被点名，不是14:26又执行了一次目标。

20份raw独立实hash均匹配execution；共有5种hash，合计host-diagnostic19、summary20，host-observation/wire/necko/resp为0：

| 正式诊断 | 次数 | 最后终态 |
|---|---:|---|
| 1:55371 | 5 | 10:04:18 |
| 1:98085 | 1 | 09:01:19 |
| 1:76877 | 1 | 09:22:41 |
| 1:1337365 | 12 | 14:02:29 |
| 仅summary | 1 | 13:38:59 |

同scope的320061...先仅summary，随后dd246...才有绑定side的失败诊断；两次仍非成功终态，不能用“存在summary”代替执行完成。

## 2. LeadingPad安装声明，不等于实际编译命中

当前helper绑定hash为c5243aeb...；磁盘helper及scope一致。最新笔记显示先后有内容eval、内容Function、sandbox/loader Function和compartment trim等改动。这些说明实现确实迭代，不能把全部20次叫严格同输入未改动重复。

但是，**正式raw/side没有提供对应的实际LeadingPad/compile/eval/constructor命中marker或编译输入输出hash**。最新side只保留已有j5/jj各2、debuggee=released等采样和原位置；其字段里没有前述wrapper命中计数。

因此三个层次必须拆开：

1. helper有函数定义/安装调用，或存在某属性：只证明声明/安装设计；
2. 真实动态脚本经过该wrapper：需要该动态调用的可关联marker；
3. 改写后语义等价且推动目标：还需要编译输入输出/行为对照和目标请求证据。

本轮正式产物没有完成第2、3层。缺marker不证明wrapper绝对没被调用；但也不能把wrapper定义、compartment安装体存在直接写成真实脚本已经命中和修复成功。

## 3. raw同列与token来源的限制

12次1337365 raw完全同一字节hash32a2ac26...；最新5c3f17cb的raw225字节、side642字节，分别与上一dd246d63一致（最新side hashb89ae10c...）。

这证明正式窄collector结果没有移动，不证明每次停在同一份动态脚本、同一调用或同一运行时状态。sourceForm=token、sourceClass=other并没有携带故障动态源码hash；collector诊断中的绑定source hash不能自动充当抛错动态脚本身份。

scope目标仍HTMLFormElement.submit 1:75507；当前1:1337365/matched=false是源外slow-script。它不能直接证明Function.prototype.constructor就是失败原因；原型路径只是一条需要实际调用证据的候选。

## 4. 14:26点名的是下一写入，不是已经验收的修复

`20261022-function-prototype-constructor-named.md`明确helper仍c524...、scope仍b183...、baseline仍5c3f17cb，没有改helper/重签/新正式执行。它提出下一处写 `RealFunction.prototype.constructor=fn`，并限制不改其它裁剪或调用点。

本轮只确认“下一动作被改成点名该赋值”，不能宣称该赋值已安装、命中或通过。候选是否安全、native-like原型关系是否正确、LeadingPad变换是否等价由技术切片分析；运行态审计不替它下语义结论，也不执行该动作。

## 5. 工具证据闭环与stale核验

当前实际load_scope成功；5直接引用+13dependency共 **18份文件全部实hash匹配**，未发现helper/runner比scope新导致漂移。state→execution和execution→side的实际verify_ref均通过，side绑定纠偏仍有效。

只读消费者实际结果：verified_classification拒绝（host cycle is not classified）；_verified_host_pair=False；serverAccepted/localReproduced/requestBoundaryAligned三轴False。旧pair/classification没有误当当前scope新通过。

这些完整性检查证明当前绑定关系一致，不证明来源内容本身正确或目标业务成功。代码中的新门不是execution的一部分，门允许继续也不能替代动态观测。

## 6. 真实进程与范围限制

14:30快照中无psa runner/xpcshell/firefox目标进程，PID15636不存活，最终复读state未变。无现存目标活句柄需要等待或重启。

Grok3592及3个常驻MCP仍在，另有14:18启动的Grok35200和2个MCP；本切片不推断它属于psa或并发写入。会话/客户端在线不等于目标在跑。

exit1且timedOut=false、summary存在，不能笼统叫OS崩溃或外层超时杀进程；临时probe的内部时限也不等于外层receipt的timedOut。没有正式网络行仅说明这个窄collector没有捕获/证明请求，不能推出整个执行环境没有HTTP活动。

## 结论

**有证据的增量**：持续新scope/实现迭代、side封存及依赖绑定一致性保持；没有把失败误写业务成功。

**没有证据的升级**：20次新baseline仍全失败，latest raw/side不变、无host-observation和实际编译marker；不能把LeadingPad函数存在或新点名原型路径写成真实命中/语义正确/提交推进。

**下一条应查的不是重复同列本身**：应区分真实动态脚本身份和wrapper实际命中。此处仅为审计限制，不授权本切片补探针、改helper或消费当前action。
