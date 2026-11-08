# 2026-10-22 点名沙箱 eval 的自身标记

盖章 `repair_sandbox_eval_own_flag` / `blocked`，updatedAt `2026-10-22T07:22:18Z`。helper 没有改，scope 没有重签，没有新的官方执行。

官方 baseline 仍是 `13e79448ee6a4d55b6dff4d705bdfa0b`，停在源文件外第 1 行第 1337365 列。同一张 side：第 55373 列的调用实参是原始数字，`lengthSource` 是 `call-argument`。慢脚本 `compileEntry` 是 `eval`，`compileRealm` 是 `Sandbox`，`compileMatch` 是 `source`。

`installLeadingPadEval` 开头用 `host.__leadingPad` 判断。沙箱的原型是页面窗，页面窗已经有这个标记，所以 `installLeadingPadEval(sb)` 在包上 eval 之前返回。沙箱里的 eval 仍是原来的编译入口。

下一处只允许把这个判断改成 `Object.prototype.hasOwnProperty.call(host, "__leadingPad")`。不得新增包装，不得改裁剪谓词，不得改 `leadingPadSource`，不得改构造器赋值，不得在无 document 分支新增调用。完成轴保持 false。
