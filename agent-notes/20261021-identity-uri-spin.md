# 身份文档的真实 URI 在有界等待后提交

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T18:15:27Z`，动作 `repair_submit_host_behavior`，`turnGate=blocked`。约束含 `same-scope`、`one-host-behavior`、`submit-callsite-only`、`no-completion-facts`。本拍没有再跑 `next`。

官方 baseline `bca827a5a7b34eb79e3ffe3d14968597` 仍停在第 3 行第 586 列。该列是页面 `Function` 里的 `call`。分类器改动没有改变这张回执的 raw 与 side。

同一条 RuyiDOM 文档上，真实 document URI 类是 about，主体和 docshell 当前 URI 类是 https。内容 `replaceState` 传入空 URL 时写入 state。传入身份 https URL 时抛 `SecurityError`。chrome `addState` 同样抛 `SecurityError`。字符串通道打开后再等事件，真实 URI 类变成 https，同一个内容调用写入 state。

这一处只改 `loadIdentityDocument`。通道打开后 `spinEventLoopUntil` 等到 `rawDocumentSpec` 等于身份 URL，或满 1.5 秒。没有 `processNextEvent`，没有定时器。页面 `Function` 源串没有改，前缀仍是 99。Location、contentWindow、`Window.prototype` 兜底没有装回。没有第二处 history 包装。

带这处改动的同一安装路径，短文档调用身份 URL 的 `replaceState` 写入了 state，真实 URI 类是 https。构造墙钟 8405 毫秒，含原有 8 秒 iframe 泵，没有到 13 秒脚本预算。这不是 `host run` 回执。

helper 文件 sha256 `40861d5c88857957f0f80abef96b4a10ca38a7073b21d5ae7b2e7db893dcce32`。scope 仍是 `0aaf7b764e69bfdea2c8740159c5efce323c8de8cea649053c2b437a2ebf7cd8`，绑定 helper 仍是 `e89a87584ef1b37d1b47960a3cb5459d7edb68b97cbbfefe82b5b17861946db6`。未重签，未重跑官方 baseline。`load_scope` 报绑定文件哈希已变。直接门返回 `verify_host_scope`，`turnGate=blocked`。

回归 `test_shipped_identity_load_spins_until_real_uri_or_bound`、`test_identity_uri_spin_leaves_bca827a5_unrebased_until_verify`、`test_shipped_history_state_swallows_only_security_error`、`test_history_call_security_error_authorizes_one_host_repair`、`test_history_call_security_error_nearby_shapes_stay_verify`、`test_shipped_ca950504_injected_security_error_authorizes_repair` 通过。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。
