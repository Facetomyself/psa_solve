# 失败记录落盘后再跑 next 仍不放行

2026-10-21。官方失败记录笔记已经在盘上。本拍再跑一次 `next`，动作仍是 `verify_host_execution`，`turnGate=blocked`。约束含 `no-new-host-surface` 与 `goal-incomplete-does-not-override`。文档只允许写 `docs/web/index.md`。

本拍工具重核，不沿用上一份笔记：

- `load_scope` 通过。scope 前缀 `75fe61cf541e`，与 state 一致。scope 内 18 个绑定文件漂移 0。
- state 的 baseline 仍指向 `356e17e4159e4aee8da0a6cc37d3d8c8`，`verify_ref` 通过。
- status `failed`，exitCode 1，timedOut false。`failure` 仍是 `execution did not complete successfully`。
- 再调用 `validate_execution`，仍是这个 `ValueError`。
- raw 222 字节。事件是 `host-diagnostic` 和 `summary`。没有 `host-observation`。第 2 行第 3028 列，matched false。
- side class `other`，kind `other`。`_out_of_file_slow_script` 返回 None。

原因是 baseline 没有成功完成，不是文件或 scope 漂移。class `other` 的行内第 3028 列不放行宿主修补。本拍没有改 helper，没有重跑，没有新开宿主面。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
