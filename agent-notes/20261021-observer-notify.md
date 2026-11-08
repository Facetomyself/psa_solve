# 2026-10-21 PerformanceObserver 同步通知

`web_case.py next` 对回执 `8232a2dac3cd46b8a795d876420ce020` 仍是 `repair_submit_host_behavior`，`turnGate=blocked`。这一拍没有再跑 `next`。

上一回内联 XHR 之后，诊断仍是源文件外第 1337365 列，墙钟仍约 22.7 秒。`iframe-parent.json` 里 `observe` 为 1，回调却只挂在计时器上。同一次脚本堆栈里计时器不会跑。这一处只改 helper：`runObserverNotify` 在 `observe` 返回前先调用回调，再保留 0ms 和 200ms 计时器。脚本时限仍是 13。真 eval 保留。`__watchEval` 没有打开。`setTimeout` 没有被替换。采集器、`ruyidom.js`、Node `host-dom.js` 没有改。

helper sha256 `4a26bc865d75a0d112d10bebc8d89be330f98d46475791dda108232036f3b1a5`。scope `9776d304a14379f1fef7ae2ef18fea958b6bd27e253194529374190693f289fa`。priorScope 是 `c9650afd06bd8048`，其中 baseline 是 `8232a2dac3cd46b8a795d876420ce020`。Gecko 五份锁定哈希未变。`load_scope` 通过。

已发布测试 4 项通过：`runObserverNotify` 从 helper 源码抽出，顺序是 `fire,0,200`；回调抛错后计时器仍是 `0,200`。真 eval 和源文件外慢脚本门仍在。

官方 baseline `1adb882440784c2598bfe4e52395139c`：status failed，exitCode 1，timedOut false，墙钟约 22.7 秒。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 55371 列，matched false，base 为 object。side 的 kind 是 `other`，class 是 `slow-script`，sourceClass 是 `other`，sourceForm 是 `token`。编排脚本第 1 行长度是 120793，所以这一列在源文件里面。没有 `host-observation`。证书 document POST 是 0。这列没有写成观察。调用点仍是第 75507 列。父页计数仍是 iframe 已连接、`entries` 1、`observe` 1。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
