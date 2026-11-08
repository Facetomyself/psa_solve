# 2026-10-21 performance.timeOrigin 跟随重定原点

`repair_submit_host_behavior` 这一拍 `turnGate=blocked`。只改了页面 `performance.timeOrigin`。沙箱 `Date.now` 重读 `cITimeS`、`now` 的 12 小时重定、XHR、PerformanceObserver、`getEntries` 和脚本时限都没改。时限仍是 13，真 eval 仍在，`__watchEval` 没有打开。没有写完成轴。

上一回官方 baseline `8904782b90314eb2be3795545231861a` 已经把 `clockAnchor` 记成 `anchored`，诊断仍是第 1 行第 1337365 列。官方路径没有打开 `__watchEval`，所以 `enter`、`leave`、`now`、`digest`、`random`、`worker`、`raf` 都是 0，`hits` 是空的。这不能说明那些调用没有发生。能看见的仍是 `entries`=1、`observe`=1，以及锚定的时钟。

`performance.now` 在 `Date.now` 比已捕获原点早过 12 小时时会把内部原点改到当前读数。`timeOrigin` 原先是安装时写下的数字，重定之后不跟着变。这一回安装体里的 `align` 同时给定 `now` 和 `timeOrigin`。读取 `timeOrigin` 时，超差就重定再返回原点；12 小时以内的回退不重定。`timeOrigin` 装成这个函数的 getter。安装时返回的 `origin` 仍是当时的快照。

helper sha256 `ba123bf572d050476f555a0157e4f30a7311ab6f78178eff0001adbcc36f20b1`。scope 重签为 `1ec81e7b3804df06f3db52e3a2418c42ea065b05ec4dcdacc36ca261460e1db6`。上一回 scope `e6034c78cc971cd3caf9fa46d8808ac195dc226d4ee33b192e6b19831c7ca55b` 与 baseline `8904782b90314eb2be3795545231861a` 留在 priorScope。runner 与 Gecko 锁定哈希未变。

官方 baseline `b882fe520cb24afeaebd7bae4649a1ed`：exitCode=1，timedOut=false，约 22.71 秒。诊断是第 1 行第 1337365 列，kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`，matched false，base=`object`。raw 225 字节，与 `8904782b90314eb2be3795545231861a` 字节相同。事件只有 `host-diagnostic` 和 `summary`。侧记 `clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-installed`，`clockAnchor`=`anchored`。`entries` 仍是 1，`observe` 仍是 1。

慢脚本列仍是 1337365，不是 `HTMLFormElement.submit` 的第 75507 列。没有证书 document POST 行，也没有同租约回读行。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
