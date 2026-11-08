# 2026-10-21 挑战锚点改读 cITimeS

`repair_submit_host_behavior` 这一拍已经盖章，`turnGate=blocked`。没有再跑 `web_case.py next`。只改了挑战时钟读取的秒字段。页面构造器、`performance.now` 的 12 小时重定原点、沙箱 `Function` 安装、XHR、PerformanceObserver、`getEntries` 和脚本时限都没改。时限仍是 13，真 eval 仍在，`__watchEval` 没有打开。没有写完成轴。

保存的页面对象有 16 个字段。秒级时间在 `cITimeS`，是 10 位数字，与当前墙钟相差超过 43200 秒。先前锚点读取的名字不在这 16 个字段里，所以构造器换成 `installed` 之后，`Date.now` 仍返回墙钟。这一回页内 `current` 和 chrome 回退都读 `cITimeS`。超差时把 `__clockAnchor` 写成 `anchored`，否则写成 `live`。`rememberPageClock` 在泵之前读回页面标记；页面标记还不是这两个值时，才读沙箱标记。

helper sha256 `f191405a65e7f4b624699a4d4301abbb31866a7eaad497c4be0d289ed9b8b1a3`。scope 重签为 `60ea952d016863dc0ccac1b34990d1e549ca21310406dea91903897d690987ce`。上一回 scope `56c5660873f731dbf78ad98c5eaef911053404deae8b3734059736df61cb556d` 与 baseline `2cce87b688f34c08bb42f7021e966e81` 留在 priorScope。runner 与 Gecko 锁定哈希未变。

官方 baseline `c33e6a1bafaa4b4ba5a624ffc3c17498`：exitCode=1，timedOut=false，约 22.7 秒。诊断是第 1 行第 1337365 列，kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`，matched false，base=`object`。raw 225 字节，与 `2cce87b688f34c08bb42f7021e966e81` 字节相同。事件只有 `host-diagnostic` 和 `summary`。侧记 `clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-installed`，`clockAnchor`=`live`。`entries` 仍是 1，`observe` 仍是 1。

`performance.now` 的安装发生在页面选项写入之前。那一次 `Date.now` 会把标记写成 `live`。同一全局之后如果读到超差的 `cITimeS`，会改写成 `anchored`。这次标记停在 `live`。页面标记已经是 `live` 时，沙箱上的标记不会再覆盖它。

没有证书 document POST 行，也没有同租约回读行。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
