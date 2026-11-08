# 2026-10-21 沙箱时钟重读 cITimeS

`repair_submit_host_behavior` 这一拍 `turnGate=blocked`。只改了沙箱时钟。页面 `challengeDateInstallBody`、`performance.now` 的 12 小时重定原点、XHR、PerformanceObserver、`getEntries` 和脚本时限都没改。时限仍是 13，真 eval 仍在，`__watchEval` 没有打开。没有写完成轴。

沙箱全局先于页面选项出现。`installSandboxClock` 用该全局自己的 `Function`，把页面窗口传进安装函数。每次 `Date.now` 再读 `cITimeS`，顺序是本全局、页面窗口、`parent`、`top`。秒值大于 1000000000 且与墙钟相差超过 43200 秒时，返回该秒的毫秒值，并把 `__clockAnchor` 写成 `anchored`。选项还不存在时不写 `live`。`rememberPageClock` 见到任一全局的 `anchored` 就记 `anchored`，即使页面窗口上先有 `live`。

helper sha256 `ece3c904a2b0a48ae41bc31775e73287a2c698a7f32bb37dcaa8a769ab014bc7`。scope 重签为 `e6034c78cc971cd3caf9fa46d8808ac195dc226d4ee33b192e6b19831c7ca55b`。上一回 scope `60ea952d016863dc0ccac1b34990d1e549ca21310406dea91903897d690987ce` 与 baseline `c33e6a1bafaa4b4ba5a624ffc3c17498` 留在 priorScope。runner 与 Gecko 锁定哈希未变。

官方 baseline `8904782b90314eb2be3795545231861a`：exitCode=1，timedOut=false，约 22.7 秒。诊断是第 1 行第 1337365 列，kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`，matched false，base=`object`。raw 225 字节，与 `c33e6a1bafaa4b4ba5a624ffc3c17498` 字节相同。事件只有 `host-diagnostic` 和 `summary`。侧记 `clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-installed`，`clockAnchor`=`anchored`。`entries` 仍是 1，`observe` 仍是 1。

慢脚本列仍是 1337365，不是 `HTMLFormElement.submit` 的第 75507 列。没有证书 document POST 行，也没有同租约回读行。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
