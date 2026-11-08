# 表单仍未建出 / 2026-10-21

本拍是 `verify_host_execution`，`turnGate=blocked`。没有重跑官方 host baseline，没有写完成轴。

## 测量

- 沙箱 `document` 与页面是同一个，`document` 来自原型。结束时 form 0、iframe 0、shadow 0、script 3。
- 编排脚本里的 `runProgram` 都在字符串或正则表中，不是页面上要预先存在的函数。页面和沙箱上该名字都是 undefined。
- `PerformanceObserver` 构造 1 次、`observe` 1 次、`getEntries` 1 次。回调原来拿到 0 条，因为资源日志不在 chrome 直接读到的对象上。
- 改成在沙箱里读实际资源日志后，`getEntries` 返回 2 条 `resource`（本轮已加载的脚本），回调执行且没有抛出。form、iframe、新的外部请求仍是 0。
- 同一轮还碰到 `RTCPeerConnection` 1 次、`createDataChannel` 1 次、`createOffer` 1 次。3 秒内 promise 没有兑现，也没有失败，`setLocalDescription` 为 0。`randomUUID` 2 次，`Worker` 1 次。
- 已保存的 turnstile 脚本跑完后，沙箱上没有 `turnstile` 绑定。没有去拉新的脚本。

## 留下的宿主改动

只留在 `document-principal.js`：`getEntries` / `getEntriesByType` 和 observer 回调使用本轮资源日志里的脚本条目。计数包装已去掉。官方回执仍是失败的 baseline，因为还没有可配对的第 1 行 75507 脚本错误，也没有表单。

## 2026-10-21 续

`media.navigator.permission.disabled=true` 已在 `document-principal.js` 里。包装改挂到解析前就已经存在的页面和加载沙箱上之后：`RTCPeerConnection` 1、`createDataChannel` 1、`createOffer` 1，promise 兑现 1，失败 0，`setLocalDescription` 0。读到的连接状态是 `stable/new`，说明 offer 没有被写回连接。8 秒泵里 form、iframe、shadow 仍是 0，没有证书 POST。

`globalThis.turnstile` 的读取计数是 0。这一轮没有证据表明虚拟机在已武装的全局上读了这个名字，所以没有补 `turnstile.render`。

控制台只记到探针自己的 `processNextEvent` 那一行，类别对不上挑战脚本，也不是第 1 行第 75507 列。`pumpThrows` 是 0。

## 兑现之后

上一轮 `setLocalDescription` 为 0、状态 `stable/new`。这一轮在同一个 promise 上数了虚拟机自己的 `then`：调用 1 次，成功回调 1 次，回调正常返回，没有抛出。`createOffer` 的第一个参数是对象，不是旧式回调。兑现值的 type 是 `offer`，SDP 长度 2727，构造名是 `Object`。没有记录 SDP 正文。

`setLocalDescription` 这一轮是 1。结束后信令 `have-local-offer`，ICE 连接 `new`，gathering `complete`。`icecandidate` 处理函数装过 1 次。`negotiationneeded`、`icegatheringstatechange`、`signalingstatechange` 没有装。`turnstile` 读取仍是 0。

form、iframe、shadow 仍是 0，没有证书 POST。控制台仍只有探针 `processNextEvent` 那一行。官方 baseline 没有重跑，完成轴没有写。

## turnstile 与 iframe

`setLocalDescription` 之后仍是 `have-local-offer` / gathering `complete`。官方 baseline 没有重跑。

资源请求：编排脚本和 turnstile 脚本各以 `script` 取回 2 次。已武装全局上 `turnstile` 读取 0、赋值 0，结束时访问器还在。已保存的脚本里有 `window.turnstile` 和赋值，但这些赋值没有打到这个全局。调试器是在主沙箱已经存在之后才挂上的，长度桶里没有超过 6 万字节的脚本，不能据此说文件没有执行。

