# 2026-10-22 页面窗口内的 length 仍停在第 55371 列

今早 08:19 的审计认为上轮 side 绑定、receiver 的 unknown/empty 分型、Location/contentWindow/window 默认隔离已经落地。Debugger 观察后释放也在。submit 没有出现。新偏差是默认 helper 把 `xdiN1`、`SSvM5`、`xPLd9` 填成空函数。这三项现在仍在默认安装路径上。本笔记不把它们写成已恢复的宿主合同。

`web_case.py next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T00:51:17Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。上一发在特权侧 `defineProperty` 没有离开第 55371 列。这一处只改 `installChallengeClock`：赋值放进页面窗口自己的 `Function`，把 `Number.prototype.length` 写成 0。沙箱里的 `defineProperty` 没动。没有新函数，没有改 13 秒时限，没有改编排脚本。

helper sha256 `691635adc94185a44536dd02b2a3e210789f273911653ad85acb5144724797ee`。scope 重签为 `81b6ff83266bbab04448a816c44fabf92c27bbc0613eacc83a175dd7542bda92`。`560298f21934597d7d80c4053d8bdc91a8a12721e40e71fa9d24d41fd91db50e` 与 baseline `8abdfc23a61142a2ace10d0bc9ed4d09` 留在 priorScope。`load_scope` 通过。

官方 baseline `42fc0fca8bfd4b199850246006053bd3`：pid 15676，exitCode 1，timedOut false，耗时 22986052000 ns。诊断仍是第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`，没有 errorName，没有接收者字段。raw sha256 `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha256 `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。与上一发相同。事件仍是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。

没有到第 75507 列。没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。这次列号不是求解进度。
