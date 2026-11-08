# 页面 Date 构造器身份

日期：2026-10-21

动作：`repair_submit_host_behavior`。只改 `challengeDate`。

## 上一回为什么没动

`c9d67de103124d38bbc60b3ea4370527` 把 `getEntries` / `getEntriesByType` 放进页面 `Function`。官方 raw 225 字节，与 `e9251003e0514f5d8dd6b4d39debe9fd` 相同。侧记 `entries` 仍是 1，`observe` 仍是 1。一次读取不是这段 13 秒慢脚本的热路径，返回值形状也没进 raw。所以落点停在第 1337365 列。

## 这一处

页面实例改为挂在 `Patched.prototype` 上。`constructor.now` 与 `Date.now` 使用同一个页内时钟。原 `Date.prototype` 保持不动，沙箱时钟不改。

已有测试 `test_shipped_window_date_constructor_uses_challenge_clock` 执行了这具函数。通过，0.119s。探针打印 `date-ok 16` 和 `clock-branch-ok 20`。

## 重签

- helper sha256 `556d4516b805cd313008837b06ddce33d06366868e54cdd13e1c26cae3cd5cac`
- scope `6d9a3c422ced0bc1944a2708e3084601d55a167de64efa0f6d57de55a4c84846`
- priorScope `12e9914655ebf4fd56fe6b3fb1b7ac10c74831a1dd8084d759280721bf3714e5`，baseline `c9d67de103124d38bbc60b3ea4370527`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`31dafe09fa2f425e83b49fa3374b33e3`：exitCode=1，timedOut=false，约 22.72s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `c9d67de103124d38bbc60b3ea4370527` 字节相同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。`entries` 1，`observe` 1。侧记没有 `__clockCtor`。这次不能证明页面构造器安装已经生效，也不能把列号当成 eval 已返回或没有网络请求。

没有其他事件行。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。调用点仍是第 75507 列。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
