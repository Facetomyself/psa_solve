# 沙箱 Date 使用页面构造器

日期：2026-10-21

动作：`repair_submit_host_behavior`。只改沙箱 `Date` 的构造器身份。页内 `performance.now` 的原点重定留着。

## 上一回

`3d4afa40cb5f42eab1bd37a301454f03` 让页内 `performance.now` 在挑战时钟回跳超过 12 小时后重定原点。官方 raw 225 字节，与 `71bd1c190fde43a2b3551592e7de16dd` 相同。落点仍是第 1337365 列。这次不把那段重定撤回。

## 这一处

沙箱原先让 `Patched.prototype` 等于 `RealDate.prototype`。实例的 `constructor.now` 因此仍是墙钟。页面路径已经把实例挂到 `Patched.prototype`。这一回沙箱调用同一个 `challengeDate`。`current` 的读写没改。

测试 `test_shipped_sandbox_date_constructor_uses_challenge_clock` 抽出这段安装体并执行。和页面 Date 测试一起通过，0.156s。探针要求 `sandbox-date-ok 9`：实例的 `constructor.now` 落在挑战锚点上，原 `Date.prototype.constructor.now` 仍是墙钟。

## 重签

- helper sha256 `bc85307e46064467ee5b4bc412e3ae50f4aa833238583a65ddff21aae78cee4d`
- scope `342ef8a0935dc7c039889db68542c3165015e66b30a3f6c752a52da098ac13e5`
- priorScope `6a05433781efa692eab37b85e82e8f9163b2090f82e61076aa04a0c13cdefa07`，baseline `3d4afa40cb5f42eab1bd37a301454f03`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`12894c3b70894772bf5c0fb65a2a252a`：exitCode=1，timedOut=false，约 22.72s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `3d4afa40cb5f42eab1bd37a301454f03` 和 `71bd1c190fde43a2b3551592e7de16dd` 字节相同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。

`clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-throw`。`entries` 1，`observe` 1。其余计数是 0。沙箱安装标记仍是 throw，所以这次不能证明沙箱构造器已经换上。列号只记慢脚本落点。

没有其他事件行。没有证书 document POST 行。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
