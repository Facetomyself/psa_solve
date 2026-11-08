# 页面 Date 安装侧记

日期：2026-10-21

动作：`repair_submit_host_behavior`。只放宽页面 Date 安装条件，并记下构造器是否装上。

## 上一回为什么不能证明

`31dafe09fa2f425e83b49fa3374b33e3` 把页面实例挂到 `Patched.prototype`。官方 raw 225 字节，与 `c9d67de103124d38bbc60b3ea4370527` 相同。侧记没有 `__clockCtor`。原型身份比较可以在跨区失败并留下 `split`，失败后才会做 chrome `now`。那次回执不能证明页面构造器装上。

## 这一处

安装条件改为 `Patched.now===current`、原型存在、`constructor===Patched`。不再因为 `Object.getPrototypeOf(Patched.prototype)!==RealDate.prototype` 拒绝。`rememberPageClock(this.window)` 在泵之前读回 `__clockCtor` 和 `__clockInstall`。`iframe-parent.json` 增加 `clockCtor`、`clockInstall`、`clockResource`。沙箱时钟、XHR、观察者、`getEntries` 和脚本时限没改。

`installSandboxClock` 仍在页面路径返回之后写 `resourceLoaderClock`。所以 `clockResource` 看到的是沙箱结果，不是页面安装结果。

已有测试 `test_shipped_window_date_constructor_uses_challenge_clock` 执行了这具函数，并要求 `date-ok 16` 与 `clock-branch-ok 26`。通过，0.124s。

## 重签

- helper sha256 `234b07381aecfb181eb3457f2f17955a0243570590cad277edf69b8735ea1279`
- scope `a067d37ed2116383bf164fe61dc9a70bcac402e0837ccffb8fc48fe934c400e7`
- priorScope `6d9a3c422ced0bc1944a2708e3084601d55a167de64efa0f6d57de55a4c84846`，baseline `31dafe09fa2f425e83b49fa3374b33e3`
- runner `31746c03fd9890d4` 与 geckoLib `9f21705d909f5e5c` 未变
- `load_scope` 通过后才跑官方 baseline

## 官方 baseline

`71bd1c190fde43a2b3551592e7de16dd`：exitCode=1，timedOut=false，约 22.72s。失败原因是执行未成功完成。

raw 只有 `host-diagnostic` 和 `summary`，225 字节，与 `31dafe09fa2f425e83b49fa3374b33e3` 和 `c9d67de103124d38bbc60b3ea4370527` 字节相同。与 223 字节的 `9d5ad8f983f04af599232c184804181a` 不同。诊断是第 1 行第 1337365 列，matched false，base `object`。侧记 kind=`other`，class=`slow-script`，sourceClass=`other`，sourceForm=`token`。

`clockCtor`=`installed`，`clockInstall`=`installed`，`clockResource`=`sandbox-throw`。`entries` 1，`observe` 1。其余计数是 0。页面构造器已经装上。`sandbox-throw` 是之后沙箱时钟盖掉资源标记。列号只记慢脚本落点，不能当成 eval 已返回，也不能当成没有网络请求。

没有其他事件行。没有工具证据证明证书 document POST 或约 5 秒后的同租约 HTTP 200 已发生。调用点仍是第 75507 列。

页面构造器已经装上，raw 仍与上一回相同，所以这段慢脚本不取决于安装失败。这不说明 submit 的原因。

`serverAccepted`、`localReproduced`、`requestBoundaryAligned` 保持 false。`experimentHygiene` 仍是 `ok`。
