# 2026-10-22 早间纠偏与技术增量审计

## 0. 范围和快照

仅只读比较上一轮 10 月 21 日深夜报告之后到今早 08:12 笔记的技术增量；未运行目标、测试、网络、patch、next 或 facts。旧报告锁的是当时已读的 22:20 `02b1...`；其后 22:25 产生过 `69cede48...`，不能把旧快照误作整夜最终状态。

本轮当前快照：

- scope：`614ff6bf72def2d56c26e6f5e3d992dfb0ed75eaf204d6fb9d034ded03037f8f`；
- helper：`6ad5ffb19ea7d746588f7ac4a8e604c8bb9c5bb8b98895f62455b4822eed0a0d`；
- baseline：`a11a7f0a2c1c4b8290fd25d9b2f57048`，failed/exit1/timedOut=false；
- 目标 source 仍是 `262a1bf5...`，没有据不同 source 拼进度；
- 新 raw 回到 1:55371 slow-script，无 submit 1:75507 host-observation。

哈希与脱敏 side/raw 在 `diagnostics/morning-correction-audit-20261022/technical/`。运行统计与活态由另一切片处理，本报告不另全量扫描执行目录。

## 1. 结论

**上轮最硬的 side 漏绑和 receiver 默认占位问题，已出现实际工具修复；Location/contentWindow/window 干预也已退出默认安装。Debugger 的帧级读值和静态循环分解有真实诊断价值，今早没有继续把看不到的宿主硬补成全局，这一点应给足。**

**新主要偏差更严重地影响“推进”解释：默认 helper 又把三个没有真实行为合同的短名填成空函数/return undefined。错误列离开 98085/76877 是这种未验证兜底后的局部执行，不能作为原生补环境恢复或求解更接近成功的证据。** 当前仍没有新的正式 FO/submit/业务验收里程碑。

## 2. 上轮纠偏核对

| 上轮问题 | 当前状态 | 实际证据与边界 |
|---|---|---|
| side 未被 execution 绑定，gate直接读邻接文件 | **已改，当前产物与 consumer 都落地** | execute写receipt.side，当前a11的side hash匹配；consumer只接受receipt ref并verify_ref、校验路径，不再认任意sibling side |
| receiverId恒填null，被当真实空对象 | **默认已改，且新增帧级观察；仍有口径限制** | 默认unknown/uncollected；98085有Debugger查值产生empty；empty合并null/undefined，非唯一native identity |
| Location广catch/静态URL/原型guard | **默认已隔离，遗留定义仍在** | 函数定义保留，但当前wrapped和onNewGlobalObject无对应安装调用，不把死代码继续算当前污染 |
| frame contentWindow变0对象、top/parent=self | **默认已隔离** | 原函数未删，但活动入口不再调用installFrameWindowPrimitive/installSandboxIdentity等；不重报已隔离问题 |
| eval剥空白/直接return数字捷径 | **保持撤除** | 无恢复默认strip/fastPad；watch eval仅诊断开关。新问题是空函数兜底，不混同旧实现 |
| 失败和业务完成轴 | **保持正确** | 当前failed/exit1，三轴false；没有将summary.ok或新gate放行当业务完成 |
| 未归因时按列号放行新宿主 | **机制仍在继续扩形状** | 新30458等特许条件仍是诊断授权，不是browser/local双条件；但今早笔记已选择不再据此安装未知宿主 |

## 3. side 绑定已真正修好，不再重复昨日漏洞

`skill/web-reverse/scripts/host_evidence.py:277–283,334–336`：

- collector执行后，如side存在，把 `submit-host-side.json` path/hash写进execution.side；
- 验证时verify_ref并限制为raw同目录的指定side。

`web_case.py:3764–3779` 的 `_bound_collector_side` 也要求receipt.side存在、hash匹配、路径相符，再读JSON；宿主gate调用了该consumer。

当前a11 execution确有side ref，实际SHA-256为`ca42cb1f...`，与磁盘一致。本轮审计快照也计算为sideHashMatches=true。因此“只改side即可让旧ref全不变仍放行”的漏洞在当前消费路径已收口。

