# 2026-10-22 page-window Function pad named

baseline `9a2d0ab3f80147ab83ff13ab2d0bc58b` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。页面窗调用、沙箱调用、删掉 document 早退、以及 `padText` 直接 `return via` 都没有改变 raw/side。

超时脚本的 sourceForm 不是 `eval`。已有的 `installLeadingPadEval` 包不到它。side 上观察到的属性名是 `Function`，接收者类是 `Window`。

下一处只允许在页面文档替换里、紧挨 `installLeadingPadEval(this.window)` 调用 `installLeadingPadFunction(this.window)`。这个新函数只用已有的 `leadingPadSource` 包住该窗的 Function 构造器。短脚本不裁。不得改 `padText`，不得改 eval 包装的调用点，不得在 worker 的无 document 分支调用它。

- helper `c0a334eeb869138388362eeb2a2f0bb1d290e0aeb46fc932a9f718d6ab51c4e0` 未改
- scope `c454797a825165ecb4660363b0f7593bed5d21d70760cbdf2845320c6041e8e9` 未重签
- 盖章 `repair_function_leading_pad` / `blocked` / `2026-10-22T04:25:57Z`
- 完成轴保持 false
