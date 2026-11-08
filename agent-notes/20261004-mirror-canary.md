# Source aligned mirror canary

Copied the existing source-aligned Chromium diagnostic runner to runtime/mirror-canary.js for controlled replay. It uses no network: XHR/fetch are local stubs and the frame response is the already recorded HTML input. This is a diagnostic branch only; it does not alter the production runner or write acceptance flags.
## 运行结果

source-aligned mirror canary 运行到 `frameEval=ok`、`_cf_chl_opt=37`，且 `PQak3` 仍未定义。与隔离 runner 不同，它不在同步入口抛 constructor；首个异步错误为 `IV[w6(...)][w6(...)] is not a function`，调用栈位于 `zQ -> zt -> iR -> Timeout`，随后出现 `x[bf(...)][bf(...)] is not a function`。

这证明 bridge/eval/realm 关系确实改变了边界：同步 constructor 卡点已被越过，但仍未出现 FO request 或 PQak3 define。该 canary 仍是离线诊断，不是生产验收。

## 单变量补丁：classList.remove

mirror canary 原本只有 `classList.contains/add`，补入与浏览器事实一致的 `remove` 后，首个异步错误从 `IV[w6(...)][w6(...)] is not a function` 消失，边界继续推进到 `x[bf(...)][bf(...)] is not a function`（`Timeout.It`，约 offset 213722）。这确认前一错误就是 `classList.remove` 缺失，而不是抽象 receiver 问题。

仍未出现 FO request 或 `PQak3` define；该补丁仅用于离线 source-aligned canary。

## 单变量补丁后的当前边界

`classList.remove` 已将首个错误推进到 `x[bf(...)][bf(...)] is not a function`。source hash 仍为 `05102bb5158cd0ba9a41329021f124cad8778a9a556db9a0e802b11c07115262`，`frameEval=ok`、`_cf_chl_opt=37`、`PQak3` 未定义、XHR=0。

下一步不应继续补 classList；需要对异步 `Timeout.It` 做静态 source-site 定位并对其 receiver/property 做动态记录，再决定是缺少 DOM/URL/状态对象方法还是响应生命周期。

## Timeout 调用链复核

对 source-aligned canary 增加 timer wrapper 后，目标错误仍由 `setTimeout` 回调触发，且未产生新的 XHR/FO。V8Trace 的同源 throw context 显示错误前最后业务操作是 `#refresh` 导航、文案 `textContent` 写入和 `classList.remove`；`classList.remove` 补丁已消除对应首错。当前 `x[bf(...)]` 仍是后续 obfuscated method，不能从现有脱敏 trace 直接还原属性值。

## 当前证据边界

V8Trace 明确给出 `Timeout.It` 内 `textContent`/`classList.add` 的后续调用序列，但脱敏 trace 没记录最终 `x[bf(...)]` 的 property 字面值；Node mirror 只能稳定复现 `x[bf(...)][bf(...)] is not a function`，无法从现有材料合法推导应补的方法名。没有 request boundary，继续猜方法会变成无证据枚举。

## 定时器调度事实

mirror runner 已记录到 `Timeout.It` 是页面自己通过 `setTimeout(..., 0)` 注册的回调，和 `Li` / onload 其他 0ms callback 同时进入队列；当前 runner 能复现该回调异常，但无同 session response 数据进入，因此 `x[bf(...)]` 的属性仍不可从现有 trace 推断。现阶段最有价值的下一刀是对 fresh browser run 做同一回调窗口的 property/descriptor 采集，而不是继续离线补方法。

## Fresh browser response pointer cross-check

现有同一 RuyiTrace run 的第一个 Turnstile FO response 已确认是 opaque：798300 bytes，SHA-256 `47d704c3b9ff5249e83bb784aa04ed275ee84bb2cc6c61e6d76aa1c6a53c265a`。该值只作为 evidence pointer 写入 mirror 输出，不回放或注入 Node。mirror 仍停在 `x[bf(...)]`，说明缺口是 response/callback 生命周期而非可直接搬运的 FO body。

## Response lifecycle contract

同一 browser run 的 FO 响应顺序为 `798300 → 117964 → 6776` bytes，最后一跳带 `cf-chl-out` 与 `cf-chl-out-s`，content-type 从 text/plain 转为 text/html。该顺序是 callback lifecycle 的 browser fact；mirror 仅记录脱敏 shape，不注入任一 response body。

