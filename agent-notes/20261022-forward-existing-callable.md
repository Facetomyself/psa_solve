# 2026-10-22 转发已有函数后停在第 76877 列

第 97846 列的读取是 Window 上的字符串名。名字不在源文件第 1 行。读空以后，第 98085 列抛出空接收者。本拍没有把空函数装回去，也没有改采集器。

已有的 `installTurnstileScriptMarker` 仍装在同一个 Window 上。这里只加转发：该名字还不是函数时，读取依次看 `pageClockWindow`、`resourceLoaderSandbox`，以及最多 8 个 `resourceLoaderGlobals`。命中的必须是对方自己的函数，并且不是这个转发器。没有命中就返回 undefined。随后写到 Window 上会换成可写数据属性。`SSvM5` 和 `xPLd9` 没有安装。Location、contentWindow、window 没有装回默认路径。13 秒时限、编排脚本、worker 早退都没动。

改动前的 `web_case.py next` 盖章 `verify_host_execution` / `blocked` / `2026-10-22T01:07:21Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再 next。

helper sha256 `dde5a34fd98958f98da6ff53022ab0c53ebca7252175ce4642fe5fa9a7f46ea4`。scope 重签为 `eacafdbe190e7e8cd6db2c33c034fb1dacb2702dca935e472a0ef1d0b7b50f7d`。`c7ba301a032a89c1c455d7004475e94842fa2e085a5571688c3302b5194162d7` 与 baseline `b5288af49577424284f95fd188a3b2f5` 留在 priorScope。`load_scope` 通过。

官方 baseline `0b75daed91e244a29e7dcad115cf5dfc`：pid 16532，exitCode 1，timedOut false，耗时 9286506200 ns。诊断是第 1 行第 76877 列，kind `other`，class `null-receiver`，sourceForm `other`，sourceClass `other`，errorName `TypeError`，insecure false。`receiverState` 是 `unknown`，`receiverId` 是 `uncollected`。这不是采集器比较过的空接收者。side 的 propertyName 是 `Function`，propertyColumn 97865，jrClass `Window`，frameName `jj`，j5Entries 1，jjEntries 1，jjAtThrow 1，receiverWatch `armed`，receiverWatchColumn 76877。propertyWatch 是 `step`，取样落在 97492 到 97876。debuggee 是 null。callee 字段为空。raw sha256 `6042c67cc178510a0d15014f8b019982f05d1610ab1fdb4908129990336bd289`，223 字节。side sha256 `3fb87bdede509de9005c2dfa364623723acd2dc79562b024a85d01dfd891c41f`，793 字节。事件是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。matched false。没有 `host-observation`，没有请求行。

第 97865 列读到 Function，说明这次 Window 查找没有再落空，执行离开了第 98085 列。新的停点是第 76877 列。回执没有给出这一列的属性名。没有到第 75507 列。`_out_of_file_slow_script` 返回空。直接门仍是 `verify_host_execution`，约束含 `no-new-host-surface`，没有 `one-host-behavior`。磁盘盖章仍是改动前那张。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。离开第 98085 列不是求解进度。
