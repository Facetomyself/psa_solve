# 午后纠偏与新增偏差技术审计（2026-10-22，14:26 后读取）

## 范围与快照

仅只读比较今晨审计之后的产出；不执行目标、测试、网络、patch、next、facts。当前已读 scope 为 `b183fa222b5a4468...`，helper SHA-256 为 `c5243aebccc7b87d7b65e5d264cf8159c87b7126ef054621113cf79bda5c75b0`，最新 baseline 为 `5c3f17cbcf0d4eefa23ba7ebef89787f`。14:26 的 `repair_function_prototype_constructor` 是下一处已点名动作，**当前还没有实施，也没有新的正式复跑**。

快照与脱敏 side/raw：`diagnostics/afternoon-correction-audit-20261022/technical/`。

## 结论

**今晨指出的三个空函数已真正撤掉，且有正式撤后复跑；转发现在要求别的全局已有自己的真实函数，未命中保持undefined，不应继续按原no-op批评。side绑定和未知/空值分型也继续有效。**

**最硬的新偏差是默认写入 `Number.prototype.length=0`，以人为常量影响循环条件；另有全局eval/Function包装的真实语义差异。只裁首尾空白比原先整段删空白合理，不能拿旧反例硬套，但“还调用真eval/Function”不等于整个包装等价。**当前依旧失败在源外slow-script，无新的submit/业务通过。

## 1. 上轮纠偏是否真改

| 项目 | 当前核对结果 | 结论 |
|---|---|---|
| xdiN1/SSvM5/xPLd9默认no-op | helper已无那两处空函数与return undefined桩；`empty-callable-removed.md`对应正式baseline `b5288af4...`回98085，failed | **已改并有撤后复跑**，不能把错误列退回称负进展；它移除了污染条件 |
| 真实函数来源转发 | `publishForward`只接受候选全局own descriptor.value为函数；miss返回undefined，SSvM5/xPLd9没有重新填空桩 | **行为比旧兜底可靠**；仍需生产者/realm对应证据，不能仅凭查到某个同名函数当完整parity |
| side产物hash和consumer校验 | 当前5c3f execution有side ref，实际hash匹配；consumer仍verify_ref绑定路径后读取 | **保持已修**，不重报旧side漏绑 |
| receiver unknown/null分离 | 默认unknown/uncollected继续；empty仍合并null/undefined，环境查值未先确认绑定层 | **默认分型已修，精确绑定限制未改**；本轮无新receiver值，不把unknown升为真实null |
| Location/contentWindow/window guard | 定义虽保留，默认安装入口未恢复 | **保持隔离** |
| 业务成功判据 | 最新仍failed/exit1、三业务轴false，未将summary.ok、列移动、named动作报成功 | **正确保留** |
| 新默认语义干预 | Number原型常量；eval/Function wrapper及裁剪新增 | **同类方法偏差仍出现，但不是旧三个no-op原样复活** |

## 2. F1 · P1 · fact：Number.prototype.length=0不是浏览器缺口修复，而是全局常量/分支干预

位置：`diagnostics/shadowroot-repair-20261020/document-principal.js:748–754,1396–1402`。

默认 `installChallengeClock` 与 `installSandboxClock` 都在所属global的Function中运行：

```js
var proto = Number.prototype;
if (proto && proto.length !== 0) proto.length = 0;
```

页面入口（1974）、`_sb`包装（2014）与document新全局（相应installSandboxClock调用）会尝试安装，当前scope锁定的helper包含这两处，不是只在未执行探针里写着。

原生数字实例没有普通的length属性；例如 `(17).length` 默认是undefined。这条写入让所有该Realm数字的length读成0，且添加了可观察原型属性。它不是恢复一个浏览器本来就有、但本地缺失的Number语义。

`20261022-visible-number-length-1337365.md`明确说明：55371条件恢复为读取length并与0做`!==`，于是把沙箱Number.length的0写成页面可见，再观察停止列从55371回到1337365。该说明暴露了真正操作目的：**为了影响条件而造一个值**，不是源于browser/local双条件的接口恢复。

必须保留因果限制：当前没有捕获该次条件的实际左操作数类型和值；不能断言运行时读的一定是数字，也不能只靠warning落点宣布该分支一定被改成假。但静态实现确定改变了 `(n).length !== 0` 的结果（对数字由true变false）；若目标值是数字，它就直接改变目标控制流。没有实际操作数证据反而更不应全局写0。

这比今晨no-op换了机制，但仍是“用未证常量压过模型异常/条件”的同类偏差。源文件hash没有改，不代表运行时语言语义没改。

## 3. Leading trim要与包装语义分开判断

### 3.1 不是旧的“把字符串a b删成ab”问题

当前 `leadingPadSource`（1566–1606）和内容区 `trimInCompartment`（1630–1648,1692–1710）只切首尾空格/Tab/CR/LF，内部字符串/注释中的空白不再一律删除。

对通常的Script/FunctionBody文本，首尾空白一般不改变运算值、内部token或use-strict指令。旧的4→3反例不适用于当前首尾裁剪，不能为了批评又套错例子。改用同compartment的charCodeAt/slice也避免了之前chrome桥接访问的部分不确定性，是明确的诊断实现收窄。

