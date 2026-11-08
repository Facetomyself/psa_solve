# 2026-10-22 Function 内容区裁剪后仍停在 1337365

`next` 盖章 `verify_host_execution` / `blocked`，updatedAt `2026-10-22T06:03:15Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

这一处只改 `installLeadingPadFunction` 里 `new host.Function` 的函数体。内容区调用 `trimInCompartment(body);`，用该区自己的 `charCodeAt` 和 `slice`。谓词与已有首尾空白规则相同。短脚本不裁。没有调用 chrome 的 `pad(body)`。`leadingPadSource`、eval 的 `trimInCompartment(code);`、调用点和 worker 无 document 分支都没改。

helper sha256 `c5243aebccc7b87d7b65e5d264cf8159c87b7126ef054621113cf79bda5c75b0`。scope `b183fa222b5a4468a744f32e1815622d5d41de7f4bdd3d569ccb0a906460badb`。上一态 `576e53375865cd16bf7ce69818fb97cb9d735be04ef87aa5235b12065c837050` 与 baseline `dd246d638d7e47f187effa8b799a2603` 留在 priorScope。

官方 baseline `5c3f17cbcf0d4eefa23ba7ebef89787f`：pid 15636，exitCode 1，timedOut false，耗时 22920135800 ns。诊断仍是源文件外第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`。raw `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，side `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`。与上一发相同。

没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。
