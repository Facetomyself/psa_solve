# 核验 TypeError baseline，不新开宿主面

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T15:49:46Z`，动作 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。本拍只调用已发布的 `load_scope`、`verify_ref`、`validate_execution`、`_bound_collector_side` 和 `_injected_blank_security_error`。没有改 helper，没有重签 scope，没有重跑 baseline。

## 工具结果

`load_scope` 通过。state、scope、回执的 scopeId 都是 `9748c9debe1a5d4a6b5256b9bfda7e8cdbe38214f4c46b4425bbfec7e8ca79bd`。

baseline `18a7b243140a4bacb69f4c5cad907909`：status failed，exitCode 1，timedOut false。回执 failure 与 `validate_execution` 抛出的原文都是 `execution did not complete successfully`。runner、runtime、input、source、config、raw、stdout、stderr、side，以及 scope 上的 helper、Node、CLI、Gecko 和静态依赖，全部 `verify_ref` 通过。

诊断第 2 行第 3028 列，matched false，base object。事件只有 host-diagnostic 和 summary。raw sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。side sha256 `6f73b50ff7ce929ad5fae37c8bfa9cf99e58519a88b443aba71bc586b26920d3`。

绑定 side：errorName `TypeError`，insecure false，sourceForm injected，sourceClass about-blank-injected，parentLine 1447，sourceLineLength 0，receiverState unknown，receiverId uncollected。`_receiver_observation` 返回 unknown。`_injected_blank_security_error` 返回 false，这份身份不落在 SecurityError 放行上。

## 完成轴

没有 host-observation，没有请求行，没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
