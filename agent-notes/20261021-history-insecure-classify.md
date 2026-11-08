# 历史调用的 SecurityError 由 chrome 识别

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T17:16:54Z`，动作 `repair_submit_host_behavior`，`turnGate=blocked`。约束是 `same-scope`、`submit-callsite-only`、`one-host-behavior`、`no-completion-facts`，没有 `no-new-host-surface`。放行的身份是官方 baseline `6d17ea97bfbb437794d2b43fb9ef5065`：第 3 行第 487 列，errorName `SecurityError`，sourceForm `other`。该列在页面 `Function` 体里，落在 `return orig.call(hist,state,title,url)` 的 `return` 上。构造器没有写到 `finished`，所以这次异常没有被页面读法认出来，被重新抛出。

## 这一处改动

只改 `installHistoryState`。chrome 增加 `historyExceptionInsecure`：先读异常自己的 name 和 message，读不到再 `Cu.waiveXrays` 读一次。只有 `SecurityError` 或消息含 `The operation is insecure` 才返回 true。页面守卫先问 `host.__historyInsecure`。返回 false，包括空名字的权限拒绝，仍然抛出。`reportError` 仍只包在吞掉之后。`orig.call` 的三个参数没变，没有第二处 history 安装。

helper sha256 `28cb94c5274fcfe5ae7b7bb3add07ccd82834fea2ced9b5651d84e095a9b85f8`。scope 仍是 `bd277f696a4110228c3c645a5f46d66c8dc5bddb8a4a016a5939e11d9fbbad0f`，还指着旧 helper `4d372380e88455b1423b8b7cfa55d6ec7edf7f69384eb0e3e24e5be8bce57499`。本拍没有重签，没有重跑 baseline。

## 测试

`test_history_call_security_error_authorizes_one_host_repair` 对这条身份返回 `repair_submit_host_behavior`。邻近形状仍是 `verify_host_execution`。`test_shipped_history_state_swallows_only_security_error` 通过：页面能读到的 `SecurityError` 仍返回 undefined，`TypeError` 和空名字拒绝仍抛出，隐藏 name/message 但 waive 后是 `SecurityError` 的对象被吞掉，隐藏的空名字拒绝仍抛出。helper 文件已经和 scope 哈希不一致，所以 `test_shipped_6d17ea97_unbound_after_history_classifier_stays_verify_scope` 对已发布的 `_host_evidence_gate` 得到 `verify_host_scope`。facts 字节未变。

## 完成轴

没有新的证书 document POST，也没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。
