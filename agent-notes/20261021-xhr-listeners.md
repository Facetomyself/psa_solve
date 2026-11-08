# 内联 XHR 同时通知监听器

2026-10-21。回执 `e352216956a24bf2936f55ad78deb7e4` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

平台 `XMLHttpRequest.send` 会通过 `on*` 和 `_listeners` 分发 `readystatechange`、`load` 或 `error`，然后再分发 `loadend`。helper 换掉 `send` 之后，`finish` 只调用了 `onreadystatechange`、`onload`、`onerror`，没有事件对象，也没有 `addEventListener` 和 `loadend`。这一回 `xhrNotify` 按状态发这些事件。`xhrDispatch` 调用属性处理，再调用 `_listeners` 里的函数和 `handleEvent`。单个处理抛错不再挡住同一次事件的后续监听。`finish` 仍由页面 `setTimeout(0)` 在 `send` 返回后执行。缺状态、0 和负数仍写成 0。状态大于等于 200 仍是 `load`，状态 0 仍是 `error`。脚本时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。

`test_shipped_xhr_finish_waits_until_send_returns` 抽出已发布的 `xhrNotify` 并执行。状态 404 的顺序是属性 `readystatechange`、属性 `load`、函数监听、`handleEvent`、属性 `loadend`、`loadend` 监听。抛错的 load 监听没有挡住 `loadend`。状态 0 是属性 `error`、error 监听、`loadend` 监听。状态 100 只有 `readystatechange` 和 `loadend`。原有 9 个状态样本和 6 个事件名样本仍通过。调度顺序仍是先 `0`，执行排队函数后才是 `finish`。

helper sha256 `b364ef41d657b024e214dc93a1f1768824cd3ca904d57be6fa9321dbdd2a2e72`。scope `164feeb9db17370e96a7195a83a0583a7a057e640443f130884be9857ec58416`。priorScope 是 `e8ac28cf46e5370965b973c7e4555c19850781fcfef10b650841615756390e0b`，其中 baseline 是 `e352216956a24bf2936f55ad78deb7e4`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `869824e67a524e90ab47ab86016fd64b`：status=failed，exitCode=1，timedOut=false，墙钟约 22.728s。失败原因是执行未成功完成。raw 事件是 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。side 是 base=`object`，finished=true，getEntries=`function`，threw 为空，variant=`baseline`。host-observation 为 0。`iframe-parent.json` 是 iframeParentConnected=`yes`，enter/leave/largeEnter/largeLeave/lastLargeLen/now/digest/random/worker/raf 都是 0，entries=1，observe=1，hits 和 hashes 为空。

这回 raw 与 `e352216956a24bf2936f55ad78deb7e4` 字节相同，长度 225。这次没有同一 eval 的进入、返回和 realm 记录。列号只记慢脚本落点，不是观察，也不能说明 eval 已返回。调用点仍是第 75507 列。

采集器 raw 不记 wire、necko、resp，也没有同租约回读行。没有请求事件行，所以没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已经发生。没有请求事件行也不是“没有发生网络”的证明。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
