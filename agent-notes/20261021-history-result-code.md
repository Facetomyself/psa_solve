# 2026-10-21 history result/code 分类

盖章 `repair_submit_host_behavior`，`turnGate=blocked`，updatedAt `2026-10-21T18:02:16Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再跑 `next`。

上一张官方 baseline `e11524b7d3994378bb59ec4192d7c18a` 停在源文件第 3 行第 586 列。该列仍是页面 `Function` 里的 `call`，前缀 99。`QueryInterface` 路径没有让回执离开这一列。

这一处只改 `installHistoryState` 里的 chrome `historyExceptionInsecure`：

- nsresult 常量放进独立 try。缺少 `Components` 时分类函数返回 false，不再把异常抛出页面 `catch`。
- 对象自身的 `.result` 等于该常量，或 `code` 为 18，算命中。
- `QueryInterface` 到 `nsIException` 后，名字命中或 result 命中才返回 true。查询抛错则这一支为 false。
- `defineAs` 抛错时再导出一次并赋值。
- 页面 `Function` 源串没有改。空名字拒绝和 `TypeError` 仍抛出。

节点回归 `test_shipped_history_state_swallows_only_security_error`、`test_history_call_security_error_authorizes_one_host_repair`、`test_history_call_security_error_nearby_shapes_stay_verify` 通过。

helper sha256 `e89a87584ef1b37d1b47960a3cb5459d7edb68b97cbbfefe82b5b17861946db6`。scope 重签为 `0aaf7b764e69bfdea2c8740159c5efce323c8de8cea649053c2b437a2ebf7cd8`，status 先是 `issued`，executions 为空。`f6fcf62ec9f730c0a0d66b453827ac1e758a9d43b8eb9fc1fd812f07b5cc4f91` 整份 state（baseline `e11524b7d3994378bb59ec4192d7c18a`）留在 priorScope。`load_scope` 通过。没有用 `create_scope`。

官方 `host run --variant baseline --timeout 90` 没有 `--allow-network`。回执 `bca827a5a7b34eb79e3ffe3d14968597`，execution sha256 `629ba01224714c298c202e4d560445a0725b7a3b2ac387f6bafb5bb6b2bd95ca`。status `failed`，exitCode 1，timedOut false，pid 6540，elapsedNs 3260981700。failure 是 `execution did not complete successfully`。stdout 与 stderr 为空。raw 221 字节，sha256 `b7203663851d548e681db159d2022ffcce929a5d52ecb951e4def2276ab668c3`。side 470 字节，sha256 `6d5189e177ba8ed066c8790de393ea38a11b924fa93d1d2abcaa763914f88226`。这两个哈希与 `e11524b7` 和 `8f3d0b6d0cab4fde811c3be60ac8fda6` 相同。事件只有 `host-diagnostic` 和 `summary`。诊断第 3 行第 586 列，matched false，base `object`。side 仍是 kind/class/sourceForm/sourceClass `other`，errorName `SecurityError`，insecure true，parentLine 0，sourceLineLength 0，keywordAtColumn false，stackShape `other`，flags 0，categoryClass `content-javascript`，receiverState `unknown`，receiverId `uncollected`，finished false。没有 `host-observation`，没有请求行，没有到第 75507 列。

没有证书 document POST，也没有同租约回读。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。facts 与 dispatcher 字节在这次 `host run` 前后没有变。

直接调用门仍返回 `repair_submit_host_behavior`。这不是新盖章。完成轴没有写。
