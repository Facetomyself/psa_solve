# 第 98085 列 jz 的真实接收者

2026-10-21。官方路径只改了采集探针，没有改 helper，也没有新宿主面。`describeScriptError` 在没有读到绑定时仍写 `unknown` / `uncollected`。Debugger 在异常展开时读取帧环境里的 `jz`。只有第 1 行、列落在 `jz[ND(He.dk)](jr,jC)` 上，并且 `nsIScriptError` 也是第 1 行第 98085 列时，才把这份绑定写入 `scriptError`。

第一次只把 content window 加为 debuggee。baseline `08f1ac38ce2f4017bf2a0f71e6b45ef8`，scope `8631cd7ca5d822022624d72c7d0c0d6a51c340a9a5873185b17fb8638d4d6eeb`，`receiverWatch` 是 `armed`，接收者仍是 `uncollected`。编排脚本跑在沙箱里，不在那个 window 上。

第二次用 `addAllGlobalsAsDebuggees`，并在新 global 上补 debuggee。scope `a9d69f577c65b6a364348671ddb1158e9b86184ca26e575a3cae76dfbec3fdf5`，runner `6c346b231c836b4dbfe993ddbe43c8d1bb5b0907a3a3536d9bfce75f3ee5f31c`，helper 仍是 `75a3a9487b61a462ddf83ddd7c33ea0f1670651f505a84192993f717fdc69b85`。baseline `624f044972e0458d9ff39bc2df559881`，execution `38af6e8f35474ae5a6229b0482309afb9b0172c903d4950a97bf36a24756bbc4`，pid 52892，elapsedNs 9285735400，exitCode 1，timedOut false。side `f0d165315b9b5fa14350caa18937d6e2d13849b9da6646c6e21426b4b3d5906d`，574 字节。raw 与 `e5aa21bf` 相同，`d650d3aa3073d5f9d686d9c013ce6eff0d2c367905024ecb76e77abe515b0ee0`，223 字节。事件仍是 `host-diagnostic` 和 `summary`，没有 `host-observation`。

`jz` 的绑定是空：`receiverWatch` 是 `empty`，`receiverWatchColumn` 是 98085，`scriptError.receiverState` 是 `empty`，`receiverId` 是 `null`。这是读到的值，不是占位。class 仍是 `null-receiver`，`errorName` 是 `TypeError`，kind / sourceForm 仍是 `other`。调用点第 75507 列没有到达。

`next` 盖章 `verify_host_execution` / `blocked` / `2026-10-21T20:18:30Z`，约束含 `no-new-host-surface`，没有 `one-host-behavior`。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
