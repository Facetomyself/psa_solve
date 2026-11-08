# 页面 Date 的时钟留在页面内

2026-10-21。回执 `f970b6fc4a674df984364ea884a94e01` 上的盖章仍是 `repair_submit_host_behavior`，`turnGate=blocked`。只改了一处，没有再跑 `next`。

上一回页面 `Function` 已经在页面区诞生 `Patched`，但传进去的 `current` 仍是 `Cu.exportFunction` 包过的 chrome `now`。每次无参 `new Date()` 都离开页面。`iframe-parent.json` 仍是 `observe` 1、`entries` 1，观察者有触发。看门狗停在第 1 行第 1337365 列，对应先前长度为 1337363 且没有返回的那次 eval。

这一处只改时钟来源。`challengeDateInstallBody` 在页面函数里捕获原生 `RealDate.now`，按挑战锚点自己计算 `current`，再交给已有的 `challengeDate`。调用改成 `factory.call(host, host.Date)`，不再把 chrome `now` 传进去。返回空或抛错时不替换构造器。沙箱调用仍不带构造器开关。脚本时限仍是 13。真 eval 仍在。`setTimeout` 没有替换。`__watchEval` 没有打开。

`test_shipped_window_date_constructor_uses_challenge_clock` 从已发布 helper 抽出安装体，用 `new Function` 跑 12 项检查，输出 `date-ok 12`。

helper sha256 `f7ea7358e85384f342a5c4b0b77ceec37a0415fe6205060744243c1413d4cbe0`。scope `2d6dfc952924bfd95e684b9157e046348ddc25c9a9f27a682fcbef1e103760e5`。priorScope 是 `40ffac4b2c670dd8`，其中 baseline 是 `f970b6fc4a674df984364ea884a94e01`。runner sha256 仍是 `31746c03fd9890d48317faec1e2aa5ff5f99c7d63e0ce27c87b0956a5fa54d8a`。geckoLib 仍是 `9f21705d909f5e5c11bcf06af2187be7446b2112974090a3981e04a3cd11ce61`。`load_scope` 通过后才跑。

官方 baseline `13a5d2e400e74067934b6155d4063651`：status=failed，exitCode=1，timedOut=false，墙钟约 22.711s。失败原因是执行未成功完成。raw 只有 `host-diagnostic` 和 `summary`。诊断是第 1 行第 55371 列，matched false，base=`object`。scriptError 是 class=`slow-script`，kind=`other`，sourceClass=`other`，sourceForm=`token`。`getEntries` 仍是 function，`finished` 为 true，`threw` 为空。host-observation 为 0。`iframe-parent.json` 仍是 `observe` 1、`entries` 1，大 eval 进出计数为 0。没有证书 document POST。调用点仍是第 75507 列。

页内 `current` 修改与慢脚本落点从第 1337365 列回到第 55371 列同时出现。这只是落点相关，怀疑跨区调用或时钟读数影响了执行。当时 `__watchEval` 没有打开，raw 没有同一条 eval 的输入、进入、返回或 realm 记录。不能写成「那次 eval 已经返回」或「跨区 `new Date()` 是原因」。第 55371 列仍不是 `HTMLFormElement.submit`。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。第 55371 列没有写成观察。
