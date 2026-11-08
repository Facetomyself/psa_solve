# 晚间纠偏闭合与新增偏差审计（2026-10-21，20:14 后读取）

## 范围与权威快照

只读核对上一轮 19:05 附近审计之后的产出，不执行目标、网络、测试、修复、next 或事实写入；不使用只有 14 bytes 的 last-copy 推断会话。

最新已读正式 baseline 是 `8187e4d91aa04facab98a740f72dbad1`，scope `222d589a3142544c...`。当前 helper SHA-256 为 `27aaae184eecb16b2e04231679abc1e70923ceb024d9aa0264012b22c29314a0`。快照/对照位于 `diagnostics/evening-correction-audit-20261021/technical/`。文件在活动工作区，后续 Grok 更新不属于本报告。

## 1. 上轮纠偏核对表

| 上轮问题 | 本轮核对结果 | 结论边界 |
|---|---|---|
| 默认 eval 剥空白改语义 | **已改，且正式复跑闭合** | helper 已删除变换函数、标记与默认调用；19:36 新 scope 的正式 baseline 确实使用撤除后的 helper。原错误仍在，不能说撤除后已解决卡点 |
| strip 正反例回归缺失 | **已补源级回归与记录** | test_web_case.py 明确检查生产 helper 无 strip，并让原输入=4、未交付错误拷贝=3。本代理未重跑测试；它证明反例和隔离，不证明目标成功 |
| 2:3028 gate 无真实异常来源/receiver | **只部分改观测，正式证据链未改** | 非正式探针新增 SecurityError/about-blank-injected/stack；官方 collector 仍仅 other+行列，gate 仍依赖 function 外形和缺身份字段 |
| “允许修补”误当已证 API 缺口 | **解释层承认，但后续行为仍有偏差** | 19:41 明确说 `<`/`&` 比较和泛化 SecurityError不能点名 API，随后却凭同一错误连续试 Location getter、原型和页面 identity 安装；没有新增实际参数/receiver 证据 |
| 中午同步 XHR/Observer/default200 | **修正继续保留** | 当前异步 XHR仍按_async分流，未知status回0，Observer不再同步fire。未发现这轮重新打开旧捷径 |
| exit/summary 不等于成功，业务轴保持 false | **已保留** | 正式执行仍 failed/exit1，summary.ok=true没升完成；业务三轴false，无新 submit/业务通过 |

## 2. 真正完成的纠偏：eval 不等价改写已离开默认路径

### 2.1 不是只改文档或加开关

当前 `document-principal.js` 已找不到 `stripLargeTrailingRegex`、`installLargeEvalStrip`、`__largeEvalStrip`，带 document 的新全局也不再安装该层；`__watchEval` 没有默认开。旧的 fastPadEval 也没有恢复。

`agent-notes/20261021-isolate-eval-strip.md` 与 `baseline-after-strip.md` 的链条完整：

- helper 从 `7833680f...` 换为 `8c7a9ad1...`；
- 新 scope `7eb3e7dd...` 指向新 helper，保留 priorScope；
- 正式 `host run` 产生 `dd3f7a2723a4487ea116c04c650425d9`；
- 该轮仍 failed/exit1，raw 与撤除前 `356e17...` 字节相同。

因此可确认“默认变换污染已撤除且确有正式重跑”。同时也知道：剥空白并非复现 2:3028 错误的必要条件，上一轮审计从未证明这条错误必由 strip 引起，此次也不反向抹掉 strip 自身的语义缺陷。

### 2.2 回归覆盖恰当但不等于完整求解验证

`skill/web-reverse/tests/test_web_case.py:3398–3448`：

- 直接读取已发布 helper，检查函数/标志/默认调用不存在；
- 保留 XHR/真实 eval/13 秒 watchdog 等已有运行条件；
- 原输入返回 4，测试内未交付的错误 strip 返回 3。

这是针对上轮静态反例的有效回归，不是“用通过的 mock 测试抵消目标失败”。本代理仅核对测试源码及既有记录，未在本轮运行测试或目标。

