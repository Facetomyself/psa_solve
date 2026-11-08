# 点名隔离数字原型 length 常量（2026-10-22）

官方 baseline 仍是 `5d58653574064594bab0dc6dc73a493b`，停在源文件外第 1 行第 1337365 列，sourceForm 仍是 `token`。raw/side 仍是 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84` / `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`。side 没有第 55371 列 length 条件的实际操作数，也没有慢脚本的编译入口和 realm。

`RealFunction.prototype.constructor=fn` 已经在 helper 里。默认的 `installChallengeClock` 与 `installSandboxClock` 仍执行 `if (proto && proto.length !== 0) proto.length = 0;`。这句是写在数字原型上的常量。

`next` 给出 `isolate_number_prototype_length` / `blocked`，updatedAt `2026-10-22T06:45:15Z`。下一处只允许把这句从这两处默认路径拿掉，不得换成另一个常量。同一拍的官方 side 要记下那个 length 读取的实际对象和来源，以及慢脚本的编译入口和 realm。不得新增包装。

helper sha256 仍是 `1709630ef99e24348c14ef41a7557695e9903609dbb5f5a8b3e00b4c9cef64c3`。scope 仍是 `c03b9b60785cc282667c7489e2b9d7dd37e4ae1d749dfc9f6c850dbd1a57e922`。没有改 helper，没有重签，没有新的官方执行。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。
