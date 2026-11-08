# 合同 revision 9，空接收者有界修复已进门

状态：`migrate_contracts` 已执行。helper 未改。没有新的官方 baseline。完成轴未写。

`next` 盖章是 `migrate_contracts`，`turnGate=blocked`，session 是本会话。缺的是 `metadata.currentHead`：文件里仍是 `d06b71100fe37c437ee6da96c21b059718ffe285`，仓库 HEAD 已是它的后继 `fe16e144e1849df49e6d723680338fb0038cc424`。`migrate-contracts --apply --case-class challenge --expected-revision 8` 把 revision 写成 9，`currentHead` 写成这个 HEAD。`web-case` 仍是 `challenge` / `patching`。已有 workflow 与 lineage 文件没有被模板覆盖。

同一拍里，`_out_of_file_slow_script` 对官方 baseline `02b1aecb92dd48d3b6edf237d0908795` 的直接调用返回 `repair_null_receiver_identity`。绑定源第 2 行第 3028 列仍是 `function` 关键字。side 仍是 about:blank injected `SecurityError`，parentLine 1447，源行长度 0，`stackShape` `other`，`receiverId` `null`。约束含 `no-new-host-surface`、`null-receiver`、`identity-bound`、`no-completion-facts`，没有 `one-host-behavior`。没有 `sourceForm` 的 function 关键字放行仍是 `repair_submit_host_behavior`。相邻身份形状仍是 `verify_host_execution`。

回归：`test_null_receiver_injected_security_error_yields_bounded_repair`、`test_null_receiver_injected_security_error_nearby_shapes_stay_verify`、`test_in_file_function_keyword_authorizes_one_host_repair`、`test_in_file_function_keyword_other_shapes_stay_verify` 通过。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。没有证书 document POST，也没有同租约回读。

阻塞：接收者仍空。这张有界修复不授权 Location、contentWindow、window 身份或 `Object.prototype` 补丁。
下一步：本拍不再 `next`。下一拍若 HEAD 未再移动，宿主门才会盖出 `repair_null_receiver_identity`。