## Response API surface canary

补齐 `getResponseHeader/getAllResponseHeaders` 及 XHR event handler 绑定后，mirror 边界没有变化：仍 `x[bf(...)] is not a function`，XHR=0。说明当前缺口不是 XHR response-header API 的简单缺失；需要真正的 response delivery/state transition 才能触发后续 callback。

## Response delivery state-machine canary

已把 XHR stub 扩展为显式 `readyState/status/responseText/responseURL` 及 `opened -> sent` 状态，但不注入响应。结果无变化：`xhrCount=0`、`x[bf(...)]` 仍是首个错误。说明仅有状态字段不触发 Turnstile response callback，必须有真实请求关联的 delivery 事件与 callback 顺序。

## Response-state contract output

mirror 输出现在显式包含 response-state contract：`headers(200,798300) -> loading(200,117964) -> complete(200,6776,cfChlOut=true)`。该 contract 只描述状态形状，未驱动目标 callback，也未注入 opaque body；运行边界仍为 `x[bf(...)]`，说明还需要 request-correlated delivery event。

## Delivery injection instrumentation

已为 XHR 加入 `__deliver(shape)` 和 `deliveryEvents` 观测，但当前 challenge 分支没有创建 XHR，事件列表为空。由此确认 response delivery 必须绑定在真实 FO 请求创建之后；脱离 request 的状态注入不会进入目标 callback。

## Request creation probe

静态源中 `/fo/` 和 `/eb/` 由 XHR 状态机分支构造；mirror 同时探测 XHR/fetch，仍无 request 创建和 delivery event。当前 `Timeout.It` 走的是本地错误/刷新分支，尚未满足 request 状态机的上游条件。下一刀应定位触发 `/fo/` 构造的 gate，而不是继续注入 delivery。

## FO gate source fact

静态 source 已确认：`/fo/` request 由状态机在 `setTimeout(F,100,er,eV)` 路径中构造，前置包括 `iR()`、`iq()`、`iU()` gate 和 `runProgram` 返回值；mirror 当前没有 request/event，说明失败发生在该 gate 之前，而不是 delivery API。

## iU/iq gate static result

`iq()` 明确在 `/fo/` 构造前执行 `iU()`，而 `iU()` 只做状态/计时器与 fallback 文档路径；`iq()` 还要求 `navigator`、`iN`、`iX` 等条件和 `runProgram` 前置。当前 mirror 错在 `Timeout.It`，尚未进入这些 gate；下一刀应记录 `iU/iq/iR` 的返回/调用顺序，而不是注入 request。

## Gate instrumentation result

对 source 中三个已知 gate（`iU/iq/iR`）做入口插桩后，运行时 `gateTrace=[]`。这不是 gate 返回 false，而是当前 mirror 在调用它们之前就已经停在 `Timeout.It`；因此下一刀应继续向上游定位 `Timeout.It` 的错误条件/状态对象，不能直接 patch gate 返回值。

## Pre-gate timer trace

当前运行的定时器序列为：`ij(0ms)`、onload callback `0ms`、`Li(0ms)`、refresh `3600000ms`、`It(0ms)`；`gateTrace=[]`。`It` 是当前最早错误分支，且发生在 iU/iq/iR 之前。下一刀应对 `It` 的状态参数/分支条件做观测，不再假定 gate 已进入。

## It pre-gate state

静态 `iU()` 本身只是构造 fallback/refresh iframe 与 timer；`iq()` 还要求 `navigator`、`iN`、`iX` 等前置判定。当前 mirror 的 `It` 0ms callback 在这些 gate 之前执行，入口 trace 为空。下一步需要记录 `It` 的参数/receiver 和先前 `ij/Li` callback 对状态对象的写入，不能直接改 gate。

## Callback trace result

在 mirror timer wrapper 里记录实际 fired callback 后，仍只看到调度函数列表，`callbackTrace` 为空，因为当前输出窗口先执行 report/退出且 It 异常由 Node timer 路径捕获；gate 仍未进入。下一步应在 runner 内延长并区分 report timer 与目标 timer，避免把诊断输出当作业务 callback。

## Final-window callback trace

