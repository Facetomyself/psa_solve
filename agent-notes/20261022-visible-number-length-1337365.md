# 2026-10-22 可见的 Number.length 停在源文件外第 1337365 列

`next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T02:08:32Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。原因是源文件内第 1 行第 55371 列，调用点仍是第 1 行第 75507 列。约束含 `one-host-behavior`。本拍没有再 `next`。

第 55371 列的 `for` 条件在旋转 398 次后读取 `length`，再和数字 0 做 `!==`。同一段初始化用 `fill(0)` 的返回值写进实例上的单字符字段。数字的 `length` 走 `Number.prototype`。`installSandboxClock` 原来用特权 `defineProperty`，页面脚本看不见。页面窗口那条已经在自己的 `Function` 里写过，官方停点仍是第 55371 列。这一处只把沙箱和新全局那条改成同一个全局自己的 `Function` 赋值。没有第二处 length 写入，没有装回空函数，没有安装 `xPLd9`，没有改 13 秒时限，首尾空白包装还在。

helper sha256 `8c9c9f33fe0eb47ded23fd273bc2d5ba4554bcc064f38242e995dc4786e6725c`。scope 重签为 `692ddc40cbf0345d56fa0ddc5e146e664d0e700411b9913e1e20585e88df7866`。`8626c40c322aba3a01351495dff986d3cd4e073c0df11c46807e2e2f8f2c54fb` 与 baseline `8758d438996c4bb7af99c2c33959d13e` 留在 priorScope。

官方 baseline `53d3ee5ee6e74d7bacd6d18a920ce07b`：pid 46588，exitCode 1，timedOut false，耗时 24731361900 ns。诊断离开第 55371 列，停在源文件外第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。没有 errorName，没有接收者字段。raw sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，225 字节。side sha256 `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`，642 字节。与 publish-forward 那次源文件外回执相同。`summary.ok` 不是 `serverAccepted`。

没有到第 75507 列。没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
