# d3ec59e2 为何 exit 1 且没有 side

2026-10-21。`next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。回执只解开这一支：`validate_execution` 失败后 `_out_of_file_slow_script` 返回空，所以不是 `repair_submit_host_behavior`。没有改 helper，没有重跑，没有写完成轴。

`host_submit_collector.py` 的 `collect_rows` 只在 side 能解析出脚本错误时先写一行，再写 summary。`ok` 等于这之前有没有行。没有 side 时 raw 只有 `{"event":"summary","summary":{"ok":false}}`。`main` 在没有 `host-observation` 时返回 1。这就是回执里的 exitCode 1，不是采集器 25 秒击杀。

墙钟 19.708 秒，低于采集器 25 秒期限，也低于 CLI 的 70 秒。循环是因为 Node CLI 自己退出。CLI 在引擎进程结束且 stdout 没有 JSON 结果行时抛出并返回 1。探针只在 `new RuyiDOM` 返回之后才 `writeJson`。构造器没有 try/finally。控制台监听只对非 warning、行号不小于 1 的脚本错误写 side。

对照 `b841fe67`：墙钟 25.131 秒，是采集器击杀仍活着的 CLI。它的 stderr 留下两次 worker 进入 DoRunLoop，以及内容脚本超时。side 和 diagnostic 都在。这次 16:29 的 CLI 目录已被正常 finally 删掉，说明 Node 走完了失败收尾。留下的 profile `C:\Users\mengma\AppData\Local\Temp\ruyidom_4ee0d4c919834d38a7be73ca46cde24b` 时间是 16:29:27。`finalizeFromFiles` 只在 JSON 解析失败时于删除 profile 之前返回。该目录没有 minidump。16:28–16:32 的 Application 日志没有事件。

因此引擎在构造器返回前自己结束，side 没机会写出。hook 里的 `installWorkerGlobalClock` 对 JS 异常有 catch，单靠那里的可捕获异常到不了 `RuyiDOM.exit`。进程结束符合 `RuyiDOM.main` 拒绝后 `TerminateProcess`，或引擎直接中止；现有文件分不出这两条。和上一份能写出 side 的回执之间，helper 多出来的行为只有无 document 且带 `importScripts` 的新全局会在 `onNewGlobalObject` 里安装 Date。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
