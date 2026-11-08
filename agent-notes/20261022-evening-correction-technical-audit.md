# 晚间纠偏与技术增量审计（2026-10-22，19:43 后读取）

## 范围与结论

只读核对14:32报告之后到19:43的新产出，不执行目标、测试、网络、patch、next或事实写入。当前scope=`e9dbde8d...`，helper SHA-256=`626e1672475856e01ebcd3c69726b450e4486eb14d49ef39c87221ed598eb4b0`，baseline=`40b28d0a4e224679920a7f70c9a1b110`。

**上轮Number原型常量确已撤并正式复跑，新增了绑定的参数/编译入口观察；空函数未回、side绑定有效，这是实质纠偏。**

**新的主要问题是String.split缓存只按字符串化后的separator分类，却允许自定义Symbol.split/可变receiver，存在确定的可构造语义反例。fresh slice和移到Realm内有价值，但不能使整个wrapper等价。eval/Function根本语义仍未闭合，新增native toString外观不证明行为恢复。**最新仍失败，无submit或业务通过项。

## 1. 上轮问题是否改正

| 项 | 结果 | 证据边界 |
|---|---|---|
| Number.prototype.length=0 | **已从默认路径撤除，并有正式撤后run** | `isolate-number-prototype-length-baseline.md`、13e79448执行；当前helper没有该写入，不能继续按活动常量批评 |
| no-op短名/Location等旧guard | **未恢复默认** | 当前仍用真实own-function转发，旧primitive guard保持隔离；不重报已撤项 |
| side产物hash/消费者校验 | **保持** | 当前40b28 execution有side ref且与磁盘匹配，身份事件不再仅靠邻接路径 |
| 实际操作数/Realm观察 | **有正式新证据，但范围有限** | 13e侧记有55373 call-argument number/primitive与eval/Sandbox/source；不等于直接捕获length getter的receiver |
| eval direct/indirect与Function包装合同 | **未全面修复** | 包装仍默认，RealFunction.prototype.constructor赋值已执行；own/inherited标志解决重复安装，但不恢复direct eval环境与完整内建外观 |
| toString | **新增外观伪装，不是语义验收** | self/Function/split分支报告captured native text；当前target效果未证 |
| split cache | **新增默认优化，有等价性漏洞** | fresh copy避免共享返回数组，但custom Symbol.split/receiver coercion的语义未保留 |
| 业务完成轴 | **保持正确** | 最新failed/exit1、三轴false，无虚报通过 |

## 2. Number常量撤除的闭合证据及新采样价值

`20261022-isolate-number-prototype-length-baseline.md`对应helper `edce2621...`、scope `535f4944...`、正式baseline `13e79448ee6a4d55b6dff4d705bdfa0b`，failed/exit1，仍停1:1337365。当前helper也未再出现那两处Number.prototype.length写入或换成其它数值。

该run的绑定side确有：

- lengthWatch=seen、lengthColumn=55373、lengthSource=call-argument；
- lengthObject=number、lengthHolder=primitive、lengthProto=none；
- lengthThis/lengthRealm=Sandbox、lengthCalleeEntry=eval；
- compileEntry=eval、compileRealm=Sandbox、compileMatch=source。

collector `host_submit_collector.py:523–553`检查older frame的位置，再取当前frame.arguments[0]。因此这是真实Debugger函数实参观测，不是AI从变量名推断。

但必须准确命名：**采到的是传给某个callee的第一个参数**，不自动等于该程序读取 `.length` 前的持有对象。若参数本来就是先前length读取后的结果，它为number很正常。因此它支持“该次调用实参是number”，不能单凭此证明该在Number.prototype上安装length；撤掉常量是恢复可信基线，不等于已找出循环根因。

## 3. F1 · P1 · fact：split缓存存在可构造的非等价输入，当前target是否触发未知

### 3.1 默认实现

helper `installSplitCache`:1658–1696，且在 `installLeadingPadFunction`:1706先调用，随后才判断own/inherited Function是否需要包装。

核心逻辑1668–1680：

1. 仅在arguments.length===1时考虑cache；其它参数数目回orig，显式limit因此没有被直接缓存错；
2. 不要求receiver/separator为primitive string，先String(text)、String(sep)量长度；
3. textLen>=4096、String(sep).length===1时，以String(sep)为key；
4. 同一text相等即返回缓存row.slice，不再执行orig.split；
5. miss也调用orig后立即返回row.slice。

当前scope锁的helper和正式generated probe包含该默认安装路径；不是只有测试里存在的算法。

### 3.2 确定的静态反例（本轮不运行）

```js
const text = "x".repeat(4096);
let calls = 0;
const separator = {
  toString() { return "|"; },
  [Symbol.split]() { return [++calls]; }
};
text.split(separator);
text.split(separator);
```

原生String.prototype.split每次调用separator的Symbol.split，两个结果分别[1]、[2]。当前wrapper第一次缓存[1]，第二次text相同/key相同，直接slice返回[1]，不再调用Symbol.split。

