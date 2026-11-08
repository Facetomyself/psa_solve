# 2026-10-22 页面窗口数字 length

`web_case.py next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T00:47:01Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。约束含 `same-scope`、`one-host-behavior`、`submit-callsite-only`、`no-completion-facts`。这一拍没有再跑 `next`。

同一处宿主行为写在已有的 `installChallengeClock` 和 `installSandboxClock`。页面窗口的写入放在 `waiveXrays` 之后、提前返回之前。两边都用 `Object.defineProperty` 把 `Number.prototype.length` 设为 0。没有新函数，没有改 `dom.max_script_run_time`，没有改编排脚本。

helper sha256 `5c1b806e797e82a1522c0fd3a04f1e61dbd7cf0cfb37f30609b9f8830838842c`。scope 重签为 `560298f21934597d7d80c4053d8bdc91a8a12721e40e71fa9d24d41fd91db50e`。`c54954da9227aae50af956ec0145f80dedd71ccb3b5670083849c821e67e3313` 与 baseline `5a175cf8749a48258a04caa3041007cf` 留在 priorScope。`load_scope` 通过。

官方 baseline `8abdfc23a61142a2ace10d0bc9ed4d09`：pid 14392，exitCode 1，timedOut false，耗时 22720002400 ns，失败原因是执行未成功完成。诊断仍是第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`，没有 errorName，没有接收者字段。raw sha256 `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha256 `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。事件仍是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。

这一处写入没有让诊断离开第 55371 列，也没有到第 75507 列。没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。
