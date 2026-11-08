# 显式同步 XHR 在 send 返回前完成

`repair_submit_host_behavior`，`turnGate=blocked`。只改了 `scheduleXhrFinish` 对异步标志的处理。

平台 `open` 把 `async !== false` 记到 `_async`，但 `send` 不读它。helper 的 `send` 以前一律 `setTimeout(0)`。现在 `_async === false` 时，`finish` 在 `send` 返回前运行，`readyState`、状态和 `load`/`error`/`loadend` 都在这次调用里发生。缺省以及 `_async !== false` 仍交给页面 `setTimeout(0)`，计时器抛错时不补同步调用。状态缺省、0 和负数仍是 0。大于等于 200 仍是 `load`，只有 0 是 `error`。脚本时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。

`test_shipped_xhr_finish_waits_until_send_returns` 跑了已发布的 `scheduleXhrFinish` 和 `send`。显式 `false` 在返回前写到 readyState 4 并调用 `onload`。`true` 和缺省 `_async` 在返回时仍是 readyState 1，只有排队函数执行后才完成。stdout：`xhr-ok 9`，`xhr-event-ok 6`，`xhr-listen-ok 6`，`xhr-async-ok 2`，`xhr-send-ok 3`。

helper sha256 `90d4ad6c8060ab3f1571a2affa3affdbf1000d0b4de306927aafca0e5f41dc4c`。scope 重签为 `8ed7e127a4352a7ff940147fd5c2f41b0202a7950f1c7f419329857f1d164a62`。`164feeb9db17370e96a7195a83a0583a7a057e640443f130884be9857ec58416` 与 baseline `869824e67a524e90ab47ab86016fd64b` 留在 priorScope。runner 与 geckoLib 哈希未变。

官方 baseline `e9251003e0514f5d8dd6b4d39debe9fd`：exitCode=1，timedOut=false，约 22.725s。诊断是第 1 行第 1337365 列，kind=`other`，sourceForm=`token`，matched false，没有写成观察。raw 225 字节，与 `869824e67a524e90ab47ab86016fd64b` 字节相同。`observe` 仍是 1，`entries` 仍是 1。采集器不记 wire、necko、resp。没有请求事件行，也没有同租约回读行。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。调用点仍是第 75507 列。列号只记慢脚本落点，不说明这次 eval 已返回，也不说明没有网络活动。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
