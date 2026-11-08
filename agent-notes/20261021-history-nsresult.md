# 2026-10-21 history nsresult

盖章 `contracts/dispatcher-turn.json`：`repair_submit_host_behavior`，`turnGate=blocked`，updatedAt `2026-10-21T17:43:53Z`，sessionId `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再跑 `next`，没有重签 scope，没有跑 baseline。

一处改动在 `diagnostics/shadowroot-repair-20261020/document-principal.js` 的 `historyExceptionInsecure`。已有的 waive 名字判断之后，对 waive 后的对象 `QueryInterface(Ci.nsIException)`。返回 true 只在两种情况：查询结果仍能认出 `SecurityError`，或 `result` 等于 `Components.results.NS_ERROR_DOM_SECURITY_ERR`。查询或读取抛错时落到 `return false`。空名字权限拒绝和 `TypeError` 继续抛出。

页面 `Function` 源串没有改。`_shifted_history_call` 仍为真：第 586 列记号是 `call`，前缀长度 99。helper 文件 sha256 `007d46580a8cef28f67b476c8a7f2feb28906bf28f91dd145d934c48e67ed174`。

`contracts/host-evidence/scope.json` 的 scopeId 仍是 `b82ca60163f25bc0bad569638074765efad8e9d18b89f84ce3f817da4f963fc1`，其中 helper sha256 仍是 `28cb94c5274fcfe5ae7b7bb3add07ccd82834fea2ced9b5651d84e095a9b85f8`。`verify_ref` 与 `load_scope` 都报 `bound file hash changed`。对未改的 facts 调用 `_host_evidence_gate` 得到 `verify_host_scope`，`turnGate=blocked`，约束含 `no-new-host-surface`。这不是新的盖章。

官方 baseline 仍是 `8f3d0b6d0cab4fde811c3be60ac8fda6`。status `failed`，exitCode 1，timedOut false，finished false。side 仍是第 3 行第 586 列 `SecurityError`，sourceForm `other`，insecure true。事件仍是 `host-diagnostic` 与 `summary`。priorScope 的 baseline 仍是 `6d17ea97bfbb437794d2b43fb9ef5065`。没有请求行，没有证书 document POST，没有同租约回读。

`contracts/auto-decision-facts.json` 字节未改。`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。revision 53。

回归从 `skill/web-reverse/tests` 跑了四项，2.959 秒，OK：`test_shipped_history_state_swallows_only_security_error`（出口 2 到 13 仍在，匹配的 nsresult 出口 14 吞掉，其它 nsresult 出口 15 抛出，安全名字出口 16 吞掉，抛错的 QueryInterface 出口 17 抛出）、`test_history_call_security_error_authorizes_one_host_repair`、`test_history_call_security_error_nearby_shapes_stay_verify`、`test_shipped_8f3d0b6d_helper_drift_returns_verify_scope`。

`docs/web/index.md` 仍是 80 行。`doc_health` 为 `[]`。