延长 runner 到 report timer 完成后，真实 callback trace 已确认：`ij -> onload -> Li -> It`。最终 gate trace 为 `iR -> iq`，说明 gate 确实在 report 前后进入过；当前异常仍发生在 `It`，但已经不是“gate 从未调用”。这修正了上一轮的诊断：`iU` 可能因 source wrapper/函数族命名未命中，不能据此判定未进入。

## It callback arguments

延长窗口后的 `It` callback 观测显示它由 `setTimeout` 无参数调用（`args=[]`），所以问题不是 timer 参数丢失；`x[bf(...)]` 使用的是闭包/全局状态。gate trace 同时显示 `iR -> iq` 已进入，下一刀应记录 gate 写入的具体状态字段与 `It` 读取的对象身份。

## Gate state-write probe

加入 `Object.defineProperty` 对 global/window/_cf_chl_opt 的 state-write 观测后，仍未得到可用 stateWrites；当前关键状态多通过普通 assignment/闭包对象写入。已确认 `iR -> iq` 进入且 `It` 无参数，下一步需对这些闭包对象的关键字段读取做 source-aligned property proxy，而不是只拦截 defineProperty。

## State-write proxy fact

source-aligned mirror 捕获了大量状态字段安装：`cVqg7/mGhI7/tnAvq1/WCMuS9/xdiN1/...` 等函数/对象/数值都通过 `Object.defineProperty` 写入全局，但 `proxyReads=[]`，说明 `window` proxy 没包住实际 eval receiver。最有价值的字段是 `xdiN1`（此前已知为队列写入函数）；下一步应在实际 eval realm 上对这些字段做读/调用追踪，而不是外层 global proxy。

## xdiN1 wrap result

对全局 `xdiN1` 定义做 wrapper 后仍未捕获调用；说明 `It` 失败路径没有经过该全局队列函数，或函数存在于另一个 eval realm。`Object.defineProperty` 只确认了安装，不能证明实际读取/调用。下一步仍需直接在实际 eval realm 包装函数生成点。

## Eval-realm probe status

当前 runner 已进入 source-aligned eval realm，但 `xdiN1` wrapper 仍无调用，说明 defineProperty wrapper 位于错误 receiver 或函数被复制到另一个 realm 后调用。入口/回调事实保持：`iR -> iq`，`It` 无参数，尚无 FO request。

## Eval trace result

在 Node `eval` 入口记录 source length 后，错误栈明确显示 `It` 位于 `eval at global.eval`，说明它确实来自动态 eval realm；当前未观察到 xdiN1 调用。下一步应围绕该 eval 生成的函数闭包/对象做包装，而不是继续改外层 window。

## Eval source inventory

当前 eval 序列已记录：2453、1205、238847、4、86732、238636、4 bytes。主要动态 source 是 orchestrate 238847、turnstile API 86732、iframe inline 238636；`It` 栈位于这些 eval 生成函数内。下一步应对 238847/238636 eval 的返回函数与闭包对象做代理，不能仅包 global.eval 外层。

## Eval return inventory

动态 eval 返回值进一步确认：init eval 返回 `_cf_chl_opt` object；orchestrate 238847 与 iframe 238636 eval 返回 `undefined`，4-byte eval 返回 number。It 的函数来自 eval 副作用定义，而非 eval return function。下一步应对 eval 执行中的函数定义/闭包注册做 source-aligned instrumentation。

## Definition-site inventory

`Object.defineProperty` 记录到的函数定义集合包括 `cVqg7/WCMuS9/xdiN1/SMMhU4/naaL6/.../runProgram/BGgf6/SSvM5/HxNX2`，每个出现两次（bridge/window 两个 receiver）。这证明函数复制发生在双 receiver 层；外层 wrapper 只包第一份，实际 It 闭包很可能引用第二份。下一步是对第二 receiver 的 define value 做同样包装。

## Receiver duplication detail

state-write trace confirms every function is defined twice: once on `window`, once on `global`. `xdiN1` wrapper still sees no calls on either copy, so It's failing method is a different closure-local property, not the exported queue function. This rules out simply wrapping the second global receiver.

## Current closure instrumentation limit

当前仍只能在 eval 外层获得 source/definition inventory；It 本体及 closure-local `x` 未暴露给可代理对象。未发现新的 FO/XHR 边界。下一步需要对动态 eval 的脚本执行环境本身做 realm-local instrumentation，不能继续在 global 层堆 wrapper。
