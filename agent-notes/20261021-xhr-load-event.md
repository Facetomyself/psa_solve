# XHR 的 HTTP 完成走 onload

2026-10-21。回执 `9d5ad8f983f04af599232c184804181a` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

`xhrLoadEvent` 在状态大于等于 200 时返回 `load`，状态 0 时返回 `error`，其余返回 `none`。`finish` 按这个结果调用 `onload` 或 `onerror`。404 和 500 现在走 `onload`。状态 0 仍走 `onerror`。`finish` 仍由页面 `setTimeout(0)` 在 `send` 返回后执行。缺状态、0 和负数仍写成 0。脚本时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。

`test_shipped_xhr_finish_waits_until_send_returns` 抽出已发布的 `xhrLoadEvent`。0、200、304、404、500、100 的结果是 `error,load,load,load,load,none`。状态样本仍是 9 个。调度顺序仍是先 `0`，执行排队函数后才是 `finish`。

helper sha256 `c01b15ab0625afbde63a1365d4910e3357acfe0667125f841dca7b71c011f3ef`。scope `ada41886c98ad313156b3282c295df2bf090d4aacca2d9cea2f8325b916c25f0`。priorScope 是 `9b4494a4317fb4a0a4597b877dd1c0de7d9929a63b726667671f0d4121bf9269`，其中 baseline 是 `9d5ad8f983f04af599232c184804181a`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `ede2f9817e5b4ae993accaa8a61d4d14`：status=failed，exitCode=1，timedOut=false，墙钟约 22.519s。失败原因是执行未成功完成。raw 事件是 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。side 是 base=`object`，finished=true，getEntries=`function`，threw 为空，variant=`baseline`。host-observation 为 0。`iframe-parent.json` 是 iframeParentConnected=`yes`，enter/leave/largeEnter/largeLeave/lastLargeLen/now/digest/random/worker/raf 都是 0，entries=1，observe=1。

这回 raw 与 `b048030da1eb4576aa72793adf2f2cff` 字节相同，长度 225。上一回官方落点是第 55371 列。这次没有同一 eval 的进入、返回和 realm 记录。列号只记慢脚本落点。调用点仍是第 75507 列。这列没有写成观察。

采集器 raw 不记 wire、necko、resp，也没有同租约回读行。没有请求事件行，所以没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已经发生。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