## 3. 本轮正式产出：四轮新 baseline，错误形态完全未变

| 正式 baseline | 用途/改动 | raw SHA-256 | side / 完成情况 |
|---|---|---|---|
| `dd3f7a27...` | 默认 strip 撤除后 | `534609ca...` | finished=false、2:3028 other、receiver空 |
| `9d37d27a...` | Location 安装时原语兜底 | 同上 | 与上一轮 side 字节相同 |
| `0b68c289...` | 扩到 Location 原型守卫 | 同上 | 与上一轮 side 字节相同 |
| `8187e4d9...` | 页面窗口补 identity 安装 | 同上 | 与上一轮 side 字节相同 |

这四轮都为 baseline、failed、exitCode=1、timedOut=false，约 9.1 秒。所有 raw 与上轮 `356e17...` 相同，只含 host-diagnostic/summary。最新 side 仍没有实际 receiverId、access、threw、sourceName、异常名/文本或原始调用栈。

**解释：** 这些补丁可能已经尝试安装、被原生 descriptor/compartment 限制拒绝、或确实执行但没有影响首错。当前稀疏 raw 无法区分。不能由“同样失败”证明补丁绝对没执行，也不能由“测试过安装顺序”证明补丁已经对目标生效。

工具没有把失败升为成功，这是正确的；但四轮同样的未归因错误，尚未产生下一种行为修补所需的新证据。

## 4. 观测改善是实质产出，但还未进入正式链

19:32 非正式探针新增了具体错误：SecurityError / The operation is insecure，srcLabel=about-blank-injected，stack 包含 injected:2:3028、2:3345，receiverId仍null；sourceLineLength=0，keywordAtColumn=false。

19:41 `20261021-comparator-3028.md` 对源码的解释也正确：绑定源 2:3028 是两个参数的 `<` 函数，下一帧是 `&`，两者都不点名 Web API；泛化 SecurityError不能据此确定某个 API。

这些信息比下午只有 other/行列更有用。它们提示应追参与比较的两个操作数及其原语转换/安全 wrapper，而不是把 function 关键字当 API。

但正式 `host_submit_collector.py` 没改，生产回执仍丢掉这些身份字段。既有 gate 又偏偏要求 sourceForm/sourceClass **缺失** 才放行 3028，因此新探针并未提高正式授权证据的强度。只在笔记承认 receiver未知，不等于修好了机器消费链。

## 5. F1 · P1/P2 · fact：从“API 无法点名”转而连续改 Location，缺新的双条件证据

依据：`agent-notes/20261021-comparator-3028.md` → `location-primitive.md` → `location-proto-guard.md` → `page-window-identity.md`。

19:41 刚确认比较运算函数没有宿主名、错误是泛化 SecurityError、receiver空；其后把候选指向 Location，并从安装时对象转换扩展到共享原型，再把既有 identity 安装补到页面窗口。四轮正式 raw/side不变，也未保存“参与 `<` 的操作数确实是 Location”或“浏览器同点允许该原语转换”的新证据。

这是**假设驱动的覆盖范围扩大**，而不是已证 receiver/property 的单行为修复。现有笔记没有谎称修好卡点，反而诚实记了无变化；偏差在于没有先证实假设，就把安全异常兜底长期留在默认 helper 继续下一轮。

可以把 Location 当候选，用隔离探针记录 getter/原语转换是否真被触发；但不能因为 message=SecurityError 就把异常压成字符串，再拿没有变化的正式回执为继续扩大覆盖背书。

## 6. F2 · P2 · fact：Location guard 的覆盖与笔记“只处理 SecurityError”不完全相符

当前位置：`document-principal.js:860–904`。

### 6.1 location getter 抛任何异常都会走替身分支

- 886 行 `try { locObj=g.location } catch (...) {locObj=null;locGetThrew=true}` 没检查异常名或文本。
- 896–899 行只要 locGetThrew=true 就构造 `{href,toString,valueOf}` 替身并尝试覆盖 location getter。

