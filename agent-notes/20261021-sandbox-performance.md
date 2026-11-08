# 2026-10-21 沙箱 performance 对齐

`repair_submit_host_behavior`，`turnGate=blocked`。同一 scope 只改了一处宿主行为：文档全局在沙箱 `Date` 安装之后，把该全局已有 `performance` 的 `now` 和 `timeOrigin` 换成页面同一段对齐函数。没有改页面 `wrapped` 里的安装，没有改 XHR、`Date` 重读、脚本时限、采集器或 `ruyidom.js`。时限仍是 13。真 eval 仍在。`__watchEval` 没有打开。没有写完成轴。

保存的页面 `/fo/` 第 1 行 106880 字符，cloudflare `/fo/` 第 1 行 798108 字符，编排脚本第 1 行 120793 字符，turnstile iframe 第 1 行 258319 字符。这些行都不含第 1337365 列，也不含这串数字。慢脚本 sourceForm 是 `token`，所以来源名不是带 `://` 的 FO 地址。这一列仍是运行时填充 eval 的看门狗末列。

官方 baseline `b841fe67bcbd47f8982e21bfbfbdcc02`。scope `5ec1558628e5f8014ec1b9ccfe11f052648120fcaa9ce7b5b4aebef456621b69`。helper sha256 `9b3566a722458a62ae967d70e72c151e2a981e931aecafd1dee473e544c1a29c`。上一回 `1ec81e7b3804df06f3db52e3a2418c42ea065b05ec4dcdacc36ca261460e1db6` 和 baseline `b882fe520cb24afeaebd7bae4649a1ed` 留在 priorScope。exitCode=1，timedOut=false，约 25.1s。诊断是第 1 行第 1337365 列，kind=`other`，sourceForm=`token`，matched false。raw 225 字节，与上一回字节相同。事件只有 `host-diagnostic` 和 `summary`。没有证书 document POST 行，没有同租约回读行。

侧记 `perfAligned`=`yes`，`clockAnchor`=`anchored`，`clockResource`=`sandbox-installed`，`entries`=1，`observe`=1。`iframe-parent.json` 在 `perfAligned` 后面多了一个引号，值仍是 `yes`。官方计数仍是 0，因为 `__watchEval` 关闭。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
