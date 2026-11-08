# 2026-10-22 sandbox Function pad baseline

官方 baseline `ae4b837fc029499ca1b99ecc9fa439f5` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。raw 与 side 和上一发字节相同。

这一处只在现有 `_sb` 包装里调用 `installLeadingPadFunction(sb)`，用已有的 `leadingPadSource` 包住该沙箱的 Function 构造器。短脚本不裁。`padText`、页面窗 Function 包装、worker 无 document 分支都没有改。

- helper `7c0173773578e273003e011cb8c1477e4f9aaab00e965f76195195baf838c30e`
- scope `b0e94d1822a51e47148ff82ce830525e4092317eacd043a908e253fb1c6a0afb`
- exec `437e20ce0381bf99f6db1e174de9d3b4c09126c0e68eef3edd8ec1ac2e248bf6`
- pid 48012，耗时 22720061200 ns，exitCode 1，timedOut false
- 盖章 `verify_host_execution` / `blocked` / `2026-10-22T04:51:11Z`
- 含 `no-new-host-surface`。不得再发未点名的宿主修复
- 完成轴保持 false
