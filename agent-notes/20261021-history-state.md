# history.replaceState / pushState 只吞 SecurityError

2026-10-21。盖章是 `repair_submit_host_behavior`，`turnGate=blocked`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。绑定失败是 about:blank 注入脚本上的 `SecurityError`。案例记录里，about:blank viewer 的 `history.replaceState` / `pushState` 会抛这个错误。本拍只加 `installHistoryState`：原函数照常返回；只有 `SecurityError` 或消息含 `The operation is insecure` 时返回 `undefined`。其它异常继续抛出。调用点在 `installInlineXHR(this.window)` 之后、`orig.apply` 之前。没有恢复 Location、contentWindow、Window.prototype 兜底，没有 `addDebuggee`。

## 回归

`test_shipped_history_state_swallows_only_security_error` 抽出已发布的 `installHistoryState`，用 Node 驱动：`SecurityError` 返回 `undefined`，成功的 `pushState` 把参数交回原函数并返回原值，`TypeError` 继续抛出，第二次安装不重复包装。`test_default_path_isolates_unproven_identity_fallbacks` 通过。

## 重签与官方基线

helper sha256 `90929b5aa0925a6e01adf36d7edca3051dcff8ec04633980002a7b15a300d362`。scope `9748c9debe1a5d4a6b5256b9bfda7e8cdbe38214f4c46b4425bbfec7e8ca79bd`。`load_scope` 通过。`201ebcb1f13417f0e334bbbc6d57ff5aaa15e0836c59e24c65d210e12573682e` 与 baseline `ca950504b7124f57ad468e0893e93830` 留在 priorScope。

官方 baseline `18a7b243140a4bacb69f4c5cad907909`：failed，exitCode 1，timedOut false，pid 53260，约 9.079 秒。failure 是 `execution did not complete successfully`。绑定引用含 side，全部 `verify_ref` 通过。诊断仍是第 2 行第 3028 列，matched false，base object。事件只有 host-diagnostic 和 summary。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`，与 `ca950504` 相同。

side sha256 `6f73b50ff7ce929ad5fae37c8bfa9cf99e58519a88b443aba71bc586b26920d3`。scriptError：kind other，class other，sourceForm injected，sourceClass about-blank-injected，errorName `TypeError`，insecure false，parentLine 1447，sourceLineLength 0，keywordAtColumn false，stackShape other，receiverState unknown，receiverId uncollected。`access` 与 `threw` 仍是 null。没有 host-observation，没有请求行，没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