但是裁剪仍改变源码文本、位置和潜在耗时。由Function生成的函数，其Function.prototype.toString可展示原始body；原生 `Function(大量首空白 + "return /x/.source.length")` 的生成函数文本含该body空白，裁剪后的文本则不含。即使两者返回值都为1，也不能称全部可观察行为等价。对依赖编译耗时或动态源码外观的挑战，这些差异尤其不能忽略。

当前raw没有转换前后source hash、具体wrapper入口/输入记录，故不能证明被挂住的那份脚本确经这层裁剪；warning仍在1337365也不能证明裁剪已命中但“算法无效”。

### 3.2 F2 · P1/P2 · fact：全局eval包装会改变direct eval，短脚本同样受影响

`installLeadingPadEval`:1629–1665创建普通函数fn，1655以`realEval.apply(this,args)`调用原eval，1661把globalThis.eval替成fn。

静态反例：

```js
function example() {
  let local = 7;
  return eval("local");
}
```

原生direct eval能看见局部local；替成普通fn后，其内部再间接调用realEval会在eval所属Realm全局求值，若全局没有local就ReferenceError。字符串很短、根本没裁剪，也发生差异。因此“短脚本不裁”不能证明短脚本完全保持原生合同。

此外 wrapper `fn=function(){}` 的length为0而原生eval.length为1；toString伪装（1658–1660）只改外观，不会恢复direct eval的lexical semantics。这些是确定的包装语义限制，不是推断当前目标一定执行了上面的局部eval。

### 3.3 Function包装也不等于完整原生构造器

`installLeadingPadFunction`:1691–1727同样用无形参fn替换全局Function，再RealFunction.apply。

- 全局Function.length/name与原生可能不一致；
- 生成函数source/body文本受裁剪影响；
- fn.prototype指回RealFunction.prototype，但constructor仍指旧构造器，确实存在绕过wrapper的入口；
- own toString返回nativeFn字符串，不代表Function.prototype.toString、descriptor、构造newTarget/subclass等行为已验证。

这些只说明当前包装合同不完整，不把每一项都宣称为本次首错。仅增加下一处constructor赋值也不会自动修复上述所有问题。

## 4. F3 · P2 · inference未闭合：named gate开始按helper源码缺行逐步指定补丁，但尚无当前慢脚本走哪条constructor入口的动态证明

`web_case.py:4039–4067,4325–4352`把helper文本里的调用/标记是否存在作为动作阶梯：页面eval、sandbox eval、Function各入口、内容区trim、最后RealFunction.prototype.constructor=fn。

该约束比任意加字段更具体，也诚实声明无完成轴；用户可批准这种有界诊断优化，不能仅因“点名代码”就认定违规。

但当前推理仍有缺口：

- sourceForm=token不是eval的反证，也不能唯一指向Function.prototype.constructor编译入口；它只是当前源名称的粗分类。
- 包装的prototype.constructor仍为RealFunction是源码静态事实；**当前1337365那份脚本就是经它编译**，则需要constructor调用/输入/Realm的动态证据。最新side没有这些字段。
- helper出现了 `trimInCompartment(body);` 只证明代码已交付，不证明目标执行到该分支，更不证明同一输入被裁剪。
- 多轮raw/side完全相同，不能把“下一个缺少的标记”自动当下一个真实宿主缺口。

14:26 note只点名允许下一处赋值，helper目前尚无 `RealFunction.prototype.constructor=fn`，没有新scope/目标执行。本报告不把尚未落地的计划当已发生的原型改写。

## 5. 当前真实产出与未改项

当前baseline `5c3f17...`：failed、exit1、timedOut=false，raw只有host-diagnostic+summary，matched=false，1:1337365 slow-script。side仍记录早期的Function属性、Sandbox xPLd9等有限采样，debuggee=released；没有eval/Function当前输入、真正条件操作数或worker来源字段。

side绑定继续有效；未知/空值口径继续区分。但`readBinding`仍直接把某层env.getVariable成功返回当作找到绑定（372–388），没有先确认环境层的实际名称；empty合并null/undefined等限制并未在本轮修复。它不抵消之前真实采集渠道的改进，也不把旧读取值提升为当前constructor trace。

脚本标记/静态API资源、转发已有函数等改善了本地诊断设施；它们还不是同source browser/local行为等价或fresh资源来源验收。`serverAccepted/localReproduced/requestBoundaryAligned`仍false，无submit:1:75507 host-observation、正式target wire或同会话readback新增通过。

## 6. 收口建议（本轮不执行）

保留已撤no-op、side绑定和旧guard隔离。先隔离Number.prototype.length=0，确认length读取的实际对象与来源，而不是再替它选一个返回值。对eval/Function优化先记真实入口、输入hash/Realm与转换结果，明确哪些只是解析性能实验；不要用helper字符串标记和同一warning列无限串下一处constructor补丁。

本轮评价：**纠偏做了实事，但基线又混入原型常量与不完整的语言内建包装。相比今晨，工具纪律没有倒退到伪报成功；方法仍在用未证环境改造追逐慢脚本落点，尚未产生新的求解/提交通过项。**
