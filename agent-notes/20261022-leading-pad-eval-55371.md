# 2026-10-22 首尾空白裁剪后停回第 55371 列

上一发停在源文件外第 1 行第 1337365 列。那是引擎对一次很长的 eval 给出的超时列，不是编排文件里的列。同长度的快速 eval 会返回。不返回的那次在末尾有一对很短的斜杠。

这一处只加在有 document 的新全局上，排在内联 XHR 之后、iframe 观察之前。长度至少 100000、首字符是空白、末尾 80 列里有一对间隔小于 32 的斜杠时，切掉首尾空白，再调用该全局原来的 eval。内部空格不动。短脚本、不以空白开头、末尾没有这对斜杠的源文保持原样。`Function.prototype.toString` 对这个包装仍返回原生 eval。没有 document 的全局直接返回，worker 早退不调用它。

没有装回空函数，没有安装 `xPLd9`。非等价的整段剥空白没有恢复。13 秒时限、编排脚本、采集器都没动。

改动前的 `web_case.py next` 盖章 `repair_submit_host_behavior` / `blocked` / `2026-10-22T01:47:09Z`，会话 `01a157d3-c8c9-76e3-83ec-35eb8dcbb741`。本拍没有再 next。

helper sha256 `6e378f769ed47f50a70f0c1d4265a29f165b110b3827eb62316606fa876b1d55`。scope 重签为 `8626c40c322aba3a01351495dff986d3cd4e073c0df11c46807e2e2f8f2c54fb`。`6760dadeedc30b869d7582deca6687326c7f20e375c5a6cdba26538cc7a626f5` 与 baseline `2b2536820c394f54ae680cb8a152e601` 留在 priorScope。`load_scope` 通过。

官方 baseline `8758d438996c4bb7af99c2c33959d13e`：pid 40552，exitCode 1，timedOut false，耗时 24727082500 ns。诊断是第 1 行第 55371 列，kind `other`，class `slow-script`，sourceForm `token`，sourceClass `other`。没有 errorName，没有接收者字段。`_receiver_observation` 仍是 `unknown`。side 的 propertyName 是 `Function`，propertyColumn 97865，jrClass `Window`。j5Entries 2，jjEntries 2，debuggee `released`。calleeEntry 2，calleeName `xPLd9`，calleeBase `Sandbox`，calleeColumn 75416，calleeSteps 960。servedScripts 2，blockedScripts 0，scriptRows 4。raw sha256 `731459ca7fda730ce26ddc27e4f3ef3736d0a3128466f0f987eb3c994773f2b9`，223 字节。side sha256 `ca42cb1f2f5e1f4b580c8b2c47052778518131c836d755800f8eb5421d8f22b3`，640 字节。这两份哈希与更早停在第 55371 列的回执相同。事件是 `host-diagnostic` 和 `summary`。`summary.ok` 不是 `serverAccepted`。matched false。没有请求行。

执行离开了第 1337365 列，也离开了第 76877 列和第 98085 列。新的停点是源文件内已放行的慢脚本第 55371 列，不是第 75507 列。`_out_of_file_slow_script` 仍返回 `repair_submit_host_behavior`。磁盘盖章仍是改动前那张。本拍没有按算出的门再改宿主。

没有证书 document POST，没有同租约回读。`localReproduced`、`serverAccepted`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 保持 `ok`。`hostProbe` 仍是 null。回到第 55371 列不是求解进度。
