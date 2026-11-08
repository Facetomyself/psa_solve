# 页内 Date 成功后不再写回 chrome now

2026-10-21。回执 `ede2f9817e5b4ae993accaa8a61d4d14` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

`installChallengeClock` 在页内构造器替换成功（`host.Date = patched`，`ctorMark` 为 `installed`）后直接返回。返回前不再对安装前捕获的原 `Date` 做 `Object.defineProperty(dateObj, "now", wrappedNow)`。`Patched.prototype` 仍是原 `Date.prototype`，构造器没有改写，所以 `Date.prototype.constructor` 仍是原 `Date`。这次不把 chrome `now` 写到那条路径上。`Patched.now` 仍是页内 `current`，它在安装时记下 `RealDate.now`。替换得到空值、构造器安装抛错，或 `replaceConstructor` 为假时，仍把 chrome `now` 赋给原 `Date`。沙箱的 `installChallengeClock(sb)` 不带替换标志，仍走赋值。`challengeDateInstallBody` 和 `performanceNowInstallBody` 没改。XHR 完成时机、状态和 load 事件没改。`runObserverNotify` 仍只武装 0ms 和 200ms。`nsITimer` 抛错且 delay 为 0 时，`arm` 仍同步调用 `fire`。脚本时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。

`test_shipped_window_date_constructor_uses_challenge_clock` 抽出已发布的 `installChallengeClock` 并执行。构造器安装抛错时，假 `Date.now` 变成带标记的 chrome 函数。不带替换标志的沙箱同样被赋值。页内安装成功时，`page.Date.now()` 是挑战锚点，`Date.now` 和 `Date.prototype.constructor.now` 仍是安装前的函数，且没有 chrome 标记。原有 12 项页内时钟检查仍通过。

helper sha256 `f050bac336fe5b0370c8c6a1fd2b10efa4cca1245ac037888d7ffed23c2e3130`。scope `e8ac28cf46e5370965b973c7e4555c19850781fcfef10b650841615756390e0b`。priorScope 是 `ada41886c98ad313156b3282c295df2bf090d4aacca2d9cea2f8325b916c25f0`，其中 baseline 是 `ede2f9817e5b4ae993accaa8a61d4d14`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `e352216956a24bf2936f55ad78deb7e4`：status=failed，exitCode=1，timedOut=false，墙钟约 22.714s。失败原因是执行未成功完成。raw 事件是 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。side 是 base=`object`，finished=true，getEntries=`function`，threw 为空，variant=`baseline`。host-observation 为 0。`iframe-parent.json` 是 iframeParentConnected=`yes`，enter/leave/largeEnter/largeLeave/lastLargeLen/now/digest/random/worker/raf 都是 0，entries=1，observe=1，hits 和 hashes 为空。

这回 raw 与 `ede2f9817e5b4ae993accaa8a61d4d14`、`b048030da1eb4576aa72793adf2f2cff`、`c0a92703cc7144cd8b1804fe406c69fc`、`1fdcbce6d45044ff9f4dc2d3efd46ccd` 字节相同，长度 225。这次没有同一 eval 的进入、返回和 realm 记录。列号只记慢脚本落点，不是观察，也不能说明 eval 已返回。调用点仍是第 75507 列。

采集器 raw 不记 wire、necko、resp，也没有同租约回读行。没有请求事件行，所以没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已经发生。没有请求事件行也不是“没有发生网络”的证明。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