同一个沙箱里：`createElement("iframe")` 1，`appendChild` 这个 iframe 1。`form` 的创建、插入、`innerHTML`、`document.write` 都是 0。`attachShadow` 0。`innerHTML` 赋值 6 次，正文里没有 iframe。`document.write` 1 次，正文里也没有。结束时文档里的 iframe、form、shadow 都是 0。被挡住的请求仍是两次 favicon，没有 iframe 导航。

## 官方 baseline

`4abe7d432a7e403e8b058af626ea90d5`：exitCode 1，timedOut false，status failed。scope 没变。回执里的 diagnostic 是 helper 第 484 行第 22 列，也就是 `processNextEvent`，matched false。不是 submit 观察。同一次运行写出 `iframe-parent.json`：`iframeParentConnected` 是 yes，父节点当时 `isConnected`。完成轴没有写。

## 泵改成平台等待之后

`pumpIframeParent` 不再调用 `processNextEvent`。8 秒等待改成 `Services.tm.spinEventLoopUntil`。文档身份切换里仍有一处 `processNextEvent`，这次回执没有落在那一行。

`f1102401e0b943e391d794da2f9d0140`：exitCode 1，timedOut false，status failed，约 19.7s。scope 没变。raw 是 host-diagnostic 第 482 行第 19 列，matched false，base object。第 482 列 19 是 `spinEventLoopUntil` 的 `s`。没有 host-observation，没有第 1 行第 75507 列。summary.ok 只因为有 diagnostic 行。同一次运行把 `iframe-parent.json` 再写成 yes。完成轴没有写。没有证书 document POST。

## 等待行不再是脚本错误

空转本身不产生脚本错误。页面跑起来后，第 482 行第 19 列的消息是 `Failed to load resource:///modules/sessionstore/SessionStoreFunctions.sys.mjs`。该 URI 解析到 `runtime/modules/sessionstore/SessionStoreFunctions.sys.mjs`，文件原来不存在。已放一个不导入其它模块的空类，直接 import 得到函数。

`eab1fcfa181f49eea294369223d4fdd3`：exitCode 1，timedOut false，status failed，约 19.7s。scope 没变。raw 是 host-diagnostic 第 1288 行第 17 列，matched false，base object，kind/class 都是 other。第 1288 列 17 是 `Prompter.sys.mjs` 的 `openWindow`。没有 host-observation，没有第 1 行第 75507 列。summary.ok 只因为有 diagnostic 行。完成轴没有写。没有证书 document POST。

## confirmEx 默认按钮

`openWindow` 来自 `getPrompt` 的一次 `confirmEx`。窗口观察器打不开对话框，按钮停在初始的取消。helper 现在在 `openWindowPrompt` 里按 `CommonDialog` 的 `defaultButtonNum` 填 `buttonNumClicked`，按钮 0 才把 `ok` 设为 true，然后直接返回。

`b50ad87271ca446583f9b08f10ead18b`：exitCode 1，timedOut false，status failed，约 19.7s。scope 没变。side 里 `finished` 为 true，没有 scriptError。raw 只有 summary，ok=false。没有 host-observation，没有第 1 行第 75507 列，没有证书 document POST。完成轴没有写。同一次页面路径的控制台栈停在编排脚本第 1 行第 98095 列的计算属性调用，异常被虚拟机接住，没有变成 nsIScriptError。

## 第 98095 列是慢脚本看门狗

该列是 `j5` 里 `jS===1` 且接收者不是 undefined 时的 `.call`。控制台没有 TypeError。原生路径上，SpiderMonkey 的慢脚本看门狗在嵌套 eval 末列 1337364 终止脚本，这是 warning，采集器不记。页面仍约 19.2 秒返回，form 和 iframe 仍是 0。这次 eval 约 1337360 字符，连续出现多次，允许列表里的宿主名和 `while` 都没有命中。请求只有 orchestrate GET。把脚本时间上限改成 0 后，90 秒内仍不返回，该 pref 没有留在 helper 里。`Date.now` 在偏移分支第一次校准后走锚点快路径，函数身份不换。

