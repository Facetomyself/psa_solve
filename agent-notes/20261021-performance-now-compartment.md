# performance.now 改在页面内

2026-10-21。回执 `13a5d2e400e74067934b6155d4063651` 上的盖章是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

上一回页内 `Date` 让长度为 1337363 的 eval 返回。看门狗停在源行内第 55371 列，那是编排函数里解释器的 else 分支。循环体和紧随其后的函数都没有字面宿主 API 名。`performance.now` 当时仍由 `Cu.exportFunction` 导出，每次读取都会离开页面。

这一处只改 `now` 的所在区。`performanceNowInstallBody` 交给页面 `Function`，用页面 `Date.now` 计算原点，再调用已有的 `monotonicNow`。`timeOrigin` 使用同一次原点。安装失败时不把 chrome 函数赋上去。`getEntries` 没有改。脚本时限仍是 13。真 eval 仍在。`setTimeout` 没有替换。`__watchEval` 没有打开。

`test_shipped_performance_now_advances_from_date` 抽出 `monotonicNow` 和安装体。5 个差值样本仍是 0、0、40、0、0。页面安装体在原点 5000 上给出 `now` 0、75、0。

helper sha256 `3be5e1e0208f90498b0c7b1597f8e477a4427c049456306c29a88694b75d9443`。scope `cdba75add9baa1b7286992478be2a942daf64b731afc26dc8eb7e7ebde058ce5`。priorScope 是 `2d6dfc952924bfd9`，其中 baseline 是 `13a5d2e400e74067934b6155d4063651`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `c0a92703cc7144cd8b1804fe406c69fc`：status=failed，exitCode=1，timedOut=false，墙钟约 22.713s。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 1337365 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。`getEntries` 仍是 function，`finished` 为 true，`threw` 为空。host-observation 为 0。`iframe-parent.json` 仍是 `observe` 1、`entries` 1。没有证书 document POST。调用点仍是第 75507 列。

页内 `performance.now` 没有让脚本走过第 55371 列。看门狗退回源行外第 1337365 列，长度为 1337363 的 eval 再次没有返回。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 1337365 列没有写成观察。
