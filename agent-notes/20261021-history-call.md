# history 守卫改到页面 Function，不写完成轴

2026-10-21。`next` 会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`，updatedAt `2026-10-21T16:38:07Z`，动作 `run_host_baseline`，`turnGate=blocked`。上一回 `ea18496ee8c9455191d9b0ba4f70602e` 的 errorName `unknown` 来自跨区 `apply` 读取数组 `length` 被拒绝，不是 `SecurityError`。这一处只改已有的 `installHistoryState`：用页面 `Function` 安装守卫，`orig.call` 逐个传入 state、title、url。仍然只吞 `SecurityError` 或消息含 `The operation is insecure`。权限拒绝继续向外抛。没有改采集器，没有把这条异常改写成 `SecurityError`。

回归 `test_shipped_history_state_swallows_only_security_error` 和 `test_default_path_isolates_unproven_identity_fallbacks` 通过。三条具名参数能到达原函数。`apply` 被换成会抛空名字异常时，调用仍走 `call`。空名字的拒绝不会被吞掉。helper sha256 `dce0c26a11376011f3082f594f4c296d82e24d32984e363b8e3c463f4033839e`。scope 重签为 `cad998e64e5e73772ec42c3d32dd391e453d8c92b708a0107861d0db29ffa920`。`15346d164e2ca88f9cec427071dd7116646d6ccb3f745a904509ed9408ab8fae` 与 baseline `ea18496ee8c9455191d9b0ba4f70602e` 留在 priorScope。`load_scope` 通过。

官方 baseline `d0d52ad4073e4515b48f9d01c3d72c0c`：failed，exitCode 1，timedOut false，pid 52420，约 6.672 秒。failure 是 `execution did not complete successfully`。runner、runtime、input、source、config、raw、stdout、stderr 的 `verify_ref` 通过。没有 side 文件。raw 47 字节，sha256 `b441668b639a2f5131505f3e9f487cc348c64e5bc5162cebe63f8cede6702d32`，只有一行 summary，`ok` 为 false。没有 host-diagnostic，没有 host-observation，没有请求行。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是 `ok`。facts revision 仍是 53。
