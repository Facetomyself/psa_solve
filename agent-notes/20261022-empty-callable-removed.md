# 2026-10-22 撤掉三个默认空函数后停在第 98085 列

今早审计要求默认路径不再安装三个没有浏览器行为合同的空函数。本拍只撤这两处：`installTurnstileScriptMarker` 里的 `xdiN1` 与 `SSvM5`，以及 `installSandboxClock` 里的 `xPLd9`。没有换成别的桩。页面窗口和沙箱里已有的 `Number.prototype.length` 写入留着。13 秒时限、编排脚本、worker 早退都没动。Location、contentWindow、window 没有装回默认路径。

改动前的 `web_case.py next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T00:57:31Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再 next。

helper sha256 `14a1c0a751ed1cb0f8499f2f8a110205a0ab6c2a8ad916cab04ecfff5ac1f416`。scope 重签为 `c7ba301a032a89c1c455d7004475e94842fa2e085a5571688c3302b5194162d7`。`81b6ff83266bbab04448a816c44fabf92c27bbc0613eacc83a175dd7542bda92` 与 baseline `42fc0fca8bfd4b199850246006053bd3` 留在 priorScope。`load_scope` 通过。

官方 baseline `b5288af49577424284f95fd188a3b2f5`：pid 50524，exitCode 1，timedOut false，耗时 9283463100 ns。诊断是第 1 行第 98085 列，kind `other`，class `null-receiver`，sourceForm `other`，sourceClass `other`，errorName `TypeError`，insecure false。`receiverState` 是 `empty`，`receiverId` 是 `null`，这是采集器比较过的空接收者。side 的 propertyName 是 `xdiN1`，propertyColumn 97846，jrClass `Window`，frameName `j5`，j5Entries 1，receiverWatch `empty`，receiverWatchColumn 98085。debuggee 是 null。callee 字段为空。raw sha256 `d650d3aa3073d5f9d686d9c013ce6eff0d2c367905024ecb76e77abe515b0ee0`，223 字节。side sha256 `fb55d442756a9e8867babd62886763b7d6bd2ff815ea0eb94dfcedefa07a7293`，819 字节。事件是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。matched false。没有 `host-observation`，没有请求行。

没有到第 75507 列。`_out_of_file_slow_script` 对这一列返回空，因为放行仍只认第 55371 列的慢脚本。直接门是 `verify_host_execution`，约束含 `no-new-host-surface`，没有 `one-host-behavior`。磁盘盖章仍是改动前那张。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。列号离开第 55371 列不是求解进度。三个空函数没有装回去。
