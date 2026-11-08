# 2026-10-22 官方 baseline 重跑离开第 80263 列

绑定 scope `2650dcba2b133020ea31aab1dfc7693547af903ccfe51ddc69068af79ec2acbc`，helper `6ad5ffb19ea7d746588f7ac4a8e604c8bb9c5bb8b98895f62455b4822eed0a0d`。上一代 scope 仍是 `fec6b910f1c99398455d3ac59f6a74c4c6af9307232c09be2bc43fe2b62f4ad5`，baseline `860cec79c89140578e7bd698efddd70f`。`installSandboxClock` 没有改。文档沙箱上的 `xPLd9` 仍由该沙箱自己的 `Function` 构造。Window 标记仍只安装 `xdiN1` 与 `SSvM5`，调用次数仍是 1。

同一 helper 的官方重跑是 `e33f35e4e6044dc7ae37af85fb92c6ac`。进程 58700，耗时 25135465200 ns，未超时，exitCode 1。终态是源文件内第 1 行第 30458 列的慢脚本：`kind=other`，`class=slow-script`，`sourceForm=token`，`sourceClass=other`。没有 errorName，side 上没有 receiverState。`j5` 进入 22904 次。`jj` 仍是 11 次，第 2 次进入的 callee 仍是沙箱上的 `xPLd9`。异常展开仍经过第 1 行第 76867 列。`servedScripts` 是 2，`blockedScripts` 是 0。raw 只有 `host-diagnostic` 与 `summary`，`matched` 是 false。没有证书 document POST，也没有同租约回读。

上一张回执 `5c2db54083b14c2c86c6a5b808c9a31e` 仍在盘上，已经不是绑定指针。它停在第 3 行第 80263 列。那一列的记号 `j` 是本地递减，不是宿主 API。这次重跑没有停在那一列。第 30458 列不是已放行的第 55371、75507、76877、98085 或 80263 列。本拍没有加宿主面。

`web_case.py next` 的新印是 `verify_host_execution` / `blocked` / `2026-10-21T21:46:52Z`，约束仍含 `no-new-host-surface`。完成轴保持 false。
