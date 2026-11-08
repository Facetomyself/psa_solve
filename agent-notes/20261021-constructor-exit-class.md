# 构造器提前退出是引擎中止

2026-10-21。`next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有改 helper，没有改采集器，没有写完成轴。

在已保存的 `d3ec59e2` 探针上，给 `new RuyiDOM` 加了 try/finally。可捕获异常会先把 `constructorExit=thrown` 写进 side，再抛出。构造器正常返回则写 `returned`。side 只记异常名、种类、行号、列号和消息长度。

同一探针跑了两次，墙钟 19.475 秒和 19.48 秒，CLI 都是 1，side 都不存在。finally 没有写成文件。CLI 错误码是 `RUYIDOM_OUTPUT_PARSE_FAILED`，会话层 exitCode 为 -1。stderr 尾部在慢脚本栈的底部帧之后是两次 FATAL ERROR：非本地网络被禁止，连接目标是 `firefox.settings.services.mozilla.com`。尾部帧列是 56684、65697、28952、8055、9081，与 `b841fe67` 那份慢脚本栈的底部一致。1337365 不在这 10 行尾部里。

这不是 `RuyiDOM.main` 能接住的构造器异常。进程被引擎的非本地连接 FATAL ERROR 中止，所以 side 写不出来。盖章不允许新宿主面，helper 没有改。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。
