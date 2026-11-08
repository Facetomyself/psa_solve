# 2026-10-22 Function 原型构造器已点名

`next` 盖章 `repair_function_prototype_constructor` / `blocked`，updatedAt `2026-10-22T06:23:49Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

官方 baseline 仍是 `5c3f17cbcf0d4eefa23ba7ebef89787f`，第 1 行第 1337365 列，sourceForm `token`。raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`。helper sha256 仍是 `c5243aebccc7b87d7b65e5d264cf8159c87b7126ef054621113cf79bda5c75b0`。scope 仍是 `b183fa222b5a4468a744f32e1815622d5d41de7f4bdd3d569ccb0a906460badb`。

绑定的 side 只有已有的采样计数，没有 `worker` 字段。内容区 eval 已经调用 `trimInCompartment(code);`，Function 体已经调用 `trimInCompartment(body);`。这两处都没有离开第 1337365 列。

包装函数执行 `fn.prototype=RealFunction.prototype`，因此 `prototype.constructor` 仍是原来的构造器。经它编译的脚本文件名归成 `token`，并且不进入 `trimInCompartment(body);`。helper 里还没有 `RealFunction.prototype.constructor=fn`。

下一处只允许在 `installLeadingPadFunction` 里 `new host.Function` 的函数体中，紧挨 `fn.prototype=RealFunction.prototype` 写上 `RealFunction.prototype.constructor=fn`。不得改裁剪谓词，不得改 `leadingPadSource`，不得改 eval 包装，不得新增调用点，不得改 `installLeadingPadEval(raw)` 和 `installLeadingPadFunction` 的调用点，不得在 worker 的无 document 分支调用 `installLeadingPadEval` 或 `installLeadingPadFunction`。

本拍没有改 helper，没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
