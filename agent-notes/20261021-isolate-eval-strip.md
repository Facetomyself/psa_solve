# 大 eval 剥空白离开默认路径

2026-10-21。下午审计要求把不等价的大 eval 剥空白撤出默认安装，并先记下真实异常名、来源和接收者。本拍改了 helper、重签了 scope、补了回归测试。门、采集器、`ruyidom.js`、完成轴都没动。没有官方 baseline。

`stripLargeTrailingRegex`、`installLargeEvalStrip` 和 document 全局上的调用已从 helper 去掉。`__watchEval` 仍关闭。XHR 只在 `_async === false` 时于 `send` 返回前完成。PerformanceObserver 仍只 `armTimer(0)` 和 `armTimer(200)`。脚本时限仍是 13。`loadIdentityDocument` 仍不泵线程。

回归测试 `test_shipped_large_eval_strip_stays_off_the_default_path` 走已交付的 helper：文件里没有上述三个名字，document 安装切片不调用剥空白，`installInlineXHR` 仍在，`__watchEval` 未设为 true。审计反例在未改写时求值为 4。测试里一份未交付的本地拷贝把同一输入求成 3。打印 `eval-strip-off 4 3`。

helper sha256 `8c7a9ad1e29758b2274eab54092cb26370cc8c8b8d020ee5a127399dcc0f1fe2`。scope 重签为 `7eb3e7dd9771abb76ad703fa40fbeb16afcf8434e30dbb71b031f874bc986aa6`，status `issued`，executions 为空。`load_scope` 通过。priorScope 是整份旧 state：scope `75fe61cf541e6e34f494fdf1732f4adb6ddaf6d86473d065344f2418fa6e54d5`，官方 baseline `356e17e4159e4aee8da0a6cc37d3d8c8`。替换 helper 哈希前，runner、runtime、源、输入、配置、Node、CLI、Gecko 的 `verify_ref` 漂移为 0。

非正式探针不是 `execute()` 回执。剥空白离开默认路径之后，CLI 仍以非 JSON 结束，退出码 -1。侧记 `errors[0]`：name `SecurityError`，message `SecurityError: The operation is insecure.`，srcLabel `about-blank-injected`，parentLine 1447，line 2，column 3028，flags 0，category `content javascript`，sourceLineLength 0，keywordAtColumn false，receiverId null。stackShape `injected@2:3028|injected@2:3345|other@1447:10|other@1447:8|helper@1408:19|other@1191:12`。base 是 object，getEntries 是 function，finished false，access 与 threw 为空。采集器自己的 `scriptError` 仍只有 kind `other`、class `other`、line 2、column 3028。错误对象没有带上源行，所以这一列的关键字不是从抛错行读出来的。绑定文件上的结构位置不能当成宿主 API 的名字。本拍没有安装新 API。

同一 `SecurityError` 在剥空白已经离开默认路径之后仍出现。它不能证明剥空白造成了第 3028 列，也不能证明执行到了证书 document POST 或同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`，本拍没有改它。

`workspace.json.next` 仍是上一张 `repair_submit_host_behavior`，`turnGate=blocked`。本拍没有跑 `next`。executions 为空时，下一次 `next` 会回到 `run_host_baseline`。官方采集器仍不记 sourceName、错误消息和栈。那张回执不能单独补上这次探针里的身份字段，也不能写成提交进度。
