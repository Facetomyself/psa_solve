# 放行注入 SecurityError 的同 scope 修补

2026-10-21。官方 baseline `ca950504b7124f57ad468e0893e93830` 的绑定 side 是 about:blank 注入脚本上的 `SecurityError`，第 2 行第 3028 列，`receiverState=unknown`，`receiverId=uncollected`。此前只要 side 带了 sourceForm / sourceClass，门就回到 `verify_host_execution`。

## 门

`_injected_blank_security_error` 只认这一组绑定字段：sourceForm `injected`，sourceClass `about-blank-injected`，errorName `SecurityError`，insecure true，parentLine 1447，sourceLineLength 0，keywordAtColumn false，stackShape `other`，flags 0，categoryClass `content-javascript`，receiverState `unknown`，receiverId `uncollected`。源文件第 2 行第 3028 列仍须是 `function` 关键字的最后一个字符，kind 与 class 仍是 `other`。

命中后动作是 `repair_submit_host_behavior`，`turnGate=blocked`。约束是 `same-scope`、`submit-callsite-only`、`one-host-behavior`、`no-completion-facts`，没有 `no-new-host-surface`。已观测的空接收者、历史占位 `receiverId="null"`、未绑定或被改过的 side，以及上面任一字段不同的邻近形状，仍是 `verify_host_execution`。

## 回归

`test_injected_blank_security_error_authorizes_one_host_repair` 走夹具采集器再调用已发布的 `next_command`。`test_shipped_ca950504_injected_security_error_authorizes_repair` 对真实 scope 与这份 baseline 调用已发布的 `_host_evidence_gate`，facts 文件字节不变。邻近形状、无 sourceForm 的 function 关键字放行、未绑定 side、历史 `69cede48` 占位，一并通过。9 项测试 OK。

## 盖章

`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T15:39:11Z`。动作 `repair_submit_host_behavior`，`turnGate=blocked`。原因指向第 2 行第 3028 列的注入 SecurityError，调用点是 `HTMLFormElement.submit` 第 1 行第 75507 列。

绑定 side 的 `access`、`threw` 仍是 null，顶层 `receiverId` 仍是 `uncollected`。这一拍不改 helper，不重签 scope，不跑 baseline。不恢复已离开默认路径的 Location、contentWindow、Window.prototype 兜底。没有证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
