# 2026-10-22 loader Function pad baseline

官方 baseline `9c7ea1fbdc0d4dcaa7dd191158a24c1d` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。raw 与 side 和上一发字节相同。

这一处只在有 document 的新全局分支里调用 `installLeadingPadFunction(raw)`，用已有的 `leadingPadSource` 包住该全局的 Function 构造器。短脚本不裁。`padText`、页面窗包装、沙箱包装、worker 无 document 分支都没有改。

- helper `543b22003f008fe8fc07e93230bbb14c7b4a4ea1075aa9c61e053a924ac69170`
- scope `f6a91ef0959d48e37cae4a21ac27fd5dda9198f09b99884e71e0099026c2d1e4`
- exec `9d55dcd4f14f53286203fecc90ebffbb8a1a879e2f189b76e99fb12725dd39ff`
- pid 38636，耗时 24730410100 ns，exitCode 1，timedOut false
- 盖章 `verify_host_execution` / `blocked` / `2026-10-22T05:08:16Z`
- 含 `no-new-host-surface`。不得再发未点名的宿主修复
- 完成轴保持 false
