# PerformanceObserver 改回计时器通知

2026-10-21。回执 `c0a92703cc7144cd8b1804fe406c69fc` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

`runObserverNotify` 不再调用 `fireNow()`。它只执行 `armTimer(0)` 和 `armTimer(200)`。计时器回调仍调用 `fire`。`nsITimer` 创建失败且 delay 为 0 时，`arm` 仍会同步调用 `fire`；这次没有改这条失败回退。

`installInlineXHR` 仍在 `send` 返回前写状态并调用页面回调。页内 `performance.now` 保持上一回的安装。脚本时限仍是 13。真 eval 仍在。`setTimeout` 没有替换。`__watchEval` 没有打开。

`test_shipped_observer_notifies_before_timers` 抽出 `runObserverNotify`。正常回调和抛错回调的顺序都是 `0,200`。函数文本里没有 `fireNow()`。stdout 是 `observer-ok 2`。

helper sha256 `3c0f09d36487316d7e0fb9092505e3efb0eed38cd3b8c00a7d5b249611681e72`。scope `f48d1625bd85b5cb8df60cdd89d3697be9aa6590f5be5fceecf22bdbed6a3dd7`。priorScope 是 `cdba75add9baa1b7286992478be2a942daf64b731afc26dc8eb7e7ebde058ce5`，其中 baseline 是 `c0a92703cc7144cd8b1804fe406c69fc`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `1fdcbce6d45044ff9f4dc2d3efd46ccd`：status=failed，exitCode=1，timedOut=false，墙钟约 22.720s。失败原因是执行未成功完成。raw 事件是 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。side 是 base=`object`，finished=true，getEntries=`function`，threw 为空，variant=`baseline`。host-observation 为 0。`iframe-parent.json` 是 iframeParentConnected=`yes`，enter/leave/largeEnter/largeLeave/lastLargeLen/now/digest/random/worker/raf 都是 0，entries=1，observe=1。`observe` 只计 `observe` 被调用一次。这次没有页面回调是否在计时器上运行的记录。

采集器 raw 不记 wire、necko、resp。没有请求事件行，所以没有工具证据证明 FO、XHR、submit 或证书 POST 已发生。调用点仍是第 75507 列。落点与上一回同列。`__watchEval` 关闭，没有同一 eval 的进入、返回和 realm 记录。列号只记慢脚本落点。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列没有写成观察。
