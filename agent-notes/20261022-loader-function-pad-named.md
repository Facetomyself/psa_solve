# 2026-10-22 loader Function pad named

官方 baseline `ae4b837fc029499ca1b99ecc9fa439f5` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。页面窗和沙箱的 Function 构造器都已经用 `leadingPadSource` 包过，同一列没有离开。

下一处只允许在有 document 的新全局分支里、紧挨 `installLeadingPadEval(raw)` 调用 `installLeadingPadFunction(raw)`。短脚本不裁。不得改 `padText`，不得改页面窗和沙箱包装，不得在 worker 的无 document 分支调用它。

- helper 仍是 `7c0173773578e273003e011cb8c1477e4f9aaab00e965f76195195baf838c30e`
- scope 仍是 `b0e94d1822a51e47148ff82ce830525e4092317eacd043a908e253fb1c6a0afb`
- 本拍没有改 helper，没有重签，没有新的官方执行
- 盖章 `repair_loader_function_leading_pad` / `blocked` / `2026-10-22T05:01:35Z`
- 完成轴保持 false
