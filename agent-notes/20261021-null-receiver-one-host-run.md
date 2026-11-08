# 空接收者放开一处同 scope 宿主行为

状态：门已改，`next` 已盖章。helper 未改。scope 未重签。没有新的官方 baseline。完成轴未写。

`02b1aecb` 的 side 仍是 about:blank injected `SecurityError`，parentLine 1447，源行长度 0，`stackShape` `other`，`receiverId` 字符串 `null`。这一形状的 `repair_null_receiver_identity` 去掉 `no-new-host-surface`，加上 `one-host-behavior`，`turnGate=run`。邻近形状仍返回 `verify_host_execution`，并保留 `no-new-host-surface`。

回归 `test_null_receiver_injected_security_error_yields_bounded_repair`、`test_null_receiver_injected_security_error_nearby_shapes_stay_verify`、`test_shipped_02b1_side_returns_null_receiver_repair` 通过。正式门读取 `02b1aecb` 的 side，facts 文件字节未变。

`next` 盖章：action `repair_null_receiver_identity`，`turnGate=run`。约束是 `tool-evidence-required`、`ai-notes-are-not-facts`、`same-scope`、`one-host-behavior`、`null-receiver`、`identity-bound`、`no-completion-facts`。没有 `no-new-host-surface`。session 是本会话，updatedAt `2026-10-21T14:19:19Z`。

盖章理由仍写明 receiverId 是 null。这一处不得重复已关闭的 Location、contentWindow、window 身份或 `Object.prototype`。本拍因此没有改 helper。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。

阻塞：宿主 API 仍未点名。
下一步：同一 scope 只做一处新的宿主行为，不写完成轴。
