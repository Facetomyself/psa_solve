# 2026-10-23 早间纠偏与技术产出审计

## 范围与快照

只读比较10月22日20:04报告后的新产出。不运行目标、测试、网络、补丁、next或facts。当前正式Gecko scope仍为`c8e9652b...`，latest baseline=`7e39848290c24e83867be54eb6ed8fca`、failed/exit1、3:544。夜间新增主工作面是另一条vanilla Node链，不能把Node消息/HTTP探针当成这份Gecko scope已通过。

源代码、笔记、正式/自定义回执哈希见`diagnostics/morning-correction-audit-20261023/technical/`。

## 执行摘要

**有实质新产出：split旧反例的适用域收窄已经实施；fresh Node路径有POST challenge-fo完成200的观测，并实际启动第二段blob Worker、装上onmessage。比昨天只有Gecko慢脚本更接近真实请求生命周期。**

**仍没有证书HTTP POST或同会话业务200。最强新偏差是Worker被同线程同步模拟、GPU能力被无证整套合成、form.submit的XHR请求尚未验证document导航合同。**最新几轮只是诊断parent内部同步dispatch循环，没有足够证据点名下一个可补宿主。Grok没有把FO200、solverReportedOk或postMessage误报成业务成功，这一点正确。

## 1. 上轮纠偏状态

| 项目 | 核对结果 | 边界 |
|---|---|---|
| split对object separator/Symbol.split/coercion乱缓存 | **主要旧反例已修** | 当前只缓存primitive string receiver + primitive单字符separator + 恰好1参数；对象/boxed receiver/显式limit回原函数，没有提前String() |
| cache返回数组身份/可变性 | **fresh slice保留** | 常规字符串场景每次新Array，不直接暴露cache row；不是全语言合同证明 |
| split实际命中/Realm安装验证 | **未闭合** | 正式side仍无split-hit，3:544位置没有移动；不能把规则收窄称根因解决 |
| eval direct/Function合同 | **未全面修** | 默认eval/Function包装仍在，toString native外观不等于direct eval lexical、length/name/newTarget/源码反射正确 |
| Number原型常量/no-op短名/旧Location guard | **未见恢复默认旧干预** | 本轮不重报已撤；新Node stub的问题单独按当前代码判断 |
| side/hash、失败判据 | **保持** | Gecko正式side继续绑定，Node新探针未冒称同一正式host完成 |
| 业务完成轴 | **保持false** | 没有cert document POST/readback通过，FO200未被当serverAccepted |

split仍有残余适用域边界：primitive separator也可以继承String.prototype上的自定义Symbol.split，当前没有检测该方法是否被改写；row.slice也受Array原型/Species影响。但上轮自定义**对象**separator和提前coercion反例已经退出cache，不重复算作未修主缺陷。当前目标是否触发残余边界未知。

## 2. Node的FO200是什么证据，不是什么证据

`diagnostics/post-worker2-20261023/trace-summary.json`的事件顺序明确为：

- send POST，urlClass=challenge-fo；
- done，status=200；
- 创建blob、第二个Worker启动、onmessage=function；
- 父页随后注册error/unhandledrejection，进入大量Reflect.apply循环，后续tick停止。

对应`node-trace-receipt.json`给出fresh Node https采集时间、403 challenge页、200 orchestrate、各自材料长度和cookiePairs；声明没有复制浏览器session或历史challenge body。

当前`runtime/lib/transport.js`默认非capture分支（159行起）确实通过http/https.request发请求，响应status来自res.statusCode，body来自res data/end；只有环境CF_CAPTURE_ONLY=1才走pending/回灌分支。代码与上述fresh回执支持“Node已实际走到challenge请求完成观测”，不是form本地fixture返回的200。

**证据强度限制：**这组目录只保留脱敏trace-summary和项目自定义receipt，没有执行环境hash、原始响应/取证脚本/捕获模式的正式工具链绑定，不能独立重建每次网络来源。应记作“有真实发送/完成观测、默认实网代码路径支持的新请求进展”，而不是已完成与browser oracle同scope parity验收。

`post-*`目录中的post大部分指postMessage/第二Worker之后，不是证书HTTP POST。实际记录仍是parentPostMessage=0、form/submit=0或没有它们的观察，certDocumentPost=false；一些未启动第二Worker的fresh会话能约3.5秒结束并读回403。不能把不同fresh source、启动分支或结束模式混为单变量因果对照。

## 3. F1 · P1 · fact：Worker模型没有浏览器的并发/消息任务语义，可能污染当前挂起诊断

位置：`runtime/lib/host-async.js:83–148,181–203`。

- Worker构造器直接调用bootWorker；bootWorker用`vm.createContext`/`vm.runInContext`同步执行脚本。这是独立Realm，不是独立线程/Agent或浏览器Worker任务循环。
- 父页postMessage直接deliverWorker，当场调用worker.onmessage/listeners；worker侧postMessage又当场调用父页handler。handler赋值时也同步flush队列。
- event.data原样传入，没有structured clone/transfer；发送后修改对象可被对方看到，函数等浏览器应DataCloneError的值也不会被拒。
- VM脚本异常和消息handler异常大范围吞掉；onerror/messageerror没有对应传播。外层“Worker构造没有throw”因此不必然证明内部脚本运行成功。