这证明缓存不是一般split的等价实现。另一个问题是提前多次String(receiver)/String(separator)改变coercion顺序、次数和副作用；原生会优先处理separator的Symbol.split，未必应先把它字符串化。自定义Symbol.split还可以返回非Array对象，wrapper若发现它有slice就擅自调用，甚至第一次miss也会改变返回值。

这些是**可构造输入下的确定语义差异**，不是声称当前challenge用到了自定义separator，也不是声称缓存造成3:544。最新正式side没有split call/hit/custom separator观测，目标影响仍未知。

### 3.3 哪些设计值得保留

- 对严格限定的长primitive string、普通一字符primitive separator、未改内建方法的场景，split是可缓存的纯计算，fresh slice能保证每次有新数组，调用方改返回数组不会直接污染缓存row；这比返回同一数组靠谱。
- 多参数/显式limit走原函数，避免了一类常见cache key缺项。
- 每个Realm各自创建cache与数组，有助减少之前chrome数组访问/原型混淆；但未记录实际安装到哪一个String.prototype或命中多少次，不能从两种安装通道“都调用过”推导目标已被优化。

剩余边界：row.slice没有固定intrinsic，Array.prototype.slice/constructor/Symbol.species变更会产生额外行为；cache按sep保留最后的text/row而无淘汰，实际内存开销尚未测。无需把所有理论边界都判为已触发，但不能用几个普通字符串测试覆盖整个语言合同。

## 4. toString和Function own/inherited纠偏：有进展，但不是根本语义恢复

- Function重复shadow inherited构造器一度停到1:34；当前1707–1714只包装own且尚未包装的Function。这修正了一个自身引入的重复安装问题，16:25正式run回到3:544，属于诊断模型纠错。
- RealFunction.prototype.constructor=fn已在1762落地，修补了wrapper入口一致性；不等于当前慢脚本确实经过该constructor入口。
- eval wrapper仍通过realEval.apply调用（installLeadingPadEval内），替换全局eval。上轮direct eval局部变量反例仍成立，短字符串不裁剪也受影响；这一点没有被own-property guard修复。
- Function.length/name、生成函数source反射、subclass/newTarget等完整合同未通过browser/local parity验证。

18:05新增Function.prototype.toString分支（1643）会对spoof自身、leadingPadFunction和splitCache报告captured native字符串。这是外观处理，不能证明行为等价；不因做toString就推断它必然阻碍成功，但应避免把“返回[native code]”当“实现恢复native”。当前raw/side未因该动作改变。

## 5. 3:544是真实采到的新坐标，但与原source及submit先后的动态关系未闭合

当前40b28的raw为slow-script line3/column544，matched=false；side仍有length call-argument number，但compileEntry=unmatched、compileRealm=unmatched、compileMatch=absent。

所以需要分开三层：

1. **工具事实**：引擎该次warning报了3:544，绑定side/raw可复核；
2. **源码事实**：原始绑定orchestrate第3行同坐标是offset对象属性点，decoder会split长字面表；
3. **尚未证明**：报错动态source就是这份原始文件的同坐标、缓存拦到了那次split、它位于当前submit调用的实际前置路径。

编译输入已经过eval/Function包装和首尾trim，位置映射更需source identity；raw写入的sourceSha256仍是collector的绑定输入hash，不是warning脚本内容现场求得。当前compileMatch=absent不能证明“不是原文件”，但也不能把静态坐标直接提升为同点动态身份。

Grok最新note已承认这颗dot不是split本身、没加dot getter，且缓存没有改变warning位置；这一判断正确。问题不是它声称已成功，而是连续三轮没有split命中/安装回执，仍主要根据停止列与静态调用链推优化。

该3:544又被特许为repair_submit_host_behavior形状，仍是授权策略，不是browser/local证明split缺失或太慢。可以做受控诊断性能实验，但不要记成“已定位submit前最后一个宿主”。

## 6. 当前真实状态与最短建议

最新40b28仍baseline failed/exit1/timedOut=false，raw仅diagnostic/summary，3:544，matched=false；side与前两轮realm-cache尝试字节相同，当前side hash ref匹配。无成功patched/pair/classify、submit host-observation、fresh target wire或同会话readback新增证据，三业务完成轴保持false。

最短方向是保留Number常量撤除和no-op隔离；将split cache限制到已证明纯计算的输入域，或先隔离，再记录真实split receiver/separator/limit、调用与cache hit、返回Realm。并补慢脚本source identity/输入hash，不用native toString或helper安装代码存在性替代结果验证。

**本轮总体：纠偏有实效，新增参数/Realm观测比之前强；但仍在修正自建运行模型而未新增业务里程碑。主要新偏差不是“用了缓存就错”，而是缓存边界过宽且未实测目标命中，语言内建wrapper的不等价仍未清完。**

证据：`diagnostics/evening-correction-audit-20261022/technical/audit-input-hashes.json`、`latest-execution.redacted.json`。本轮无凭据、Cookie、token原值输出。
