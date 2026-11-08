# revision 9 盖章 repair_null_receiver_identity

状态：只执行这张盖章。helper 未改。scope 未重签。没有新的官方 baseline。完成轴未写。

`next` 对 contract revision 9、`currentHead` `fe16e144e1849df49e6d723680338fb0038cc424` 给出 `repair_null_receiver_identity`，`turnGate=blocked`。session 是本会话。约束是 `tool-evidence-required`、`ai-notes-are-not-facts`、`same-scope`、`no-new-host-surface`、`null-receiver`、`identity-bound`、`no-completion-facts`。没有 `one-host-behavior`。

官方 baseline 仍是 `02b1aecb92dd48d3b6edf237d0908795`。诊断仍是源文件内第 2 行第 3028 列，不是 `HTMLFormElement.submit` 第 1 行第 75507 列。side 仍是 about:blank injected `SecurityError`，parentLine 1447，源行长度 0，`stackShape` `other`，`receiverId` `null`。

这一拍没有加 Location、contentWindow、window 身份或 `Object.prototype`。没有改 `document-principal.js`。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。没有证书 document POST，也没有同租约回读。

阻塞：接收者仍空，这张盖章禁止未定位的宿主补丁。
下一步：本拍不再 `next`。
