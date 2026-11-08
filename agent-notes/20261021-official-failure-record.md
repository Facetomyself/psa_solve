# 356e17e4 的官方失败记录已经在回执上

2026-10-21。动作仍是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。本拍用工具重核已绑定的 baseline `356e17e4159e4aee8da0a6cc37d3d8c8`，没有改 helper，没有重跑。

`host` 子命令只有 `scope`、`run`、`pair`、`classify`、`acceptance-policy`、`verify-readback`。失败记录的写入者是 `host_evidence.execute`：`validate_execution` 抛错后，它把异常字符串写入 `execution.json` 的 `failure`，并把 `state.executions.baseline` 指到这份回执。

本拍读到的就是这份记录：

- `load_scope` 通过。scope 前缀 `75fe61cf541e`，与 state 一致。state 指向该 `execution.json`，`verify_ref` 通过。
- status `failed`，exitCode 1，timedOut false。`failure` 为 `execution did not complete successfully`。
- 再调用 `validate_execution`，仍是这个 `ValueError`。成功谓词要求 status `completed`、exitCode 0、timedOut false，本回执在这里停下。
- raw 222 字节，sha256 前缀 `534609ca23a0472c`。事件是 `host-diagnostic` 和 `summary`。没有 `host-observation`。第 2 行第 3028 列，matched false。
- side class `other`，kind `other`，没有 sourceForm。`_out_of_file_slow_script` 返回 None。

没有另写一份完成回执。`fact record` 不写完成轴。没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
