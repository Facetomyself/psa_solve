# 2026-10-22 page-window Function pad baseline

官方 baseline `8fbf4db77e7b48aba1790b0c2fe9b57a` 仍停在第 1 行第 1337365 列，sourceForm 仍是 `token`。raw 与 side 和上一发字节相同。

这一处只在页面文档替换里调用 `installLeadingPadFunction(this.window)`，用已有的 `leadingPadSource` 包住该窗的 Function 构造器。短脚本不裁。`padText`、eval 包装调用点、worker 无 document 分支都没有改。

- helper `89a3e7fe850562478afdf384ddb1413751058896e2d93163c985f70d16d8a7e4`
- scope `f4a6114730f212654f39227e1cdf2d99a77ab66a703fc3ad564cb9e9f1c8712b`
- pid 56056，耗时 22717762400 ns，exitCode 1，timedOut false
- 盖章 `verify_host_execution` / `blocked` / `2026-10-22T04:36:42Z`
- 含 `no-new-host-surface`。不得再发未点名的宿主修复
- 完成轴保持 false
