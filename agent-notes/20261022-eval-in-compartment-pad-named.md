# 2026-10-22 内容区 eval 裁剪已点名

`next` 盖章 `repair_eval_in_compartment_pad` / `blocked`，updatedAt `2026-10-22T05:28:59Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

官方 baseline 仍是 `9c7ea1fbdc0d4dcaa7dd191158a24c1d`，第 1 行第 1337365 列，sourceForm `token`。raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`。helper sha256 仍是 `543b22003f008fe8fc07e93230bbb14c7b4a4ea1075aa9c61e053a924ac69170`。scope 仍是 `f6a91ef0959d48e37cae4a21ac27fd5dda9198f09b99884e71e0099026c2d1e4`。

页面窗、沙箱包装、有 document 的新全局都已经调用 `installLeadingPadEval` 和 `installLeadingPadFunction`。这些调用没有离开第 1337365 列。浏览器证据里同长度一类 eval 以空白开头，末尾 80 列里有一对间隔为 8 的斜杠，已有谓词对得上。裁剪函数仍在 chrome，经 `exportFunction` 读内容区字符串，内容区自己的 `charCodeAt` 没有做这次裁剪。

下一处只允许改 `installLeadingPadEval` 里 `new host.Function` 的函数体，调用 `trimInCompartment(code);`。谓词不变：长度至少 100000、首字符是空白、末尾斜杠间隔 1 到 31。短脚本不裁。不得改 `leadingPadSource`，不得改 Function 包装，不得新增调用点，不得在 worker 的无 document 分支调用它。

本拍没有改 helper，没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
