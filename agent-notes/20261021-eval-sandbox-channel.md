# 大 eval 包装改走沙箱通道

2026-10-21。`next` 是 `repair_submit_host_behavior`，`turnGate=blocked`。同一 scope 只改了一处：有 document 的新全局仍剥末尾短斜杠对之外的空白，再调用该 realm 的真 eval，但安装改用 `Cu.evalInSandbox`。没有 document 的全局仍然只装 worker 时钟。

上一回 `dd990f178b9746639d302788b53acb8b` 用 `new host.Function` 安装，正式列仍是第 1337365 列，raw 仍是 225 字节。这次动手前的探针不是 `host run`。探针只数进入次数和长度。`Function` 安装结果是 `yes`，长度达到 100000 的 eval 进入次数是 0。`__watchEval` 保持关闭。探针侧记仍是慢脚本第 1 行第 1337365 列，kind `other`，sourceForm `token`。

`test_shipped_large_eval_strips_padding_around_trailing_regex` 与 `test_shipped_sandbox_document_xhr_finishes_sync_send` 一起跑过，2 个测试，0.111 秒，OK。脚本时限仍是 13。采集器、`ruyidom.js` 和 XHR 完成时机都没改。

helper 摘要变为 `18a66513d10a9d841f0d7196b09e382865e41d633823daac5cbc1d8494f9ec08`。scope 重签为 `4b38ab2bb03779b64cac600f247718bd84ceb601f9a2c9753c1dc9daee0aa311`。上一份 state 整份在 `priorScope`：scope `f26367ddaa1ec1c1185a0d0fa682c40858e79ad56b1077a2e187245128905472`，baseline `dd990f178b9746639d302788b53acb8b`。

官方 baseline `f1e44ef3dfda48a4aaafa2752655b0c7`：status `failed`，exitCode 1，timedOut false，墙钟 22.715 秒。raw 223 字节，sha256 `12182cd6c06d7ee3ccffcfd184ea5722d8aefc78df91ca53e0c1305c3e5acc2f`。上一回 raw 是 225 字节，sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`。诊断是 helper 第 1439 行第 21 列，落在 `wrapped` 读取 `slot.origOpen` 的位置，matched false，base object。side 已写出，kind `other`，sourceForm `url`，sourceClass `helper`，class `slow-script`。stderr 与 stdout 都是空的，FATAL 计数是 0。raw 只有 `host-diagnostic` 和 `summary`，summary 的 ok 是 true。没有 `host-observation`，没有 wire、necko、resp。没有证书 document POST，也没有同租约回读。`HTMLFormElement.submit` 第 1 行第 75507 列没有出现在这张回执里。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
