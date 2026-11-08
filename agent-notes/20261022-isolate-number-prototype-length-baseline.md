# 拿掉数字原型 length 常量（2026-10-22）

`installChallengeClock` 和 `installSandboxClock` 的默认路径不再执行 `if (proto && proto.length !== 0) proto.length = 0;`。没有换成另一个常量，没有再写一处 length。`RealFunction.prototype.constructor=fn`、两处 `trimInCompartment` 和 `leadingPadSource` 没改。

helper sha256 `edce262177341ff8d0c01c69ea0f1e67b92ef2a747db09d9e461709d08817be3`。scope `535f4944dfc84bb3b47d1cda5535bb6b41e027776cd8db7f21c788edf2c552c8`。上一档 `c03b9b60785cc282667c7489e2b9d7dd37e4ae1d749dfc9f6c850dbd1a57e922` 与 baseline `5d58653574064594bab0dc6dc73a493b` 留在 priorScope。

官方 baseline `13e79448ee6a4d55b6dff4d705bdfa0b`：pid 38000，exitCode 1，timedOut false，耗时 23325646300 ns。停点仍是源文件外第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`。raw sha256 仍是 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`。

同一张 side 记下：第 55373 列调用的实参是原始数字，来源是 `call-argument`，holder 是 `primitive`，`this` 与 realm 是 `Sandbox`，callee 编译入口是 `eval`。慢脚本本身的编译入口是 `eval`，realm 是 `Sandbox`，`compileMatch` 是 `source`。

随后 `next` 是 `verify_host_execution` / `blocked`，updatedAt `2026-10-22T07:01:33Z`。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。
