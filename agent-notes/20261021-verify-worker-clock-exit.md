# 重验 d3ec59e2：side 没写出，修补门不开

2026-10-21。`web_case.py next` 是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface`。没有改 helper，没有重跑，没有写完成轴。

对当前 state 的 baseline 调用 `host_evidence.validate_execution`。

- state status failed，scopeId 与 scope 一致，前缀 `089d6963ae6a5bae`。
- 回执 `d3ec59e2583f4bd1ab800fdaca77792c`：status failed，exitCode 1，timedOut false，variant baseline，墙钟约 19.708s。
- runner、runtime、input、source、config 五份绑定都与 scope 相同。
- `validate_execution` 抛出 `execution did not complete successfully`。
- raw 1 行，event 只有 summary，summary.ok false。stdout 与 stderr 长度都是 0。
- `submit-host-side.json` 不在该回执目录。
- `_out_of_file_slow_script` 返回空。它要求正好一条 matched false 的 host-diagnostic，以及 side 里的 slow-script。这次两条都不满足，所以不是 `repair_submit_host_behavior`。

保存的探针在 `new RuyiDOM` 返回之后才把 `finished` 写成 true 并 `writeJson`。这条 side 文件不存在，控制台监听也没有为非 warning、行号不小于 1 的错误留下文件。iframe 侧记仍是更早一次运行写出的，不是这回的 `pumpIframeParent`。因此这回没有慢脚本列，也没有证书 document POST 行。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。

同日再次 `next` 仍返回同一章。工具重读未变：scope 前缀 `089d6963ae6a5bae`，回执 `d3ec59e2583f4bd1ab800fdaca77792c`，墙钟 19.708s，五份绑定一致，raw 47 字节且只有 summary，stdout/stderr 长度为 0，side 不存在，修补门返回空。没有改 helper，没有重跑。
