# performance.now 跟随挑战时钟回跳

日期：2026-10-21

动作：`repair_submit_host_behavior`。只改页内 `performance.now` 的原点。

## 上一回

`71bd1c190fde43a2b3551592e7de16dd` 证明页面构造器已经装上。`clockCtor` 和 `clockInstall` 都是 `installed`。官方 raw 225 字节，与 `31dafe09fa2f425e83b49fa3374b33e3` 相同。落点仍是第 1337365 列。这段慢脚本不取决于安装失败。

## 这一处

页内 `now` 仍用 `Date.now` 减原点。原点如果停在回跳之前，差值会一直是 0。这一回读数比原点早过 12 小时时，把原点改到当前读数，之后的差值可以继续增加。不到这个幅度的回退仍记为 0。函数仍在页面里，没有改回 `Cu.exportFunction`。Date、沙箱时钟、XHR、观察者和 `getEntries` 没改。

已有测试 `test_shipped_performance_now_advances_from_date` 执行了安装体。通过，0.067s。小幅回退仍是 0。12 小时以上的回跳之后，再前进 40 毫秒得到 40。

## 重签

- helper sha256 `9e6203c6aa5eafe7eae93b397f341ab00172698b5623e17bbf8f434739e5a9c0`
- scope `6a05433781efa692eab37b85e82e8f9163b2090f82e61076aa04a0c13cdefa07`
- priorScope `a067d37ed2116383bf164fe61dc9a70bcac402e0837ccffb8fc48fe934c400e7`，baseline `71bd1c190fde43a2b3551592e7de16dd`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`3d4afa40cb5f42eab1bd37a301454f03`：exitCode=1，timedOut=false，约 22.71s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `71bd1c190fde43a2b3551592e7de16dd` 和 `31dafe09fa2f425e83b49fa3374b33e3` 字节相同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。

`clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-throw`。`entries` 1，`observe` 1。其余计数是 0。列号只记慢脚本落点，不能当成 eval 已返回，也不能当成没有网络请求。

没有其他事件行。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。调用点仍是第 75507 列。

落点没动，raw 与上一回相同。这次不能把原点重定写成慢脚本的原因。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
