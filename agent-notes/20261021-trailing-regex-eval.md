# 末尾短斜杠对外空白的真 eval

2026-10-21。`next` 是 `repair_submit_host_behavior`，`turnGate=blocked`。同一 scope 只改了一处：有 document 的新全局在已有 `installInlineXHR` 之后调用 `installLargeEvalStrip`。没有 document 的全局仍然只装 worker 时钟，不装这层。

上一回官方 baseline `d6d9e711c240447babb8ff9f5b108e8a` 把 `send` 装进有 document 的新全局后，列和 raw 都没动。这次动手前的探针不是 `host run`。探针计数里没有 `xhr-send`。进入和离开相差 1 的那次 eval 长度始终是 1337363。它的非空白计数是 30，数字 17，逗号 2，字母 4，其他 7，斜杠 2，圆括号 0，点 2，星号 2，斜杠位置 1337334，两斜杠间隔 9。更早、同样带填充、非空白更短的脚本有返回。第一段大脚本的非空白长度是 231843，包装在对外非空白超过 80 时不剥。探针当时打开了 `__watchEval`，正式路径没有这个开关。探针把慢脚本记成 helper、`sourceForm` url、第 1337364 列，那是观察包装自己的落点，不是正式分类。

包装只在长度至少 100000、末尾 80 列内有一对斜杠、间隔小于 32、对外非空白不超过 80 时，剥掉这对斜杠之外的空白，然后调用该 realm 的真 eval。短脚本、长数字表达式、间隔更大的斜杠对都不剥。`__watchEval` 保持关闭。脚本时限仍是 13。没有改采集器、`ruyidom.js`、XHR 完成时机或状态映射。

`test_shipped_large_eval_strips_padding_around_trailing_regex` 跑过，输出 `eval-strip-ok 7`。同一轮 `test_shipped_sandbox_document_xhr_finishes_sync_send` 仍是 `sandbox-xhr-ok 9`。

helper 摘要变为 `a9ee6e328351d5e0ab032b321a5af3e9a8cc84daa735e98fad55dd678ba2d259`。scope 重签为 `f26367ddaa1ec1c1185a0d0fa682c40858e79ad56b1077a2e187245128905472`。上一份 state 整份在 `priorScope`：scope `01db0897026321906f1f3b796224c6b454d0a6578a56e245719ad5acb5585401`，baseline `d6d9e711c240447babb8ff9f5b108e8a`。

官方 baseline `dd990f178b9746639d302788b53acb8b`：status `failed`，exitCode 1，timedOut false，墙钟 22.715 秒。raw 225 字节，sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，与 `d6d9e711c240447babb8ff9f5b108e8a` 字节相同。诊断是第 1 行第 1337365 列，matched false，base object。side 已写出，kind `other`，sourceForm `token`，sourceClass `other`。源文件第 1 行长 120793，该列在源文件外。stderr 与 stdout 都是空的，FATAL 计数是 0。raw 只有 `host-diagnostic` 和 `summary`，summary 的 ok 是 true，没有 `host-observation`。没有 wire、necko、resp。没有证书 document POST，也没有同租约回读。正式回执没有 eval 进入计数，所以这次回执不能单独证明包装是否执行。列和 raw 都没动。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
