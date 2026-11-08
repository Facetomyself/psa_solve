# XHR 完成改到 send 返回之后

2026-10-21。回执 `1fdcbce6d45044ff9f4dc2d3efd46ccd` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

`scheduleXhrFinish` 只调用传入的 `delay(finish, 0)`。`send` 在处理资源之后不再写 `readyState`，也不调用 `onreadystatechange`、`onload`、`onerror`。这些步骤放进 `finish`，由页面 `setTimeout` 在 0ms 后执行。`setTimeout` 抛错时 `finish` 留在发送栈之外，不补同步调用。`xhrCompletion` 的状态合成没有改：缺状态或状态不大于 0 时仍写成 200。脚本时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。

`test_shipped_xhr_finish_waits_until_send_returns` 抽出 `xhrCompletion` 和 `scheduleXhrFinish`。6 个状态样本仍与原来的合成一致。调度顺序是先记下 `0`，此时 `finish` 还没运行；执行排队函数之后才是 `finish`。`send` 文本里 `finish()` 只出现在函数定义，`onreadystatechange` 在 `function finish` 之后。

helper sha256 `9e5ff08ba8a4351ee9991abaa7cccc9aa01be3d48e15ea9f402deb73754dda30`。scope `e54384443d7acc26fe65b2275186a194550562a620dcbad7f5784bea79fcf65e`。priorScope 是 `f48d1625bd85b5cb8df60cdd89d3697be9aa6590f5be5fceecf22bdbed6a3dd7`，其中 baseline 是 `1fdcbce6d45044ff9f4dc2d3efd46ccd`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `b048030da1eb4576aa72793adf2f2cff`：status=failed，exitCode=1，timedOut=false，墙钟约 22.719s。失败原因是执行未成功完成。raw 事件是 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。side 是 base=`object`，finished=true，getEntries=`function`，threw 为空，variant=`baseline`。host-observation 为 0。`iframe-parent.json` 是 iframeParentConnected=`yes`，enter/leave/largeEnter/largeLeave/lastLargeLen/now/digest/random/worker/raf 都是 0，entries=1，observe=1。

采集器 raw 不记 wire、necko、resp，也没有同租约回读行。没有请求事件行，所以没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已经发生。调用点仍是第 75507 列。落点与上一回同列。这次没有同一 eval 的进入、返回和 realm 记录。列号只记慢脚本落点。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列没有写成观察。
