# 2026-10-22 sandbox Function pad named

baseline `8fbf4db77e7b48aba1790b0c2fe9b57a` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。页面窗的 `installLeadingPadFunction(this.window)` 没有改变 raw/side。

超时脚本的 sourceForm 不是 `eval`。页面窗的 Function 构造器已经包过。现有 `_sb` 包装只调用了 `installLeadingPadEval(sb)`，没有调用 `installLeadingPadFunction(sb)`。

下一处只允许在这个包装里、紧挨 `installLeadingPadEval(sb)` 调用 `installLeadingPadFunction(sb)`。只用已有的 `leadingPadSource`。短脚本不裁。不得改 `padText`，不得改页面窗的 Function 包装，不得在 worker 的无 document 分支调用它。

- helper `89a3e7fe850562478afdf384ddb1413751058896e2d93163c985f70d16d8a7e4` 未改
- scope `f4a6114730f212654f39227e1cdf2d99a77ab66a703fc3ad564cb9e9f1c8712b` 未重签
- 盖章 `repair_sandbox_function_leading_pad` / `blocked` / `2026-10-22T04:46:33Z`
- 完成轴保持 false
