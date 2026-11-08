# 重核 f1e44ef3 仍不放行

2026-10-21。本拍 `next` 仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。helper 没有改，baseline 没有重跑，完成轴没有写。

工具重核，不沿用上一份笔记：

- `load_scope` 通过。state scopeId 与 scope 一致，前缀 `4b38ab2bb037`。status `failed`。
- 绑定文件 `verify_ref` 漂移 0。
- `validate_execution` 抛出 `ValueError: execution did not complete successfully`。回执 status `failed`，exitCode 1，timedOut false，variant baseline。stdout 与 stderr 都是 0 字节。
- raw 223 字节，事件只有 `host-diagnostic` 和 `summary`。没有 `host-observation`。诊断第 1439 行第 21 列，matched false，行和列都是 int。
- side：class `slow-script`，kind `other`，sourceForm `url`，sourceClass `helper`，同一行同一列，finished true。
- 编排源 3 行。第 1439 行不在源内。`_out_of_file_slow_script` 返回 None。调用点仍是第 1 行第 75507 列。
- helper 第 1439 行含 `slot.origOpen`。第 21 列落在 `slot`。`proto.open` 的读取不在第 1439 行。

因此失败原因是执行没有成功完成，不是文件或 scope 漂移。行界已经让修补门返回空；kind `other` 且 sourceForm `url` 也不在放行分支。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`，本拍没有改它。