它仍不是防本机全权限伪造的签名，但已经覆盖设计承诺的产物一致性；不能把这个有效修复贬成“只多写了一个字段”。

## 4. receiver 采集真实前移，但不是所有字段都已成为精确身份

### 4.1 默认unknown与实测empty已经分开

collector `describeScriptError` 当前默认 `receiverState=unknown,receiverId=uncollected`（659–660），不再把未记录状态恒填null。

针对98085，collector装Debugger.onExceptionUnwind，按frame offset与错误位置配对，在environment读取jz，再将读值归类（419–479）；仅当正式nsIScriptError也在1:98085时才写回（362–369）。历史正式baseline `624f0449...` 的side确有receiverWatch=empty、receiverWatchColumn=98085、jzReceiver.empty，不是笔记凭异常文本臆断。

这是实际观察渠道的改进。准确说法是“该次Debugger查值得到empty归类”，不能再说它仍只是昨日那个常量placeholder。

### 4.2 保留的观测限制

- receiverRecord将null与undefined合并成empty/null（346–348），所以不能断言具体是null而不是undefined。
- 环境查找只要getVariable不抛错就found=true（453–455），没有先确认该层环境绑定存在；也会沿older帧查同名变量。它不是对象nativeId/creation provenance。
- 观察点基于源码范围和函数名；不能把一次j5/jj帧读值泛化为所有调用或整个VM状态已恢复。
- 当前a11的slow-script没有errorName/receiverState；顶层receiverId为JSON null，不是新的真实null receiver证据。

因此真正的增量是“能区分未知并在部分帧读到了值”，不是“所有卡点receiver已经闭合”。

## 5. F1 · P1 · fact：未验证的短名空函数已进入正式默认基线

### 5.1 实际安装代码与默认入口

当前helper明确有：

1. `installTurnstileScriptMarker`:1584–1603：
   - 遇到Window上缺失的`xdiN1`、`SSvM5`，创建 `function () {}` 并export/赋上去；
   - 没有转发到真实producer，也没有恢复参数、返回值或副作用。
2. `installSandboxClock`:1384–1385：
   - Sandbox缺`xPLd9`时，执行 `host.xPLd9 = new host.Function("return undefined;")`。

`wrapped`:1744–1745默认调用marker并改写要喂给document.write的HTML；文档新全局钩子1815默认调用installSandboxClock，所以这三项不是独立未交付的探针。当前scope锁定的helper hash正是包含这些代码的`6ad5ffb1...`。

### 5.2 为什么这不是充分证明的宿主修复

名字是否混淆不是判据。它们可以是目标动态资源注册的回调、helper或其它runtime属性，不能仅因短名就断言“VM内部”。真正的问题是：**没有对应浏览器实际函数合同，却用无副作用/undefined填补它们。**

从本地读取过该名字、随后not-callable TypeError，可证明“程序期待一个可调用值”；不能证明该函数应该什么也不做。空函数会自然消除not-callable异常，却可能丢失队列写入、注册、promise、返回值或其它目标状态。

`window-callable-passed-98085.md`和`sandbox-function-left-76877.md`把错误列离开相应位置记为局部结果，事实可以保留；但应注明这是**空函数干预后的条件执行**，不是原生功能恢复。源码hash未变也不保证目标语义未变，因为运行时全局绑定已被改写。

若用于隔离因果的临时实验，可以记录“将缺callee换成no-op会怎样”；当前问题是它们留在正式默认helper，使后续55371循环也运行在尚未验证的返回值/副作用条件上。不能用那条循环来反证其它原生API，也不能把“越过异常”直接计为求解进度。

### 5.3 marker资源本身也不等于真实加载次序

同一marker会插入两个async脚本标签：一个URL供finder看见，另一个不同shape URL供collector提供保存的API正文（1604–1624）。这可作为明确的离线资源夹具实验；但多插标签、改src读取回退与两条URL，不自动等价于真实页面原本的脚本注册链。servedScripts=2表示fixture映射被服务，不是fresh网络/协议验收。

