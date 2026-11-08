# 转发 history 的具名参数，不写完成轴

2026-10-21。绑定源第 2 行长度 23576，第 3028 列仍是两参数 `<` 函数的 `function` 关键字末尾。这个函数体只有比较。官方 baseline `18a7b243140a4bacb69f4c5cad907909` 的绑定 side 是注入 `TypeError`。同一 helper 的非正式探针把该消息归类为 `History.replaceState` 至少要 2 个参数、实际 0 个。包装函数把原始 `arguments` 交给 `apply` 时，原生方法看不到内容参数。

这一处只改已有的 `installHistoryState`。`replaceState` 和 `pushState` 改为把具名的 state、title、url 放进本区数组再 `apply`。仍然只吞 `SecurityError` 或消息含 `The operation is insecure`。不读 `arguments.length`，不吞 `TypeError`，不加第二层包装。

读 `arguments.length` 会变成对属性 `length` 的权限拒绝。把该权限拒绝也吞掉之后，进程以退出码 -1 结束，没有 side。因此这一拍不吞权限拒绝。

回归 `test_shipped_history_state_swallows_only_security_error` 和 `test_default_path_isolates_unproven_identity_fallbacks` 通过。helper sha256 `e65aedaadb76f459838aa88854d4859b2f7eaa4ec92bbedb650b01e437e90742`。scope 重签为 `15346d164e2ca88f9cec427071dd7116646d6ccb3f745a904509ed9408ab8fae`，`9748c9debe1a5d4a6b5256b9bfda7e8cdbe38214f4c46b4425bbfec7e8ca79bd` 与 baseline `18a7b243140a4bacb69f4c5cad907909` 留在 priorScope。`load_scope` 通过。

官方 baseline `ea18496ee8c9455191d9b0ba4f70602e`：failed，exitCode 1，timedOut false，pid 3036，约 9.081 秒。failure 是 `execution did not complete successfully`。诊断仍是第 2 行第 3028 列，matched false，base object。事件只有 host-diagnostic 和 summary。raw 仍是 222 字节，sha256 `534609ca23a0472c035bc74092454398420761e448eb632583db28adac35ac2c`。side sha256 `ebd3d3603608218e5feacc0f6b69707a273c15faa065effb27850cf1acd2496c`。errorName 现为 `unknown`，insecure false，parentLine 1447，接收者 unknown。同一 helper 的探针把这条消息归类为权限拒绝，被拒属性是 `length`。没有 host-observation，没有请求行，没有证书 document POST，没有同租约回读。

`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。
