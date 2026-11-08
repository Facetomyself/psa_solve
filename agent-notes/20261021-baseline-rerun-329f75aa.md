# 回执 bfd29989 无文件漂移，同 scope 官方 baseline 重跑失败

`web_case.py next` 是 `verify_host_execution`，`turnGate=blocked`，约束含 `no-new-host-surface` 和 `goal-incomplete-does-not-override`。没有改门，没有开新宿主面，没有写完成轴。

核对用已发布的 `load_scope`、`verify_ref`、`validate_execution`、`_out_of_file_slow_script`。

- scope 前缀 `66687399f484a9e2`。`scopeId` 与去掉 `scopeId` / `acceptancePolicy` 后的 canonical 一致。`load_scope` 通过。state.scopeId 与 scope 一致。
- 回执 `bfd29989deb2429db7c4ad22b78a2ff5` 的 runner、runtime、input、source、config 与 scope 相同，`verify_ref` 通过。
- 依赖 helper、node、cli、geckoExe、geckoXul、geckoPluginContainer、geckoMozglue、geckoLib 的 `verify_ref` 都通过。
- argvHash 与按 raw 路径重算的命令一致。raw、stdout、stderr 的引用通过。
- 没有漂移的文件，也没有漂移的 scope。失败原因是执行未成功完成：status=failed，exitCode=1，timedOut=false。`validate_execution` 抛出 `execution did not complete successfully`。`_out_of_file_slow_script` 返回空。

随后按官方命令重跑同一 scope 的 baseline，超时 90 秒。新回执 `329f75aa9405418dbc6332d9af2780a8`：status=failed，exitCode=1，timedOut=false，约 22.721s，failure 相同。raw 事件是 host-diagnostic、summary。没有 host-observation，没有 wire / necko / resp。诊断 matched=false，第 1 行第 1337365 列。side 只有 kind、class、sourceClass、sourceForm、line、column：kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。repair 仍为空。

旧目录 `evidence/host-executions/bfd29989deb2429db7c4ad22b78a2ff5` 仍在。官方 `host run` 把 state 的 baseline 槽换成了新回执。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 仍是 false。`experimentHygiene` 仍是此前的 `ok`。没有证书 document POST，也没有同租约回读。
