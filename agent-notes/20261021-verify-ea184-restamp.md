# 再次核验 unknown baseline，戳记未授权宿主修补

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T16:26:26Z`，动作 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。上一张 16:22:55Z 的核验笔记已经落盘，这张是新戳记。本拍只调用已发布的 `load_scope`、`verify_ref`、`validate_execution`、`_bound_collector_side`、`_receiver_observation`、`_injected_blank_security_error` 和 `_host_evidence_gate`。没有改 helper，没有重签 scope，没有重跑 baseline。

## 工具结果

`load_scope` 通过。state、scope、回执的 scopeId 都是 `15346d164e2ca88f9cec427071dd7116646d6ccb3f745a904509ed9408ab8fae`。

baseline 仍是 `ea18496ee8c9455191d9b0ba4f70602e`：status failed，exitCode 1，timedOut false，pid 3036，`finishedAt - startedAt` 为 9081014400 纳秒，约 9.081 秒。回执 failure 与 `validate_execution` 抛出的原文都是 `execution did not complete successfully`。回执上的 runner、runtime、input、source、config、raw、stdout、stderr、side 全部 `verify_ref` 通过。

诊断第 2 行第 3028 列，matched false，base object。事件只有 host-diagnostic 和 summary。raw 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。side sha256 `ebd3d3603608218e5feacc0f6b69707a273c15faa065effb27850cf1acd2496c`。

绑定 side：errorName `unknown`，insecure false，sourceForm injected，sourceClass about-blank-injected，receiverState unknown，receiverId uncollected。顶层 access null，threw null，finished false。`_receiver_observation` 返回 unknown。`_injected_blank_security_error` 返回 false。`_host_evidence_gate` 仍返回 `verify_host_execution`，约束仍含 `no-new-host-surface`。这张戳记没有签发 `repair_submit_host_behavior`。

## 完成轴

没有 host-observation，没有请求行，没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。文件没有漂移。errorName `unknown` 不放行同 scope 宿主修补，所以本拍没有改宿主。