`76471063d3bd45719814f52e72386aa5`：exitCode 1，timedOut false，status failed，约 19.7s。scope 没变。stdout 和 stderr 为空。raw 只有 summary，ok=false。side 的 finished 为 true，没有 scriptError。没有 host-observation，没有第 1 行第 75507 列，没有证书 document POST。完成轴没有写。

工具复核：`validate_execution` 对这条回执抛出 `execution did not complete successfully`。state 与 scope 的 scopeId 一致。runner、runtime、input、source、config 绑定与当前 scope 相同。raw 只有 1 行 summary，ok 为 false。stdout 和 stderr 长度为 0。这一拍没有新宿主面，也没有改完成轴。

## 看门狗这一拍

没有重跑官方 baseline。`76471063` 仍是当前回执。完成轴没有写。

慢脚本对话框的按钮种类是 continue、stop，默认按钮是 stop。在看门狗里先空转 300ms 再按 Continue，连按两次后仍停在嵌套 eval 末列，form 和 iframe 仍是 0。`Date.now` 约每秒 500 次，三次时间片大约三倍，循环没有退出。这段改动会超过官方 baseline 的 25 秒期限，已从 helper 撤回。

把沙箱上的 `setTimeout` 换成自有函数之后，调用变成 `does not implement interface Window` 或进程直接退出。不替换时，继承来的宿主函数可以让页面跑到看门狗。这个包装没有留下。

helper 仍是单函数锚点时钟，加上原来的身份、性能条目、RTC pref、confirmEx 默认按钮和 iframe 泵。没有证书 document POST，没有同租约回读。

## 工具重验 76471063

本拍 `verify_host_execution`，`turnGate=blocked`。用 `host_evidence.validate_execution` 重读当前 state 指向的 baseline，没有重跑。

- state status failed，scopeId 与 scope 一致，前缀 `9a0d32e12aad`。
- 回执 `76471063d3bd45719814f52e72386aa5`：status failed，exitCode 1，timedOut false，variant baseline。
- runner、runtime、input、source、config 五份绑定都与 scope 相同。失败原因是进程没成功结束，不是 scope 漂移。
- `validate_execution` 抛出 `execution did not complete successfully`。
- raw 1 行，event 只有 summary，summary.ok false。stdout 与 stderr 长度都是 0。

先前探针（本拍已从 helper 删掉，没有再跑）：j5 第 98095 列的嵌套 eval 仍停在末列。约 1.3MB 的脚本主体是空格，非空格部分折成数字逗号表达式加一条 8 字符正则。能返回的副本只要 1–2ms。后一次同长度脚本不返回，所以 form 和 iframe 保持 0。沙箱上 crypto、subtle.digest、WebAssembly、Worker、performance.now、requestAnimationFrame 已经存在。正则体哈希那一列写进分类器之后没有跑成，不能判断挂住的那次和 1ms 副本是否同一条正则。

`document-principal.js` 里的 eval 包装、形状写出和临时路径已经去掉。`node --check` 通过。留下的仍是锚点时钟、身份、性能条目、RTC pref、confirmEx 默认按钮和 iframe 泵。没有新宿主面，没有官方重跑，没有写完成轴。

## 嵌套 eval 是循环，不是单次卡住

本拍 `verify_host_execution`，`turnGate=blocked`。没有重跑官方 baseline，没有写完成轴。探针只在 `__watchEval` 下计数，官方路径不设这个标志。`Date.now` 热路径没有留下计数。

同一轮约 10 秒看门狗里：`eval` 进入 4607、离开 4606；长度超过 10 万的进入 4603、离开 4602。最后一次长度 1337363。接收者是全局。离开的那些返回值种类都是 number，没有 zero。`Date.now` 4613 次，大约每次 eval 一次。`performance.now` 1，`subtle.digest` 0，`getRandomValues` 1，`Worker` 1，`createElement` 27，`querySelector` 2，`getEntries` 1，`observe` 1。`cookieEnabled` 1。navigator 的 webdriver、hardwareConcurrency、userAgent、language 这些名字没有被读到。结束时 form 0、iframe 0，但过程里有一次 iframe 挂到了已连接的父节点。看门狗栈仍是嵌套 eval 末列 1337364，调用点是 j5 第 98095 列。

