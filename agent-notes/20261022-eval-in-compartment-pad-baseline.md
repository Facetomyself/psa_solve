# 内容区 trimInCompartment 后的官方 baseline

2026-10-22。会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。

只改了 `installLeadingPadEval` 里 `new host.Function` 的函数体。内容区定义 `trimInCompartment`，并调用 `trimInCompartment(code);`。裁剪用该区自己的 `charCodeAt` 和 `slice`，谓词与已有首尾空白规则相同。短脚本不裁。函数体不再调用 chrome 的 `pad(code)`。`leadingPadSource`、Function 包装、调用点和 worker 无 document 分支都没动。

helper sha256 `6e0303af3c9193ebd3437c9c63477f743df2125ff6f11948f08ec6a76b5d5d26`。scope `576e53375865cd16bf7ce69818fb97cb9d735be04ef87aa5235b12065c837050`。priorScope 是 `f6a91ef0959d48e37cae4a21ac27fd5dda9198f09b99884e71e0099026c2d1e4` / baseline `9c7ea1fbdc0d4dcaa7dd191158a24c1d`。

第一次采集 `320061a99057413bad129f5c600f92ec` 在采集器时限处结束，回执没有绑定 side，raw 只有未完成的 summary。这张不是停点。

绑定的官方 baseline `dd246d638d7e47f187effa8b799a2603`，execution sha256 `4161f8e08b3a2442733b0941ddc4180d3b28b96ddd1afcd64b5f788fee5cf345`。pid 41296，exitCode 1，timedOut false，耗时 24727822400 ns。失败文本仍是 execution did not complete successfully。

诊断仍是第 1 行第 1337365 列，kind other，class slow-script，sourceForm token，sourceClass other。没有 errorName，没有接收者字段。raw sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，225 字节。side sha256 `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`，642 字节。与上一发相同。事件只有 host-diagnostic 和 summary。summary.ok 不是 serverAccepted。matched false。wire 0。没有到第 75507 列。

同一列没有离开。内容区裁剪没有把绑定停点移开。

`next` 盖章 `verify_host_execution` / `blocked`，updatedAt `2026-10-22T05:44:49Z`，含 `no-new-host-surface`。不得再发未点名的宿主修复。

没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 ok。`hostProbe` 仍是 null。facts sha256 仍是 `3440737267cfafd35667c1c836d4425a49ed46b409c8486e7e82fcd2473f44a9`。
