# 剥空白离开默认路径后的官方 baseline

2026-10-21。`next` 给出 `run_host_baseline`，`turnGate=blocked`，约束含 `no-new-host-surface`。本拍只跑了一次 `host run --variant baseline --timeout 90`。没有改 helper、门、采集器。没有写完成轴。

scope `7eb3e7dd9771abb76ad703fa40fbeb16afcf8434e30dbb71b031f874bc986aa6`。helper sha256 `8c7a9ad1e29758b2274eab54092cb26370cc8c8b8d020ee5a127399dcc0f1fe2`。runner sha256 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。

官方 baseline `dd3f7a2723a4487ea116c04c650425d9`：status `failed`，exitCode=1，timedOut=false，pid 36328，约 9.1s。failure 是 `execution did not complete successfully`。stdout 与 stderr 都是空文件，sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`。argvHash `5792c9c356a0ef8cd7fd02b39da6a8b3d3e8dc8edb299c30180e857d3c31b4ff`。

raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 priorScope 里的官方 baseline `356e17e4159e4aee8da0a6cc37d3d8c8` 字节相同。事件只有 `host-diagnostic` 和 `summary`。诊断是第 2 行第 3028 列，matched false，base 是 object，sourceSha256 `262a1bf5d34372c576dee9a5941b7ae491f20b496ed6108fb072ae632c6c36cd`。没有 `host-observation`。raw 没有请求行。

side：base `object`，getEntries `function`，finished false，access、threw、receiverId 都是空。`scriptError` 只有 kind `other`、class `other`、line 2、column 3028。官方采集器仍不记 sourceName、错误消息和栈。`summary.ok` 只是摘要事件里的字段，执行状态仍是 failed。

这张回执没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。列号与上一张官方 raw 相同，不能写成提交进度。非正式探针里的 `SecurityError` 仍只在 `agent-notes/20261021-isolate-eval-strip.md`，没有进入这张官方 side。