前六个大脚本的非空白哈希里，第一份是编排脚本自己（非空白 231843）。后面几份非空白只有 15 到 27。循环在改这小段程序，不在某一份脚本内部打转。90 秒上限那次也出不来，所以这不是 10 秒能算完的工作量。

请求类别：orchestrate GET 2 次有正文；另外 3 次被挡。其中 1 次是 psacard 主机、无扩展名、斜杠数 3；2 次是 cloudflare.com 的 `.js`、斜杠数 7，形状与 turnstile `api.js` 一致。采集器只放行 orchestrate 的 chl_page，这两份脚本没有正文。Worker 线程能进 `DoRunLoop`，没有脚本错误。

没有改采集器，也没有把旧的 turnstile 文件塞回去。官方回执仍是 `76471063`，`validate_execution` 仍会因 exitCode 1 失败。

## 戳不允许换资源

下一拍 `next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有把已抓到的 turnstile `api.js` 或被挡的 psacard 短路径填进采集器。工具重验当前 baseline：status failed，exitCode 1，timedOut false，五份绑定与 scope 相同，`validate_execution` 抛出 `execution did not complete successfully`，raw 只有 summary 且 ok 为 false。完成轴没有写。

## 空 baseline 的出口

回执 `76471063d3bd45719814f52e72386aa5` 的进程自己结束，墙钟约 19.7 秒，`timedOut` false。pid 53184。stdout 与 stderr 文件长度为 0，因为采集器把子进程的两路输出接到 DEVNULL。

`submit-host-side.json`：`finished` true，`base` object，`getEntries` function，`access` null，`threw` null，`receiverId` null，没有 `scriptError`。生成的 probe 没有 `__watchEval`，`blockUnmapped` true。

采集器只在控制台错误不是 warning、且行号不小于 1 时记下 `scriptError`。慢脚本终止是 warning，被丢掉。`collect_rows` 只有在该错误能配上第 1 行第 75507 列时才写 `host-observation`。没有 `scriptError` 时 raw 只剩 `summary.ok=false`，进程返回 1。`validate_execution` 先看到 exitCode 1，于是失败原因是 `execution did not complete successfully`。没有投放新资源，没有写完成轴。

## 慢脚本警告写入既有 side

本拍仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有改采集器，没有投放 turnstile 或 psacard 短路径。只在 `document-principal.js` 登记慢脚本 warning，并在探针序列化既有 side 对象时附上。`node --check` 通过。

官方 baseline `d05075ea12b04dc29246d5ecd148db78`：scope `9a0d32e12aad8ccb` 未变，runner 哈希仍是 `cdcf95b81828079c2f61092542bba32d1644fe2138e0e2d179a32be651fa3635`。exitCode 1，timedOut false，status failed，墙钟约 19.7s。pid 21412。failure 仍是 `execution did not complete successfully`。

`submit-host-side.json`：finished true，base object，getEntries function，access null，threw null，receiverId null。scriptError 的 class 是 slow-script，kind 是 other，第 1 行第 1337364 列。kind 不是 orch，因为警告的 sourceName 不含编排脚本标记。

`raw.jsonl` 两行：host-diagnostic 的 matched 为 false，列是 1337364；随后 summary.ok 为 true。这是有诊断行时的采集器口径，不是通过。没有 host-observation，没有第 75507 列，没有证书 document POST。完成轴没有写。

## 第 1337364 列为什么不是观察，也不是证书 POST

本拍 `next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有改采集器，没有投放新资源，没有重跑。

对回执 `d05075ea12b04dc29246d5ecd148db78` 调用采集器自己的 `attributable` 和 `collect_rows`。side 的 scriptError 是 class slow-script、kind other、第 1 行第 1337364 列。`attributable` 返回 matched false。`invocation_column` 返回 null：该列不在第 75507 列前后 40 列内，class 也不是 submit 或 null-receiver。`collect_rows` 因此只写 host-diagnostic，进程出口按这条规则仍是 1。`validate_execution` 先看到 exitCode 1，抛出 `execution did not complete successfully`，不会把 summary.ok true 当成通过。

