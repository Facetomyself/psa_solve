# 沙箱文档全局的 XHR send

2026-10-21。`next` 是 `repair_submit_host_behavior`，`turnGate=blocked`。同一 scope 只改了一处：有 document 的新全局在已有沙箱时钟之后调用 `installInlineXHR`。没有 document 的全局仍然只装 worker 时钟，不装这层 `send`。没有改 XHR 的同步例外、状态映射、`load`/`error`、`loadend`，没有改采集器、`ruyidom.js`、脚本时限或 `__watchEval`。时限仍是 13。真 eval 仍在。

页面窗口上的 `send` 包不住另一个 realm 的 `XMLHttpRequest.prototype`。长度为 1337363 的 eval 停在自己的末列，调用发生在带 document 的全局上。同步 `open(..., false)` 仍在 `send` 返回前完成；缺省异步仍交给 `setTimeout(0)`。

`test_shipped_sandbox_document_xhr_finishes_sync_send` 跑过，输出 `sandbox-xhr-ok 9`。

helper 摘要变为 `b0b5e20dba9658e6079e4998d73ddf036f183157f3c91c2ee2622389346d7fa4`。scope 重签为 `01db0897026321906f1f3b796224c6b454d0a6578a56e245719ad5acb5585401`。上一份 state 整份在 `priorScope`：scope `2ff1f07db69c1c1179d38107dfc83404c8bcfd9812b0d721da06a187ba7e513c`，baseline `7e9d471ac9a34d5293ca66a8b58b448a`。

官方 baseline `d6d9e711c240447babb8ff9f5b108e8a`：status `failed`，exitCode 1，timedOut false，墙钟 22.716 秒。raw 225 字节，与 `7e9d471ac9a34d5293ca66a8b58b448a` 的 raw 字节相同，sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`。诊断是第 1 行第 1337365 列，matched false。side 已写出，kind `other`，sourceForm `token`，sourceClass `other`。源文件第 1 行长 120793，该列在源文件外。stderr 的 FATAL 计数是 0。没有 `host-observation`，没有 wire、necko、resp。没有证书 document POST，也没有同租约回读。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
