# 接住的 SecurityError 交给现有监听器，scope 已重签

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T16:59:58Z`，动作 `verify_host_scope`，`turnGate=blocked`。约束含 `no-new-host-surface`、`legacy-unverified`、`goal-incomplete-does-not-override`。原因是绑定文件已变，先重建工具 scope，不抹旧事实。

`d0d52ad4073e4515b48f9d01c3d72c0c` 的采集器退出码是 1，stdout 和 stderr 都是 0 字节，因为采集器把子进程标准流丢掉，自己只把行写进 raw。raw 只有 `summary.ok false`，是因为 side 文件不存在。监听器只在未捕获、非警告、行号至少为 1 的脚本错误上写 side。`new RuyiDOM` 返回后才会把 `finished` 写进 side。页面 `Function` 把 `SecurityError` 接住并返回 `undefined`，这条异常到不了监听器；构造函数没有返回，结束写也没有发生。

这一处只改已有的 `installHistoryState`。接住 `SecurityError` 或 `The operation is insecure` 之后，若页面窗口有 `reportError`，先把同一个异常对象交给它，再返回 `undefined`。`reportError` 缺失或抛错仍留在这次吞掉里。TypeError 和空名字的权限拒绝继续向外抛。没有第二处 history 包装，没有改采集器分类，没有把这条异常改写成别的列号。

`test_shipped_history_state_swallows_only_security_error`、`test_shipped_collector_records_reported_history_security_error` 和 `test_default_path_isolates_unproven_identity_fallbacks` 通过。前者确认 SecurityError 会进入 `reportError`，抛错的 `reportError` 仍返回 `undefined`。采集器测试把该异常送进已发布的 `describeScriptError`：`errorName` 为 `SecurityError`，`insecure` 为 true，记录里没有消息正文。`collect_rows` 在有这个身份时写出 host-diagnostic。没有 side 时仍只有 `summary.ok false`。行号 0 的描述不会被监听器条件留下。

helper sha256 现为 `4d372380e88455b1423b8b7cfa55d6ec7edf7f69384eb0e3e24e5be8bce57499`。scope 重签为 `bd277f696a4110228c3c645a5f46d66c8dc5bddb8a4a016a5939e11d9fbbad0f`。只换了 helper 引用。`load_scope` 通过。状态是 `issued`，`executions` 为空。`cad998e64e5e73772ec42c3d32dd391e453d8c92b708a0107861d0db29ffa920` 与 baseline `d0d52ad4073e4515b48f9d01c3d72c0c` 留在 priorScope。本拍没有重跑 baseline。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。