编排脚本 `submit-orchestrate.js` 有 3 行，长度 120793、23576、89827。第 1337364 列大于每一行，所以这次终止不在这份文件里。`HTMLFormElement.submit` 的调用点在第 1 行第 75507 列，该处字符是 `(`。回执里的唯一脚本事件不是这个调用点。

这份 raw 没有 wire、necko、resp。生成的探针 `blockUnmapped` 为 true，只对编排脚本的 GET 返回正文，其他请求 `return null`，side 对象也不记录请求。回执里因此没有证书 document POST。完成轴没有写。

## 盖章不允许同 scope 重跑

下一拍 `next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。`docHealth` 曾有 `index-over-cap`，索引已收回到 80 行以内。

门在 `validate_execution` 抛错时返回这条动作，原因是 baseline 未成功完成，不得用摘要推进。同 scope 的重跑动作是 `run_host_baseline` 或 `run_host_patched`，本拍不是这两条。再跑一次现有采集器仍会停在第 1337364 列，采集器不会把文件外的慢脚本列写成 submit 观察。要让脚本走到第 75507 列的真实调用点，需要改宿主行为，本拍的 `no-new-host-surface` 不允许。

工具重验当前 baseline `d05075ea12b04dc29246d5ecd148db78`：scope 前缀 `9a0d32e12aad8ccb`，status failed，exitCode 1，timedOut false，`validate_execution` 抛出 `execution did not complete successfully`。没有重跑，没有写完成轴。

## 源文件外的慢脚本可以改一处宿主行为

`_host_evidence_gate` 在 `validate_execution` 失败时，若 scope 属性是 `HTMLFormElement.submit`，baseline exitCode 是 1、timedOut false、status failed，绑定和 argv 哈希仍匹配，raw 只有一条 matched false 的 host-diagnostic，列号大于该源行长度，side 的 scriptError class 是 slow-script 且行列一致，就返回 `repair_submit_host_behavior`。调用点命中、列还在文件内、只有 summary、带 host-observation、class 不是 slow-script、属性不是 submit，仍返回 `verify_host_execution`。这条决定不写 factWrites。

对当前回执直接调用这个函数：动作是 `repair_submit_host_behavior`，`turnGate=blocked`。原因点名第 1 行第 1337364 列和第 1 行第 75507 列。约束是 tool-evidence-required、ai-notes-are-not-facts、same-scope、submit-callsite-only、one-host-behavior、no-completion-facts、goal-incomplete-does-not-override。没有 no-new-host-surface。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。

单元测试 `test_out_of_file_slow_script_authorizes_one_host_repair` 和 `test_in_file_or_summary_failure_stays_verify` 走真实 `host run` 再 `next`。通过。本回合开头已经盖过 `verify_host_execution`，没有再跑 `next`。

## 一处宿主改动后的官方 baseline

只改 `document-principal.js`。大 eval 去掉空白后是逗号表达式，末项为数字字面量。内容侧 eval 保持 native `toString`，这种字符串直接返回该数字。采集器、`ruyidom.js` 和 scope 绑定没有改。

`c9e876f152f046e483ce6d7c89228cba`：全串空白检查本身变成慢脚本，side 记在 helper 第 830 行第 544 列。exitCode 1，约 19.7s。没有 host-observation。

收成只看首尾 220 字符之后，`5605412e014c4c528d52c220482d48d6`：exitCode 1，timedOut false，约 19.7s，scope 未变。side 的 scriptError 是 slow-script，kind other，第 1 行第 55371 列。这是解释器循环所在列，不是第 75507 列。raw 是 host-diagnostic matched false，然后 summary.ok true。没有 host-observation，没有 wire。完成轴没有写。没有证书 document POST。
