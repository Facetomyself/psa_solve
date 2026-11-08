# 2026-10-22 恢复已绑定的 host scope

本拍 `web_case.py next` 盖章 `verify_host_scope` / `blocked` / `2026-10-22T00:40:30Z`，会话是 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。原因是当时 helper 字节和 scope 里的绑定不一致，`load_scope` 失败。约束含 `no-new-host-surface` 和 `legacy-unverified`。没有再跑 `next`。

页面窗口上的 `Object.defineProperty` 还没进任何官方回执。这一拍把它收回上一次已绑定的 helper，sha `97b5fa2407f061c28dba05335045a698b5a5f9bd73e4b25d9753ea2fc8175d43`。scope 仍是 `c54954da9227aae50af956ec0145f80dedd71ccb3b5670083849c821e67e3313`。`load_scope` 通过。state 仍是 `failed`，baseline 仍是 `5a175cf8749a48258a04caa3041007cf`。没有重签，没有 `host run`，没有改 13 秒时限。

该回执的诊断仍是第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`。raw sha `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。`summary.ok` 不是 `serverAccepted`。

`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。没有证书 document POST，没有同租约回读。
