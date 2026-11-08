# 2026-10-22 Window 可调用接收者越过第 98085 列

官方 baseline `c5ea593acece4f359aa568bb0cf8fe61`，scope `af18fb7f76360ac464daad343753f3763f4859e8abdfff6e7cf8d33a05fc6bce`，helper `05cc10733a4a5950c0ce3c7236ffc816ba0a4c338241d6984415d6bf6cda4176`。进程 11496，未超时，exitCode 1。没有证书 document POST，也没有同租约回读。

`installTurnstileScriptMarker` 仍是唯一宿主面。它在看到的 Window 上安装两个短名可调用接收者：`xdiN1` 与 `SSvM5`。调用次数仍是 1。

第 1 行第 98085 列的 TypeError 已离开。同一次 `j5` 在第 97865 列读到 `jrClass=Window`、`propertyName=Function`。当前脚本错误是第 1 行第 76877 列 TypeError，`frameName=jj`，`jjAtThrow=2`。这一次的属性名是 `xPLd9`，基对象类是 `Sandbox`，不是 marker 拿到的 Window。`receiverState` 仍是 `unknown`，`receiverId` 仍是 `uncollected`。没有 `host-observation`。

盖章仍是 `verify_host_execution` / `blocked` / `2026-10-21T20:18:30Z`。完成轴保持 false。Sandbox 上的查找没有打开新宿主面。
