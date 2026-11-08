# 2026-10-22 Function 内容区裁剪已点名

`next` 盖章 `repair_function_in_compartment_pad` / `blocked`，updatedAt `2026-10-22T05:54:53Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

官方 baseline 仍是 `dd246d638d7e47f187effa8b799a2603`，第 1 行第 1337365 列，sourceForm `token`。raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`。helper sha256 仍是 `6e0303af3c9193ebd3437c9c63477f743df2125ff6f11948f08ec6a76b5d5d26`。scope 仍是 `576e53375865cd16bf7ce69818fb97cb9d735be04ef87aa5235b12065c837050`。

内容区 eval 已经调用 `trimInCompartment(code);`。这一处没有离开第 1337365 列。Function 工厂仍通过 `exportFunction` 调用 chrome 的 `leadingPadSource`，helper 里还没有 `trimInCompartment(body);`。

下一处只允许改 `installLeadingPadFunction` 里 `new host.Function` 的函数体，调用 `trimInCompartment(body);`。谓词不变：长度至少 100000、首字符是空白、末尾斜杠间隔 1 到 31。短脚本不裁。不得改 `leadingPadSource`，不得改 eval 的 `trimInCompartment`，不得改调用点，不得在 worker 的无 document 分支调用它。

本拍没有改 helper，没有重签，没有新的官方执行。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
