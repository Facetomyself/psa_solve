# 02b1 正式门回归

状态：只加回归。helper 未改。scope 未重签。没有新的官方 baseline。完成轴未写。

`test_shipped_02b1_side_returns_null_receiver_repair` 读取 `evidence/host-executions/02b1aecb92dd48d3b6edf237d0908795/submit-host-side.json`，再调用已发布的 `_host_evidence_gate`。side 是 about:blank injected `SecurityError`，parentLine 1447，第 2 行第 3028 列，源行长度 0，`stackShape` `other`，`receiverId` `null`。

门返回 `repair_null_receiver_identity`，`turnGate=blocked`。没有返回 `verify_host_execution`。约束含 `no-new-host-surface`、`same-scope`、`identity-bound`、`null-receiver`，没有 `one-host-behavior`。因此没有同一 scope 的宿主行为改动，也没有新表面。

调用前后 `contracts/auto-decision-facts.json` 字节相同。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。

同一次还跑了 `test_null_receiver_injected_security_error_yields_bounded_repair`，通过。

阻塞：接收者仍空。
下一步：本拍不再 `next`。