这些是确定的模型语义差异。例如真实Worker的忙循环可以在另一个Agent运行；这里直接占住Node主线程。真实postMessage应排任务；这里同步重入，可能在调用者初始化完成前执行对方handler。

**不能倒推当前根因：**最新target确实在Worker启动脚本中设置了onmessage，记录并非人为直接把handler塞到scope；但父页没有对该实例postMessage，worker启动后也没调用postMessage/Atomics/timer，所以尚未证明当前loop恰由消息队列问题导致。正确结论是“这种模型不能用于排除真正Worker并发/调度问题”，不是“把它换线程就必然求解成功”。

最新入站队列修复确实补上了“handler安装前消息被丢”的本地缺陷；但note明确已存在handler时仍当场送达，所以它只修队列保存，不是完整原生消息行为恢复。

## 4. F2 · P1/P2 · fact：仅读到navigator.gpu缺失，就默认合成整套能力和成功结果

位置：`runtime/lib/host-globals.js:74–143`；`agent-notes/20261022-navigator-gpu.md`。

实际新实现默认暴露gpu，requestAdapter必定resolve adapter、requestDevice必定resolve device，features/limits/canvas format为固定模板。device的compute/render/queue是no-op；createBuffer忽略请求大小/用途，mapAsync成功而getMappedRange永远给空ArrayBuffer。

这是会让程序沿“GPU可用”分支继续的真实行为/值干预，不是只恢复属性存在性。任何执行到buffer映射或计算的代码都会得到与成功GPU设备不一致的结果。

现有证据只说明本地target读过navigator.gpu，不说明browser同点是否有GPU、是否应返回null、adapter/device能力是什么，也没有证明target调用过这些新增方法。GPU_OK只验证作者写的stub按预期返回，不是browser fact或硬件联合一致性证明。

因此不能认定该GPU代码已造成当前循环；但它也不能作为“已证单surface补齐”进入默认可信基线。用固定成功能力补一个getter缺口，和之前用no-op压错误是同类方法风险。报告不输出实际或模板指纹原值。

## 5. F3 · P2 · fact：form.submit目前是XHR发送器，尚未证明document导航合同等价

位置：`runtime/lib/host-dom.js:481–496`，`runtime/lib/transport.js:80–84`。

form.submit读取控件、序列化表单并创建XMLHttpRequest；transport自动给它XHR的Sec-Fetch-Dest empty、Sec-Fetch-Mode cors。浏览器表单提交的document navigation还涉及destination/mode、URL/导航、referrer/credentials、响应消费及cookie上下文，当前没有建立对应合同。

纯协议客户端可以用HTTP库乃至XHR模拟正确提交，**不是“用了XHR就禁止”**；问题在于当前仅因为URL位于/cert就标cert-document，不能证明已模拟browser document POST。需要请求/响应与oracle逐项对齐，不能拿FORM_SURFACE_OK的capture-only本地断言作证书导航成功。

Grok笔记没有误报这一点：两轮form surface后的fresh Node仍无certPOST；最新post-inbound也明确未创建form或调用submit。因此这是一项实现/验收缺口，不是虚报已经提交的发现。

## 6. 其它增量与观察边界

- currentScript默认null比undefined更符合“无经典脚本正在执行”的状态，src执行期间设置/恢复也有具体实现；这可以保留为有限合同，不代表所有脚本/模块时序已验证。
- EventTarget从丢监听器变成按对象分桶，确实恢复了可观察监听生命周期；但dispatchEvent仍欠完整Event/defaultPrevented/异常报告合同。未见当前target实际dispatch该事件，不能用这个不完整点另猜首错。
- elementFromPoint对视口内任何坐标固定返回body，是简化几何模型；没有真实hit-test/browser同点对象身份，所以不能当完整layout行为。与GPU一样，不应从“读取过名字”推导任意方便的返回值。
- 最新几轮没有因为Worker里缺TextEncoder/MessageChannel就继续硬补；trace没看到target读取它们。也没有改时钟或替内部算术函数，这比无证枚举稳。
- 采样只覆盖有限函数/时间窗，toString还可能被包装；“没看到标准长宿主名”不是已穷尽所有间接宿主行为。当前note没有强行宣称不可模拟，这个边界保留正确。

## 7. 正式基线与验收现状

Gecko当前仍scope c8e...、execution7e398... failed/exit1、3:544；split pure-domain正式回执与旧raw/side相同且无split-hit。Node新鲜HTTP/Worker探针是另一条runner和source/session链，有局部请求进展，不能写回Gecko localReproduced或requestBoundaryAligned。

最新仍无证书document POST、同会话业务200、Node final runtime/parity通过；三业务轴false。solverReportedOk=true、FO200和worker boot都没有被误写为serverAccepted。

**本轮评价：上轮cache主要缺陷改了，Node真的新增了挑战请求/Worker生命周期观测；但新宿主模型有调度与固定能力语义风险，完成验证仍未前进。下一步应优先记录真实消息/Worker Agent与调用返回合同，冻结可信输入域，不用更完整的假API表代替browser证据。**