所以这里不仅会处理 SecurityError，也会吞掉一般 Error/TypeError 等，和 `location-primitive.md` 的“仅当 SecurityError 或 insecure”范围不一致。单元测试只构造 SecurityError的 getter，并未证明其它异常被保留。

### 6.2 fallback 是安装时闭包值，不按实际 receiver 查文档

- 860–862 行在安装时捕获 `g.document.documentURI` 为 hrefText。
- `guardPrim` 原函数失败后直接返回该 hrefText（866–871），没有核验 `this === 被观察对象`、实际 owner document 或原生安全主体。
- 894 行对已拿到对象的原型调用 armLocProto；882 行覆盖该原型已有 toString/valueOf。因此不只影响最初那一个对象，也可能影响共享原型对象、借用方法或后续文档状态。

对于健康调用，原函数正常返回这一点确实保留，不能说所有 Location 都被强制常量化。但发生被拦异常时，返回的是**当前安装全局的静态 URL**，不是实际 receiver 的经过浏览器验证的结果。如果原来是合法的跨源拒绝，这会把“应该抛错”的行为改成成功字符串；如果文档地址变化，则可能使用旧文本。现有证据没有证明目标这次实际触发这些情况，故这些是确定的实现语义/覆盖风险，不是已证卡点根因。

## 7. F3 · partial/unknown：页面 identity 安装扩大了影响，但尚无真实安装成功/父子关系证据

`document-principal.js:838–850` 的同一函数会尝试把 window、self、globalThis、top、parent 都定义成返回 g 的 getter；1452–1455 新增把它应用到 waive 后的页面窗口，随后才 `orig.apply`。

- 对真实顶层窗口，top/parent=self 本身可以正确；
- 若该默认函数也应用到带 document 的 iframe realm，top/parent 都回 self 则不符合 iframe 父子关系；现有新全局入口并没有顶层判定；
- 真实 Window/Location 上许多属性受原生 descriptor/安全 wrapper约束，defineProperty 可失败，代码 catch 后吞掉；当前 caller也没记录 installSandboxIdentity 的返回值或重新读取身份。

所以只能确认“新增了安装调用并且 scope锁了新 helper”，不能确认“目标 realm 身份已经修正”。iframe 关系风险必须标为潜在，当前回执没有证明触发；不能把一项只检查源码调用顺序的 Node测试当 Firefox Window/Xray语义验收。

`test_web_case.py:3450...` 的 Location测试用 Node vm.createContext、手写可配置对象及人工 SecurityError，证明的是作者希望怎样兜底，不是实际浏览器允许这样访问的证据。

## 8. 未改与保留项

- function-keyword gate 仍是人工 diagnostic continuation 类型的放行，不是 submit 双条件。允许进一步读真实异常本身没有问题；本轮没有完成将其收窄为有来源/receiver的行为授权。
- 三个业务轴保持 false，未把 summary.ok=true、相同 raw 或测试通过冒充求解成功。
- scope/helper重签、priorScope、真实进程退出、失败拒绝继续保留，是正确的证据纪律。
- 恢复旧 CLI路径时按 note使用了与原绑定hash一致的 HEAD blobs，这是工具治理/运行可用性动作，不构成目标求解进度；本轮只核既有绑定与记录，不评价另一个治理任务的文件操作。
- raw仍不覆盖完整请求，不能从零请求行证明网络绝对没有发生；也没有新的独立证据证明 fresh FO/submit/证书 POST/readback 出现。

## 9. 最短收敛方向（本轮不执行）

保留已经闭合的 eval 撤除；停止以同一泛化错误继续扩 Location覆盖。先把非正式探针已经取得的真实异常名、source identity、完整 stack 与参与比较的操作数身份纳入正式可重复工具观测，确认具体哪个原语转换/安全边界抛错。未证实是 Location之前，不把安全拒绝改成当前 URL常量，也不要用改默认对象外观代替原生语义。

本轮评价：**上轮最硬的 eval 不等价问题已真正改正；正式归因缺口没有闭合，本轮新改动仍是无动态 receiver支持的 Location/window 假设扩展。产出有纠偏价值，但没有新增求解或提交通过项。**