本报告没有把这些名称预判为某一种VM opcode，也没有声称未知的正确函数实现是什么；只指出当前实现选择了无证的no-op行为。

## 6. 真正有价值的新增：缩短Debugger驻留和静态控制流恢复

### 6.1 采集器观察后清理Debugger，方向正确

collector:503–517在两处有限观察完成后清onEnterFrame、onExceptionUnwind、onNewGlobalObject并removeAllDebuggees，side.debuggee=released。此前仅removeAllDebuggees会被新global hook再加回，这个遗漏被修正。

a11与bf38的正式回执说明：释放后计数停在j5Entries=2/jjEntries=2，终态仍slow-script 1:55371。对减少观察者效应有帮助，但不证明13秒循环已不受任何debug模式影响，也不是业务成功。

### 6.2 55371的源级分解有真实排查价值

当前绑定源在该位置确为 `for(;j[...](jw[...],0);){...switch...}`，并非一个可直接按名字安装的global。今晨笔记进一步追索引别名、split字面表、旋转、比较槽、69个case，以及switch内break与for退出的区别。

这些把“有很多短名所以也许缺一个宿主”收窄为可检验的静态数据流。特别是笔记不再给局部量包split、不改VM、不改13秒，也没有凭新gate继续装未知global，是正确收敛。

但应分开证据等级：for/switch位置与结构可由绑定源码静态核验；“398次唯一旋转、槽704为!==、左操作数某字段length”等目前主要记录在分析笔记，没有新增正式动态操作数值。它们可以作为source恢复结论继续复核，不应写成运行时已读到该length或该条件值。

## 7. F2 · P2 · inference过强：慢脚本采样不证明13秒持续未离开同一for

`20261022-55371-switch-condition.md`称“慢脚本停在for头上，说明这13秒里条件仍为真，异常也没有逃出这个try”。

现有工具支持的是：**中断采样时执行位置在该for头**。它没有记录该次for进入/退出、实例身份、每次条件值、catch计数或13秒完整路径。相同源码可以被不同实例/调用多次执行，先前也可能进入/离开该循环后又回来；watchdog还可能在条件求值尚未完成时打断。

因此这句话应降为“终止时仍采到该循环，怀疑循环/解释器未收敛”，不宜当成整段时间持续同一条件为真的定论。

同样，“循环体无宿主字面名字”只支持没有**直接点名**的宿主调用。解释器通过动态表/值调用时，宿主可能在被调用函数或值的来源链上，静态名字缺席不等于宿主原因穷尽。不过当前笔记选择不再凭此新补API，行动方向并无新增偏差。

## 8. 当前实际状态、gate与未完成项

当前a11：failed、exit1、timedOut=false，raw只有diagnostic/summary，matched=false；source1:55371，不是submit1:75507。无新的host-observation、target wire或独立readback证据，三业务轴仍false。

新30458等gate特许仍属于策略放行：按确切列/错误形状允许一处same-scope行为，不是机器推导出的WebAPI合同。今早返回55371后，Grok已明确“没有宿主名就不改helper”，未再据空gate任选API，这一点比上一轮更稳。

Location/contentWindow/window primitive函数虽保留在文件中，但当前wrapped/onNewGlobalObject没有这些安装调用，新全局记录为identity-isolated；因此上一轮这些风险**已从默认路径隔离**，不应重报为当前活动污染。需要保留这个改正，而不是为了处理新的no-op问题再把它们恢复。

## 9. 后续最短方向（本轮不执行）

保留side绑定、unknown/empty分型、有限Debugger观察后释放，以及已经隔离的旧guard。先给三个短名真实producer/调用/返回/副作用找到同source浏览器合同，或将no-op严格标成诊断干预并移出默认基线；否则继续解析55371会混入人为undefined。再对该循环记录一次有实例身份的条件操作数/退出链，区分未收敛的目标状态与采样位置，不把warning列号替代动态条件。

最终评价：**证据工具和源级理解确实前进；目标执行出现新的可观察点，但默认空函数兜底让“越过异常”缺乏等价性。当前最该修的是基线的行为真实性，而不是再给一个新列号加gate。**
