# 2026-10-22 转发访问器写到加载全局后停在源文件外

第 76877 列在 `jj` 里。采集器没有采样这一列的接收者，所以上一发是 unknown/uncollected，不是比较过的空接收者。历史第二次进入才在沙箱上读到 `xPLd9`。本拍没有把空函数装回去，也没有改采集器。

已有的 `installTurnstileScriptMarker` 仍是唯一改动面。读取时若 `pageClockWindow`、`resourceLoaderSandbox` 或最多 8 个 `resourceLoaderGlobals` 里已经有自己的函数，就把同一个转发访问器写到还没有该函数的加载全局上。`xdiN1` 和 `SSvM5` 都走这条查找。没有命中就返回 undefined。`xPLd9` 没有安装。Location、contentWindow、window 没有装回默认路径。13 秒时限、编排脚本、worker 早退都没动。

改动前的 `web_case.py next` 盖章 `verify_host_execution` / `blocked` / `2026-10-22T01:27:11Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再 next。

helper sha256 `533e343eb873776679911b7aa1444703fef8b98728545f3e64c29938cdbfde00`。scope 重签为 `6760dadeedc30b869d7582deca6687326c7f20e375c5a6cdba26538cc7a626f5`。`eacafdbe190e7e8cd6db2c33c034fb1dacb2702dca935e472a0ef1d0b7b50f7d` 与 baseline `0b75daed91e244a29e7dcad115cf5dfc` 留在 priorScope。`load_scope` 通过。

官方 baseline `2b2536820c394f54ae680cb8a152e601`：pid 55316，exitCode 1，timedOut false，耗时 24725735900 ns。诊断是第 1 行第 1337365 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。没有 errorName，没有接收者字段。`_receiver_observation` 仍是 `unknown`。side 的 propertyName 是 `Function`，propertyColumn 97865，jrClass `Window`，propertyWatch `step`，取样落在 97492 到 97876，共 233 步。j5Entries 2，jjEntries 2，jjAtThrow 空，frameName 空，debuggee `released`。calleeEntry 2，calleeName `xPLd9`，calleeBase `Sandbox`，calleeColumn 75416，calleeSteps 960。servedScripts 2，blockedScripts 0，scriptRows 4。raw sha256 `32a2ac26aae79d8d94a2c6b810846bad9e1dc16f36d8d5210a84f7a0b45bda84`，225 字节。side sha256 `b89ae10c0461d09f909ada6cf9308bcefd890e9554839670a4f63a3cd71363bc`，642 字节。事件是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。matched false。没有 `host-observation`，没有请求行。

第 97865 列仍读到 Function。执行离开了第 76877 列，也离开了第 98085 列。新的停点在源文件外，不是第 75507 列。`_out_of_file_slow_script` 返回 `repair_submit_host_behavior`，约束含 `same-scope`、`one-host-behavior`、`submit-callsite-only`、`no-completion-facts`，没有 `no-new-host-surface`。磁盘盖章仍是改动前那张 `verify_host_execution`。本拍没有按算出的门再改宿主。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。离开第 76877 列不是求解进度。
