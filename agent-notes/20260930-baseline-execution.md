# 2026-09-30 clean baseline execution

## 状态

- 结论：`terminal / record-rejected`。一次性 baseline 已真实启动并退出，未重启；治理回执登记失败，不把该失败误报成引擎失败或业务通过。
- 执行 PID：`30140`；启动 `2026-09-30T08:43:35.536999Z`，结束 `2026-09-30T08:44:06.335053Z`，exit code `0`。
- claim 只执行一次，fresh material 只生成一次；session 目录为受限证据目录中的本轮新目录。
- 执行前确认：RuyiDOM status healthy；原始 runner、clean candidate、`web-case.json`、`contracts/auto-decision-facts.json` hash 与 claim 一致；`factsUnchanged=true`。

## 观测摘要

- harness：`harnessHealthy=true`，RuyiDOM run `ok=true`、`timedOut=false`。
- 业务轴：`businessAccepted=false` / `not-proven`；没有独立业务 readback。
- `forms=0`、`submits=0`；没有 `cert` document POST；观察到 7 条受限请求边界，其中包含 challenge `/fo/` POST。
- widget complete 和 clearance cookie 相关观测不提升为业务接受；Worker/Blob/WebCrypto 诊断项均按 `probe-disabled` 记录，不能从 0 推断不存在。

## 登记阻塞

wrapper 生成的 `execution-receipt.json` 缺少合同要求的 `claimBindingSha256` 字段，`web_case.py ... --phase record` 因 `execution receipt fields invalid; business facts forbidden` 拒绝登记；同时实际结束时间比 claim 的 `executeBefore` 晚约 1.04 秒，不能篡改时间或重跑 claim。事实、`stop-search`、runner、candidate 均未修改。

## 证据

- 受限运行目录：`evidence/web/diagnostic-cleanup-baseline/restricted/3503f21ee6a34e33a35bbb52b1ee9dc2/`
- 执行回执：`.../execution-receipt.json`
- 引擎 stdout/stderr：`.../engine-stdout.json`、`.../engine-stderr.txt`
- 边界摘要：`.../boundary-summary.json`
- claim 绑定：`evidence/web/diagnostic-cleanup-baseline/claim-binding.json`
- 状态：`agent-notes/20260930-clean-baseline-state.json`

遗留：治理登记需修复 wrapper receipt schema/claim window 后另行审阅；本次预算已消费，禁止自动重启或重新 claim。
